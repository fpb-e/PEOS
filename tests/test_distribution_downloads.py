"""Verify the committed public download and the narrow binary exception."""
import hashlib
from pathlib import Path
import re
import sys
import tempfile
import unittest
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_public_release import (DISTRIBUTION_ARCHIVES, distribution_errors,
    forbidden_file, manifest_errors, publication_errors)

RELATIVE = 'downloads/PEOS_GITHUB_PACKAGE_rev0.316.zip'


class DistributionDownloadTests(unittest.TestCase):
    def test_original_public_zip_is_allowed_only_at_its_pinned_path(self):
        data = (ROOT / RELATIVE).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), DISTRIBUTION_ARCHIVES[RELATIVE])
        self.assertEqual(forbidden_file(RELATIVE, data), [])
        for name in ['renamed.zip', 'downloads/other.zip', 'downloads/PEOS_PRIVATE_EVIDENCE_rev0.316.zip']:
            with self.subTest(name=name):
                self.assertIn('EMBEDDED_ARCHIVE', forbidden_file(name, data))

    def test_matching_filename_cannot_publish_changed_or_private_bytes(self):
        data = (ROOT / RELATIVE).read_bytes()
        self.assertIn('EMBEDDED_ARCHIVE', forbidden_file(RELATIVE, data + b'changed'))
        self.assertIn('EMBEDDED_ARCHIVE', forbidden_file(RELATIVE, b'PK\x03\x04synthetic private archive'))
        self.assertIn('EXCLUDED_ORIGINAL_BYTES', forbidden_file(
            RELATIVE, data, {hashlib.sha256(data).hexdigest()}))

    def test_download_shelf_detects_missing_zip_and_wrong_checksum(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(distribution_errors(root), [])
            (root / 'downloads').mkdir()
            errors = distribution_errors(root)
            self.assertIn('DISTRIBUTION_ARCHIVE_MISSING:' + RELATIVE, errors)
            self.assertIn('DISTRIBUTION_CHECKSUMS_DIFFER', errors)
            (root / RELATIVE).write_bytes(b'changed')
            (root / 'downloads/SHA256SUMS').write_text('wrong checksum\n')
            self.assertIn('DISTRIBUTION_ARCHIVE_BYTES_DIFFER:' + RELATIVE, distribution_errors(root))

    def test_download_checksum_and_size_match_the_immutable_public_zip(self):
        self.assertEqual(distribution_errors(ROOT), [])
        self.assertEqual((ROOT / RELATIVE).stat().st_size, 577135)

    def test_archive_crc_manifest_scope_and_five_canons(self):
        with zipfile.ZipFile(ROOT / RELATIVE) as archive, tempfile.TemporaryDirectory() as temp:
            self.assertIsNone(archive.testzip())
            names = archive.namelist()
            self.assertEqual(len(names), 118)
            self.assertEqual(len(set(names)), 118)
            self.assertFalse(any(name.startswith('downloads/') or Path(name).suffix == '.zip'
                                 for name in names))
            for name in names:
                self.assertFalse(Path(name).is_absolute())
                self.assertNotIn('..', Path(name).parts)
                self.assertEqual(forbidden_file(name, archive.read(name)), [])
            archive.extractall(temp)
            self.assertEqual(manifest_errors(temp), [])
            self.assertEqual(publication_errors(temp), [])
            for path in (ROOT / 'prompt').glob('*.md'):
                self.assertEqual(archive.read('prompt/' + path.name), path.read_bytes())

    def test_readme_and_install_manual_resolve_to_the_actual_download(self):
        readme = (ROOT / 'README.md').read_text()
        before, manual = readme.split('## インストールマニュアル\n', 1)
        self.assertIn('(' + RELATIVE + '?raw=true)', before)
        self.assertIn('(' + RELATIVE + '?raw=true)', manual)
        for path in [ROOT / 'README.md', ROOT / 'downloads/README.md']:
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                url = urlsplit(link)
                if not url.scheme and url.path:
                    self.assertTrue((path.parent / url.path).is_file(), (path.name, link))


if __name__ == '__main__':
    unittest.main()
