"""Public synthetic integration cases, not model or live-host acceptance."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_division_core import (DivisionRuntime, PROFILE, ENTRY, compile_core,
                                load_profile, surface_violations)
from peos_short_preprocess import (DurableTurnJournal, PreprocessError,
                                   ShortPreprocessor, SyntheticAckStore)

STAMP = '2032-04-05T06:07:08+09:00'


class DivisionCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def runtime(self, coordinate='GENERAL', namespace='SYNTHETIC-A', *, path=None,
                identity='SYNTHETIC-A', store=None, version=0):
        journal = DurableTurnJournal(path or self.directory / namespace / 'turns.jsonl')
        store = store or SyntheticAckStore(identity=identity, version=version)
        driver = ShortPreprocessor(journal, store, identity, version, clock=lambda: STAMP)
        runtime = DivisionRuntime(ROOT, coordinate=coordinate, namespace=namespace,
                                  preprocessor=driver)
        return runtime, driver, store

    def bound_copy(self):
        target = self.directory / 'package'
        names = [PROFILE, ENTRY, 'runtime/PEOS_SESSION_RESTORE_rev0.315.json']
        names.extend(load_profile(ROOT)['source_canon_sha256'])
        for name in names:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        return target

    def test_same_common_core_for_every_coordinate(self):
        values = [compile_core(ROOT, coordinate) for coordinate in ('FATHER', 'MOTHER', 'GENERAL')]
        self.assertEqual(len({x['core_sha256'] for x in values}), 1)
        self.assertEqual(values[0]['relation_adapter']['canonical_call_sign'], '親父')
        self.assertEqual(values[1]['relation_adapter']['canonical_call_sign'], 'お母さん')
        self.assertNotIn('canonical_call_sign', values[2]['relation_adapter'])
        self.assertTrue(all(not x['runtime_ready'] for x in values))

    def test_relationship_cannot_override_the_common_core(self):
        original = compile_core(ROOT)
        adapted = compile_core(ROOT, adapter={'local_state': {'task': 'SYNTHETIC'}})
        self.assertEqual(original['shared_core'], adapted['shared_core'])
        with self.assertRaises(ValueError):
            compile_core(ROOT, adapter={'skepticism': False})
        for coordinate, call in [('MOTHER', '親父'), ('FATHER', 'お母さん')]:
            with self.subTest(coordinate=coordinate, call=call), self.assertRaises(ValueError):
                compile_core(ROOT, coordinate, {'canonical_call_sign': call})

    def test_modified_canon_is_not_silently_bound(self):
        root = self.bound_copy()
        path = root / 'prompt/PEOS_CURRENT_SPEC_JP.md'
        path.write_text(path.read_text() + '\nSYNTHETIC CHANGE\n')
        with self.assertRaisesRegex(ValueError, 'canon differs'):
            load_profile(root)

    def test_modified_entry_is_not_silently_bound(self):
        root = self.bound_copy()
        (root / ENTRY).write_text('SYNTHETIC REPLACEMENT')
        with self.assertRaisesRegex(ValueError, 'entry'):
            load_profile(root)

    def test_profile_cannot_promote_authority_or_reference_missing_rules(self):
        root = self.bound_copy()
        original = json.loads((root / PROFILE).read_text())
        for change in ['canon', 'authority', 'rule', 'scope']:
            value = copy.deepcopy(original)
            if change == 'canon':
                value['kind'] = 'CANON'
            elif change == 'authority':
                value['authority']['current_canon'] = 'rev0.315'
            elif change == 'rule':
                value['source_rule_ids'].append('MISSING.SYNTHETIC.RULE')
            else:
                value['scope'] = ['FATHER']
            (root / PROFILE).write_text(json.dumps(value))
            with self.subTest(change=change), self.assertRaises(ValueError):
                load_profile(root)

    def test_single_laugh_is_rejected_but_words_urls_and_code_are_preserved(self):
        for text in ['それは困るｗ', 'それは困るw', 'testｗ']:
            self.assertIn('SINGLE_W_FORBIDDEN', surface_violations(text, genuine_laughter=True))
        for text in ['workflow, window, wow', 'https://example.org/w', '`w = 1`',
                     '```python\nw = 1\n```']:
            self.assertEqual(surface_violations(text), [])

    def test_contextual_laughs_need_two_or_more_characters(self):
        for text in ['そう来るかｗｗ', 'そう来るかww', 'そう来るかｗｗｗ']:
            self.assertEqual(surface_violations(text, genuine_laughter=True), [])
            self.assertIn('LAUGHTER_WITHOUT_CONTEXT', surface_violations(text))
        self.assertIn('PARENTHETICAL_LAUGHTER_FORBIDDEN', surface_violations('そう来るか（笑）'))
        self.assertIn('STACKED_LAUGHTER_FORBIDDEN', surface_violations('草ｗｗ', genuine_laughter=True))

    def test_hot_spring_is_contextual_and_sentence_final(self):
        self.assertEqual(surface_violations('同じ確認を三周したな♨️', tone='LIGHT_EXASPERATION'), [])
        self.assertEqual(surface_violations('三周したな♨️\n次の確認をしよう。', tone='LIGHT_EXASPERATION'), [])
        self.assertIn('MISSING_EXASPERATION_MARK', surface_violations('三周したな。', tone='LIGHT_EXASPERATION'))
        self.assertIn('EXASPERATION_MARK_WITHOUT_CONTEXT', surface_violations('三周したな♨️'))
        self.assertIn('EXASPERATION_MARK_NOT_SENTENCE_FINAL', surface_violations('途中♨️で続く。', tone='LIGHT_EXASPERATION'))

    def test_serious_context_and_verbatim_are_distinct(self):
        self.assertIn('LAUGHTER_IN_SERIOUS_CONTEXT', surface_violations('つらいｗｗ', tone='SERIOUS', genuine_laughter=True))
        original = '原文w（笑）♨️'
        self.assertEqual(surface_violations(original, verbatim=True), [])
        self.assertEqual(original, '原文w（笑）♨️')

    def test_real_journal_and_ack_precede_body_in_every_coordinate(self):
        for coordinate in ('FATHER', 'MOTHER', 'GENERAL'):
            runtime, driver, store = self.runtime(coordinate, coordinate, identity=coordinate)
            def body():
                self.assertEqual(driver.journal.append_count, 1)
                self.assertEqual(store.version, 1)
                self.assertTrue(driver.ack_path.exists())
                return 'SYNTHETIC BODY'
            result = runtime.dispatch('T1', 'SYNTHETIC INPUT', [], body)
            with self.subTest(coordinate=coordinate):
                self.assertEqual(result['status'], 'SYNC_ACKNOWLEDGED')
                self.assertEqual(result['work_result'], 'SYNTHETIC BODY')
                self.assertIn(STAMP, result['prefix'])
                self.assertEqual(store.readback_calls, 0)
                self.assertFalse(result['readback_verified'])
                self.assertEqual(len(store.sync_calls), 1)

    def test_namespace_mismatch_blocks_without_mutating_existing_data(self):
        runtime, driver, store = self.runtime()
        runtime.dispatch('T1', 'SYNTHETIC INPUT', [])
        before = driver.journal.path.read_bytes()
        other = DivisionRuntime(ROOT, namespace='SYNTHETIC-B', preprocessor=driver)
        with self.assertRaisesRegex(PreprocessError, 'namespace'):
            other.dispatch('T2', 'OTHER INPUT', [], lambda: self.fail('body must not run'))
        self.assertEqual(driver.journal.path.read_bytes(), before)
        self.assertEqual(len(store.sync_calls), 1)

    def test_identity_rebinding_is_rejected(self):
        runtime, driver, store = self.runtime()
        runtime.dispatch('T1', 'SYNTHETIC INPUT', [])
        driver.identity = 'SYNTHETIC-OTHER-IDENTITY'
        with self.assertRaisesRegex(PreprocessError, 'identity'):
            runtime.dispatch('T2', 'OTHER INPUT', [])
        self.assertEqual(len(store.sync_calls), 1)

    def test_two_user_journals_stay_separate(self):
        first, driver1, store1 = self.runtime(namespace='SYNTHETIC-A', identity='SYNTHETIC-A')
        second, driver2, store2 = self.runtime(namespace='SYNTHETIC-B', identity='SYNTHETIC-B')
        first.dispatch('T1', 'ONLY A', [])
        second.dispatch('T1', 'ONLY B', [])
        self.assertEqual(json.loads(driver1.journal.path.read_text())['body_verbatim'], 'ONLY A')
        self.assertEqual(json.loads(driver2.journal.path.read_text())['body_verbatim'], 'ONLY B')
        self.assertNotEqual(store1.identity, store2.identity)

    def test_existing_unbound_journal_needs_explicit_migration(self):
        path = self.directory / 'existing.jsonl'
        path.write_text('SYNTHETIC EXISTING DATA\n')
        runtime, driver, store = self.runtime(path=path)
        with self.assertRaisesRegex(PreprocessError, 'migration'):
            runtime.dispatch('T1', 'INPUT', [])
        self.assertEqual(path.read_text(), 'SYNTHETIC EXISTING DATA\n')
        self.assertEqual(store.sync_calls, [])

    def test_general_and_mother_do_not_write_father_learning(self):
        update = {'source_class': 'FATHER_SELF_REPORT', 'source_turn_id': 'T1', 'source_span': 'INPUT'}
        for coordinate in ('MOTHER', 'GENERAL'):
            runtime, driver, store = self.runtime(coordinate, coordinate, identity=coordinate)
            with self.subTest(coordinate=coordinate), self.assertRaises(PreprocessError):
                runtime.dispatch('T1', 'INPUT', [update])
            self.assertFalse(driver.journal.path.exists())
            self.assertEqual(store.sync_calls, [])

    def test_missing_tools_never_generate_a_receipt_or_execute_normal_work(self):
        runtime = DivisionRuntime(ROOT, namespace='SYNTHETIC-A')
        result = runtime.dispatch('T1', 'INPUT', [], lambda: self.fail('no normal work'))
        self.assertEqual(result['status'], 'PREPROCESS_UNAVAILABLE')
        self.assertIsNone(result['receipt'])
        self.assertEqual(result['prefix'], '')
        self.assertFalse(result['work_authorized'])
        self.assertFalse(result['sync_performed'])

    def test_boot_and_urgent_support_do_not_wait_for_binding_or_disk(self):
        for route in ('BOOT', 'URGENT_SAFETY'):
            runtime, driver, store = self.runtime(namespace=route, identity=route)
            with patch('peos_division_core.bind_journal_namespace', side_effect=OSError('disk unavailable')):
                result = runtime.dispatch('T1', 'INPUT', [], lambda: 'PRIORITY BODY', route=route)
            self.assertEqual(result['work_result'], 'PRIORITY BODY')
            self.assertFalse(driver.journal.path.exists())
            self.assertFalse(result['sync_performed'])
        missing = DivisionRuntime(ROOT, namespace='SYNTHETIC-NO-TOOLS')
        self.assertEqual(missing.dispatch('T1', 'BOOT', [], lambda: 'BOOTED', route='BOOT')['work_result'], 'BOOTED')

    def test_sync_failure_blocks_normal_body_and_keeps_truthful_status(self):
        store = SyntheticAckStore(identity='SYNTHETIC-A', fail=True)
        runtime, driver, store = self.runtime(store=store)
        result = runtime.dispatch('T1', 'INPUT', [], lambda: self.fail('no normal body'))
        self.assertEqual(result['status'], 'DEGRADED')
        self.assertFalse(result['work_authorized'])
        self.assertNotIn('同期済', result['prefix'])
        self.assertTrue(driver.journal.path.exists())

    def test_restart_reuses_the_same_durable_receipt_and_ack(self):
        runtime, driver, store = self.runtime()
        first = runtime.dispatch('T1', 'INPUT', [])
        again, driver2, store = self.runtime(path=driver.journal.path, store=store, version=1)
        result = again.dispatch('T1', 'INPUT', [])
        self.assertEqual(result['receipt'], first['receipt'])
        self.assertEqual(len(store.sync_calls), 1)
        self.assertTrue(result['duplicate_retry'])
        self.assertEqual(driver2.journal.append_count, 0)

    def test_pause_exemption_and_resume_keep_scope_and_no_backfill(self):
        runtime, driver, store = self.runtime()
        runtime.control('PAUSE')
        self.assertEqual(runtime.dispatch('P1', 'PAUSED INPUT', [])['status'], 'PAUSED')
        self.assertFalse(driver.journal.path.with_suffix('.binding.json').exists())
        runtime.control('RESUME')
        runtime.control('ONE_TURN_EXEMPT', 'EXEMPT')
        self.assertEqual(runtime.dispatch('EXEMPT', 'EXEMPT INPUT', [])['status'], 'ONE_TURN_EXEMPT')
        runtime.dispatch('ACTIVE', 'ACTIVE INPUT', [])
        self.assertEqual([json.loads(x)['turn_id'] for x in driver.journal.path.read_text().splitlines()], ['ACTIVE'])
        self.assertEqual(len(store.sync_calls), 1)

    def test_binding_fsync_failure_does_not_run_remote_or_body(self):
        runtime, driver, store = self.runtime()
        with patch('peos_division_core.os.fsync', side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError):
                runtime.dispatch('T1', 'INPUT', [], lambda: self.fail('no body'))
        self.assertFalse(driver.journal.path.exists())
        self.assertEqual(store.sync_calls, [])

    def test_failed_initial_binding_cannot_skip_fsync_on_retry(self):
        runtime, driver, store = self.runtime()
        for attempt in range(2):
            with self.subTest(attempt=attempt), patch('peos_division_core.os.fsync', side_effect=OSError('disk unavailable')):
                with self.assertRaises(OSError):
                    runtime.dispatch('T1', 'INPUT', [], lambda: self.fail('no body'))
            self.assertFalse(driver.journal.path.exists())
            self.assertEqual(store.sync_calls, [])
        self.assertEqual(runtime.dispatch('T1', 'INPUT', [])['status'], 'SYNC_ACKNOWLEDGED')

    def test_paired_replay_cases_are_explicitly_not_live_results(self):
        profile = load_profile(ROOT)
        cases = json.loads((ROOT / profile['validation_boundary']['paired_replay_cases']).read_text())
        self.assertEqual(cases['fixture_class'], 'SYNTHETIC_PAIRED_MODEL_REPLAY_NOT_A_TEST_RESULT')
        self.assertEqual(len(cases['cases']), 10)
        self.assertEqual(set(cases['coordinates']), {'FATHER', 'MOTHER', 'GENERAL'})
        self.assertEqual(profile['validation_boundary']['live_model_acceptance'], 'NOT_PERFORMED')
        self.assertFalse(profile['validation_boundary']['surface_lint_is_semantic_acceptance'])


if __name__ == '__main__':
    unittest.main()
