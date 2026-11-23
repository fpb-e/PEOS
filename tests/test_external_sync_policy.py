"""A ledger receipt cannot stand in for current calendar evidence."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from peos_session_policy import calendar_plan


class ExternalSyncPolicyTests(unittest.TestCase):
    def item(self,**changes):
        value={'status':'CONFIRMED','fingerprint':'SYNTHETIC-EVENT',
               'latest_body_checked':True,'changes_and_cancellations_checked':True,
               'start_at':'2032-04-05T14:00:00+09:00','start_time_confirmed':True,
               'meeting_url':'https://synthetic.invalid/meeting-old'}
        value.update(changes);return value

    def test_changed_start_updates_existing_instead_of_duplicating(self):
        old=self.item();new=self.item(start_at='2032-04-05T15:00:00+09:00')
        self.assertEqual(calendar_plan(new,[old],explicit_write_authorized=True),'UPDATE_EXISTING_EVENT')

    def test_changed_meeting_url_updates_the_same_identity(self):
        old=self.item();new=self.item(meeting_url='https://synthetic.invalid/meeting-new')
        self.assertEqual(calendar_plan(new,[old],explicit_write_authorized=True),'UPDATE_EXISTING_EVENT')

    def test_unknown_start_time_is_never_invented(self):
        for changes in [{'start_at':None},{'start_at':'2032-04-05'}, {'start_time_confirmed':False}]:
            with self.subTest(changes=changes):
                self.assertEqual(calendar_plan(self.item(**changes),[],explicit_write_authorized=True),'HOLD_START_TIME_UNCONFIRMED')

    def test_ledger_ack_is_not_external_notification_evidence(self):
        item=self.item(latest_body_checked=False,ledger_sync_ack=True)
        self.assertEqual(calendar_plan(item,[],explicit_write_authorized=True),'RECHECK_LATEST_THREAD')

    def test_unchanged_event_does_not_create_a_copy(self):
        item=self.item()
        self.assertEqual(calendar_plan(item,[dict(item)],explicit_write_authorized=True),'KEEP_EXISTING_NO_DUPLICATE')

    def test_missing_latest_fields_do_not_erase_existing_values(self):
        old=self.item();new=self.item();new.pop('meeting_url')
        self.assertEqual(calendar_plan(new,[old],explicit_write_authorized=True),'KEEP_EXISTING_NO_DUPLICATE')

    def test_ambiguous_identity_needs_review(self):
        item=self.item()
        self.assertEqual(calendar_plan(item,[dict(item),dict(item)],explicit_write_authorized=True),'REVIEW_MULTIPLE_EXISTING_MATCHES')
        self.assertEqual(calendar_plan(self.item(fingerprint=None),[],explicit_write_authorized=True),'HOLD_EVENT_IDENTITY_UNCONFIRMED')

    def test_current_write_scope_must_be_a_boolean(self):
        with self.assertRaises(ValueError):calendar_plan(self.item(),[],explicit_write_authorized='false')
        self.assertEqual(calendar_plan(self.item(),[],explicit_write_authorized=False),'READ_ONLY')
