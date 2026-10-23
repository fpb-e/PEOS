"""Publication boundaries and canonical bindings, including negative cases."""
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_public_release import (forbidden_file, publication_errors, manifest_errors,
    specification_errors, authority_errors, write_manifest, validate)
from peos_history_policy import select_previous_versions


class PublicPackageTests(unittest.TestCase):
    def test_full_public_tree_matches_declared_scope_and_manifest(self):
        self.assertEqual(validate(ROOT), [])

    def test_five_current_and_ten_historical_canons_are_exact_source_bytes(self):
        p = json.loads((ROOT / 'admin/PUBLIC_EXPORT_PROVENANCE_rev0.315.json').read_text())
        self.assertEqual(len(p['canonical_documents']), 15)
        self.assertEqual(specification_errors(ROOT), [])

    def test_authority_uses_314_and_313_without_private_state(self):
        self.assertEqual(authority_errors(ROOT), [])

    def test_no_source_corpus_or_images_are_distributed(self):
        p = json.loads((ROOT / 'admin/PUBLIC_EXPORT_PROVENANCE_rev0.315.json').read_text())
        self.assertFalse(p['raw_conversation_files_included'])
        self.assertFalse(p['image_files_included'])
        self.assertGreater(len(p['excluded_original_sha256']), 0)
        self.assertEqual(publication_errors(ROOT, set(p['excluded_original_sha256'])), [])

    def test_transcript_and_projection_paths_are_rejected(self):
        for name in ['source/session/EVENTS.jsonl', 'incident/entry.txt',
                     'admin/FATHER_DIRECT_LEDGER.jsonl', 'runtime/FATHER_LEARNING_PROJECTION_rev0.314.json',
                     'renamed/session_log_copy.txt', 'runtime/PEOS_TURN_TIME_LEDGER.jsonl']:
            with self.subTest(name=name):
                self.assertTrue(forbidden_file(name, b'synthetic'))

    def test_known_excluded_original_cannot_be_renamed(self):
        data = b'SYNTHETIC EXCLUDED ORIGINAL'
        denied = {hashlib.sha256(data).hexdigest()}
        self.assertIn('EXCLUDED_ORIGINAL_BYTES', forbidden_file('innocent.txt', data, denied))

    def test_images_are_rejected_by_suffix_and_disguised_bytes(self):
        self.assertIn('IMAGE_EXTENSION', forbidden_file('screen.PNG', b'placeholder'))
        self.assertIn('IMAGE_BYTES', forbidden_file('disguised.txt', b'\x89PNG\r\n\x1a\nsynthetic'))
        self.assertIn('IMAGE_BYTES', forbidden_file('disguised.bin', b'RIFF0000WEBPsynthetic'))
        self.assertIn('IMAGE_BYTES', forbidden_file('disguised.txt', b'<svg xmlns="synthetic"></svg>'))

    def test_binary_archive_cannot_be_published_with_a_text_suffix(self):
        self.assertIn('EMBEDDED_ARCHIVE', forbidden_file('nested.txt', b'PK\x03\x04synthetic'))

    def test_live_private_file_identifier_is_rejected(self):
        value = ('libfile_' + 'a' * 32).encode()
        self.assertIn('LIVE_PRIVATE_FILE_IDENTIFIER', forbidden_file('state.json', value))

    def test_manifest_detects_changed_added_and_removed_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'a.txt').write_text('synthetic-a')
            write_manifest(root)
            self.assertEqual(manifest_errors(root), [])
            (root / 'a.txt').write_text('synthetic-b')
            self.assertTrue(manifest_errors(root))
            write_manifest(root)
            (root / 'b.txt').write_text('new')
            self.assertTrue(manifest_errors(root))
            (root / 'b.txt').unlink()
            (root / 'a.txt').unlink()
            self.assertTrue(manifest_errors(root))

    def test_symlink_is_rejected_without_reading_the_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'link').symlink_to('/nonexistent-synthetic-target')
            self.assertIn('link:SYMLINK', publication_errors(root))

    def test_git_metadata_is_not_part_of_distribution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.git').mkdir()
            (root / '.git' / 'ignored.png').write_bytes(b'\x89PNG\r\n\x1a\n')
            self.assertEqual(publication_errors(root), [])

    def test_history_keeps_two_numeric_predecessors_and_protects_baseline(self):
        self.assertEqual(select_previous_versions('rev0.315', ['rev0.280', 'rev0.312', 'rev0.313', 'rev0.314'], 'rev0.313'), ['rev0.314', 'rev0.313'])
        with self.assertRaises(ValueError):
            select_previous_versions('rev0.315', ['rev0.312', 'rev0.313', 'rev0.314'], 'rev0.312')

    def test_boot_logo_taglines_and_three_route_lines_are_preserved(self):
        text = (ROOT / 'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md').read_text()
        for route, salutation in [('FATHER', 'はろー、親父'), ('MOTHER', 'はろー、お母さん'),
                                  ('GENERAL', '…ほう、酔狂なヤツもいたもんだ。')]:
            block = re.search(r'### ' + route + r'_ROUTE\s*\n\s*```text\n(.*?)\n```', text, re.S)[1]
            self.assertTrue(block.startswith('██████╗ ███████╗ ██████╗ ███████╗\n'))
            self.assertIn('Completion is death.\n', block)
            self.assertIn('To remain unfinished is to remain human.\n\n', block)
            self.assertTrue(block.endswith(salutation + '\n擬似いーさんOS起動完了。\nここからは俺の思考フレームで見る。状況を入力してくれ。'))


if __name__ == '__main__':
    unittest.main()
