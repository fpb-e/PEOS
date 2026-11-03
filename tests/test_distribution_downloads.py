"""Repository-only download checks, excluded from the nonrecursive ZIP."""
import hashlib,json,re,sys,tempfile,unittest,zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from peos_distribution import load_packages,distribution_errors,archive_errors,registered_archive_errors
from peos_public_release import forbidden_file
class DistributionDownloadTests(unittest.TestCase):
    def test_registered_archives_have_exact_bytes_and_safe_members(self):
        for name,item in load_packages(ROOT).items():
            with self.subTest(name=name):self.assertEqual(registered_archive_errors(name,(ROOT/name).read_bytes(),item),[])
    def test_changed_or_unregistered_archive_is_rejected(self):
        for name,item in load_packages(ROOT).items():
            data=(ROOT/name).read_bytes();self.assertTrue(registered_archive_errors(name,data+b'changed',item))
            self.assertIn('EMBEDDED_ARCHIVE',forbidden_file('downloads/private.zip',data))
    def test_private_and_recursive_content_cannot_use_matching_archive_hash(self):
        stream=BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('source/EVENTS.jsonl','SYNTHETIC PRIVATE');z.writestr('downloads/nested.zip',b'PK\x03\x04synthetic')
        errors=archive_errors(stream.getvalue());self.assertTrue(any('PRIVATE_SOURCE_DIRECTORY' in e for e in errors));self.assertTrue(any('RECURSIVE' in e for e in errors))
    def test_missing_registry_zip_and_changed_checksum_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'downloads').mkdir();self.assertIn('DISTRIBUTION_REGISTRY_MISSING',distribution_errors(root))
            (root/'downloads/PUBLIC_PACKAGES.json').write_bytes((ROOT/'downloads/PUBLIC_PACKAGES.json').read_bytes())
            self.assertIn('DISTRIBUTION_CHECKSUMS_DIFFER',distribution_errors(root));self.assertTrue(any('MISSING' in e for e in distribution_errors(root)))
    def test_original_rev316_zip_remains_immutable(self):
        self.assertEqual(hashlib.sha256((ROOT/'downloads/PEOS_GITHUB_PACKAGE_rev0.316.zip').read_bytes()).hexdigest(),'7a35699d30153ae8ce30234f20aa35bef7a2f1520060ff85af398da4e3016915')
        self.assertEqual(distribution_errors(ROOT),[])
    def test_primary_download_and_local_manual_links_resolve(self):
        primary=json.loads((ROOT/'downloads/PUBLIC_PACKAGES.json').read_text())['primary']
        before,manual=(ROOT/'README.md').read_text().split('## インストールマニュアル\n',1)
        self.assertIn('('+primary+'?raw=true)',before);self.assertIn('('+primary+'?raw=true)',manual)
        for path in [ROOT/'README.md',ROOT/'downloads/README.md']:
            for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                u=urlsplit(link)
                if not u.scheme and u.path:self.assertTrue((path.parent/u.path).is_file(),link)
