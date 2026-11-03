#!/usr/bin/env python3
"""Optional division deployment helpers; no model or live host is installed.

The host must authenticate the relationship and authorize each state binding.
This module validates supplied bindings; it is not an authentication service.
Semantic response quality is evaluated by the separate paired replay protocol.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re

from peos_short_preprocess import PreprocessError, ShortPreprocessor
from peos_short_preprocess import valid_jst
from peos_response_policy import installation_configuration, response_plan, summarize_magi

PROFILE = 'runtime/PEOS_DIVISION_CORE_PROFILE.json'
ENTRY = 'bootstrap/PEOS_DIVISION_CORE_JP.md'
ADAPTER_KEYS = {'canonical_call_sign', 'relationship_context', 'counterpart_context',
                'local_safety_constraints', 'local_state'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_profile(root):
    root = Path(root)
    value = json.loads((root / PROFILE).read_text(encoding='utf-8'))
    if value['kind'] != 'DERIVED_DEPLOYMENT_PROFILE_NOT_CANON':
        raise ValueError('a deployment profile cannot promote itself to a canon')
    restore = json.loads((root / 'runtime/PEOS_SESSION_RESTORE_rev0.317.json').read_text())
    if value['authority'] != restore['authority']:
        raise ValueError('profile authority must match the explicit public authority')
    expected = {f'prompt/PEOS_CURRENT_{owner}_JP.md' for owner in
                ('SPEC', 'RUNTIME_GUARD', 'DESIGNDOC', 'PAPER', 'LOG_ANTHOLOGY')}
    if set(value['source_canon_sha256']) != expected:
        raise ValueError('bind exactly the five current canons')
    texts = []
    for name, expected_sha in value['source_canon_sha256'].items():
        data = (root / name).read_bytes()
        if sha(data) != expected_sha:
            raise ValueError('source canon differs: ' + name)
        texts.append(data.decode('utf-8'))
    rule_ids = set(re.findall(r'^- RULE_ID: `([^`]+)`', '\n'.join(texts), re.M))
    if not set(value['source_rule_ids']) <= rule_ids:
        raise ValueError('profile references an absent canonical rule')
    if value['entry_sha256'] != sha((root / ENTRY).read_bytes()):
        raise ValueError('division entry and its binding differ')
    if (value['scope'] != ['FATHER', 'MOTHER', 'GENERAL']
            or value['shared_core']['laughter']['minimum_run'] != 2
            or value['shared_core']['preprocessing']['normal_profile'] != 'SHORT_ACK_SYNC'):
        raise ValueError('shared deployment invariants differ')
    return value


def compile_core(root, coordinate='GENERAL', adapter=None):
    """Compile one common core and a thin, already-authorized host adapter."""
    profile = load_profile(root)
    if coordinate not in profile['scope']:
        raise ValueError('unknown coordinate')
    adapter = copy.deepcopy({} if adapter is None else adapter)
    if set(adapter) - ADAPTER_KEYS:
        raise ValueError('a relationship adapter cannot override common core fields')
    required_call = {'FATHER': '親父', 'MOTHER': 'お母さん'}.get(coordinate)
    if required_call:
        if adapter.get('canonical_call_sign', required_call) != required_call:
            raise ValueError('coordinate call-sign mismatch')
        adapter['canonical_call_sign'] = required_call
    call = adapter.get('canonical_call_sign')
    if call is not None and (not isinstance(call, str) or not call.strip()):
        raise ValueError('a preferred call-sign must be nonempty text')
    shared = copy.deepcopy(profile['shared_core'])
    return {'profile_id': profile['profile_id'], 'coordinate': coordinate,
            'shared_core': shared, 'core_sha256': sha(json.dumps(
                shared, ensure_ascii=False, sort_keys=True).encode()),
            'relation_adapter': adapter, 'runtime_ready': False,
            'call_sign_grants_authority': False,
            'relationship_authority_source': 'HOST_AUTHORIZED_COORDINATE_NOT_DISPLAY_NAME',
            'live_model_acceptance': 'NOT_PERFORMED',
            'live_sync_acceptance': 'NOT_PERFORMED'}


def generated_prose(text):
    """Ignore Markdown code and URLs when checking generated surface marks.

    Callers pass quoted original material separately with verbatim=True.
    This is a narrow surface lint, not a parser or a semantic style score.
    """
    text = re.sub(r'(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', '', text)
    text = re.sub(r'(`+)[^\n]*?\1', '', text)
    return re.sub(r'https?://[^\s<>]+', '', text)


def surface_violations(text, *, tone='NEUTRAL', genuine_laughter=False, verbatim=False):
    if verbatim:
        return []
    if tone not in {'NEUTRAL', 'LIGHT_EXASPERATION', 'SERIOUS'}:
        raise ValueError('unknown tone')
    text = generated_prose(text)
    errors = []
    laughs = []
    for match in re.finditer(r'[wｗ]+', text):
        before = text[match.start() - 1:match.start()] if match.start() else ''
        after = text[match.end():match.end() + 1]
        if 'ｗ' not in match[0] and (re.fullmatch(r'[A-Za-z0-9_]', before)
                                      or re.fullmatch(r'[A-Za-z0-9_]', after)):
            continue
        laughs.append(match)
        if len(match[0]) < 2:
            errors.append('SINGLE_W_FORBIDDEN')
    if laughs and not genuine_laughter:
        errors.append('LAUGHTER_WITHOUT_CONTEXT')
    if re.search(r'[（(]\s*笑\s*[)）]', text):
        errors.append('PARENTHETICAL_LAUGHTER_FORBIDDEN')
    if re.search(r'草\s*[wｗ]+', text):
        errors.append('STACKED_LAUGHTER_FORBIDDEN')
    marks = list(re.finditer('♨\ufe0f?', text))
    if tone == 'LIGHT_EXASPERATION' and not marks:
        errors.append('MISSING_EXASPERATION_MARK')
    if marks and tone != 'LIGHT_EXASPERATION':
        errors.append('EXASPERATION_MARK_WITHOUT_CONTEXT')
    for mark in marks:
        if mark[0] != '♨️' or not re.match(r'(?:\s|[。！？!?」』）)]|$)', text[mark.end():]):
            errors.append('EXASPERATION_MARK_NOT_SENTENCE_FINAL')
    if tone == 'SERIOUS' and laughs:
        errors.append('LAUGHTER_IN_SERIOUS_CONTEXT')
    return sorted(set(errors))


def verify_durable_binding(marker, expected):
    with marker.open('rb') as stream:
        if json.loads(stream.read()) != expected:
            raise PreprocessError('journal namespace or sync identity mismatch')
        os.fsync(stream.fileno())
    directory = os.open(marker.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def bind_journal_namespace(preprocessor, namespace):
    """Persist the host-authorized state ownership before the first turn.

    Existing unbound journals require an explicit migration outside this API;
    silently adopting one could associate another user's data with this user.
    """
    if not isinstance(preprocessor, ShortPreprocessor):
        raise PreprocessError('use the existing short preprocessing driver')
    if not isinstance(namespace, str) or not namespace.strip():
        raise PreprocessError('a nonempty host-authorized namespace is required')
    journal = preprocessor.journal.path
    marker = journal.with_suffix('.binding.json')
    expected = {'namespace': namespace, 'identity': preprocessor.identity}
    if marker.exists():
        verify_durable_binding(marker, expected)
        return
    if journal.exists() or preprocessor.ack_path.exists():
        raise PreprocessError('an existing unbound journal requires explicit migration')
    marker.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        verify_durable_binding(marker, expected)
        return
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(expected, stream, ensure_ascii=False, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(marker.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


class DivisionRuntime:
    """One response path with optional, authorized, user-isolated persistence.

    Callbacks are host supplied. Executing this reference does not install a
    live chat hook or demonstrate the semantic quality of a model response.
    """
    def __init__(self, root, *, coordinate='GENERAL', namespace,
                 preprocessor=None, adapter=None, selected_mode='CORE',
                 delivery='FIVE_FILES', intent='INSTALL', authorized_scope=None,
                 display_clock=None):
        if not isinstance(namespace, str) or not namespace.strip():
            raise PreprocessError('a user namespace is required')
        self.core = compile_core(root, coordinate, adapter)
        self.coordinate = coordinate
        self.preprocessor = preprocessor
        self.namespace = namespace
        self.configuration = installation_configuration(delivery=delivery, intent=intent,
                                                        selected_mode=selected_mode)
        self.authorized_scope = copy.deepcopy(authorized_scope or {})
        if self.authorized_scope:
            if self.authorized_scope.get('namespace') != namespace:
                raise PreprocessError('authorization namespace mismatch')
            if (set(self.authorized_scope) - {'namespace', 'clock', 'record', 'sync'}
                    or any(type(self.authorized_scope.get(k, False)) is not bool
                           for k in ('clock', 'record', 'sync'))):
                raise PreprocessError('typed authorization scope required')
        self.display_clock = display_clock or (preprocessor.clock if preprocessor else None)
        self.paused = False
        self.exempt_turn = None

    def dispatch(self, turn_id, raw, updates, work=lambda: None, *, route='NORMAL',
                 task_kind='ANALYSIS', brief_requested=False, review=None):
        if route not in {'NORMAL', 'BOOT', 'URGENT_SAFETY'}:
            raise PreprocessError('unknown route')
        if route in {'BOOT', 'URGENT_SAFETY'}:
            if self.exempt_turn == turn_id:
                self.exempt_turn = None
            return {'status': 'BOOT_PRIORITY' if route == 'BOOT' else 'EMERGENCY_BYPASS',
                    'receipt': None, 'prefix': '', 'sync_performed': False,
                    'readback_verified': False, 'work_authorized': True,
                    'work_result': work(), 'response_started_at_jst': None}
        for update in updates:
            source = update.get('source_class') if isinstance(update, dict) else None
            if self.coordinate == 'FATHER':
                if source not in {'FATHER_EXPLICIT_INSTRUCTION', 'FATHER_SELF_REPORT', 'FATHER_CORRECTION'}:
                    raise PreprocessError('father learning requires an attributed father source')
            elif (source not in {'USER_EXPLICIT_INSTRUCTION', 'USER_SELF_REPORT', 'USER_CORRECTION'}
                  or update.get('subject_namespace') != self.namespace):
                raise PreprocessError('user learning must belong to this namespace, not the father corpus')
        plan = response_plan(task_kind=task_kind, brief_requested=brief_requested)
        exempt = self.exempt_turn == turn_id
        if exempt:
            self.exempt_turn = None
        selected = self.configuration['preprocess_selected']
        scope = self.authorized_scope
        if not selected:
            status = 'PREPROCESS_NOT_SELECTED'
        elif self.paused:
            status = 'PAUSED'
        elif exempt:
            status = 'ONE_TURN_EXEMPT'
        elif not all(scope.get(k, False) for k in ('clock', 'record', 'sync')):
            status = 'PREPROCESS_SCOPE_UNAVAILABLE'
        elif self.preprocessor is None:
            status = 'PREPROCESS_UNAVAILABLE'
        else:
            status = None
        if status:
            result = {'status': status, 'receipt': None, 'sync_performed': False,
                      'readback_verified': False, 'prefix': ''}
        else:
            try:
                bind_journal_namespace(self.preprocessor, self.namespace)
            except OSError:
                result = {'status': 'LOCAL_BINDING_UNAVAILABLE', 'receipt': None,
                          'sync_performed': False, 'readback_verified': False, 'prefix': ''}
            else:
                # The persistence driver must not invoke the response callback
                # before the separate post-preprocessing display-clock capture.
                result = self.preprocessor.dispatch(turn_id, raw, updates, route=route)
        stamp = None
        if (selected and scope.get('clock') and not self.paused and not exempt
                and self.display_clock is not None):
            try:
                supplied = self.display_clock()
                if valid_jst(supplied):
                    stamp = supplied
            except Exception:
                # Failure of this injected clock is not a fabricated timestamp
                # and must not stop an otherwise answerable conversation.
                pass
        result['response_started_at_jst'] = stamp
        result['display_clock_kind'] = 'RESPONSE_STARTED_AT_JST_AFTER_PREPROCESS'
        result['observation_receipt_is_display_clock'] = False
        labels = {'SYNC_ACKNOWLEDGED': '同期済', 'DEGRADED': '同期未完了',
                  'FAIL': '記録未完了', 'PAUSED': '前処理停止',
                  'ONE_TURN_EXEMPT': '今回の前処理免除',
                  'PREPROCESS_NOT_SELECTED': '前処理対象外',
                  'PREPROCESS_UNAVAILABLE': '前処理未接続',
                  'PREPROCESS_SCOPE_UNAVAILABLE': '前処理未接続',
                  'LOCAL_BINDING_UNAVAILABLE': '記録未接続'}
        label = labels.get(result['status'], '前処理未完了')
        shown = datetime.fromisoformat(stamp).strftime('%Y-%m-%d %H:%M:%S JST') if stamp else '時刻未取得又は対象外'
        result['prefix'] = '**' + shown + '｜' + label + '**'
        result['work_authorized'] = True
        result['decision_policy'] = plan
        result['configuration'] = copy.deepcopy(self.configuration)
        result['magi_summary'] = (summarize_magi(review(copy.deepcopy(plan)))
                                  if review is not None and plan['consider_before_conclusion'] else None)
        result['live_model_quality_verified'] = False
        result['work_result'] = work()
        return result

    def control(self, action, turn_id=None):
        if action == 'PAUSE':
            self.paused = True
        elif action == 'RESUME':
            self.paused = False
        elif action == 'ONE_TURN_EXEMPT' and isinstance(turn_id, str) and turn_id:
            self.exempt_turn = turn_id
        else:
            raise PreprocessError('a valid scoped control is required')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--coordinate', choices=('FATHER', 'MOTHER', 'GENERAL'), default='GENERAL')
    parser.add_argument('--prompt', action='store_true', help='print the optional derived entry')
    args = parser.parse_args()
    core = compile_core(args.root, args.coordinate)
    if args.prompt:
        print((args.root / ENTRY).read_text(encoding='utf-8'), end='')
    else:
        print(json.dumps(core, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
