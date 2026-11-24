"""Shared style transport and scope boundaries; no model prose is graded."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_style_policy import COORDINATES, style_contract
from peos_response_policy import response_plan
from peos_division_core import compile_core


class SharedStyleTests(unittest.TestCase):
    def test_learning_origin_does_not_restrict_authorized_application(self):
        styles = [style_contract(coordinate=c) for c in COORDINATES]
        self.assertTrue(all(x == styles[0] for x in styles))
        self.assertEqual(styles[0]['source_coordinate'], 'FATHER')
        self.assertEqual(styles[0]['application_coordinate'], 'ALL')
        self.assertEqual(styles[0]['authorized_coordinates'], list(COORDINATES))
        self.assertEqual(style_contract(), styles[0])

    def test_unknown_route_cannot_claim_style_application(self):
        with self.assertRaises(ValueError):
            style_contract(coordinate='SYNTHETIC_UNKNOWN')
        with self.assertRaises(ValueError):
            response_plan(coordinate='SYNTHETIC_UNKNOWN')

    def test_mutating_one_route_cannot_change_another_routes_contract(self):
        first = style_contract(coordinate='FATHER')
        first['cadence_resources']['negative_variants'].clear()
        first['authorized_coordinates'].clear()
        later = style_contract(coordinate='MOTHER')
        self.assertEqual(set(later['cadence_resources']['negative_variants']),
                         {'じゃねーよ', 'じゃねえよ', 'じゃねぇよ'})
        self.assertEqual(later['authorized_coordinates'], list(COORDINATES))

    def test_reported_cadence_has_no_invented_quota_or_rotation(self):
        value = style_contract()
        resource = value['cadence_resources']
        close = resource['ellipsis_close']
        self.assertEqual([f'U+{ord(c):04X}' for c in close['text']], close['codepoints'])
        self.assertEqual(close['text'], '…。')
        self.assertEqual(resource['pause_or_unfinished_close'], '…')
        self.assertEqual(close['usage_basis'], 'OWNER_REPORTED_MOST_COMMON_NOT_MEASURED')
        for key in ('fixed_frequency', 'fixed_ratio', 'sentence_ending_assignment', 'variant_rotation'):
            self.assertIsNone(value[key])
        self.assertFalse(value['resources_required_every_turn'])
        self.assertFalse(value['resources_required_every_sentence'])
        self.assertFalse(resource['negative_variants_ordered'])
        self.assertIsNone(resource['negative_variants_strength_ranking'])

    def test_style_does_not_supply_private_relation_state_or_authority(self):
        value = style_contract(coordinate='GENERAL')
        self.assertEqual(value['relation_fields'], 'EXISTING_SCOPED_ADAPTER_ONLY')
        self.assertTrue({'call_sign', 'private_history', 'authority'} <=
                        set(value['relation_fields_not_inherited_from_style_source']))
        self.assertNotIn('relation_adapter', value)
        self.assertNotIn('local_state', value)
        self.assertNotIn('canonical_call_sign', value)

    def test_quote_spelling_and_assistant_example_attribution_are_not_rewritten(self):
        quoted = '「じゃねーよ…」と「じゃねえよ。」は異なる引用。'
        before = quoted.encode('utf-8')
        value = style_contract()
        self.assertEqual(value['quote_policy'],
                         'PRESERVE_ORIGINAL_SPELLING_PUNCTUATION_AND_ATTRIBUTION')
        self.assertFalse(value['automatic_text_rewrite'])
        self.assertFalse(value['assistant_examples_are_owner_quotes'])
        self.assertEqual(quoted.encode('utf-8'), before)
        self.assertFalse(value['examples_are_output_templates'])

    def test_five_canon_projection_does_not_require_reinject_supplements(self):
        value = style_contract()
        self.assertEqual(value['normative_source'], 'FIVE_CURRENT_CANONS')
        self.assertEqual(value['required_supplement_files'], [])
        self.assertFalse(value['surface_marks_prove_semantic_acceptance'])
        self.assertEqual(value['live_model_acceptance'], 'NOT_PERFORMED')

    def test_response_plans_transport_same_style_for_all_coordinates(self):
        for task in ('ANALYSIS', 'ORDINARY', 'ACK', 'FIXED_FORMAT'):
            plans = [response_plan(task_kind=task, coordinate=c) for c in COORDINATES]
            self.assertTrue(all(p['speech_style'] == style_contract() for p in plans))
            self.assertTrue(all(p['semantic_acceptance'] ==
                                'REQUIRES_ACTUAL_MODEL_RESPONSE_REVIEW' for p in plans))

    def test_brevity_is_turn_local_and_does_not_erase_shared_voice(self):
        brief = response_plan(brief_requested=True, coordinate='MOTHER')
        ordinary = response_plan(coordinate='MOTHER')
        self.assertEqual(brief['length'], 'BRIEF_FOR_THIS_TURN')
        self.assertEqual(ordinary['length'], 'LONG_REASONED_BY_DEFAULT')
        self.assertEqual(brief['speech_style'], ordinary['speech_style'])
        self.assertEqual(response_plan(task_kind='ACK')['length'], 'BRIEF_FOR_THIS_TURN')
        self.assertEqual(response_plan(task_kind='FIXED_FORMAT')['length'], 'HONOR_FIXED_FORMAT')

    def test_low_affinity_length_exception_preserves_style_and_reasoning_floor(self):
        with patch('peos_response_policy.response_context', return_value={'affinity_band': 'LOW'}):
            low = response_plan(relationship_state={'synthetic': True}, namespace='SYNTHETIC', coordinate='GENERAL')
        ordinary = response_plan(coordinate='GENERAL')
        self.assertEqual(low['length'], 'CONCISE_REASONED_LOW_AFFINITY')
        self.assertEqual(low['speech_style'], ordinary['speech_style'])
        self.assertEqual(low['quality_floor'], ordinary['quality_floor'])

    def profile(self):
        return {'profile_id': 'SYNTHETIC_STYLE_PROFILE', 'scope': list(COORDINATES),
                'shared_core': {'prose': {'first_person': '俺'}}}

    def test_compilation_keeps_shared_style_hash_with_scoped_adapters(self):
        profile = self.profile()
        original = copy.deepcopy(profile)
        with patch('peos_division_core.load_profile', return_value=profile):
            values = [compile_core(ROOT, c, {'local_state': {'namespace': c}}) for c in COORDINATES]
        self.assertEqual(profile, original)
        self.assertEqual(len({v['core_sha256'] for v in values}), 1)
        self.assertTrue(all(v['shared_core']['speech_style'] == style_contract() for v in values))
        self.assertEqual(values[0]['relation_adapter']['canonical_call_sign'], '親父')
        self.assertEqual(values[1]['relation_adapter']['canonical_call_sign'], 'お母さん')
        self.assertNotIn('canonical_call_sign', values[2]['relation_adapter'])
        self.assertTrue(all(v['runtime_ready'] is False for v in values))

    def test_relation_adapter_cannot_replace_global_speech_contract(self):
        with patch('peos_division_core.load_profile', return_value=self.profile()):
            for coordinate in COORDINATES:
                with self.subTest(coordinate=coordinate), self.assertRaises(ValueError):
                    compile_core(ROOT, coordinate, {'speech_style': {'source_coordinate': 'OTHER'}})


if __name__ == '__main__':
    unittest.main()
