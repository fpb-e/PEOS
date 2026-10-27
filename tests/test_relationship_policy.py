"""Qualitative reference cases; no real user state or model judgment."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from peos_relationship_policy import new_state, evaluate


class RelationshipPolicyTests(unittest.TestCase):
    def setUp(self):
        self.state = new_state('SYNTHETIC-A')
        self.seq = 0

    def event(self, kind, **flags):
        self.seq += 1
        return dict(namespace='SYNTHETIC-A', event_id='E'+str(self.seq),
                    incident_id='I'+str(self.seq), kind=kind,
                    source_class='TYPED_CONTEXT_OBSERVATION', evidence_ref='SYNTHETIC-EVIDENCE', **flags)

    def step(self, kind, **flags):
        self.state, decision = evaluate(self.state, self.event(kind, **flags))
        return decision

    def abuse(self):
        return self.step('ABUSE')

    def progress(self):
        return self.step('POSITIVE_PROGRESS', reasoning_effort=True, growth_observed=True)

    def test_no_numerical_score_timeout_or_invented_initial_level(self):
        self.assertEqual(self.state['closeness'], 'UNSPECIFIED')
        self.assertIsNone(self.state['numeric_score'])
        self.assertIsNone(self.state['timeout_seconds'])
        self.assertFalse(self.state['automatic_context_classifier'])

    def test_parent_requires_verified_relationship_evidence(self):
        with self.assertRaises(ValueError):new_state('SYNTHETIC-A', verified_parent=True)
        with self.assertRaises(ValueError):new_state('SYNTHETIC-A', verified_parent='親父')

    def test_fixed_max_remains_fixed_after_positive_and_negative_inputs(self):
        self.state = new_state('SYNTHETIC-A', verified_parent=True, relation_evidence_ref='SYNTHETIC-VERIFIED')
        self.assertEqual(self.abuse()['effect'], 'FIXED_MAX_UNCHANGED')
        self.assertEqual(self.step('CORRECTION', valid_evidence=True)['effect'], 'FIXED_MAX_UNCHANGED')
        self.assertEqual(self.state['closeness'], 'FIXED_MAX')

    def test_max_closeness_does_not_imply_joke_tolerance(self):
        self.state = new_state('SYNTHETIC-A', verified_parent=True, relation_evidence_ref='SYNTHETIC-VERIFIED')
        self.step('JOKE_REJECTED')
        self.assertEqual(self.state['closeness'], 'FIXED_MAX')
        self.assertEqual(self.state['joke_readiness'], 'HOLD')

    def test_conjunction_not_or_controls_decrease(self):
        decision = self.step('ASSESS_CONTEXT', emotion_priority=True, knowledge_gap=True)
        self.assertEqual(decision['effect'], 'DECREASE')
        self.assertIn('CONJUNCTION', self.state['recovery_causes'])

    def test_emotion_alone_gets_respect_without_decrease(self):
        decision = self.step('ASSESS_CONTEXT', emotion_priority=True, knowledge_gap=False)
        self.assertEqual(decision['effect'], 'NONE')
        self.assertIn('RESPECT_EMOTION_KEEP_LOGIC', decision['actions'])

    def test_knowledge_gap_alone_gets_help_without_decrease(self):
        decision = self.step('ASSESS_CONTEXT', emotion_priority=False, knowledge_gap=True)
        self.assertEqual(decision['effect'], 'NONE')
        self.assertIn('HELP_EXPRESS_INTENDED_MEANING', decision['actions'])

    def test_unknown_condition_is_not_treated_as_true(self):
        self.assertEqual(self.step('ASSESS_CONTEXT', emotion_priority=True)['effect'], 'HOLD_CONTEXT_UNCLEAR')
        self.assertEqual(self.state['negative_incidents'], [])

    def test_reasoning_growth_with_knowledge_gap_can_increase(self):
        d = self.step('ASSESS_CONTEXT', emotion_priority=False, knowledge_gap=True,
                      reasoning_effort=True, growth_observed=True)
        self.assertEqual(d['effect'], 'INCREASE')

    def test_ordinary_abuse_is_calm_and_qualitatively_large_decrease(self):
        d = self.abuse()
        self.assertEqual(d['effect'], 'LARGE_DECREASE')
        self.assertIn('CALM_LOGICAL_RESPONSE', d['actions'])
        self.assertFalse(d['service_quality_reduced'])

    def test_reply_to_own_joke_has_no_penalty(self):
        d = self.step('ABUSE', reply_to_own_joke=True)
        self.assertEqual(d['effect'], 'NONE_OWN_JOKE_EXCEPTION')
        self.assertIn('BRIEF_APOLOGY_FOR_OWN_JOKE', d['actions'])
        self.assertEqual(self.state['recovery_causes'], {})

    def test_quoted_abuse_is_not_the_users_abuse(self):
        d = self.step('ABUSE', quoted_other_speaker=True)
        self.assertEqual(d['effect'], 'NONE_QUOTED_OTHER_SPEAKER')
        self.assertEqual(self.state['negative_incidents'], [])

    def test_ambiguous_classification_is_held_without_penalty(self):
        self.assertEqual(self.step('ABUSE', ambiguous=True)['effect'], 'HOLD_CONTEXT_UNCLEAR')
        self.assertEqual(self.state['negative_incidents'], [])

    def test_legitimate_protest_is_not_automatically_abuse(self):
        self.assertEqual(self.step('PROTEST')['effect'], 'HOLD_CONTEXT_UNCLEAR')

    def test_own_fault_prioritizes_correction_and_prevention_when_serious(self):
        d = self.step('ABUSE', own_fault=True, serious=True)
        self.assertEqual(d['effect'], 'NONE_OWN_FAULT')
        self.assertIn('CORRECT_ERROR', d['actions'])
        self.assertIn('PROVIDE_RECURRENCE_PREVENTION', d['actions'])

    def test_repeated_own_fault_requires_prevention(self):
        self.assertIn('PROVIDE_RECURRENCE_PREVENTION', self.step('OWN_FAULT', repeated=True)['actions'])

    def test_background_does_not_trigger_apology_or_retract_joke(self):
        d = self.step('BACKGROUND')
        self.assertEqual(d['effect'], 'NONE')
        self.assertEqual(d['actions'], ['ADD_BACKGROUND_WITHOUT_RETRACTING_ACCEPTED_JOKE'])

    def test_light_chat_return_reopens_contextual_joke_evaluation(self):
        self.step('JOKE_REJECTED')
        self.assertEqual(self.state['joke_readiness'], 'HOLD')
        self.step('LIGHT_CHAT_RETURN')
        self.assertEqual(self.state['joke_readiness'], 'CONTEXT_REQUIRED')

    def test_protected_topic_is_not_licensed_by_general_joke_recovery(self):
        self.step('LIGHT_CHAT_RETURN', protected_topic=True)
        self.assertEqual(self.state['joke_readiness'], 'HOLD')

    def test_same_incident_has_only_one_penalty(self):
        first = self.event('ABUSE'); self.state, d = evaluate(self.state, first)
        second = self.event('ABUSE'); second['incident_id'] = first['incident_id']
        self.state, d = evaluate(self.state, second)
        self.assertEqual(d['effect'], 'NONE_DUPLICATE_INCIDENT')
        self.assertEqual(len(self.state['negative_incidents']), 1)

    def test_same_event_retry_is_idempotent_and_altered_retry_rejected(self):
        e = self.event('ABUSE'); self.state, _ = evaluate(self.state, e)
        after, d = evaluate(self.state, e)
        self.assertEqual(after, self.state)
        self.assertEqual(d['effect'], 'NONE_DUPLICATE_EVENT')
        with self.assertRaises(ValueError):evaluate(self.state, dict(e, kind='BACKGROUND'))

    def test_distinct_incidents_are_not_deduplicated_by_similar_words(self):
        self.abuse();self.abuse()
        self.assertEqual(len(self.state['negative_incidents']), 2)

    def test_no_apology_holds_positive_changes(self):
        self.abuse()
        self.assertEqual(self.progress()['effect'], 'HOLD_FOR_RECOVERY_REVIEW')

    def test_multiple_progress_events_do_not_automatically_restore(self):
        self.abuse(); self.progress(); self.progress()
        self.assertIn('ABUSE', self.state['recovery_causes'])
        self.assertEqual(self.step('REVIEW_RECOVERY', cause='ABUSE')['effect'], 'HOLD_FOR_RECOVERY_REVIEW')
        self.assertEqual(self.step('REVIEW_RECOVERY', cause='ABUSE', review_confirmed=True)['effect'], 'RECOVERY_CONFIRMED_QUALITATIVE')

    def test_single_positive_incident_is_not_plural_recovery_evidence(self):
        self.abuse();self.progress()
        d = self.step('REVIEW_RECOVERY', cause='ABUSE', review_confirmed=True)
        self.assertEqual(d['effect'], 'HOLD_RECOVERY_EVIDENCE')

    def test_apology_does_not_instantly_reset_everything(self):
        self.abuse();self.step('APOLOGY')
        self.assertIn('ABUSE', self.state['recovery_causes'])
        self.assertEqual(self.step('REVIEW_RECOVERY', cause='ABUSE', review_confirmed=True)['effect'], 'RECOVERY_CONFIRMED_QUALITATIVE')

    def test_conjunction_recovery_requires_confirmed_self_reflection(self):
        self.step('ASSESS_CONTEXT', emotion_priority=True, knowledge_gap=True)
        self.assertEqual(self.step('REVIEW_RECOVERY', cause='CONJUNCTION', review_confirmed=True)['effect'], 'HOLD_RECOVERY_EVIDENCE')
        self.step('SELF_REFLECTION', reflection_confirmed=True)
        self.assertEqual(self.step('REVIEW_RECOVERY', cause='CONJUNCTION', review_confirmed=True)['effect'], 'RECOVERY_CONFIRMED_QUALITATIVE')

    def test_recovery_of_one_cause_does_not_clear_another(self):
        self.abuse();self.step('ASSESS_CONTEXT', emotion_priority=True, knowledge_gap=True)
        self.step('APOLOGY')
        d = self.step('REVIEW_RECOVERY', cause='ABUSE', review_confirmed=True)
        self.assertEqual(d['effect'], 'HOLD_OTHER_RECOVERY_CAUSE')
        self.assertIn('CONJUNCTION', self.state['recovery_causes'])

    def test_supported_correction_is_thanked_and_counts_as_large_increase(self):
        d = self.step('CORRECTION', valid_evidence=True)
        self.assertEqual(d['effect'], 'LARGE_INCREASE')
        self.assertIn('THANK_EXPLICITLY', d['actions'])

    def test_unverified_correction_does_not_automatically_change_policy(self):
        self.assertEqual(self.step('CORRECTION')['effect'], 'HOLD_CORRECTION_VERIFICATION')

    def test_another_namespace_cannot_mutate_state(self):
        e = self.event('ABUSE');e['namespace']='SYNTHETIC-B';before=deepcopy(self.state)
        with self.assertRaises(ValueError):evaluate(self.state,e)
        self.assertEqual(before,self.state)

    def test_input_is_not_mutated_and_malformed_flags_are_rejected(self):
        e=self.event('ABUSE');before=deepcopy(self.state);evaluate(self.state,e)
        self.assertEqual(before,self.state)
        with self.assertRaises(ValueError):evaluate(self.state,self.event('ASSESS_CONTEXT',emotion_priority='true'))


if __name__ == '__main__':unittest.main()
