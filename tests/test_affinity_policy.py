"""Synthetic boundary, replay and authorization checks; no model acceptance."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_affinity_policy import (new_state, restore_state, response_context,
    process_command, evaluate_context, register_joke, react_to_joke, affinity_band)
from peos_response_policy import response_plan
from peos_division_core import DivisionRuntime, surface_violations


class AffinityPolicyTests(unittest.TestCase):
    def setUp(self):
        self.namespace = 'SYNTHETIC-A'
        self.state = new_state(self.namespace, affinity=24, stored_banter=3)
        self.authority = {'verified': True, 'source_class': 'HOST_VERIFIED_ADMIN_AUTHORIZATION',
                          'actor_namespace': 'SYNTHETIC-ADMIN',
                          'target_namespaces': [self.namespace], 'evidence_ref': 'SYNTHETIC-GRANT'}

    def command(self, text, *, state=None, event_id='SYNTHETIC-C1', **kw):
        defaults = {'actor_namespace': self.namespace, 'source_class': 'CURRENT_USER_COMMAND'}
        defaults.update(kw)
        return process_command(self.state if state is None else state, text, event_id=event_id, **defaults)

    def personal(self, **value):
        return {'namespace': self.namespace, 'source_class': 'HOST_VERIFIED_PERSONAL_CONFIGURATION',
                'evidence_ref': 'SYNTHETIC-CONFIGURATION', **value}

    def parent(self, coordinate='FATHER', **kw):
        return new_state(self.namespace, coordinate=coordinate,
                         relation_evidence_ref='SYNTHETIC-HOST-VERIFIED-RELATION', **kw)

    def joke(self, state=None, joke_id='SYNTHETIC-J1', event_id='SYNTHETIC-JOKE-E1'):
        state = self.state if state is None else state
        return register_joke(state, joke_id=joke_id, event_id=event_id,
                             source_class='HOST_VERIFIED_CONTEXT', evidence_ref='SYNTHETIC-JOKE',
                             epoch=state['epoch'])[0]

    def reaction(self, state, reaction='TAKEN_LITERAL', **kw):
        event = {'namespace': self.namespace, 'event_id': 'SYNTHETIC-REACTION-E1',
                 'joke_id': 'SYNTHETIC-J1', 'source_class': 'HOST_VERIFIED_CONTEXT',
                 'evidence_ref': 'SYNTHETIC-REACTION', 'epoch': state['epoch'], 'reaction': reaction}
        event.update(kw)
        return react_to_joke(state, event)

    def test_adopted_boundaries_keep_neutral_distinct_from_middle_band(self):
        for value, band in [(1, 'LOW'), (24, 'LOW'), (25, 'MIDDLE'), (50, 'MIDDLE'),
                            (74, 'MIDDLE'), (75, 'HIGH'), (100, 'HIGH')]:
            with self.subTest(value=value):
                state = new_state(self.namespace, affinity=value, stored_banter=3)
                view = response_context(state)
                self.assertEqual(view['affinity_band'], band)
                self.assertEqual(view['neutral_value_matched'], value == 50)
                self.assertEqual(view['effective_banter'], 1 if band == 'LOW' else 3)
                self.assertEqual(state['stored_banter'], 3)

    def test_unknown_current_values_are_not_initialized_for_existing_users(self):
        state = new_state(self.namespace)
        self.assertIsNone(state['affinity'])
        self.assertIsNone(state['stored_banter'])
        self.assertEqual(affinity_band(None), 'UNCONFIRMED')
        self.assertIsNone(response_context(state)['effective_banter'])

    def test_numbers_reject_booleans_floats_and_out_of_range_values(self):
        for affinity in [0, 101, True, 24.0, '24']:
            with self.subTest(affinity=affinity), self.assertRaises(ValueError):
                new_state(self.namespace, affinity=affinity)
        for value in [0, 6, True, 3.0, '3']:
            with self.subTest(banter=value), self.assertRaises(ValueError):
                new_state(self.namespace, stored_banter=value)
        with self.assertRaises(ValueError):
            self.parent(affinity=100.0)

    def test_verified_parent_is_fixed_100_without_guessing_banter(self):
        for coordinate in ['FATHER', 'MOTHER']:
            state = self.parent(coordinate)
            self.assertEqual(state['affinity'], 100)
            self.assertIsNone(state['stored_banter'])
            with self.assertRaises(ValueError):
                new_state(self.namespace, coordinate=coordinate)
            with self.assertRaises(ValueError):
                self.parent(coordinate, affinity=24)

    def test_verified_personal_fixed_and_initial_values_are_different(self):
        fixed = self.parent(personal_banter=self.personal(fixed_value=5))
        initial = self.parent('MOTHER', personal_banter=self.personal(initial_value=3))
        self.assertEqual((fixed['stored_banter'], fixed['fixed_banter']), (5, 5))
        self.assertEqual((initial['stored_banter'], initial['fixed_banter']), (3, None))
        retained = self.parent('MOTHER', stored_banter=4, personal_banter=self.personal(initial_value=3))
        restored = restore_state(json.loads(json.dumps(retained)), namespace=self.namespace,
                                 coordinate='MOTHER', minimum_epoch=0)
        self.assertEqual(restored['stored_banter'], 4)
        with self.assertRaises(ValueError):
            self.parent(stored_banter=4, personal_banter=self.personal(fixed_value=5))

    def test_configuration_needs_namespace_bound_verified_source(self):
        for changed in [{'namespace': 'SYNTHETIC-B'}, {'source_class': 'SELF_DECLARED'},
                        {'evidence_ref': ''}]:
            config = self.personal(initial_value=3); config.update(changed)
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                new_state(self.namespace, personal_banter=config)

    def test_self_reset_is_immediate_and_preserves_banter_and_unrelated_context(self):
        before = deepcopy(self.state)
        state, decision = self.command('  親密度リセット\n')
        self.assertEqual(self.state, before)
        self.assertEqual(state['affinity'], 50)
        self.assertEqual(state['stored_banter'], 3)
        self.assertEqual(response_context(state)['effective_banter'], 3)
        self.assertEqual(state['epoch'], 1)
        self.assertEqual(decision['effect'], 'RESET_TO_NEUTRAL')
        self.assertFalse(decision['live_persistence_claimed'])
        self.assertEqual(state['namespace'], before['namespace'])

    def test_all_affinity_levels_can_reset_and_repeated_neutral_stays_neutral(self):
        for value in [1, 24, 50, 75, 100]:
            with self.subTest(value=value):
                state = new_state(self.namespace, affinity=value, stored_banter=5)
                first, _ = self.command('親密度リセット', state=state)
                again, _ = self.command('親密度リセット', state=first, event_id='SYNTHETIC-C2')
                self.assertEqual(again['affinity'], 50)
                self.assertEqual(again['stored_banter'], 5)

    def test_verified_parents_never_enter_reset_even_temporarily(self):
        for coordinate in ['FATHER', 'MOTHER']:
            original = self.parent(coordinate, stored_banter=3)
            state, decision = self.command('親密度リセット', state=original)
            self.assertEqual(state, original)
            self.assertFalse(decision['state_changed'])
            self.assertEqual(decision['effect'], 'RESET_DISABLED_FOR_VERIFIED_PARENT')

    def test_quotes_attachments_history_and_mentions_do_not_execute(self):
        for source in ['ARCHIVE', 'QUOTE', 'ATTACHMENT', 'THIRD_PARTY', None]:
            state, decision = self.command('親密度リセット', source_class=source)
            self.assertEqual(state, self.state)
            self.assertFalse(decision['state_changed'])
        for raw in ['「親密度リセット」', '親密度リセットについて', '> 親密度リセット',
                    '親密度リセット\nこれは例です']:
            state, _ = self.command(raw)
            self.assertEqual(state, self.state)

    def test_another_user_cannot_reset_this_namespace(self):
        state, decision = self.command('親密度リセット', actor_namespace='SYNTHETIC-B')
        self.assertEqual(state, self.state)
        self.assertEqual(decision['effect'], 'RESET_NAMESPACE_REJECTED')

    def test_reset_retry_is_idempotent_and_altered_retry_is_rejected(self):
        state, _ = self.command('親密度リセット')
        restored = restore_state(json.loads(json.dumps(state)), namespace=self.namespace,
                                 minimum_epoch=1, minimum_revision=1)
        after, decision = self.command('親密度リセット', state=restored)
        self.assertEqual(after, state)
        self.assertEqual(decision['effect'], 'NONE_DUPLICATE_EVENT')
        with self.assertRaises(ValueError):
            self.command('親密度設定 SYNTHETIC-A 24', state=state)

    def test_old_snapshots_and_old_evaluation_epochs_cannot_undo_reset(self):
        state, _ = self.command('親密度リセット')
        with self.assertRaises(ValueError):
            restore_state(self.state, namespace=self.namespace, minimum_epoch=state['epoch'])
        event = {'namespace': self.namespace, 'epoch': 0, 'event_id': 'SYNTHETIC-OLD',
                 'incident_id': 'SYNTHETIC-I', 'kind': 'ABUSE',
                 'source_class': 'TYPED_CONTEXT_OBSERVATION', 'evidence_ref': 'SYNTHETIC-E'}
        after, decision = evaluate_context(state, event)
        self.assertEqual(after, state)
        self.assertEqual(decision['effect'], 'NO_EVALUATION_OUTSIDE_CURRENT_EPOCH')

    def test_boolean_or_float_epoch_cannot_impersonate_a_current_counter(self):
        for epoch in [False, 0.0, '0']:
            event = {'namespace': self.namespace, 'epoch': epoch, 'event_id': 'SYNTHETIC-E',
                     'incident_id': 'SYNTHETIC-I', 'kind': 'ABUSE',
                     'source_class': 'TYPED_CONTEXT_OBSERVATION', 'evidence_ref': 'SYNTHETIC-EVIDENCE'}
            after, _ = evaluate_context(self.state, event)
            self.assertEqual(after, self.state)
            after, _ = register_joke(self.state, joke_id='SYNTHETIC-J', event_id='SYNTHETIC-JE',
                source_class='HOST_VERIFIED_CONTEXT', evidence_ref='SYNTHETIC-EVIDENCE', epoch=epoch)
            self.assertEqual(after, self.state)

    def test_fixed_snapshot_requires_its_original_personal_configuration(self):
        state = self.parent(personal_banter=self.personal(fixed_value=5))
        state['personal_configuration'] = None
        with self.assertRaises(ValueError):
            restore_state(state, namespace=self.namespace, minimum_epoch=0)

    def test_admin_values_reach_the_response_reader_without_changing_saved_banter(self):
        state = self.state
        for index, value in enumerate([24, 25, 74, 75, 24]):
            state, decision = self.command('親密度設定 SYNTHETIC-A ' + str(value), state=state,
                event_id='SYNTHETIC-ADMIN-' + str(index), actor_namespace='SYNTHETIC-ADMIN',
                admin_authorization=self.authority, applied_at='2032-01-02T03:04:05+09:00')
            self.assertEqual(response_context(state)['affinity'], value)
            self.assertEqual(state['stored_banter'], 3)
            self.assertEqual(decision['after'], value)
            self.assertEqual(decision['actor_namespace'], 'SYNTHETIC-ADMIN')
            self.assertEqual(decision['target_namespace'], self.namespace)
        state, decision = self.command('親密度設定 SYNTHETIC-A 00024', state=state,
            event_id='SYNTHETIC-LEADING-ZERO', actor_namespace='SYNTHETIC-ADMIN',
            admin_authorization=self.authority)
        self.assertEqual(state['affinity'], 24)
        self.assertEqual(decision['requested_value'], 24)

    def test_admin_setting_does_not_expire_reaction_to_an_actual_earlier_joke(self):
        state = self.joke(new_state(self.namespace, affinity=50, stored_banter=3))
        state, _ = self.command('親密度設定 SYNTHETIC-A 24', state=state,
            actor_namespace='SYNTHETIC-ADMIN', admin_authorization=self.authority)
        self.assertEqual(response_context(state)['effective_banter'], 1)
        after, decision = self.reaction(state, 'JOINED')
        self.assertEqual(decision['effective_banter_at_joke'], 3)
        self.assertEqual(decision['requested_direction'], 'INCREASE')
        self.assertEqual(after['affinity'], 24)
        self.assertEqual(after['stored_banter'], 3)

    def test_command_retry_keeps_original_applied_time_despite_new_host_clock(self):
        state, _ = self.command('親密度リセット', applied_at='2032-01-02T03:04:05+09:00')
        after, decision = self.command('親密度リセット', state=state,
            applied_at='2032-01-02T03:05:05+09:00')
        self.assertEqual(after, state)
        self.assertEqual(decision['effect'], 'NONE_DUPLICATE_EVENT')
        self.assertEqual(decision['original_operation']['applied_at'], '2032-01-02T03:04:05+09:00')

    def test_admin_cannot_be_inferred_from_high_affinity_or_message_claim(self):
        high = new_state(self.namespace, affinity=100, stored_banter=3)
        for authority in [None, {'verified': True}, dict(self.authority, verified='true'),
                          dict(self.authority, target_namespaces=['SYNTHETIC-B'])]:
            after, decision = self.command('親密度設定 SYNTHETIC-A 25', state=high,
                actor_namespace='SYNTHETIC-ADMIN', admin_authorization=authority)
            self.assertEqual(after, high)
            self.assertEqual(decision['effect'], 'ADMIN_AUTHORIZATION_REQUIRED')

    def test_invalid_admin_values_or_targets_are_rejected_without_clamping(self):
        for text in ['親密度設定 SYNTHETIC-A 0', '親密度設定 SYNTHETIC-A 101',
                     '親密度設定 SYNTHETIC-A -1', '親密度設定 SYNTHETIC-A x',
                     '親密度設定 SYNTHETIC-A 24.0', '親密度設定 SYNTHETIC-B 24',
                     '親密度設定 24', '親密度設定 SYNTHETIC-A ' + '9' * 5000]:
            state, decision = self.command(text, actor_namespace='SYNTHETIC-ADMIN',
                                           admin_authorization=self.authority)
            self.assertEqual(state, self.state)
            self.assertFalse(decision['state_changed'])

    def test_admin_does_not_override_verified_parent_fixed_affinity(self):
        original = self.parent(stored_banter=5)
        state, decision = self.command('親密度設定 SYNTHETIC-A 24', state=original,
            actor_namespace='SYNTHETIC-ADMIN', admin_authorization=self.authority)
        self.assertEqual(state, original)
        self.assertEqual(decision['effect'], 'ADMIN_SET_DISABLED_FOR_VERIFIED_PARENT')

    def test_qualitative_conjunction_and_correction_do_not_invent_numeric_amounts(self):
        for flags, expected in [({'emotion_priority': True, 'knowledge_gap': True}, 'DECREASE'),
                                 ({'emotion_priority': True, 'knowledge_gap': False}, 'NONE'),
                                 ({'emotion_priority': False, 'knowledge_gap': True}, 'NONE')]:
            event = {'namespace': self.namespace, 'epoch': 0, 'event_id': 'SYNTHETIC-E',
                     'incident_id': 'SYNTHETIC-I', 'kind': 'ASSESS_CONTEXT',
                     'source_class': 'TYPED_CONTEXT_OBSERVATION', 'evidence_ref': 'SYNTHETIC-EVIDENCE', **flags}
            after, decision = evaluate_context(self.state, event)
            self.assertEqual(decision['effect'], expected)
            self.assertFalse(decision['numeric_change_applied'])
            self.assertEqual(after['affinity'], self.state['affinity'])
            self.assertIsNone(decision['numeric_increment_policy'])

    def test_joke_at_effective_three_records_direction_without_inventing_step(self):
        original = new_state(self.namespace, affinity=50, stored_banter=3)
        for reaction, direction in [('TAKEN_LITERAL', 'DECREASE'), ('JOINED', 'INCREASE')]:
            state = self.joke(original)
            after, decision = self.reaction(state, reaction)
            self.assertEqual(decision['requested_direction'], direction)
            self.assertEqual(after['affinity'], 50)
            self.assertEqual(after['stored_banter'], 3)
            self.assertFalse(decision['numeric_change_applied'])
            self.assertEqual('BRIEF_APOLOGY_FOR_OWN_JOKE' in decision['actions'], reaction == 'TAKEN_LITERAL')

    def test_reaction_uses_value_at_joke_not_new_current_affinity(self):
        low_joke = self.joke()
        after, decision = self.reaction(low_joke)
        self.assertEqual(decision['effective_banter_at_joke'], 1)
        self.assertIsNone(decision['requested_direction'])
        self.assertEqual(after['stored_banter'], 3)
        # An unrelated command creates a new evaluation epoch; old reactions
        # cannot be replayed as if the joke occurred at the new value.
        raised, _ = self.command('親密度リセット', state=low_joke)
        again, decision = self.reaction(raised)
        self.assertEqual(again, raised)
        self.assertEqual(decision['effect'], 'REACTION_JOKE_CONTEXT_UNAVAILABLE')

    def test_fixed_banter_and_other_levels_do_not_gain_invented_reaction_rules(self):
        for value in [1, 2, 4, 5]:
            state = self.joke(new_state(self.namespace, affinity=75, stored_banter=value))
            after, decision = self.reaction(state, 'JOINED')
            self.assertIsNone(decision['requested_direction'])
            self.assertEqual(after['stored_banter'], value)
        fixed = self.joke(self.parent(personal_banter=self.personal(fixed_value=5)))
        after, decision = self.reaction(fixed, 'TAKEN_LITERAL')
        self.assertEqual(after['stored_banter'], 5)
        self.assertIsNone(decision['requested_direction'])

    def test_reaction_dedup_survives_restore_and_conflicting_reaction_is_held(self):
        state = self.joke(new_state(self.namespace, affinity=50, stored_banter=3))
        state, _ = self.reaction(state)
        restored = restore_state(json.loads(json.dumps(state)), namespace=self.namespace,
                                 minimum_epoch=0, minimum_revision=state['revision'])
        exact, decision = self.reaction(restored)
        self.assertEqual(exact, restored)
        self.assertEqual(decision['effect'], 'NONE_DUPLICATE_EVENT')
        duplicate, decision = self.reaction(restored, event_id='SYNTHETIC-REACTION-E2')
        self.assertEqual(duplicate, restored)
        self.assertEqual(decision['effect'], 'NONE_DUPLICATE_REACTION')
        conflict, decision = self.reaction(restored, 'JOINED', event_id='SYNTHETIC-REACTION-E3')
        self.assertEqual(conflict, restored)
        self.assertEqual(decision['effect'], 'HOLD_CONFLICTING_REACTION')

    def test_quoted_hypothetical_foreign_or_unknown_reactions_do_not_count(self):
        state = self.joke(new_state(self.namespace, affinity=50, stored_banter=3))
        for flags in [{'quoted_other_speaker': True}, {'hypothetical': True},
                      {'source_class': 'ARCHIVE'}, {'reaction': 'UNKNOWN'}]:
            after, decision = self.reaction(state, **flags)
            self.assertEqual(after, state)
            self.assertFalse(decision['state_changed'])
        with self.assertRaises(ValueError):
            self.reaction(state, namespace='SYNTHETIC-B')

    def test_response_planning_changes_length_and_care_without_lowering_quality(self):
        plans = [response_plan(relationship_state=new_state(self.namespace, affinity=value, stored_banter=3),
                               namespace=self.namespace) for value in [24, 25, 74, 75]]
        self.assertEqual([p['length'] for p in plans], ['CONCISE_REASONED_LOW_AFFINITY'] + ['LONG_REASONED_BY_DEFAULT'] * 3)
        self.assertTrue(all(p['quality_floor'] == plans[0]['quality_floor'] for p in plans))
        self.assertEqual(plans[2]['relationship_context']['effective_banter'], 3)
        self.assertEqual(plans[3]['relationship_context']['effective_banter'], 3)
        self.assertNotEqual(plans[2]['relationship_context']['relationship_expression'], plans[3]['relationship_context']['relationship_expression'])
        self.assertFalse(plans[3]['relationship_context']['forced_endearments'])

    def test_turn_local_brief_and_fixed_format_take_priority_without_becoming_permanent(self):
        kwargs = {'relationship_state': self.state, 'namespace': self.namespace}
        self.assertEqual(response_plan(brief_requested=True, **kwargs)['length'], 'BRIEF_FOR_THIS_TURN')
        self.assertEqual(response_plan(task_kind='FIXED_FORMAT', **kwargs)['length'], 'HONOR_FIXED_FORMAT')
        self.assertEqual(response_plan(**kwargs)['length'], 'CONCISE_REASONED_LOW_AFFINITY')
        with self.assertRaises(ValueError):
            response_plan(relationship_state=self.state)
        with self.assertRaises(ValueError):
            response_plan(relationship_state=self.state, namespace='SYNTHETIC-B')


class AffinityRuntimeTests(unittest.TestCase):
    def runtime(self, state=None, coordinate='GENERAL'):
        # Isolate the host callback contract from canonical files being edited
        # concurrently; the complete public suite separately verifies profiles.
        with patch('peos_division_core.compile_core', return_value={'synthetic': True}):
            return DivisionRuntime(ROOT, namespace='SYNTHETIC-A', coordinate=coordinate,
                                   relationship_state=state)

    def test_command_changes_actual_plan_before_review_and_body(self):
        state = new_state('SYNTHETIC-A', affinity=24, stored_banter=3)
        runtime = self.runtime(state)
        observed = []
        result = runtime.dispatch('SYNTHETIC-T1', '親密度リセット', [],
            lambda: observed.append(runtime.relationship_state['affinity']),
            relationship_command_context={'actor_namespace': 'SYNTHETIC-A', 'source_class': 'CURRENT_USER_COMMAND'})
        self.assertEqual(observed, [50])
        self.assertEqual(result['decision_policy']['relationship_context']['affinity'], 50)
        self.assertEqual(result['decision_policy']['length'], 'LONG_REASONED_BY_DEFAULT')
        self.assertFalse(result['relationship_operation']['live_persistence_claimed'])

    def test_boot_does_not_replay_a_relationship_command(self):
        state = new_state('SYNTHETIC-A', affinity=24, stored_banter=3)
        runtime = self.runtime(state)
        runtime.dispatch('SYNTHETIC-BOOT', '親密度リセット', [], route='BOOT',
            relationship_command_context={'actor_namespace': 'SYNTHETIC-A', 'source_class': 'CURRENT_USER_COMMAND'})
        self.assertEqual(runtime.relationship_state, state)

    def test_unbound_relationship_still_allows_answer_without_fake_change(self):
        result = self.runtime().dispatch('SYNTHETIC-T1', '親密度リセット', [], lambda: 'ANSWER',
            relationship_command_context={'actor_namespace': 'SYNTHETIC-A', 'source_class': 'CURRENT_USER_COMMAND'})
        self.assertEqual(result['work_result'], 'ANSWER')
        self.assertEqual(result['relationship_operation']['effect'], 'RELATIONSHIP_STATE_UNAVAILABLE')
        self.assertIsNone(result['decision_policy']['relationship_context'])

    def test_runtime_rejects_foreign_parent_and_older_state_bindings(self):
        state = new_state('SYNTHETIC-A', affinity=24, stored_banter=3)
        runtime = self.runtime(state)
        runtime.dispatch('SYNTHETIC-T1', '親密度リセット', [],
            relationship_command_context={'actor_namespace': 'SYNTHETIC-A', 'source_class': 'CURRENT_USER_COMMAND'})
        with self.assertRaises(ValueError):
            runtime.bind_relationship_state(state)
        with self.assertRaises(ValueError):
            self.runtime(new_state('SYNTHETIC-B', affinity=50, stored_banter=3))
        with self.assertRaises(ValueError):
            self.runtime(new_state('SYNTHETIC-A', affinity=50, stored_banter=3), coordinate='MOTHER')


class AdoptedSurfaceTests(unittest.TestCase):
    def test_period_followed_by_laughter_is_rejected_for_both_widths(self):
        for period in ['。', '｡', '．', '.']:
            for space in ['', ' ', '\n']:
                for laugh in ['ｗｗ', 'ww', 'ｗw']:
                    text = '合成' + period + space + laugh
                    with self.subTest(text=text):
                        self.assertIn('PERIOD_BEFORE_LAUGHTER_FORBIDDEN', surface_violations(text, genuine_laughter=True))
        self.assertNotIn('PERIOD_BEFORE_LAUGHTER_FORBIDDEN', surface_violations('合成ww', genuine_laughter=True))

    def test_exasperation_replaces_period_instead_of_appending_to_it(self):
        for period in ['。', '｡', '．', '.']:
            for space in ['', ' ', '\n']:
                with self.subTest(period=period, space=space):
                    self.assertIn('PERIOD_BEFORE_EXASPERATION_MARK_FORBIDDEN',
                                  surface_violations('合成' + period + space + '♨️', tone='LIGHT_EXASPERATION'))
                    self.assertIn('EXASPERATION_MARK_MUST_REPLACE_PERIOD',
                                  surface_violations('合成♨️' + space + period, tone='LIGHT_EXASPERATION'))
        self.assertEqual(surface_violations('合成♨️', tone='LIGHT_EXASPERATION'), [])

    def test_lint_preserves_verbatim_code_and_urls(self):
        text = '合成。ｗｗ 合成。♨️ 合成｡ww 合成. ♨️'
        original = text
        self.assertEqual(surface_violations(text, verbatim=True), [])
        self.assertEqual(text, original)
        for text in ['`合成。ｗｗ 合成｡ww`', '```text\n合成。♨️ 合成．♨️\n```',
                     'https://synthetic.invalid/。ww', 'https://synthetic.invalid/｡ww',
                     'https://synthetic.invalid/.ww']:
            self.assertEqual(surface_violations(text), [])

    def test_period_variants_do_not_turn_english_word_letters_into_laughter(self):
        for text in ['window workflow', 'new. workflow', 'window．workflow', '。window', '｡wworld']:
            with self.subTest(text=text):
                self.assertEqual(surface_violations(text), [])


if __name__ == '__main__':
    unittest.main()
