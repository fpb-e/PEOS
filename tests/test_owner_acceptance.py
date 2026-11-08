"""Recorded owner adoption cannot be replaced by a PASS or accepted flag."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_public_release import release_acceptance_errors
from peos_session_policy import restore_snapshot


class OwnerAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ('admin', 'prompt', 'runtime'):
            shutil.copytree(ROOT / folder, self.root / folder)
        self.record = self.root / 'admin/REV0.318_OWNER_ACCEPTANCE.json'

    def change_record(self, **values):
        record = json.loads(self.record.read_text())
        record.update(values)
        self.record.write_text(json.dumps(record))

    def test_an_accepted_flag_without_owner_record_is_rejected(self):
        self.record.unlink()
        self.assertIn('OWNER_ACCEPTANCE_RECORD_MISSING_OR_INVALID', release_acceptance_errors(self.root))

    def test_static_pass_cannot_replace_explicit_owner_basis(self):
        self.change_record(source_class='STATIC_TEST_PASS')
        self.assertIn('OWNER_ACCEPTANCE_BASIS_DIFFERS', release_acceptance_errors(self.root))

    def test_changed_canon_is_not_covered_by_existing_acceptance(self):
        with (self.root / 'prompt/PEOS_CURRENT_SPEC_JP.md').open('a') as stream:
            stream.write('\nSYNTHETIC UNACCEPTED CHANGE\n')
        self.assertIn('OWNER_ACCEPTANCE_CANON_BINDING_DIFFERS', release_acceptance_errors(self.root))

    def test_restore_cannot_roll_back_accepted_authority(self):
        path = self.root / 'runtime/PEOS_SESSION_RESTORE_rev0.318.json'
        value = json.loads(path.read_text())
        value['authority']['current_canon'] = 'rev0.316'
        path.write_text(json.dumps(value))
        self.assertIn('OWNER_ACCEPTANCE_RESTORE_DIFFERS', release_acceptance_errors(self.root))

    def test_adoption_preserves_empty_live_state(self):
        self.assertEqual(release_acceptance_errors(self.root), [])
        restore = restore_snapshot(self.root)
        self.assertTrue(restore['release_accepted'])
        self.assertFalse(restore['runtime_ready'])
        self.assertFalse(restore['host_hook_installed'])
        self.assertIsNone(restore['source_sync_receipt'])
        self.assertEqual(restore['replay_actions'], [])
        self.change_record(live_model_acceptance='PASS')
        self.assertIn('OWNER_ACCEPTANCE_OVERCLAIMS_LIVE_STATE', release_acceptance_errors(self.root))
