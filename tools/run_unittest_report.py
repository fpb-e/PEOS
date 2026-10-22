#!/usr/bin/env python3
"""Machine-readable unittest results with no timing-dependent fields."""
from pathlib import Path
import argparse,json,sys,unittest
sys.dont_write_bytecode=True
class Capture(unittest.TestResult):
    def __init__(self):super().__init__();self.cases={}
    def addSuccess(self,test):super().addSuccess(test);self.cases[test.id()]={'status':'PASS'}
    def addFailure(self,test,err):super().addFailure(test,err);self.cases[test.id()]={'status':'FAIL','error':self._exc_info_to_string(err,test)}
    def addError(self,test,err):super().addError(test,err);self.cases[test.id()]={'status':'ERROR','error':self._exc_info_to_string(err,test)}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',type=Path);parser.add_argument('pattern');args=parser.parse_args()
    root=args.root.resolve();sys.path.insert(0,str(root/'tools'));suite=unittest.TestLoader().discover(str(root/'tests'),pattern=args.pattern)
    result=Capture();suite.run(result)
    print(json.dumps({'pattern':args.pattern,'RESULT':'PASS' if result.wasSuccessful() else 'FAIL','TEST_COUNT':result.testsRun,'PASS_COUNT':sum(v['status']=='PASS' for v in result.cases.values()),'TESTS':result.cases},ensure_ascii=False,sort_keys=True,indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
