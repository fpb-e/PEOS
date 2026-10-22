"""Black-box safety and import-plan checks for the ZIP importer CLI."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import warnings
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "peos_zip_import.py"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class ZipImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="peos-zip-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.archive = self.root / "input.zip"

    def make_zip(self, entries):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_STORED) as archive:
                for name, data in entries:
                    archive.writestr(name, data)

    def write_existing(self, path, data):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def snapshot(self):
        """Capture visible files, directories, and links without following links."""
        result = {}
        for current, directories, files in os.walk(self.repo, followlinks=False):
            for name in directories + files:
                path = Path(current) / name
                relative = path.relative_to(self.repo).as_posix()
                if path.is_symlink():
                    result[relative] = ("symlink", os.readlink(path))
                elif path.is_dir():
                    result[relative] = ("directory",)
                else:
                    result[relative] = ("file", path.read_bytes())
        return result

    def run_cli(self, *options, valid=True):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.archive), str(self.repo), *options],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=15,
        )
        stream = completed.stdout if valid else completed.stderr
        if valid:
            self.assertEqual(completed.returncode, 0, completed.stderr)
        else:
            self.assertNotEqual(completed.returncode, 0, completed.stdout)
        try:
            payload = json.loads(stream)
        except json.JSONDecodeError as exc:
            self.fail(
                "CLI did not return JSON on the expected stream: "
                f"{exc}; stdout={completed.stdout!r}; stderr={completed.stderr!r}"
            )
        self.assertIsInstance(payload, dict)
        return payload

    def reject_without_changes(self, entries, *options):
        self.make_zip(entries)
        self.write_existing("keep.txt", b"keep existing bytes\n")
        before = self.snapshot()
        self.run_cli("--apply", *options, valid=False)
        self.assertEqual(self.snapshot(), before)

    def test_wrapped_mapping_plan_classifies_changes_and_hashes(self):
        self.write_existing("prompt/changed.md", b"old text\n")
        self.write_existing("prompt/same.md", b"same text\n")
        self.make_zip([
            ("bundle/", b""),
            ("bundle/prompts/", b""),
            ("bundle/prompts/added.md", b"new file\n"),
            ("bundle/prompts/changed.md", b"new text\n"),
            ("bundle/prompts/same.md", b"same text\n"),
        ])
        before = self.snapshot()

        plan = self.run_cli("--map", "prompts=prompt")

        self.assertEqual(plan["archive_sha256"], sha256(self.archive.read_bytes()))
        self.assertIs(plan["crc_checked"], True)
        self.assertEqual(plan["stripped_prefix"], "bundle")
        self.assertIn({"source": "prompts", "destination": "prompt"}, plan["mappings"])
        self.assertEqual(plan["counts"], {"added": 1, "modified": 1, "unchanged": 1})
        self.assertIs(plan["applied"], False)
        files = {item["path"]: item for item in plan["files"]}
        expected = {
            "prompt/added.md": ("added", b"new file\n", None),
            "prompt/changed.md": ("modified", b"new text\n", sha256(b"old text\n")),
            "prompt/same.md": ("unchanged", b"same text\n", sha256(b"same text\n")),
        }
        self.assertEqual(set(files), set(expected))
        for path, (status, data, previous) in expected.items():
            with self.subTest(path=path):
                item = files[path]
                self.assertEqual(item["archive_path"], "bundle/prompts/" + Path(path).name)
                self.assertEqual(item["status"], status)
                self.assertEqual(item["sha256"], sha256(data))
                self.assertEqual(item["previous_sha256"], previous)
        self.assertEqual(self.snapshot(), before)

    def test_apply_places_all_files_and_preserves_unrelated_files(self):
        self.write_existing("prompt/changed.md", b"before")
        self.write_existing("prompt/same.md", b"same")
        self.write_existing("unrelated/nested.txt", b"not in archive")
        self.make_zip([
            ("bundle/prompts/added.md", b"added"),
            ("bundle/prompts/changed.md", b"after"),
            ("bundle/prompts/same.md", b"same"),
        ])

        plan = self.run_cli("--map", "prompts=prompt", "--apply")

        self.assertIs(plan["applied"], True)
        self.assertEqual(plan["counts"], {"added": 1, "modified": 1, "unchanged": 1})
        self.assertEqual((self.repo / "prompt/added.md").read_bytes(), b"added")
        self.assertEqual((self.repo / "prompt/changed.md").read_bytes(), b"after")
        self.assertEqual((self.repo / "prompt/same.md").read_bytes(), b"same")
        self.assertEqual((self.repo / "unrelated/nested.txt").read_bytes(), b"not in archive")
        self.assertFalse((self.repo / "bundle").exists())

    def test_dry_run_does_not_create_directories(self):
        self.make_zip([("wrapper/new/deep/file.txt", b"payload")])
        before = self.snapshot()
        self.run_cli()
        self.assertEqual(self.snapshot(), before)

    def test_auto_strip_removes_only_one_shared_directory(self):
        self.make_zip([
            ("outer/inner/one.txt", b"one"),
            ("outer/inner/two.txt", b"two"),
        ])
        plan = self.run_cli()
        self.assertEqual(plan["stripped_prefix"], "outer")
        self.assertEqual({item["path"] for item in plan["files"]}, {"inner/one.txt", "inner/two.txt"})

    def test_auto_strip_keeps_multiple_top_level_roots(self):
        self.make_zip([("one/file.txt", b"one"), ("two/file.txt", b"two")])
        plan = self.run_cli()
        self.assertIsNone(plan["stripped_prefix"])
        self.assertEqual({item["path"] for item in plan["files"]}, {"one/file.txt", "two/file.txt"})

    def test_empty_strip_prefix_disables_auto_strip(self):
        self.make_zip([("wrapper/inner/file.txt", b"payload")])
        plan = self.run_cli("--strip-prefix", "")
        self.assertIsNone(plan["stripped_prefix"])
        self.assertEqual(plan["files"][0]["path"], "wrapper/inner/file.txt")

    def test_explicit_strip_prefix(self):
        self.make_zip([("wrapper/inner/file.txt", b"payload")])
        plan = self.run_cli("--strip-prefix", "wrapper")
        self.assertEqual(plan["stripped_prefix"], "wrapper")
        self.assertEqual(plan["files"][0]["path"], "inner/file.txt")

    def test_mapping_uses_longest_matching_prefix_and_path_boundary(self):
        self.make_zip([
            ("bundle/assets/images/pixel.dat", b"pixel"),
            ("bundle/assets/readme.txt", b"readme"),
            ("bundle/assets2/untouched.txt", b"untouched"),
        ])
        plan = self.run_cli("--map", "assets=docs", "--map", "assets/images=media")
        self.assertEqual(
            {item["path"] for item in plan["files"]},
            {"media/pixel.dat", "docs/readme.txt", "assets2/untouched.txt"},
        )

    def test_mapping_directory_to_repository_root_is_allowed(self):
        self.make_zip([
            ("bundle/", b""),
            ("bundle/prompts/", b""),
            ("bundle/prompts/one.md", b"one"),
            ("bundle/prompts/nested/", b""),
            ("bundle/prompts/nested/two.md", b"two"),
        ])

        plan = self.run_cli("--map", "prompts=", "--apply")

        self.assertIs(plan["applied"], True)
        self.assertEqual(plan["counts"], {"added": 2, "modified": 0, "unchanged": 0})
        self.assertEqual({item["path"] for item in plan["files"]}, {"one.md", "nested/two.md"})
        self.assertEqual((self.repo / "one.md").read_bytes(), b"one")
        self.assertEqual((self.repo / "nested/two.md").read_bytes(), b"two")
        self.assertFalse((self.repo / "prompts").exists())

    def test_conflicting_mapping_for_same_source_is_rejected(self):
        self.reject_without_changes(
            [("bundle/source/file.txt", b"payload")],
            "--map", "source=one", "--map", "source=two",
        )

    def test_unsafe_archive_names_are_rejected(self):
        for name in [
            "../escape.txt",
            "nested/../../escape.txt",
            "/absolute.txt",
            "C:/absolute.txt",
            "nested\\escape.txt",
        ]:
            with self.subTest(name=name):
                self.reject_without_changes([("valid.txt", b"first"), (name, b"unsafe")])

    def test_unsafe_directory_entry_is_rejected(self):
        for name in ["../outside/", "/absolute/", "nested\\escape/"]:
            with self.subTest(name=name):
                self.reject_without_changes([("valid.txt", b"first"), (name, b"")])

    def test_archive_symlink_is_rejected_before_any_write(self):
        link = zipfile.ZipInfo("bundle/link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.reject_without_changes([
            ("bundle/valid.txt", b"first"),
            (link, b"../outside.txt"),
        ])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are not supported")
    def test_existing_parent_symlink_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "sentinel.txt").write_bytes(b"outside stays intact")
        try:
            (self.repo / "linked").symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"cannot create test symlink: {exc}")
        self.reject_without_changes([
            ("valid.txt", b"first"),
            ("linked/payload.txt", b"unsafe"),
        ])
        self.assertEqual((outside / "sentinel.txt").read_bytes(), b"outside stays intact")
        self.assertFalse((outside / "payload.txt").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are not supported")
    def test_existing_destination_symlink_is_rejected(self):
        outside = self.root / "outside.txt"
        outside.write_bytes(b"outside stays intact")
        try:
            (self.repo / "linked.txt").symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"cannot create test symlink: {exc}")
        self.reject_without_changes([("valid.txt", b"first"), ("linked.txt", b"unsafe")])
        self.assertEqual(outside.read_bytes(), b"outside stays intact")

    def test_duplicate_archive_file_is_rejected(self):
        self.reject_without_changes([("same.txt", b"one"), ("same.txt", b"two")])

    def test_mapping_destination_collision_is_rejected(self):
        self.reject_without_changes(
            [("bundle/alpha/file.txt", b"one"), ("bundle/beta/file.txt", b"two")],
            "--map", "alpha=shared", "--map", "beta=shared",
        )

    def test_file_directory_collision_is_rejected(self):
        self.reject_without_changes([
            ("bundle/item", b"file"),
            ("bundle/item/nested.txt", b"nested file"),
        ])

    def test_existing_file_as_destination_parent_is_rejected(self):
        self.write_existing("occupied", b"existing file")
        self.reject_without_changes([
            ("valid.txt", b"first"),
            ("occupied/nested.txt", b"unsafe"),
        ])

    def test_git_and_private_ledger_paths_are_rejected(self):
        for name in [
            ".git/config",
            "bundle/.git/config",
            "bundle/PEOS_TURN_TIME_LEDGER.jsonl",
            "bundle/nested/PEOS_TURN_TIME_LEDGER.jsonl",
        ]:
            with self.subTest(name=name):
                self.reject_without_changes([("bundle/valid.txt", b"first"), (name, b"forbidden")])

    def test_forbidden_directory_entries_are_rejected(self):
        for name in [".git/", "bundle/.git/"]:
            with self.subTest(name=name):
                self.reject_without_changes([("bundle/valid.txt", b"first"), (name, b"")])

    def test_mapping_cannot_create_git_or_private_ledger_destinations(self):
        for mapping, name in [
            ("safe=.git", "bundle/safe/config"),
            ("safe=PEOS_TURN_TIME_LEDGER.jsonl", "bundle/safe"),
        ]:
            with self.subTest(mapping=mapping):
                self.reject_without_changes(
                    [("bundle/valid.txt", b"first"), (name, b"forbidden")],
                    "--map", mapping,
                )

    def test_unsafe_mapping_destination_is_rejected(self):
        for mapping in ["safe=../outside", "safe=/absolute", "safe=nested\\outside"]:
            with self.subTest(mapping=mapping):
                self.reject_without_changes(
                    [("bundle/safe/file.txt", b"payload")], "--map", mapping,
                )

    def test_late_invalid_entry_does_not_modify_earlier_existing_file(self):
        self.write_existing("first.txt", b"original")
        self.reject_without_changes([
            ("first.txt", b"replacement"),
            ("new/deep/second.txt", b"new file"),
            ("../invalid.txt", b"invalid"),
        ])
        self.assertEqual((self.repo / "first.txt").read_bytes(), b"original")
        self.assertFalse((self.repo / "new").exists())

    def test_late_placement_validation_failure_rolls_back_files_and_directories(self):
        spec = importlib.util.spec_from_file_location("peos_zip_import_under_test", SCRIPT)
        importer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(importer)
        self.write_existing("a-existing.txt", b"original")
        self.write_existing("unrelated/keep.txt", b"keep")
        self.make_zip([
            ("a-existing.txt", b"replacement"),
            ("b-added/deep/file.txt", b"added"),
            ("z-last.txt", b"last"),
        ])
        before = self.snapshot()
        plan, repo, payloads, backups = importer.build_plan(self.archive, self.repo)
        real_destination = importer.destination
        injected = []

        def fail_after_placements(repository, parts, **kwargs):
            if parts == ("z-last.txt",) and (self.repo / "b-added/deep/file.txt").exists():
                # Prove both replacement and new-file placement happened before the failure.
                self.assertEqual((self.repo / "a-existing.txt").read_bytes(), b"replacement")
                self.assertEqual((self.repo / "b-added/deep/file.txt").read_bytes(), b"added")
                injected.append(True)
                raise importer.ImportFailure("injected late destination validation failure")
            return real_destination(repository, parts, **kwargs)

        with mock.patch.object(importer, "destination", side_effect=fail_after_placements):
            with self.assertRaisesRegex(importer.ImportFailure, "injected late destination validation failure"):
                importer.apply_plan(plan, repo, payloads, backups)

        self.assertEqual(injected, [True])
        self.assertIs(plan["applied"], False)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((self.repo / "a-existing.txt").read_bytes(), b"original")
        self.assertFalse((self.repo / "b-added").exists())
        self.assertFalse((self.repo / "z-last.txt").exists())

    def test_invalid_zip_returns_json_error_and_does_not_write(self):
        self.archive.write_bytes(b"not a ZIP archive")
        self.write_existing("keep.txt", b"existing")
        before = self.snapshot()
        self.run_cli("--apply", valid=False)
        self.assertEqual(self.snapshot(), before)

    def test_crc_failure_is_detected_before_any_write(self):
        self.make_zip([("first.txt", b"first payload"), ("second.txt", b"second payload")])
        with zipfile.ZipFile(self.archive) as archive:
            offset = archive.getinfo("second.txt").header_offset
        data = bytearray(self.archive.read_bytes())
        name_length, extra_length = struct.unpack_from("<HH", data, offset + 26)
        payload_offset = offset + 30 + name_length + extra_length
        data[payload_offset] ^= 0x01
        self.archive.write_bytes(data)
        self.write_existing("keep.txt", b"existing")
        before = self.snapshot()

        self.run_cli("--apply", valid=False)

        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
