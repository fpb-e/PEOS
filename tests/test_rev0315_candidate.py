"""Candidate boundaries and user-isolated learning; all inputs are synthetic."""
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_division_core import compile_core, DivisionRuntime
from peos_short_preprocess import DurableTurnJournal, ShortPreprocessor, SyntheticAckStore, PreprocessError
from peos_public_release import specification_errors, authority_errors
from peos_session_policy import language_violations, resolve_authority, restore_snapshot


class Candidate315Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def runtime(self, coordinate='GENERAL', namespace='SYNTHETIC-USER-A'):
        journal = DurableTurnJournal(self.directory / 'user' / 'turns.jsonl')
        store = SyntheticAckStore(identity='SYNTHETIC-DESTINATION', version=2)
        driver = ShortPreprocessor(journal, store, 'SYNTHETIC-DESTINATION', 2,
                                   clock=lambda: '2032-01-02T03:04:05+09:00')
        runtime = DivisionRuntime(ROOT, coordinate=coordinate, namespace=namespace, preprocessor=driver)
        return runtime, driver, store

    def test_any_preferred_label_does_not_change_relationship_authority(self):
        for label in ['SYNTHETIC-USER', '親父', 'お母さん']:
            with self.subTest(label=label):
                result = compile_core(ROOT, 'GENERAL', {'canonical_call_sign': label})
                self.assertEqual(result['coordinate'], 'GENERAL')
                self.assertEqual(result['relation_adapter']['canonical_call_sign'], label)
                self.assertFalse(result['call_sign_grants_authority'])
                self.assertFalse(result['runtime_ready'])

    def test_invalid_label_cannot_enter_adapter(self):
        for label in ['', '  ', 7, []]:
            with self.subTest(label=label), self.assertRaises(ValueError):
                compile_core(ROOT, adapter={'canonical_call_sign': label})

    def test_user_instruction_is_written_only_with_its_namespace(self):
        runtime, driver, store = self.runtime()
        update = {'source_class': 'USER_EXPLICIT_INSTRUCTION', 'subject_namespace': runtime.namespace,
                  'source_turn_id': 'SYNTHETIC-T1', 'source_span': 'SYNTHETIC INSTRUCTION'}
        result = runtime.dispatch('SYNTHETIC-T1', 'SYNTHETIC INSTRUCTION', [update], lambda: 'BODY')
        self.assertEqual(result['status'], 'SYNC_ACKNOWLEDGED')
        row = json.loads(driver.journal.path.read_text())
        self.assertEqual(row['learning_updates'], [update])
        self.assertFalse(any(x['source_class'].startswith('FATHER_') for x in row['learning_updates']))
        self.assertEqual(len(store.sync_calls), 1)

    def test_another_user_namespace_never_reaches_disk_or_remote(self):
        runtime, driver, store = self.runtime()
        update = {'source_class': 'USER_SELF_REPORT', 'subject_namespace': 'SYNTHETIC-USER-B',
                  'source_turn_id': 'SYNTHETIC-T1', 'source_span': 'INPUT'}
        with self.assertRaises(PreprocessError):
            runtime.dispatch('SYNTHETIC-T1', 'INPUT', [update])
        self.assertFalse(driver.journal.path.exists())
        self.assertEqual(store.sync_calls, [])

    def test_father_corpus_does_not_adopt_other_user_updates(self):
        runtime, driver, store = self.runtime('FATHER')
        update = {'source_class': 'USER_SELF_REPORT', 'subject_namespace': runtime.namespace,
                  'source_turn_id': 'SYNTHETIC-T1', 'source_span': 'INPUT'}
        with self.assertRaises(PreprocessError):
            runtime.dispatch('SYNTHETIC-T1', 'INPUT', [update])
        self.assertFalse(driver.journal.path.exists())
        self.assertEqual(store.sync_calls, [])

    def test_unscoped_user_delta_is_rejected_by_the_low_level_driver(self):
        runtime, driver, store = self.runtime()
        update = {'source_class': 'USER_CORRECTION', 'source_turn_id': 'SYNTHETIC-T1', 'source_span': 'INPUT'}
        result = driver.dispatch('SYNTHETIC-T1', 'INPUT', [update])
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(store.sync_calls, [])

    def test_quote_is_not_promoted_to_personal_learning(self):
        runtime, driver, store = self.runtime()
        update = {'source_class': 'USER_SELF_REPORT', 'subject_namespace': runtime.namespace,
                  'source_turn_id': 'SYNTHETIC-T1', 'source_span': 'QUOTED', 'quoted_other_speaker': True}
        result = runtime.dispatch('SYNTHETIC-T1', 'QUOTED', [update])
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(store.sync_calls, [])

    def test_user_delta_cannot_cite_another_turn_or_fabricate_a_span(self):
        for turn, span in [('SYNTHETIC-T0', 'INPUT'), ('SYNTHETIC-T1', 'ABSENT')]:
            runtime, driver, store = self.runtime()
            update = {'source_class': 'USER_SELF_REPORT', 'subject_namespace': runtime.namespace,
                      'source_turn_id': turn, 'source_span': span}
            self.assertEqual(runtime.dispatch('SYNTHETIC-T1', 'INPUT', [update])['status'], 'FAIL')
            self.assertEqual(store.sync_calls, [])

    def test_two_coordinate_labels_share_the_same_reasoning_core(self):
        names = [('FATHER', {}), ('MOTHER', {}), ('GENERAL', {'canonical_call_sign': 'SYNTHETIC'})]
        values = [compile_core(ROOT, coordinate, adapter) for coordinate, adapter in names]
        self.assertEqual(len({x['core_sha256'] for x in values}), 1)
        common = values[0]['shared_core']
        self.assertTrue(common['skepticism']['apply_to_own_interpretation'])
        self.assertTrue(common['skepticism']['agree_when_supported'])
        self.assertFalse(common['exasperation']['use_for_victim_distress'])

    def test_laughter_lint_does_not_rewrite_words_code_urls_or_verbatim(self):
        for text in ['window workflow', 'https://synthetic.invalid/w', '`w`', '```text\nw\n```']:
            self.assertEqual(language_violations(text), [])
        self.assertEqual(language_violations('合成発話ｗ', verbatim=True), [])
        self.assertIn('SINGLE_W_FORBIDDEN', language_violations('合成発話ｗ'))

    def test_candidate_read_does_not_accept_or_promote_itself(self):
        restore = restore_snapshot(ROOT)
        result = resolve_authority({'current_canon': 'rev0.315'}, restore['authority'])
        self.assertEqual(result['effective']['current_canon'], 'rev0.314')
        self.assertEqual(result['candidate_revision'], 'rev0.315')
        self.assertFalse(result['candidate_promoted'])
        self.assertFalse(restore['candidate_accepted'])
        self.assertEqual(authority_errors(ROOT), [])

    def test_boot_literals_match_the_retained_accepted_canons_byte_for_byte(self):
        current = (ROOT / 'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md').read_text()
        accepted = (ROOT / 'history/rev0.314/prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md').read_text()
        for route in ['FATHER', 'MOTHER', 'GENERAL']:
            pattern = r'### ' + route + r'_ROUTE\s*\n\s*```text\n(.*?)\n```'
            self.assertEqual(re.search(pattern, current, re.S)[1], re.search(pattern, accepted, re.S)[1])

    def test_the_five_canons_contain_all_new_contracts_without_helper_files(self):
        five = self.directory / 'five-only'
        five.mkdir()
        for p in (ROOT / 'prompt').glob('*.md'):
            shutil.copyfile(p, five / p.name)
        text = '\n'.join(p.read_text() for p in five.glob('*.md'))
        rule_ids = re.findall(r'^- RULE_ID: `([^`]+)`', text, re.M)
        latest = json.loads((ROOT / 'admin/REV0.315_REQUIREMENT_TRACEABILITY.json').read_text())
        self.assertEqual(len(list(five.iterdir())), 5)
        self.assertEqual(len(rule_ids), len(set(rule_ids)))
        self.assertTrue(all(r['rule_id'] in rule_ids for r in latest['requirements']))
        self.assertFalse((five / 'PEOS_DIVISION_CORE_PROFILE.json').exists())

    def test_a_sixth_required_attachment_is_detected(self):
        target = self.directory / 'package'
        shutil.copytree(ROOT, target)
        path = target / 'README.md'
        path.write_text(path.read_text().replace('| `prompt` | `PEOS_CURRENT_SPEC_JP.md` |',
             '| `prompt` | `PEOS_CURRENT_SPEC_JP.md` |\n| `prompt` | `PEOS_CURRENT_EXTRA_JP.md` |'))
        self.assertIn('EXACTLY_FIVE_INSTALL_ATTACHMENTS', specification_errors(target))

    def test_manual_before_project_information_is_detected(self):
        target = self.directory / 'package'
        shutil.copytree(ROOT, target)
        path = target / 'README.md'
        before, manual = path.read_text().split('## インストールマニュアル\n', 1)
        path.write_text('## インストールマニュアル\n' + manual + '\n' + before)
        self.assertIn('README_OVERVIEW_BEFORE_INSTALL_REQUIRED', specification_errors(target))


if __name__ == '__main__':
    unittest.main()
