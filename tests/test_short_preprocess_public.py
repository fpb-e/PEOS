#!/usr/bin/env python3
"""Meaningful synthetic tests; no real private ledger or external operations."""
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from peos_short_preprocess import *

STAMP='2032-10-23T02:44:03+09:00'
class ShortTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.journal=DurableTurnJournal(Path(self.temp.name)/'SYNTHETIC_TIME_LEDGER.jsonl')
        self.store=SyntheticAckStore();self.clock_calls=0
        def clock():self.clock_calls+=1;return STAMP
        self.driver=ShortPreprocessor(self.journal,self.store,'SYNTHETIC_LEDGER',0,clock=clock)
    def normal(self,turn='T1',raw='親父の原文',updates=None):return self.driver.dispatch(turn,raw,[] if updates is None else updates,lambda:'BODY')
    def test_01_normal_exactly_one_append_one_sync_no_readback(self):
        r=self.normal();self.assertEqual((r['status'],self.journal.append_count,len(self.store.sync_calls),self.store.readback_calls),('SYNC_ACKNOWLEDGED',1,1,0));self.assertEqual(r['work_result'],'BODY')
    def test_02_same_receipt_bold_prefix_and_row(self):
        r=self.normal();row=json.loads(self.journal.path.read_text());self.assertIn('**USER_TURN_OBSERVED_AT_JST: '+row['observed_at_jst'],r['prefix']);self.assertEqual(row['observed_at_jst'],STAMP)
    def test_03_empty_learning_delta_is_valid(self):
        self.normal();self.assertEqual(json.loads(self.journal.path.read_text())['learning_updates'],[])
    def test_04_original_typo_and_correction_are_separate_rows(self):
        self.normal(raw='teh');self.normal('T2','the');rows=[json.loads(x) for x in self.journal.path.read_text().splitlines()];self.assertEqual([r['body_verbatim'] for r in rows],['teh','the'])
    def test_05_learning_exact_span_bound_to_current_turn(self):
        update={'source_class':'FATHER_EXPLICIT_INSTRUCTION','source_turn_id':'T1','source_span':'草。'}
        self.assertEqual(self.normal(raw='草。',updates=[update])['status'],'SYNC_ACKNOWLEDGED')
    def test_06_learning_fabricated_or_foreign_turn_rejected(self):
        for span,turn in [('架空の嗜好','T1'),('草。','OTHER')]:
            r=self.normal(raw='草。',updates=[{'source_class':'FATHER_SELF_REPORT','source_turn_id':turn,'source_span':span}]);self.assertEqual(r['status'],'FAIL')
        self.assertFalse(self.journal.path.exists())
    def test_07_third_party_quote_not_learned(self):
        r=self.normal(updates=[{'source_class':'THIRD_PARTY_CLAIM','source_turn_id':'T1','source_span':'投稿'}]);self.assertEqual(r['status'],'FAIL');self.assertEqual(len(self.store.sync_calls),0)
    def test_08_readback_claim_rejected_for_ack(self):
        r=self.normal();self.assertTrue(assert_success_wording(r,r['prefix']))
        for word in ['照合済','検証済','readback PASS','SHA256 PASS']:
            with self.assertRaises(PreprocessError):assert_success_wording(r,word)
    def test_09_captured_version_not_a_future_guard(self):
        self.driver.version_basis='HISTORICAL_CAPTURE_380';self.driver.version=380;r=self.normal();self.assertEqual(r['status'],'DEGRADED');self.assertFalse(r['work_authorized']);self.assertEqual(self.store.sync_calls,[])
    def test_10_conflict_keeps_concrete_guard_no_retry(self):
        self.store.version=7;r=self.normal();self.assertEqual(r['status'],'DEGRADED');self.assertEqual(self.store.sync_calls[0]['expected_version'],0);self.assertEqual(len(self.store.sync_calls),1)
    def test_11_failed_sync_not_acknowledged(self):
        self.store.fail=True;r=self.normal();self.assertEqual(r['status'],'DEGRADED');self.assertNotIn('同期済',r['prefix']);self.assertFalse(r['work_authorized'])
    def test_12_local_fsync_failure_blocks_remote_and_body(self):
        with patch('peos_short_preprocess.os.fsync',side_effect=OSError('disk')):r=self.normal()
        self.assertEqual(r['status'],'FAIL');self.assertEqual(self.store.sync_calls,[])
    def test_13_boot_runs_before_clock_or_failing_io(self):
        self.store.fail=True;r=self.driver.dispatch('BOOT','PEOS起動',[],lambda:'BOOTED',route='BOOT');self.assertEqual(r['work_result'],'BOOTED');self.assertEqual(self.clock_calls,0);self.assertFalse(self.journal.path.exists())
    def test_14_emergency_runs_before_io(self):
        r=self.driver.dispatch('E','urgent',[],lambda:'HELP',route='URGENT_SAFETY');self.assertEqual(r['work_result'],'HELP');self.assertEqual(self.clock_calls,0)
    def test_15_one_turn_exception_does_not_leak(self):
        self.driver.control('ONE_TURN_EXEMPT','T1');self.assertEqual(self.normal()['status'],'ONE_TURN_EXEMPT');self.assertEqual(self.normal('T2')['status'],'SYNC_ACKNOWLEDGED')
    def test_16_temporary_pause_and_resume_no_backfill(self):
        self.driver.control('PAUSE');self.assertEqual(self.normal()['status'],'PAUSED');self.assertEqual(self.normal('T2')['status'],'PAUSED');self.driver.control('RESUME');self.normal('T3');rows=[json.loads(x) for x in self.journal.path.read_text().splitlines()];self.assertEqual([r['turn_id'] for r in rows],['T3'])
    def test_17_one_turn_exception_requires_identity(self):
        with self.assertRaises(PreprocessError):self.driver.control('ONE_TURN_EXEMPT')
    def test_18_duplicate_retry_no_second_clock_append_or_sync(self):
        r=self.normal();again=self.normal();self.assertEqual((self.clock_calls,self.journal.append_count,len(self.store.sync_calls)),(1,1,1));self.assertEqual(again['receipt'],r['receipt']);self.assertTrue(again['duplicate_retry'])
    def test_19_retry_body_change_rejected(self):
        self.normal();r=self.normal(raw='別の原文');self.assertEqual(r['status'],'FAIL');self.assertEqual(len(self.store.sync_calls),1)
    def test_20_same_identity_ack_version_and_local_sha_recorded(self):
        r=self.normal();saved=json.loads(self.driver.ack_path.read_text());self.assertEqual(saved['ack']['library_file_id'],'SYNTHETIC_LEDGER');self.assertEqual(saved['ack']['version'],1);self.assertEqual(saved['local_sha256'],digest(self.store.data));self.assertFalse(saved['readback_performed'])
    def test_21_wrong_identity_or_version_ack_rejected(self):
        with patch.object(self.store,'replace',return_value={'status':'succeeded','library_file_id':'OTHER','version':1,'file_id':'F'}):r=self.normal()
        self.assertEqual(r['status'],'DEGRADED');self.assertFalse(r['work_authorized'])
    def test_22_no_legacy_streak_credit(self):
        for i in range(10):r=self.normal('T'+str(i))
        self.assertEqual(r['legacy_streak_credit'],0);self.assertIsNone(r['verified_live_streak'])
    def test_23_screenshot_or_utc_time_not_valid_jst(self):
        for stamp in ['22:06','2026-10-23T02:44:03+00:00','UNKNOWN',None]:self.assertFalse(valid_jst(stamp))
    def test_24_restart_duplicate_uses_persisted_ack(self):
        self.normal();self.driver=ShortPreprocessor(self.journal,self.store,'SYNTHETIC_LEDGER',1,clock=lambda:None);r=self.normal();self.assertEqual(r['status'],'SYNC_ACKNOWLEDGED');self.assertEqual(len(self.store.sync_calls),1)
    def test_25_corrupt_local_journal_is_not_replaced(self):
        self.journal.path.write_bytes(b'{broken');before=self.journal.path.read_bytes();r=self.normal();self.assertEqual(r['status'],'FAIL');self.assertEqual(self.journal.path.read_bytes(),before);self.assertEqual(self.store.sync_calls,[])
    def test_26_boot_consumes_matching_turn_exception(self):
        self.driver.control('ONE_TURN_EXEMPT','B');self.driver.dispatch('B','boot',[],route='BOOT');self.assertEqual(self.normal()['status'],'SYNC_ACKNOWLEDGED')
    def test_27_sync_failure_recovery_preserves_original_receipt(self):
        self.store.fail=True;first=self.normal();self.store.fail=False;second=self.normal();self.assertEqual(second['receipt'],first['receipt']);self.assertEqual(self.clock_calls,1);self.assertEqual(self.journal.append_count,1)
    def test_28_empty_learning_does_not_invent_updates(self):
        self.normal('EMPTY','',[]);row=json.loads(self.journal.path.read_text());self.assertEqual((row['body_verbatim'],row['learning_updates']),('',[]))

if __name__=='__main__':unittest.main()
