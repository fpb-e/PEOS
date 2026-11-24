"""One embedded predecessor; published assets have separate retention."""
from pathlib import Path
import json,shutil,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from peos_history_policy import select_previous_versions
from peos_public_release import specification_errors

class HistoryRotationTests(unittest.TestCase):
    def test_next_generation_keeps_only_immediate_formal_reference(self):
        self.assertEqual(select_previous_versions('rev0.322',['rev0.319','rev0.320','rev0.321','rev0.322'],'rev0.321'),['rev0.321'])
        with self.assertRaises(ValueError):select_previous_versions('rev0.322',['rev0.320','rev0.321'],'rev0.320')
    def test_policy_cannot_silently_reintroduce_two_generations(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for folder in ['admin','prompt','runtime','history','docs']:shutil.copytree(ROOT/folder,root/folder)
            shutil.copyfile(ROOT/'README.md',root/'README.md')
            p=root/'admin/HISTORY_RETENTION_POLICY.json';v=json.loads(p.read_text());v['retained_previous_version_count']=2;p.write_text(json.dumps(v))
            self.assertIn('HISTORY_POLICY_SCOPE_DIFFERS',specification_errors(root))
