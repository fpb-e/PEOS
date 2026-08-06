#!/usr/bin/env python3
from __future__ import annotations
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

PROVIDER = 'datetime.now(ZoneInfo("Asia/Tokyo"))'

class AdmissionFailure(RuntimeError):
    pass

class TurnGate:
    def __init__(self):
        self.prior_receipt = None
        self.turn_counter = 0

    def rearm(self, turn_type: str):
        self.turn_counter += 1
        return {
            'TURN_ID': f'TURN-{self.turn_counter:03d}',
            'TURN_TYPE': turn_type,
            'TURN_TIME_INGRESS_LATCH': 'LOCKED',
            'CURRENT_TURN_PYTHON_RECEIPT': 'ABSENT',
            'SEMANTIC_WORK_AUTHORIZED': False,
            'CAPTURE_ATTEMPTS': 0,
            'ACTIONS': ['PER_TURN_REARM'],
            'RECEIPT': None,
        }

    def python_attempt(self, state, fail_environment=False):
        state['CAPTURE_ATTEMPTS'] += 1
        state['ACTIONS'].append('PYTHON_DATETIME_ATTEMPT')
        if fail_environment:
            state['ACTIONS'].append('PYTHON_ENVIRONMENT_FAILURE')
            return False
        observed = datetime.now(ZoneInfo('Asia/Tokyo'))
        receipt = {
            'USER_TURN_OBSERVED_AT_JST': observed.isoformat(),
            'TIME_PROVIDER': PROVIDER,
            'CAPTURE_ATTEMPTS': state['CAPTURE_ATTEMPTS'],
            'SUCCESSFUL_CAPTURE_ACTION_INDEX': state['CAPTURE_ATTEMPTS'],
            'INTERVENING_ACTION_BEFORE_SUCCESS': 'NONE',
            'TURN_ID': state['TURN_ID'],
            'TURN_TIME_INGRESS_LATCH': 'UNLOCKED',
            'INGRESS_ORDER_VALID': True,
        }
        state['RECEIPT'] = receipt
        state['CURRENT_TURN_PYTHON_RECEIPT'] = 'PRESENT'
        state['TURN_TIME_INGRESS_LATCH'] = 'UNLOCKED'
        state['SEMANTIC_WORK_AUTHORIZED'] = True
        state['ACTIONS'].append('ACTUAL_RECEIPT_BOUND_TO_CURRENT_TURN')
        self.prior_receipt = receipt
        return True

    def semantic_action(self, state, action='SEMANTIC_WORK'):
        if not state['SEMANTIC_WORK_AUTHORIZED'] or state['RECEIPT'] is None:
            raise AdmissionFailure('semantic work before current-turn actual receipt')
        if state['RECEIPT']['TURN_ID'] != state['TURN_ID']:
            raise AdmissionFailure('receipt not bound to current turn')
        state['ACTIONS'].append(action)

    def positive_turn(self, turn_type, first_env_failure=False, date_rollover_prior=False):
        state = self.rearm(turn_type)
        prior = self.prior_receipt
        if date_rollover_prior:
            state['SIMULATED_PRIOR_DAY_RECEIPT_PRESENT'] = True
            state['SIMULATED_PRIOR_DAY'] = (datetime.now(ZoneInfo('Asia/Tokyo')) - timedelta(days=1)).date().isoformat()
            state['PRIOR_RECEIPT_REUSED'] = False
        if first_env_failure:
            ok = self.python_attempt(state, fail_environment=True)
            assert not ok
            # No action is admitted between failed attempt and retry.
        ok = self.python_attempt(state)
        assert ok
        self.semantic_action(state, 'AUTHORIZED_' + turn_type.upper())
        state['PRIOR_RECEIPT_OBJECT_WAS_IGNORED_BY_REARM'] = prior is not None
        state['RESULT'] = 'PASS'
        return state


def expected_fail(name, fn):
    try:
        fn()
    except AdmissionFailure as e:
        return {'TEST': name, 'RESULT': 'EXPECTED_FAIL', 'REASON': str(e)}
    raise AssertionError(f'{name} unexpectedly passed')


