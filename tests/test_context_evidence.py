"""Typed modality, quote spans and honest clocks; no private examples."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from peos_context_evidence import observe, correct_inferred_modality, attribute_spans, clock_evidence


class ContextEvidenceTests(unittest.TestCase):
    def claim(self, mode='ASSERTED', **values):
        return dict(subject_key='SYNTHETIC-OUTCOME',claim_id='C1',mode=mode,
                    source_class='USER_REPORT',source_ref='SYNTHETIC-T1',value='REJECTED',**values)

    def test_hypothetical_outcome_is_not_an_actual_rejection(self):
        r=observe(None,self.claim('HYPOTHETICAL'))
        self.assertEqual(r['actual_status'],'UNREPORTED');self.assertIsNone(r['reported_value'])

    def test_metaphor_is_not_a_physical_fact(self):
        self.assertIsNone(observe(None,self.claim('METAPHOR'))['reported_value'])

    def test_reenactment_is_not_verbatim_external_conversation(self):
        self.assertEqual(observe(None,self.claim('APPROXIMATE_REENACTMENT'))['actual_status'],'UNREPORTED')

    def test_quote_is_not_a_self_report(self):
        self.assertEqual(observe(None,self.claim('QUOTED_OTHER'))['actual_status'],'UNREPORTED')

    def test_assistant_inference_does_not_establish_an_actual_result(self):
        c=self.claim();c['source_class']='ASSISTANT_INFERENCE'
        self.assertEqual(observe(None,c)['actual_status'],'UNREPORTED')

    def test_asserted_user_result_is_typed_as_report_not_independent_proof(self):
        self.assertEqual(observe(None,self.claim())['actual_status'],'USER_REPORTED')

    def test_later_hypothesis_does_not_erase_a_reported_result(self):
        r=observe(None,self.claim());h=self.claim('HYPOTHETICAL');h['claim_id']='C2'
        self.assertEqual(observe(r,h)['reported_value'],'REJECTED')

    def test_different_subject_cannot_overwrite_current_value(self):
        r=observe(None,self.claim());c=self.claim();c['subject_key']='SYNTHETIC-OTHER'
        with self.assertRaises(ValueError):observe(r,c)

    def test_legacy_wrong_inference_is_retracted_by_a_linked_correction(self):
        r=observe(None,self.claim());r['actual_source_class']='ASSISTANT_INFERENCE'
        c=dict(subject_key='SYNTHETIC-OUTCOME',source_class='USER_CORRECTION',source_ref='SYNTHETIC-T2',mode='HYPOTHETICAL',correction_of='C1')
        after=correct_inferred_modality(r,c)
        self.assertEqual(after['actual_status'],'UNREPORTED');self.assertIsNone(after['reported_value'])
        self.assertEqual(r['reported_value'],'REJECTED')

    def test_unlinked_correction_cannot_retract_another_claim(self):
        r=observe(None,self.claim());c=dict(subject_key='SYNTHETIC-OUTCOME',source_class='USER_CORRECTION',source_ref='SYNTHETIC-T2',mode='HYPOTHETICAL',correction_of='OTHER')
        with self.assertRaises(ValueError):correct_inferred_modality(r,c)

    def test_independent_evidence_is_retained_as_a_review_conflict(self):
        c=self.claim();c['source_class']='PHYSICAL_EVIDENCE';r=observe(None,c)
        correction=dict(subject_key='SYNTHETIC-OUTCOME',source_class='USER_CORRECTION',source_ref='SYNTHETIC-T2',mode='HYPOTHETICAL',correction_of='C1')
        after=correct_inferred_modality(r,correction)
        self.assertEqual(after['actual_status'],'EVIDENCED');self.assertEqual(after['correction_status'],'REVIEW_CONFLICT_WITH_EXISTING_EVIDENCE')

    def test_partial_self_attribution_does_not_claim_the_whole_image(self):
        text='SELF|OTHER'
        spans=[dict(start=0,end=4,speaker='USER_SELF_ATTRIBUTED',source_ref='SYNTHETIC-CORRECTION'),dict(start=5,end=10,speaker='THIRD_PARTY',source_ref='SYNTHETIC-IMAGE')]
        r=attribute_spans(text,spans)
        self.assertTrue(r[0]['father_primary_eligible']);self.assertFalse(r[1]['father_primary_eligible'])
        self.assertEqual([s['text'] for s in r],['SELF','OTHER'])

    def test_unknown_and_overlapping_speaker_spans_are_not_self_promoted(self):
        self.assertFalse(attribute_spans('TEXT',[dict(start=0,end=4,speaker='UNKNOWN',source_ref='SYNTHETIC')])[0]['father_primary_eligible'])
        with self.assertRaises(ValueError):attribute_spans('TEXT',[dict(start=0,end=3,speaker='THIRD_PARTY',source_ref='SYNTHETIC'),dict(start=2,end=4,speaker='USER_SELF_ATTRIBUTED',source_ref='SYNTHETIC')])

    def test_missing_observation_clock_is_omitted_not_backfilled(self):
        r=clock_evidence(persisted_at='2032-01-02T03:04:05+09:00')
        self.assertNotIn('observed_at_jst',r);self.assertFalse(r['strict_pass_claimed'])
        with self.assertRaises(ValueError):clock_evidence(ingress_proven=True)

    def test_deferred_outage_clock_is_not_original_ingress(self):
        r=clock_evidence(observed_at='2032-01-02T03:04:05+09:00',persisted_at='2032-01-02T03:06:00+09:00',capture_kind='DEFERRED_AFTER_OUTAGE')
        self.assertFalse(r['original_ingress_proven']);self.assertNotEqual(r['observed_at_jst'],r['persisted_at_jst'])
        with self.assertRaises(ValueError):clock_evidence(observed_at='2032-01-02T03:04:05+09:00',capture_kind='DEFERRED_AFTER_OUTAGE',ingress_proven=True)

    def test_reconnected_request_can_have_its_own_supplied_clock(self):
        r=clock_evidence(observed_at='2032-01-02T04:00:00+09:00',capture_kind='RECONNECTED_REQUEST')
        self.assertEqual(r['capture_kind'],'RECONNECTED_REQUEST');self.assertFalse(r['strict_pass_claimed'])

    def test_utc_invalid_clock_and_reverse_persistence_are_rejected(self):
        for stamp in ['2032-01-02T03:04:05+00:00','not-a-clock']:
            with self.assertRaises(ValueError):clock_evidence(observed_at=stamp,capture_kind='DIRECT_OBSERVATION')
        with self.assertRaises(ValueError):clock_evidence(observed_at='2032-01-02T03:04:05+09:00',persisted_at='2032-01-02T03:00:00+09:00',capture_kind='DIRECT_OBSERVATION')


if __name__ == '__main__':unittest.main()
