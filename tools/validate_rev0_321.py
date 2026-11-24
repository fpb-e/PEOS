#!/usr/bin/env python3
"""Validate the public export without opening or recreating private sources."""
import argparse
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
from peos_public_release import validate


def run(root):
    errors = validate(root)
    loader = unittest.TestLoader()
    suite = loader.discover(str(root / 'tests'), pattern='test_*.py', top_level_dir=str(root / 'tests'))
    result = unittest.TextTestRunner(verbosity=1, stream=sys.stderr).run(suite)
    return {
        'scope': 'PUBLIC_SPECIFICATION_AND_SYNTHETIC_TESTS_WITHOUT_ORIGINAL_CONVERSATIONS_OR_IMAGES',
        'result': 'PASS' if not errors and result.wasSuccessful() else 'FAIL',
        'structural_errors': errors, 'tests_run': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
        'private_source_validation_performed': False, 'live_runtime_acceptance': 'NOT_CLAIMED',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    report = run(args.root.resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for error in report['structural_errors']:
            print('FAIL', error)
        print(f"PUBLIC {report['result']}: {report['tests_run']} tests; "
              f"{report['failures']} failures, {report['errors']} errors, {report['skipped']} skipped")
    raise SystemExit(0 if report['result'] == 'PASS' else 1)