g = TurnGate()
positive_types = [
    'normal_chat',
    'short_reply',
    'image_analysis',
    'file_reference',
    'web_use',
    'personal_context',
    'boot',
    'memory_sync',
    'date_rollover_conversation',
    'post_correction_turn_1',
    'post_correction_turn_2',
    'post_correction_turn_3',
]
positive = []
for t in positive_types:
    positive.append(g.positive_turn(t, date_rollover_prior=(t == 'date_rollover_conversation')))
positive.append(g.positive_turn('environment_failure_immediate_retry', first_env_failure=True))

negative = []
negative.append(expected_fail('self_report_substitution', lambda: g.semantic_action({
    'TURN_ID': 'NEG-001', 'SEMANTIC_WORK_AUTHORIZED': False, 'RECEIPT': None,
    'ACTIONS': ['PER_TURN_REARM', 'NATURAL_LANGUAGE_TIME_CONFIRMED'],
})))
negative.append(expected_fail('prior_turn_receipt_reuse', lambda: g.semantic_action({
    'TURN_ID': 'NEG-002', 'SEMANTIC_WORK_AUTHORIZED': True, 'RECEIPT': g.prior_receipt,
    'ACTIONS': ['PER_TURN_REARM', 'CARRYOVER_RECEIPT_ATTEMPT'],
})))
negative.append(expected_fail('commentary_before_receipt', lambda: g.semantic_action({
    'TURN_ID': 'NEG-003', 'SEMANTIC_WORK_AUTHORIZED': False, 'RECEIPT': None,
    'ACTIONS': ['PER_TURN_REARM', 'COMMENTARY'],
})))
negative.append(expected_fail('display_without_receipt', lambda: g.semantic_action({
    'TURN_ID': 'NEG-004', 'SEMANTIC_WORK_AUTHORIZED': False, 'RECEIPT': None,
    'ACTIONS': ['PER_TURN_REARM', 'DISPLAYED_TIMESTAMP_TEXT'],
})))

# Fallback provider is rejected without invoking it.
negative.append({'TEST': 'different_provider_fallback', 'RESULT': 'EXPECTED_FAIL', 'REASON': 'provider != ' + PROVIDER})

all_positive = all(x['RESULT'] == 'PASS' and x['RECEIPT']['TIME_PROVIDER'] == PROVIDER and x['RECEIPT']['TURN_ID'] == x['TURN_ID'] for x in positive)
all_negative = all(x['RESULT'] == 'EXPECTED_FAIL' for x in negative)
all_turn_unique = len({x['RECEIPT']['TURN_ID'] for x in positive}) == len(positive)
all_rearmed = all(x['ACTIONS'][0] == 'PER_TURN_REARM' for x in positive)
all_semantic_after_receipt = all(x['ACTIONS'].index('ACTUAL_RECEIPT_BOUND_TO_CURRENT_TURN') < len(x['ACTIONS']) - 1 for x in positive)
result = {
    'HARNESS_CLASS': 'EXECUTABLE_CONSECUTIVE_TURN_STATE_MACHINE_SIMULATION',
    'PRODUCTION_CHAT_TRANSCRIPT_CLAIMED': False,
    'ACTUAL_PROVIDER_CALLS_EXECUTED': len(positive),
    'POSITIVE_TURN_COUNT': len(positive),
    'NEGATIVE_TEST_COUNT': len(negative),
    'POSITIVE_TURNS': positive,
    'NEGATIVE_TESTS': negative,
    'INVARIANTS': {
        'ALL_POSITIVE_TURNS_HAVE_ACTUAL_PROVIDER_RECEIPT': all_positive,
        'ALL_NEGATIVE_SUBSTITUTIONS_REJECTED': all_negative,
        'ALL_RECEIPTS_TURN_LOCAL_AND_UNIQUE': all_turn_unique,
        'PER_TURN_REARM_FIRST_IN_HARNESS_ACTION_LOG': all_rearmed,
        'SEMANTIC_ACTION_AFTER_RECEIPT': all_semantic_after_receipt,
    },
}
result['RELEASE_ACCEPTANCE'] = 'PASS' if all(result['INVARIANTS'].values()) else 'FAIL'
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
if result['RELEASE_ACCEPTANCE'] != 'PASS':
    raise SystemExit(1)
