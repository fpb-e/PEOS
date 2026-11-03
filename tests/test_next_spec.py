"""Synthetic reference behavior; not independent live-model acceptance."""
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from peos_division_core import DivisionRuntime,compile_core
from peos_short_preprocess import DurableTurnJournal,ShortPreprocessor,SyntheticAckStore,PreprocessError
from peos_response_policy import installation_configuration,response_plan,summarize_magi
from peos_next_spec_validation import next_spec_errors
OBSERVED='2032-04-05T06:07:08+09:00';DISPLAY='2032-04-05T06:09:10+09:00'
class NextSpecTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)
    def make(self,mode='FULL',fail=False,display=None):
        trace=[]
        def observed():trace.append('observed');return OBSERVED
        def clock():trace.append('display');return DISPLAY
        store=SyntheticAckStore(identity='SYNTHETIC-A',fail=fail);replace=store.replace
        def sync(*args,**kw):trace.append('sync');return replace(*args,**kw)
        store.replace=sync
        driver=ShortPreprocessor(DurableTurnJournal(self.path/'turns.jsonl'),store,'SYNTHETIC-A',0,clock=observed)
        runtime=DivisionRuntime(ROOT,namespace='SYNTHETIC-A',preprocessor=driver,selected_mode=mode,delivery='ZIP',
            authorized_scope={'namespace':'SYNTHETIC-A','clock':True,'record':True,'sync':True},display_clock=display or clock)
        return runtime,driver,store,trace
    def assessments(self):
        return {r:{'summary':r+' concise supplied consideration','material':False,'evidence_refs':['SYNTHETIC-E1'],'dissent':False} for r in ['MELCHIOR','BALTHASAR','CASPER']}
    def test_full_mode_is_independent_of_container(self):
        a=installation_configuration(delivery='ZIP',intent='INSTALL',selected_mode='FULL');b=installation_configuration(delivery='FIVE_FILES',intent='INSTALL',selected_mode='FULL')
        a.pop('delivery');b.pop('delivery');self.assertEqual(a,b);self.assertTrue(a['preprocess_selected']);self.assertFalse(a['creates_connections_or_permissions'])
    def test_zip_inspection_does_not_install(self):
        for intent in ['INSPECT','SUMMARIZE']:
            x=installation_configuration(delivery='ZIP',intent=intent,selected_mode='FULL');self.assertIsNone(x['selected_mode']);self.assertFalse(x['preprocess_selected'])
    def test_unspecified_mode_does_not_silently_select_full(self):
        self.assertFalse(installation_configuration(delivery='ZIP',intent='INSTALL')['preprocess_selected'])
    def test_quality_core_is_identical_for_every_coordinate(self):
        x=[compile_core(ROOT,c)['shared_core'] for c in ['FATHER','MOTHER','GENERAL']];self.assertEqual(x[0],x[1]);self.assertEqual(x[1],x[2]);self.assertFalse(x[0]['prose']['short_input_is_short_response'])
    def test_brevity_is_local_and_does_not_reduce_evidence_quality(self):
        a=response_plan(brief_requested=True);b=response_plan();self.assertEqual(a['length'],'BRIEF_FOR_THIS_TURN');self.assertEqual(b['length'],'LONG_REASONED_BY_DEFAULT');self.assertEqual(a['quality_floor'],b['quality_floor']);self.assertEqual(len(a['consider_before_conclusion']),3)
    def test_ack_does_not_invent_perspective_slots(self):
        x=response_plan(task_kind='ACK');self.assertEqual(x['consider_before_conclusion'],[]);self.assertEqual(x['length'],'BRIEF_FOR_THIS_TURN')
    def test_roles_do_not_limit_candidates_or_define_weights(self):
        x=response_plan(task_kind='CHOICE');self.assertEqual([v['label'] for v in x['roles'].values()],['合理','倫理','人間']);self.assertIsNone(x['fixed_option_count']);self.assertIsNone(x['weights']);self.assertFalse(x['requires_parallel_models'])
    def test_dissent_is_retained_without_voting_away_facts(self):
        a=self.assessments();a['CASPER']['dissent']=True;x=summarize_magi(a);self.assertEqual([v['role'] for v in x['material_explanations']],['CASPER']);self.assertEqual(x['assessments'],a);self.assertFalse(x['decision_by_majority']);self.assertFalse(x['independent_models_executed'])
    def test_incomplete_roles_and_untyped_fields_are_rejected(self):
        a=self.assessments();a.pop('CASPER')
        with self.assertRaises(ValueError):summarize_magi(a)
        a=self.assessments();a['CASPER']['material']='yes'
        with self.assertRaises(ValueError):summarize_magi(a)
    def test_display_clock_is_after_sync_and_before_body(self):
        r,d,s,t=self.make()
        def body():t.append('body');return 'BODY'
        x=r.dispatch('T1','INPUT',[],body);self.assertEqual(t,['observed','sync','display','body']);self.assertEqual(json.loads(d.journal.path.read_text())['observed_at_jst'],OBSERVED);self.assertEqual(x['response_started_at_jst'],DISPLAY);self.assertIn(DISPLAY.replace('T',' ').replace('+09:00',' JST'),x['prefix']);self.assertNotIn(OBSERVED,x['prefix']);self.assertEqual(len(s.sync_calls),1)
    def test_unconnected_full_mode_keeps_normal_chat(self):
        r=DivisionRuntime(ROOT,namespace='SYNTHETIC-A',selected_mode='FULL');x=r.dispatch('T1','INPUT',[],lambda:'ANSWER');self.assertEqual(x['work_result'],'ANSWER');self.assertIsNone(x['receipt']);self.assertFalse(x['sync_performed']);self.assertIsNone(x['response_started_at_jst'])
    def test_sync_failure_keeps_chat_and_reports_failure(self):
        r,d,s,t=self.make(fail=True);x=r.dispatch('T1','INPUT',[],lambda:'ANSWER');self.assertEqual(x['status'],'DEGRADED');self.assertEqual(x['work_result'],'ANSWER');self.assertNotIn('SYNC_ACKNOWLEDGED',x['prefix']);self.assertEqual(t,['observed','sync','display'])
    def test_bad_display_clock_does_not_reuse_observation(self):
        r,d,s,t=self.make(display=lambda:'2032-04-05T06:09:10+00:00');x=r.dispatch('T1','INPUT',[],lambda:'ANSWER');self.assertIsNone(x['response_started_at_jst']);self.assertNotIn(OBSERVED,x['prefix']);self.assertEqual(x['work_result'],'ANSWER')
    def test_retry_reuses_record_but_gets_fresh_display_clock(self):
        times=iter([DISPLAY,'2032-04-05T06:10:10+09:00']);r,d,s,t=self.make(display=lambda:next(times));a=r.dispatch('T1','INPUT',[]);b=r.dispatch('T1','INPUT',[]);self.assertEqual(d.journal.append_count,1);self.assertEqual(len(s.sync_calls),1);self.assertEqual(a['receipt'],b['receipt']);self.assertNotEqual(a['response_started_at_jst'],b['response_started_at_jst'])
    def test_pause_exempt_resume_never_backfills(self):
        r,d,s,t=self.make();r.control('PAUSE');r.dispatch('P1','PAUSED',[]);self.assertEqual(t,[]);r.control('RESUME');r.control('ONE_TURN_EXEMPT','E1');r.dispatch('E1','EXEMPT',[]);self.assertEqual(t,[]);r.dispatch('A1','ACTIVE',[]);self.assertEqual([json.loads(x)['turn_id'] for x in d.journal.path.read_text().splitlines()],['A1'])
    def test_core_mode_keeps_decision_quality_without_persistence(self):
        r,d,s,t=self.make(mode='CORE');x=r.dispatch('T1','INPUT',[],lambda:'ANSWER');self.assertFalse(d.journal.path.exists());self.assertEqual(t,[]);self.assertEqual(x['decision_policy'],response_plan())
    def test_review_precedes_conclusion_and_does_not_claim_models_executed(self):
        r,d,s,t=self.make()
        def review(p):t.append('review');return self.assessments()
        def body():t.append('body');return 'ANSWER'
        x=r.dispatch('T1','INPUT',[],body,review=review);self.assertLess(t.index('review'),t.index('body'));self.assertFalse(x['magi_summary']['model_quality_tested']);self.assertFalse(x['live_model_quality_verified'])
    def test_authorization_cannot_use_another_namespace(self):
        with self.assertRaises(PreprocessError):DivisionRuntime(ROOT,namespace='SYNTHETIC-A',selected_mode='FULL',authorized_scope={'namespace':'SYNTHETIC-B','clock':True})
    def test_boot_has_no_prefix_and_no_clock_or_persistence_wait(self):
        r,d,s,t=self.make();x=r.dispatch('BOOT','PEOS起動',[],lambda:'EXACT BOOT',route='BOOT');self.assertEqual(x['work_result'],'EXACT BOOT');self.assertEqual(x['prefix'],'');self.assertEqual(t,[]);self.assertFalse(d.journal.path.exists())
    def test_model_protocol_covers_q1_to_q6_but_is_not_an_execution_result(self):
        x=json.loads((ROOT/'tests/fixtures/next_spec_20261103_model_replay.json').read_text());self.assertFalse(x['live_model_pass']);self.assertEqual(x['status'],'NOT_EXECUTED');self.assertTrue({'Q'+str(i) for i in range(1,7)}<={v['id'] for v in x['cases']});self.assertEqual(next_spec_errors(ROOT),[])
