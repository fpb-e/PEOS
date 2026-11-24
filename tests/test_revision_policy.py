"""Specification-command scope, canonical adoption and resumable allocation."""
from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from peos_revision_policy import specification_plan

AUTHORITY = {'current_canon': 'rev0.320', 'detailed_reference': 'rev0.320',
             'accepted_baseline': 'PEOS_GITHUB_PACKAGE_rev0.319.zip'}
DIGEST = hashlib.sha256(b'SYNTHETIC_SPECIFICATION_COMMAND_AND_INPUT').hexdigest()


class SpecificationReleaseTests(unittest.TestCase):
    def plan(self, authority=None, **changes):
        args = dict(action='SPECIFY', owner_authorized=True, request_id='SYNTHETIC-1',
                    source_digest=DIGEST)
        args.update(changes)
        return specification_plan(authority or AUTHORITY, **args)

    def test_unspecified_revision_is_next_canon_with_previous_as_baseline(self):
        p = self.plan()
        self.assertEqual(p['target_authority'], {'current_canon':'rev0.321',
            'detailed_reference':'rev0.321', 'accepted_baseline':'PEOS_GITHUB_PACKAGE_rev0.320.zip'})
        self.assertTrue(p['release_accepted'])
        self.assertEqual(p['release_status'], 'ACCEPTED_BY_OWNER')

    def test_subsequent_new_command_advances_from_latest_accepted_authority(self):
        first = self.plan()
        second = self.plan(first['target_authority'], request_id='SYNTHETIC-2')
        self.assertEqual(second['target_revision'], 'rev0.322')
        self.assertEqual(second['target_authority']['accepted_baseline'], 'PEOS_GITHUB_PACKAGE_rev0.321.zip')

    def test_explicit_revision_and_owner_shorthand_override_increment(self):
        for value in ('rev0.325', 'rev.325'):
            with self.subTest(value=value):
                p = self.plan(explicit_revision=value)
                self.assertEqual(p['target_revision'], 'rev0.325')
                self.assertTrue(p['release_accepted'])
                self.assertEqual(p['target_authority']['accepted_baseline'], 'PEOS_GITHUB_PACKAGE_rev0.320.zip')

    def test_explicit_same_revision_rebuild_preserves_existing_baseline(self):
        p = self.plan(explicit_revision='rev.320')
        self.assertEqual(p['target_authority'], AUTHORITY)
        self.assertTrue(p['release_accepted'])

    def test_increment_is_integer_serial_not_decimal_rounding(self):
        a = dict(AUTHORITY, current_canon='rev0.999', detailed_reference='rev0.999')
        self.assertEqual(self.plan(a)['target_revision'], 'rev0.1000')
        a.update(current_canon='rev2.009', detailed_reference='rev2.009')
        self.assertEqual(self.plan(a)['target_revision'], 'rev2.010')

    def test_historical_and_quoted_commands_cannot_trigger_release(self):
        for source in ('ARCHIVE', 'QUOTE'):
            p = self.plan(source_context=source)
            self.assertEqual(p['effect'], 'NO_SPECIFICATION_BUILD')
            self.assertIsNone(p['target_authority'])

    def test_policy_registration_and_other_actions_do_not_consume_revision(self):
        for action in ('REGISTER_POLICY', 'DISCUSS', 'INSPECT', 'LOAD', 'BOOT'):
            with self.subTest(action=action):
                p = self.plan(action=action)
                self.assertEqual(p['current_authority'], AUTHORITY)
                self.assertIsNone(p['target_authority'])

    def test_unverified_owner_or_truthy_label_cannot_adopt(self):
        self.assertFalse(self.plan(owner_authorized=False)['release_accepted'])
        with self.assertRaises(ValueError):
            self.plan(owner_authorized='FATHER')

    def test_explicit_candidate_scope_retains_active_canon(self):
        p = self.plan(candidate_only=True)
        self.assertEqual(p['target_revision'], 'rev0.321')
        self.assertFalse(p['release_accepted'])
        self.assertIsNone(p['target_authority'])
        self.assertEqual(p['current_authority'], AUTHORITY)

    def test_retry_reuses_original_assignment_even_after_authority_advances(self):
        p = self.plan()
        before = deepcopy(p)
        retry = self.plan(p['target_authority'], previous=p)
        self.assertEqual(retry['target_revision'], 'rev0.321')
        self.assertTrue(retry['retry_reuses_assignment'])
        self.assertEqual(p, before)

    def test_reused_request_id_with_different_input_is_rejected(self):
        p = self.plan()
        for change in ({'source_digest':'a'*64}, {'explicit_revision':'rev0.325'}, {'candidate_only':True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.plan(previous=p, **change)

    def test_old_retry_does_not_roll_back_a_newer_current_canon(self):
        p = self.plan()
        latest = dict(AUTHORITY, current_canon='rev0.322', detailed_reference='rev0.322',
                      accepted_baseline='PEOS_GITHUB_PACKAGE_rev0.321.zip')
        retry = self.plan(latest, previous=p)
        self.assertEqual(retry['effect'], 'SUPERSEDED_NO_ROLLBACK')
        self.assertEqual(retry['current_authority'], latest)
        self.assertIsNone(retry['target_authority'])

    def test_invalid_authority_and_older_explicit_target_are_rejected(self):
        for change in ({'accepted_baseline':'PEOS_GITHUB_PACKAGE_rev0.280.zip'},
                       {'accepted_baseline':'PEOS_GITHUB_PACKAGE_rev0.320.zip'},
                       {'detailed_reference':'rev0.319'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.plan(dict(AUTHORITY, **change))
        with self.assertRaises(ValueError):
            self.plan(explicit_revision='rev0.319')

    def test_adoption_is_not_a_claim_of_execution_or_external_mutation(self):
        original = deepcopy(AUTHORITY)
        p = self.plan()
        self.assertEqual(p['build_status'], 'PLANNED_NOT_EXECUTED')
        self.assertEqual(p['live_model_acceptance'], 'NOT_PERFORMED')
        self.assertFalse(p['external_actions_performed'])
        self.assertEqual(AUTHORITY, original)
