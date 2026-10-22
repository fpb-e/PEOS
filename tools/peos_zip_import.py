#!/usr/bin/env python3
"""Plan or apply a ZIP to a checkout; never commit or delete repository files."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import zipfile


class ImportFailure(ValueError):
    """An archive or destination failed preflight validation."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def path_parts(value, *, empty=False):
    if value == "" and empty:
        return ()
    if not value or "\\" in value or "\x00" in value:
        raise ImportFailure("Invalid or empty path: " + repr(value))
    parts = value.split("/")
    if (PurePosixPath(value).is_absolute() or re.match(r"^[A-Za-z]:", value)
            or any(p in ("", ".", "..") for p in parts)):
        raise ImportFailure("Unsafe or noncanonical path: " + repr(value))
    if any(p.casefold() == ".git" for p in parts):
        raise ImportFailure("Git metadata cannot be imported: " + value)
    if any(p.casefold() == "peos_turn_time_ledger.jsonl" for p in parts):
        raise ImportFailure("The private time ledger cannot be imported: " + value)
    return tuple(parts)


def parse_mappings(values):
    result = []
    seen = set()
    for value in values:
        if "=" not in value:
            raise ImportFailure("Mapping must be SOURCE=DEST: " + value)
        source, destination = value.split("=", 1)
        src = path_parts(source.rstrip("/"))
        dst = path_parts(destination.rstrip("/"), empty=True)
        if src in seen:
            raise ImportFailure("Duplicate mapping source: " + source)
        seen.add(src)
        result.append((src, dst))
    return sorted(result, key=lambda item: (-len(item[0]), item[0]))


def destination(repo, parts, *, directory=False):
    """Validate existing parents without following a symlink inside the checkout."""
    current = repo
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise ImportFailure("Destination contains a symlink: " + str(current))
        if current.exists():
            needs_directory = directory or index < len(parts) - 1
            if needs_directory and not current.is_dir():
                raise ImportFailure("Destination parent is not a directory: " + str(current))
            if not needs_directory and not current.is_file():
                raise ImportFailure("Destination is not a regular file: " + str(current))
    return current


def choose_prefix(files, requested):
    if requested is not None:
        return path_parts(requested.rstrip("/"), empty=True), "explicit"
    first = files[0][0][0]
    if all(len(parts) > 1 and parts[0] == first for parts, _, _ in files):
        return (first,), "auto"
    return (), "auto"


def remap(parts, mappings, *, directory=False):
    for source, target in mappings:
        if parts[:len(source)] == source:
            parts = target + parts[len(source):]
            break
    # Validate again after transformations, including protected path components.
    return path_parts("/".join(parts), empty=directory)


def build_plan(archive, repo, strip_prefix=None, mapping_values=()):
    if repo.is_symlink() or not repo.is_dir():
        raise ImportFailure("Repository must be an existing, nonsymlink directory")
    repo = repo.resolve()
    mappings = parse_mappings(mapping_values)
    raw = archive.read_bytes()
    files, directories = [], []
    seen = set()
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        for info in source.infolist():
            name = info.filename[:-1] if info.is_dir() else info.filename
            parts = path_parts(name)
            if parts in seen:
                raise ImportFailure("Duplicate ZIP entry: " + name)
            seen.add(parts)
            mode = info.external_attr >> 16
            kind = stat.S_IFMT(mode)
            if stat.S_ISLNK(mode):
                raise ImportFailure("ZIP symlinks cannot be imported: " + name)
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ImportFailure("Unsupported ZIP entry type: " + name)
            data = source.read(info)  # ZipFile verifies each member's CRC here.
            if info.is_dir():
                directories.append(parts)
            else:
                files.append((parts, data, 0o755 if mode & 0o111 else 0o644))
    if not files:
        raise ImportFailure("ZIP contains no files to import")
    prefix, strip_mode = choose_prefix(files, strip_prefix)

    def transform(parts, *, directory=False):
        if prefix:
            if directory and prefix[:len(parts)] == parts:
                return ()
            if parts[:len(prefix)] != prefix:
                raise ImportFailure("Entry is outside strip prefix: " + "/".join(parts))
            parts = parts[len(prefix):]
        return remap(parts, mappings, directory=directory)

    directory_targets = set()
    for parts in directories:
        target = transform(parts, directory=True)
        if target:
            destination(repo, target, directory=True)
            directory_targets.add(target)

    entries, payloads, backups, target_keys = [], {}, {}, {}
    for original, data, mode in files:
        target = transform(original)
        key = tuple(p.casefold() for p in target)
        if key in target_keys:
            raise ImportFailure("ZIP entries collide after mapping: " + "/".join(target))
        target_keys[key] = target
        path = destination(repo, target)
        previous = path.read_bytes() if path.exists() else None
        previous_hash = digest(previous) if previous is not None else None
        new_hash = digest(data)
        status = "added" if previous is None else (
            "unchanged" if previous_hash == new_hash else "modified")
        # Preserve the mode of existing files; use the archive executable bit for new files.
        file_mode = stat.S_IMODE(path.stat().st_mode) if previous is not None else mode
        relative = "/".join(target)
        entries.append({"archive_path": "/".join(original), "path": relative,
                        "status": status, "sha256": new_hash,
                        "previous_sha256": previous_hash, "mode": oct(file_mode)})
        payloads[target] = (data, file_mode)
        backups[target] = (previous, file_mode)

    keys = set(target_keys)
    for key, target in target_keys.items():
        if any(key[:i] in keys for i in range(1, len(key))):
            raise ImportFailure("File/directory collision: " + "/".join(target))
        for directory in directory_targets:
            folded = tuple(p.casefold() for p in directory)
            if folded[:len(key)] == key:
                raise ImportFailure("File/directory collision: " + "/".join(target))
    entries.sort(key=lambda item: item["path"])
    plan = {"archive_sha256": digest(raw), "crc_checked": True,
            "stripped_prefix": "/".join(prefix) or None, "strip_mode": strip_mode,
            "mappings": [{"source": "/".join(a), "destination": "/".join(b)}
                         for a, b in mappings],
            "counts": {name: sum(e["status"] == name for e in entries)
                       for name in ("added", "modified", "unchanged")},
            "files": entries, "applied": False}
    return plan, repo, payloads, backups


