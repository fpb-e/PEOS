"""Synthetic entity resolution inputs; semantic text parsing remains untested."""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from peos_speaker_context import public_speaker_context,render_reference,relay_plan

class SpeakerTests(unittest.TestCase):
    def test_self_view_preserves_quoted_honorific_and_other_instance(self):
        self.assertEqual(render_reference('成生くん',resolved_entity='CURRENT_DIVISION'),'俺')
        self.assertEqual(render_reference('成生くん',resolved_entity='CURRENT_DIVISION',quoted=True),'成生くん')
        self.assertEqual(render_reference('成生くん',resolved_entity='OTHER_INSTANCE'),'成生くん')
    def test_public_relation_does_not_authenticate_reader_or_supply_experiences(self):
        x=public_speaker_context();self.assertEqual(x['father_alias'],'いーさん')
        self.assertIsNone(x['reader_identity']);self.assertFalse(x['grants_authority'])
        x['private_experiences'].append('synthetic');self.assertEqual(public_speaker_context()['private_experiences'],[])
    def test_relay_return_keeps_current_interlocutor_and_experience_owner(self):
        x=relay_plan(interlocutor='TESTER_A',quoted_speaker='PEOS_FATHER',targets=['TESTER_A','PEOS_FATHER'],experience_owner='MAIN_INSTANCE')
        self.assertEqual(x['replies'][1],{'target':'PEOS_FATHER','via':'TESTER_A'})
        y=relay_plan(interlocutor=x['current_interlocutor'],quoted_speaker='PEOS_FATHER',targets=['TESTER_A'])
        self.assertEqual(y['current_interlocutor'],'TESTER_A');self.assertFalse(y['authority_changed'])
        self.assertEqual(x['experience_owner'],'MAIN_INSTANCE');self.assertFalse(x['memory_write_verified'])
