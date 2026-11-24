"""Real reference-state transitions; not actual model conversation results."""
from pathlib import Path
import sys,unittest
from unittest.mock import Mock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from peos_conversation_boot import ConversationBoot,FIRST_CONTACT
from peos_division_core import DivisionRuntime

class BootTests(unittest.TestCase):
    def test_unknown_then_name_completes_once_without_another_boot(self):
        b=ConversationBoot(ROOT);first=b.handle('BOOT',read_and_applied=True)
        self.assertEqual(first['text'],FIRST_CONTACT);self.assertTrue(first['state']['pending'])
        done=b.handle('NAME',name='ナギ');self.assertEqual(done['effect'],'BOOT_COMPLETE')
        self.assertEqual(done['text'].count('擬似いーさんOS起動完了。'),1)
        self.assertEqual(b.handle('NAME',name='ナギ')['text'],'')
    def test_apply_does_not_boot_and_needs_actual_body_application(self):
        b=ConversationBoot(ROOT);self.assertEqual(b.handle('APPLY')['effect'],'NEED_CANON_BODY')
        self.assertEqual(b.handle('APPLY',read_and_applied=True)['text'],'')
        self.assertEqual(b.handle('BOOT')['effect'],'WAIT_NAME')
    def test_known_name_and_anonymous_choice_are_not_asked_again(self):
        b=ConversationBoot(ROOT,name='ナギ');self.assertEqual(b.handle('BOOT',read_and_applied=True)['effect'],'BOOT_COMPLETE')
        a=ConversationBoot(ROOT);a.handle('BOOT',read_and_applied=True)
        self.assertEqual(a.handle('ANONYMOUS')['effect'],'BOOT_COMPLETE')
        self.assertEqual(a.handle('BOOT')['effect'],'BOOT_COMPLETE')
    def test_diagnostics_and_intervening_consultation_preserve_pending_boot(self):
        b=ConversationBoot(ROOT);b.handle('BOOT',read_and_applied=True)
        for e in ['DIAGNOSE','OTHER','APPLY']:
            self.assertTrue(b.handle(e)['state']['pending'])
        self.assertEqual(b.handle('NAME',name='ナギ')['effect'],'BOOT_COMPLETE')
    def test_names_cannot_grant_family_role_but_verified_family_routes_work(self):
        for name in ['親父','お母さん']:
            b=ConversationBoot(ROOT);b.handle('BOOT',read_and_applied=True);r=b.handle('NAME',name=name)
            self.assertEqual(r['state']['coordinate'],'GENERAL');self.assertIn('酔狂',r['text'])
        for role in ['FATHER','MOTHER']:
            r=ConversationBoot(ROOT,coordinate=role).handle('BOOT',read_and_applied=True)
            self.assertEqual(r['effect'],'BOOT_COMPLETE');self.assertFalse(r['runtime_ready'])
    def test_quote_or_archive_cannot_apply_or_start_boot(self):
        for context in ['QUOTE','ARCHIVE']:
            b=ConversationBoot(ROOT);r=b.handle('BOOT',read_and_applied=True,source_context=context)
            self.assertEqual(r['text'],'');self.assertFalse(r['state']['canons_applied'])
    def test_dispatch_boot_has_no_persistence_clock_or_callback_dependency(self):
        fail=Mock(side_effect=RuntimeError('must not run'))
        r=DivisionRuntime(ROOT,namespace='SYNTHETIC',display_clock=fail)
        x=r.dispatch('T1','PEOS起動',[],fail,route='BOOT',boot_read_and_applied=True)
        self.assertEqual(x['work_result'],FIRST_CONTACT);fail.assert_not_called()
        y=r.dispatch('T2','ナギ',[],fail,route='BOOT',boot_event='NAME',boot_name='ナギ')
        self.assertEqual(y['boot']['effect'],'BOOT_COMPLETE');self.assertFalse(y['readback_verified'])
    def test_reapply_preserves_bound_name_coordinate_and_state(self):
        b=ConversationBoot(ROOT,name='ナギ');b.handle('BOOT',read_and_applied=True);before=dict(b.state)
        b.handle('APPLY',read_and_applied=True);self.assertEqual(b.state,before)