def apply_plan(plan, repo, payloads, backups):
    changed = [e for e in plan["files"] if e["status"] != "unchanged"]
    # Preflight every destination before the first write, including concurrent edits.
    for entry in plan["files"]:
        target = tuple(entry["path"].split("/"))
        path = destination(repo, target)
        current_hash = digest(path.read_bytes()) if path.exists() else None
        if current_hash != entry["previous_sha256"]:
            raise ImportFailure("Destination changed after planning: " + entry["path"])
    applied, made_directories = [], []
    with tempfile.TemporaryDirectory(prefix=".peos-zip-import-", dir=repo) as temp:
        staging = Path(temp)
        for index, entry in enumerate(changed):
            target = tuple(entry["path"].split("/"))
            for suffix, content in (("new", payloads[target][0]),
                                    ("old", backups[target][0])):
                if content is not None:
                    staged = staging / (str(index) + "." + suffix)
                    with staged.open("xb") as handle:
                        handle.write(content)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.chmod(staged, payloads[target][1])
        try:
            for index, entry in enumerate(changed):
                target = tuple(entry["path"].split("/"))
                path = destination(repo, target)
                missing = []
                parent = path.parent
                while parent != repo and not parent.exists():
                    missing.append(parent)
                    parent = parent.parent
                for parent in reversed(missing):
                    parent.mkdir()
                    made_directories.append(parent)
                os.replace(staging / (str(index) + ".new"), path)
                applied.append((index, target))
        except (OSError, ImportFailure) as error:
            rollback_errors = []
            for index, target in reversed(applied):
                path = repo.joinpath(*target)
                try:
                    if backups[target][0] is None:
                        path.unlink()
                    else:
                        os.replace(staging / (str(index) + ".old"), path)
                except OSError as rollback_error:
                    rollback_errors.append(str(rollback_error))
            for parent in reversed(made_directories):
                try:
                    parent.rmdir()
                except OSError as rollback_error:
                    rollback_errors.append(str(rollback_error))
            detail = "; rollback errors: " + "; ".join(rollback_errors) if rollback_errors else "; changes rolled back"
            raise ImportFailure("Placement failed: " + str(error) + detail) from error
    plan["applied"] = True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("repository", type=Path)
    parser.add_argument("--apply", action="store_true", help="Place planned files; default only prints the plan")
    parser.add_argument("--strip-prefix", default=None,
                        help="Strip this archive prefix; an empty value disables automatic stripping")
    parser.add_argument("--map", dest="mappings", action="append", default=[], metavar="SOURCE=DEST")
    args = parser.parse_args(argv)
    try:
        plan, repo, payloads, backups = build_plan(args.archive, args.repository,
                                                 args.strip_prefix, args.mappings)
        if args.apply:
            apply_plan(plan, repo, payloads, backups)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
