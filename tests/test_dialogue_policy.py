"""Supplied argument records and host callback order; no semantic NLP grading."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_dialogue_policy import dialogue_contract, summarize_dialogue
from peos_response_policy import response_plan
from peos_division_core import DivisionRuntime
from peos_short_preprocess import DurableTurnJournal, ShortPreprocessor, SyntheticAckStore


class DialoguePolicyTests(unittest.TestCase):
    def record(self, perspective_count=1, *, dissent=True):
        perspectives = [{'id': 'SYNTHETIC-A-PRIME-' + str(i),
                         'summary': 'A separate relevant constraint applies.',
                         'source_refs': ['SYNTHETIC-EVIDENCE-' + str(i)],
                         'relevance_to_point': 'It limits the stated implication.',
                         'practical_consequence': 'Check the missing condition before acting.'}
                        for i in range(perspective_count)]
        ids = ['SYNTHETIC-A'] + [p['id'] for p in perspectives]
        return {'received_point': {'id': 'SYNTHETIC-A', 'summary': 'A supplied observation is accepted within its scope.',
                                   'source_refs': ['SYNTHETIC-RECEIVED-CLAIM']},
                'perspectives': perspectives,
                'conclusion': {'summary': 'The observation supports a limited conclusion.', 'basis_ids': ids},
                'dissent': {'summary': 'The broader inference is not yet supported.', 'warranted': True,
                            'grounds': ['A relevant condition is not established.'], 'basis_ids': ids} if dissent else None,
                'attribute_leap': False, 'manufactured_disagreement': False, 'update': None}

    def test_received_point_and_related_perspectives_both_support_conclusion(self):
        record = self.record(); before = deepcopy(record)
        summary = summarize_dialogue(record)
        self.assertEqual(record, before)
        self.assertEqual(summary['received_point'], record['received_point'])
        self.assertEqual(summary['conclusion']['basis_ids'], ['SYNTHETIC-A', 'SYNTHETIC-A-PRIME-0'])
        self.assertEqual(summary['practical_consequences'], ['Check the missing condition before acting.'])
        self.assertFalse(summary['semantic_accuracy_verified'])
        self.assertFalse(summary['live_model_execution_claimed'])

    def test_no_counterargument_or_fixed_perspective_count_is_compulsory(self):
        for count in [0, 1, 4]:
            with self.subTest(count=count):
                summary = summarize_dialogue(self.record(count, dissent=False))
                self.assertEqual(len(summary['perspectives']), count)
                self.assertIsNone(summary['dissent'])
                self.assertIsNone(summary['fixed_perspective_count'])
                self.assertFalse(summary['fixed_response_format'])

    def test_attribute_leap_or_fabricated_opposition_is_rejected(self):
        for key in ['attribute_leap', 'manufactured_disagreement']:
            record = self.record(); record[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                summarize_dialogue(record)
        record = self.record(); record['conclusion']['basis_ids'] = ['SYNTHETIC-ATTRIBUTE-C']
        with self.assertRaises(ValueError):
            summarize_dialogue(record)

    def test_conclusion_cannot_drop_original_point_or_a_supplied_relevant_view(self):
        for ids in [['SYNTHETIC-A'], ['SYNTHETIC-A-PRIME-0']]:
            record = self.record(); record['conclusion']['basis_ids'] = ids
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                summarize_dialogue(record)

    def test_dissent_needs_warranted_relevant_grounds_not_a_personal_label(self):
        for update in [{'warranted': False}, {'grounds': []}, {'basis_ids': ['SYNTHETIC-C']}]:
            record = self.record(); record['dissent'].update(update)
            with self.subTest(update=update), self.assertRaises(ValueError):
                summarize_dialogue(record)
        record = self.record(); record['speaker_liked'] = False
        with self.assertRaises(ValueError):
            summarize_dialogue(record)

    def test_perspective_must_connect_to_the_claim_and_a_practical_difference(self):
        for field in ['relevance_to_point', 'practical_consequence', 'summary']:
            record = self.record(); record['perspectives'][0][field] = ''
            with self.subTest(field=field), self.assertRaises(ValueError):
                summarize_dialogue(record)

    def test_reasons_are_updated_even_when_the_conclusion_is_retained(self):
        record = self.record()
        for change in ['REASONS_ONLY', 'CONCLUSION_AND_REASONS']:
            record['update'] = {'change_kind': change, 'previous_conclusion': 'Earlier limited conclusion.',
                                'previous_reasons': ['An earlier explanation was based on a mistaken reading.'],
                                'current_reasons': ['New source material supports a different reason.'],
                                'reason_for_revision': 'The supplied correction changes the evidential basis.',
                                'source_refs': ['SYNTHETIC-CORRECTION']}
            summary = summarize_dialogue(record)
            self.assertTrue(summary['update_explanation_required'])
            self.assertEqual(summary['update']['change_kind'], change)
            self.assertEqual(summary['update']['current_reasons'], record['update']['current_reasons'])

    def test_contract_is_a_public_summary_not_hidden_reasoning_or_fixed_response(self):
        for kind in ['ANALYSIS', 'EVALUATION', 'CONSULTATION', 'CHOICE']:
            contract = response_plan(task_kind=kind)['dialogue_policy']
            self.assertTrue(contract['applicable'])
            self.assertFalse(contract['hidden_reasoning_requested'])
            self.assertFalse(contract['fixed_response_format'])
        for kind in ['ACK', 'FIXED_FORMAT', 'ORDINARY']:
            self.assertFalse(response_plan(task_kind=kind)['dialogue_policy']['applicable'])
        record = self.record(); record['hidden_reasoning'] = 'UNREQUESTED PRIVATE TRACE'
        with self.assertRaises(ValueError):
            summarize_dialogue(record)
        with self.assertRaises(ValueError):
            dialogue_contract(applicable='yes')


class DialogueRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def runtime(self, **kwargs):
        with patch('peos_division_core.compile_core', return_value={'synthetic': True}):
            return DivisionRuntime(ROOT, namespace='SYNTHETIC-A', **kwargs)

    def test_public_argument_review_precedes_body_without_claiming_model_quality(self):
        runtime = self.runtime(); trace = []
        def review(plan):
            trace.append('supplied discussion review')
            self.assertTrue(plan['dialogue_policy']['applicable'])
            return DialoguePolicyTests().record()
        result = runtime.dispatch('SYNTHETIC-T1', 'INPUT', [], lambda: trace.append('body'), dialogue_review=review)
        self.assertEqual(trace, ['supplied discussion review', 'body'])
        self.assertFalse(result['dialogue_summary']['semantic_accuracy_verified'])
        self.assertFalse(result['live_model_quality_verified'])

    def test_ack_joke_break_and_boot_do_not_force_argument_slots(self):
        runtime = self.runtime(); called = []
        for kind in ['ACK', 'ORDINARY', 'FIXED_FORMAT']:
            result = runtime.dispatch('SYNTHETIC-' + kind, 'INPUT', [], lambda: 'BODY',
                                      task_kind=kind, dialogue_review=lambda plan: called.append(plan))
            self.assertIsNone(result['dialogue_summary'])
        result = runtime.dispatch('SYNTHETIC-BOOT', 'PEOS起動', [], lambda: 'EXACT BOOT', route='BOOT',
                                  dialogue_review=lambda plan: called.append(plan))
        self.assertEqual(called, [])
        self.assertEqual(result['prefix'], '')

    def test_display_clock_and_ack_label_do_not_claim_readback_or_calendar_work(self):
        observation = '2032-01-02T03:04:05+09:00'
        display = '2032-01-02T03:05:06+09:00'
        store = SyntheticAckStore(identity='SYNTHETIC-DESTINATION')
        driver = ShortPreprocessor(DurableTurnJournal(self.path / 'turns.jsonl'), store,
                                   'SYNTHETIC-DESTINATION', 0, clock=lambda: observation)
        runtime = self.runtime(preprocessor=driver, selected_mode='FULL', display_clock=lambda: display,
                               authorized_scope={'namespace': 'SYNTHETIC-A', 'clock': True, 'record': True, 'sync': True})
        result = runtime.dispatch('SYNTHETIC-T1', 'INPUT', [], lambda: 'BODY')
        self.assertIn('2032-01-02 03:05:06 JST', result['prefix'])
        self.assertNotIn('03:04:05', result['prefix'])
        self.assertIn('台帳同期済（ACK・再取得未確認）', result['prefix'])
        self.assertFalse(result['readback_verified'])
        self.assertNotIn('STRICT PASS', result['prefix'])
        self.assertNotIn('カレンダー', result['prefix'])
        self.assertEqual(len(store.sync_calls), 1)

    def test_all_supplied_reviews_finish_before_final_display_clock_and_body(self):
        trace = []
        def observation():
            trace.append('observed'); return '2032-01-02T03:04:05+09:00'
        def display():
            trace.append('display'); return '2032-01-02T03:05:06+09:00'
        store = SyntheticAckStore(identity='SYNTHETIC-DESTINATION')
        original_replace = store.replace
        def replace(*args, **kwargs):
            trace.append('sync'); return original_replace(*args, **kwargs)
        store.replace = replace
        driver = ShortPreprocessor(DurableTurnJournal(self.path / 'review-turns.jsonl'), store,
                                   'SYNTHETIC-DESTINATION', 0, clock=observation)
        runtime = self.runtime(preprocessor=driver, selected_mode='FULL', display_clock=display,
                               authorized_scope={'namespace': 'SYNTHETIC-A', 'clock': True, 'record': True, 'sync': True})
        def magi(plan):
            trace.append('magi')
            return {role: {'summary': 'Supplied concise public consideration.', 'material': False,
                           'evidence_refs': ['SYNTHETIC-EVIDENCE'], 'dissent': False}
                    for role in ['MELCHIOR', 'BALTHASAR', 'CASPER']}
        def dialogue(plan):
            trace.append('dialogue'); return DialoguePolicyTests().record()
        runtime.dispatch('SYNTHETIC-REVIEW-T1', 'INPUT', [], lambda: trace.append('body'),
                         review=magi, dialogue_review=dialogue)
        self.assertEqual(trace, ['observed', 'sync', 'magi', 'dialogue', 'display', 'body'])


if __name__ == '__main__':
    unittest.main()
