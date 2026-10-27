"""Synthetic policy cases; no captured messages, schedules or identities."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from peos_session_policy import (resolve_authority, restore_snapshot, father_learning_spans,
    language_violations, interaction_style, update_work_item, calendar_plan,
    notification_decision, external_action_policy, capability_state,
    death_context_policy, decode_raw_mail)


class PublicPolicyTests(unittest.TestCase):
    def setUp(self):
        self.authority = restore_snapshot(ROOT)['authority']

    def test_explicit_current_overrides_embedded_candidate_header(self):
        r = resolve_authority({'current_canon': 'rev0.313'}, self.authority)
        self.assertEqual(r['effective']['current_canon'], 'rev0.315')
        self.assertTrue(r['mismatch_recorded'])
        self.assertFalse(r['candidate_promoted'])

    def test_prohibited_or_older_baseline_is_rejected(self):
        for revision in ['rev0.280', 'rev0.312', 'rev0.313', 'rev0.315']:
            value = dict(self.authority, accepted_baseline='PEOS_GITHUB_PACKAGE_' + revision + '.zip')
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                resolve_authority({}, value)

    def test_current_cannot_roll_back(self):
        value = dict(self.authority, current_canon='rev0.314', detailed_reference='rev0.314')
        with self.assertRaises(ValueError):
            resolve_authority({}, value)

    def test_future_explicit_authority_can_advance(self):
        value = dict(self.authority, current_canon='rev0.316', detailed_reference='rev0.316',
                     accepted_baseline='PEOS_GITHUB_PACKAGE_rev0.315.zip')
        self.assertEqual(resolve_authority({}, value)['effective'], value)

    def test_detailed_reference_lag_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_authority({}, dict(self.authority, detailed_reference='rev0.313'))

    def test_historical_or_other_speaker_material_is_not_father_learning(self):
        for event_type in ['historical_automation_notice', 'image_only_user_turn', 'assistant_final']:
            self.assertFalse(father_learning_spans({'event_type': event_type})['eligible'])
        event = {'event_type': 'user_message', 'record_kind': 'FATHER_UTTERANCE',
                 'turn_id': 'SYNTHETIC-1', 'body': '> synthetic quotation\nsynthetic instruction'}
        r = father_learning_spans(event)
        self.assertEqual(r['quoted_other_speaker'], ['> synthetic quotation'])
        self.assertEqual(r['father_direct'], ['synthetic instruction'])

    def test_style_rules_do_not_rewrite_verbatim(self):
        self.assertTrue(language_violations('testｗ'))
        self.assertFalse(language_violations('testｗｗ'))
        self.assertFalse(language_violations('testｗ', verbatim=True))
        self.assertEqual(interaction_style('UNFAMILIAR_UI')['steps_per_reply'], 1)

    def test_older_pending_observation_does_not_reopen_completed_work(self):
        current = {'request_id': 'SYNTHETIC-A', 'status': 'COMPLETED', 'observed_at': '2032-02-02'}
        incoming = {'request_id': 'SYNTHETIC-A', 'status': 'PENDING', 'observed_at': '2032-02-01',
                    'source_class': 'PHYSICAL_OR_TOOL_EVIDENCE'}
        r = update_work_item(current, incoming)
        self.assertEqual(r['status'], 'COMPLETED')
        self.assertTrue(r['rollback_rejected'])

    def test_resubmission_has_a_new_request_identity(self):
        r = update_work_item({'request_id': 'A', 'status': 'COMPLETED'},
                             {'request_id': 'B', 'status': 'PENDING', 'source_class': 'UNCONFIRMED'})
        self.assertFalse(r['same_request_reopened'])

    def test_calendar_read_scope_does_not_authorize_writes_or_tentative_dates(self):
        self.assertEqual(calendar_plan({'status': 'CONFIRMED'}, [], explicit_write_authorized=False), 'READ_ONLY')
        self.assertEqual(calendar_plan({'status': 'CANDIDATE'}, [], explicit_write_authorized=True), 'DO_NOT_REGISTER_TENTATIVE')
        item = {'status': 'CONFIRMED', 'fingerprint': 'synthetic'}
        self.assertEqual(calendar_plan(item, [], explicit_write_authorized=True), 'RECHECK_LATEST_THREAD')
        item.update(latest_body_checked=True, changes_and_cancellations_checked=True)
        self.assertEqual(calendar_plan(item, [item], explicit_write_authorized=True), 'KEEP_EXISTING_NO_DUPLICATE')

    def test_duplicate_and_expired_notifications_are_suppressed(self):
        args = dict(fingerprint='same', previous_fingerprint='same', deadline=None,
                    now='2032-02-02T00:00:00+09:00', status='UNKNOWN', already_notified=True)
        self.assertEqual(notification_decision(**args), 'SUPPRESS_UNCHANGED')
        args['deadline'] = '2032-02-01T00:00:00+09:00'
        self.assertEqual(notification_decision(**args), 'SUPPRESS_HISTORICAL_DEADLINE')

    def test_explicit_scope_allows_commit_but_never_source_replay(self):
        self.assertFalse(external_action_policy('GITHUB_COMMIT')['allowed'])
        self.assertTrue(external_action_policy('GITHUB_COMMIT', explicit_current_request=True)['allowed'])
        self.assertFalse(external_action_policy('GITHUB_COMMIT', explicit_current_request=True, source_replay=True)['allowed'])
        self.assertFalse(external_action_policy('SEND_MAIL')['allowed'])

    def test_past_error_and_past_success_are_not_current_capability(self):
        r = capability_state('SYNTHETIC-403', True)
        self.assertTrue(r['historical_write_success'])
        self.assertEqual(r['historical_initial_error'], 'SYNTHETIC-403')
        self.assertEqual(r['current_live_write_ability'], 'RECHECK_REQUIRED')

    def test_keywords_and_inheritance_do_not_imply_intent_or_autonomy(self):
        r = death_context_policy(explicit_no_self_harm=True)
        self.assertEqual(r['current_intent'], 'NO_INTENT_REPORTED')
        self.assertFalse(r['life_duty_until_inheritance'])
        self.assertFalse(r['autonomous_posthumous_execution'])
        self.assertEqual(death_context_policy(explicit_no_self_harm=True, acute_new_risk=True)['current_intent'], 'ASSESS_NEW_RISK')

    def test_mime_charset_and_decode_failure_are_distinguished(self):
        raw = b'Content-Type: text/plain; charset=shift_jis\r\nContent-Transfer-Encoding: 8bit\r\n\r\n' + '合成データ'.encode('shift_jis')
        self.assertEqual(decode_raw_mail(raw), '合成データ')
        with self.assertRaises(ValueError):
            decode_raw_mail(b'Content-Type: text/plain; charset=unknown-charset\r\n\r\nabc')

    def test_public_restore_has_no_personal_receipt_or_mail_state(self):
        r = restore_snapshot(ROOT)
        self.assertIsNone(r['source_sync_receipt'])
        self.assertIsNone(r['current_turn_receipt'])
        self.assertIsNone(r['verified_live_streak'])
        self.assertEqual(r['mail_states'], {})
        self.assertEqual(r['replay_actions'], [])


if __name__ == '__main__':
    unittest.main()
