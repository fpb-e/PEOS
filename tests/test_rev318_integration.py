"""Reject silent rule edits, rewritten lineage and invented live results."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_next_spec_validation import next_spec_errors


class Revision318BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ('admin', 'prompt', 'history', 'tests/fixtures'):
            shutil.copytree(ROOT / folder, self.root / folder)

    def test_unrecorded_rule_edit_is_rejected(self):
        path = self.root / 'prompt/PEOS_CURRENT_SPEC_JP.md'
        path.write_text(path.read_text().replace('親密度は1〜100', '親密度は1〜99', 1))
        self.assertTrue(any('REV318_CHANGE_BINDING' in x or 'REV318_REQUIREMENT_BINDING' in x
                            for x in next_spec_errors(self.root)))

    def test_old_requirement_trace_cannot_be_rewritten(self):
        path = self.root / 'admin/REV0.317_REQUIREMENT_TRACEABILITY.json'
        value = json.loads(path.read_text())
        value['requirements'][0]['requirement_summary'] = 'SYNTHETIC RETROACTIVE CHANGE'
        path.write_text(json.dumps(value))
        self.assertIn('REV318_HISTORICAL_TRACE_MUTATED:admin/REV0.317_REQUIREMENT_TRACEABILITY.json',
                      next_spec_errors(self.root))

    def test_removing_a_declared_change_does_not_hide_it(self):
        path = self.root / 'admin/REV0.318_RULE_DELTA.json'
        value = json.loads(path.read_text())
        value['changed_existing_rules'].pop('SPEC.REV316.REL_001')
        path.write_text(json.dumps(value))
        self.assertIn('REV318_UNDECLARED_RULE_EDIT', next_spec_errors(self.root))

    def test_fixture_plan_cannot_claim_a_live_model_pass(self):
        path = self.root / 'tests/fixtures/rev318_model_replay.json'
        value = json.loads(path.read_text())
        value.update(status='PASS', live_model_pass=True)
        path.write_text(json.dumps(value))
        self.assertIn('REV318_MODEL_RESULT_OVERCLAIM', next_spec_errors(self.root))
