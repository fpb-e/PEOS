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


class Revision320BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ('admin', 'prompt', 'history', 'tests/fixtures'):
            shutil.copytree(ROOT / folder, self.root / folder)

    def test_unrecorded_rule_edit_is_rejected(self):
        path = self.root / 'prompt/PEOS_CURRENT_SPEC_JP.md'
        path.write_text(path.read_text().replace('親密度は1〜100', '親密度は1〜99', 1))
        self.assertTrue(any('REV320_UNDECLARED_RULE_EDIT' in x or 'REV320_REQUIREMENT_BINDING' in x
                            for x in next_spec_errors(self.root)))

    def test_old_requirement_trace_cannot_be_rewritten(self):
        path = self.root / 'admin/REV0.319_REQUIREMENT_TRACEABILITY.json'
        value = json.loads(path.read_text())
        value['requirements'][0]['requirement_summary'] = 'SYNTHETIC RETROACTIVE CHANGE'
        path.write_text(json.dumps(value))
        self.assertIn('REV320_HISTORICAL_TRACE_MUTATED:admin/REV0.319_REQUIREMENT_TRACEABILITY.json',
                      next_spec_errors(self.root))

    def test_removing_a_declared_change_does_not_hide_it(self):
        path = self.root / 'admin/REV0.320_RULE_DELTA.json'
        value = json.loads(path.read_text())
        value['changed_existing_rules'].pop('SPEC.LEARNING.FATHER_STYLE_STRUCTURE')
        path.write_text(json.dumps(value))
        self.assertIn('REV320_UNDECLARED_RULE_EDIT', next_spec_errors(self.root))

    def test_fixture_plan_cannot_claim_a_live_model_pass(self):
        path = self.root / 'tests/fixtures/rev320_model_replay.json'
        value = json.loads(path.read_text())
        value.update(status='PASS', live_model_pass=True)
        path.write_text(json.dumps(value))
        self.assertIn('REV320_MODEL_RESULT_OVERCLAIM', next_spec_errors(self.root))

    def test_source_group_cannot_reference_an_absent_rule_or_wrong_owner(self):
        path = self.root / 'admin/REV0.320_REQUIREMENT_TRACEABILITY.json'
        original = json.loads(path.read_text())
        for change in ('missing', 'owner'):
            value = json.loads(json.dumps(original))
            group = value['source_requirement_groups'][0]
            if change == 'missing':
                group['existing_rule_ids'][0] = 'SYNTHETIC.ABSENT.RULE'
                group['existing_rule_bindings'][0]['rule_id'] = 'SYNTHETIC.ABSENT.RULE'
            else:
                group['existing_rule_bindings'][0]['owner'] = 'SYNTHETIC_WRONG_OWNER'
            path.write_text(json.dumps(value))
            with self.subTest(change=change):
                self.assertIn('REV320_SOURCE_GROUP_OWNER:' + group['id'],
                              next_spec_errors(self.root))

    def test_source_group_count_and_duplicates_are_detected(self):
        path = self.root / 'admin/REV0.320_REQUIREMENT_TRACEABILITY.json'
        original = json.loads(path.read_text())
        for change in ('count', 'duplicate'):
            value = json.loads(json.dumps(original))
            if change == 'count':
                value['source_requirement_group_count'] += 1
            else:
                value['source_requirement_groups'][1]['id'] = value['source_requirement_groups'][0]['id']
            path.write_text(json.dumps(value))
            with self.subTest(change=change):
                self.assertIn('REV320_SOURCE_GROUP_SCOPE', next_spec_errors(self.root))
