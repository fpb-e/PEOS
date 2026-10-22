#!/usr/bin/env python3
"""Cooperative reference barrier; no platform hook or live Library adapter is installed.

The default clock is called only by a normal run, never on import. Integration
tests inject a fixed synthetic clock and use temporary local files exclusively.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Protocol
from zoneinfo import ZoneInfo

BUILD_ID = 'PEOS-REV0.313-CANDIDATE-FROM-20261021-024240'
NORMAL_ORDER = ('TIME_CAPTURED', 'LOCAL_APPEND', 'FLUSH', 'FSYNC', 'PUBLISHED',
                'NEW_FILE_ID_READBACK', 'HASH_AND_SEQUENCE_VERIFIED', 'STATUS_AUDIT_COMMITTED')
VISIBLE = {'FINAL', 'PARTIAL_FINAL', 'SEMANTIC_COMMENTARY', 'RESPONSE_BODY_AUTHORIZED'}
VERIFY_FLAGS = ('published', 'new_file_id_verified', 'payload_hash_verified',
                'line_count_verified', 'sequence_verified', 'prior_bytes_preserved')


class BarrierError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_record(record: dict) -> bytes:
    return (json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def records_from_bytes(data: bytes) -> list[dict]:
    if data and not data.endswith(b'\n'):
        raise BarrierError('incomplete JSONL record')
    records = [json.loads(line) for line in data.splitlines()]
    if [r.get('ledger_seq') for r in records] != list(range(1, len(records) + 1)):
        raise BarrierError('nonmonotonic or duplicate ledger sequence')
    keys = [r.get('idempotency_key') for r in records]
    if any(not isinstance(key, str) or not key for key in keys) or len(set(keys)) != len(keys):
        raise BarrierError('missing or duplicate idempotency key')
    return records


def capture_runtime_jst() -> str:
    return datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds')


def valid_jst(stamp: str) -> bool:
    try:
        observed = datetime.fromisoformat(stamp)
        return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:00', stamp)) and observed.utcoffset().total_seconds() == 32400
    except (ValueError, TypeError, AttributeError):
        return False


@dataclass
class Commit:
    data: bytes
    previous_data: bytes
    ledger_seq: int
    line_count: int
    idempotent: bool
    flushed: bool = True
    fsynced: bool = True


class LocalDurableLedger:
    def __init__(self, path: Path):
        self.path = Path(path)

    def append(self, turn_id: str, stamp: str, provider: str) -> Commit:
        if not turn_id or not valid_jst(stamp) or not provider:
            raise BarrierError('invalid receipt')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a+b') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            stream.seek(0)
            before = stream.read()
            records = records_from_bytes(before)
            existing = next((r for r in records if r['idempotency_key'] == turn_id), None)
            if existing:
                if existing['user_turn_observed_at_jst'] != stamp or existing['provider'] != provider:
                    raise BarrierError('idempotency collision: immutable receipt differs')
                return Commit(before, before, existing['ledger_seq'], len(records), True)
            record = {'ledger_seq': len(records) + 1, 'idempotency_key': turn_id, 'turn_id': turn_id,
                      'user_turn_observed_at_jst': stamp, 'provider': provider,
                      'phase': 'CAPTURED_LOCAL_COMMIT_CANDIDATE'}
            expected = before + encode_record(record)
            stream.seek(0, os.SEEK_END)
            stream.write(encode_record(record))
            stream.flush()
            os.fsync(stream.fileno())
            stream.seek(0)
            if stream.read() != expected:
                raise BarrierError('local append readback mismatch')
            return Commit(expected, before, record['ledger_seq'], len(records) + 1, False)


class LocalOutcomeAudit:
    def __init__(self, path: Path):
        self.path = Path(path)

    def append(self, event: dict) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a+b') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            stream.seek(0)
            before = stream.read()
            record = encode_record(event)
            stream.seek(0, os.SEEK_END)
            stream.write(record)
            stream.flush()
            os.fsync(stream.fileno())
            stream.seek(0)
            data = stream.read()
            if data != before + record:
                raise BarrierError('outcome audit append verification failed')
            return digest(data)


@dataclass
class Publication:
    file_id: str
    previous_file_id: str | None
    version_before: int
    version_after: int
    idempotent: bool = False


class PersistentAdapter(Protocol):
    evidence_class: str
    def publish(self, data: bytes, turn_id: str) -> Publication: ...
    def read_by_file_id(self, file_id: str) -> tuple[str, bytes]: ...


class MemoryFixtureStore:
    """Synthetic versioned store; never evidence of actual persistent sync."""
    evidence_class = 'STATIC_INTEGRATION'

    def __init__(self, *, fail_publish=False, fail_read=False, corrupt=None, stale_id=False):
        self.fail_publish, self.fail_read = fail_publish, fail_read
        self.corrupt, self.stale_id = corrupt, stale_id
        self.versions: dict[str, bytes] = {}
        self.transactions: dict[str, tuple[bytes, Publication]] = {}
        self.current_file_id = None
        self.version = 0
        self.requested_read_ids: list[str] = []

    def publish(self, data: bytes, turn_id: str) -> Publication:
        if self.fail_publish:
            raise OSError('synthetic publish failure')
        if turn_id in self.transactions:
            previous, publication = self.transactions[turn_id]
            if previous != data:
                raise BarrierError('publish transaction collision')
            return Publication(**{**asdict(publication), 'idempotent': True})
        before, old_id = self.version, self.current_file_id
        self.version += 1
        self.current_file_id = f'fixture-file-{self.version}'
        self.versions[self.current_file_id] = data
        publication = Publication(self.current_file_id, old_id, before, self.version)
        self.transactions[turn_id] = (data, publication)
        return publication

    def read_by_file_id(self, file_id: str) -> tuple[str, bytes]:
        self.requested_read_ids.append(file_id)
        if self.fail_read:
            raise OSError('synthetic readback failure')
        data = self.versions[file_id]
        return ('fixture-stale-id' if self.stale_id else file_id,
                self.corrupt(data) if self.corrupt else data)


@dataclass(frozen=True)
class ScopedExemption:
    tab_id: str
    father_instruction: str

    def applies(self, tab_id: str) -> bool:
        return self.tab_id == tab_id and bool(self.father_instruction.strip())


def classify_outcome(trace: dict, require_status_audit: bool = True) -> str:
    if trace.get('emergency_bypass'):
        return 'PREPROCESS_EMERGENCY_BYPASS'
    if trace.get('scoped_admin_exemption'):
        return 'PREPROCESS_ADMIN_EXEMPT'
    if not trace.get('first_executable_valid') or trace.get('prior_visible_body'):
        return 'FAIL'
    events = trace.get('events', [])
    progress = [event for event in events if event in NORMAL_ORDER]
    if progress != list(NORMAL_ORDER[:len(progress)]):
        return 'FAIL'
    for index, event in enumerate(events):
        if event in VISIBLE and 'STATUS_AUDIT_COMMITTED' not in events[:index]:
            return 'FAIL'
    if not all(trace.get(flag) for flag in ('capture_valid', 'local_commit', 'flushed', 'fsynced')):
        return 'FAIL'
    if not all(trace.get(flag) for flag in VERIFY_FLAGS):
        return 'DEGRADED'
    if require_status_audit and not trace.get('status_audit_committed'):
        return 'DEGRADED'
    expected = list(NORMAL_ORDER if require_status_audit else NORMAL_ORDER[:-1])
    if progress != expected:
        return 'FAIL'
    return 'PASS'


@dataclass
class StreakAudit:
    streaks: dict = field(default_factory=lambda: {'STATIC_INTEGRATION': 0, 'LIVE_TRACE_VERIFIED': 0})
    seen: dict = field(default_factory=dict)
    events: list = field(default_factory=list)

    def consume(self, result: dict) -> dict:
        evidence = result.get('evidence_class')
        if evidence not in self.streaks:
            raise BarrierError('unsupported evidence class')
        if evidence == 'LIVE_TRACE_VERIFIED' and not result.get('independent_live_trace_verified'):
            raise BarrierError('independent live evidence missing')
        if result.get('turn_id') != result['trace'].get('turn_id'):
            raise BarrierError('turn identity mismatch')
        if result.get('status') != classify_outcome(result['trace']):
            raise BarrierError('status does not match trace')
        key = (evidence, result['turn_id'])
        before = self.streaks[evidence]
        duplicate = key in self.seen
        if duplicate and self.seen[key] != result['status']:
            raise BarrierError('no retroactive status promotion')
        excluded = result['status'] in {'PREPROCESS_EMERGENCY_BYPASS', 'PREPROCESS_ADMIN_EXEMPT'}
        if not duplicate and not excluded:
            self.streaks[evidence] = before + 1 if result['status'] == 'PASS' else 0
        self.seen[key] = result['status']
        after = self.streaks[evidence]
        event = {'turn_id': result['turn_id'], 'status': result['status'], 'evidence_class': evidence,
                 'streak_before': before, 'streak_after': after, 'duplicate': duplicate,
                 'excluded_from_normal_counter': excluded, 'normal_threshold_met': after >= 10,
                 'live_provisional_candidate': evidence == 'LIVE_TRACE_VERIFIED' and after >= 10,
                 'live_provisional': False, 'streak_audit_committed': False,
                 'permanent_guarantee': False, 'package_acceptance': 'PENDING',
                 'verification_binding': {k: result.get(k) for k in ('publication', 'readback_sha256', 'ledger_seq', 'line_count', 'receipt')}}
        self.events.append(event)
        return event

    def append_audit(self, path: Path, event: dict) -> dict:
        if event not in self.events:
            raise BarrierError('unrecognized streak event')
        audit_hash = LocalOutcomeAudit(path).append(event)
        return {**event, 'streak_audit_committed': True, 'audit_sha256': audit_hash,
                'live_provisional': event['live_provisional_candidate']}


class PreprocessBarrier:
    def __init__(self, local: LocalDurableLedger, remote: PersistentAdapter,
                 clock: Callable[[], str] = capture_runtime_jst,
                 provider: str = 'PYTHON_DATETIME_ZONEINFO_ASIA_TOKYO',
                 outcome_audit: LocalOutcomeAudit | None = None):
        self.local, self.remote, self.clock, self.provider = local, remote, clock, provider
        self.outcome_audit = outcome_audit or LocalOutcomeAudit(local.path.parent / 'PREPROCESS_OUTCOME_AUDIT.jsonl')
        if self.outcome_audit.path.resolve() == local.path.resolve():
            raise BarrierError('outcome audit must not alter verified ledger payload')

    def run(self, turn_id: str, work: Callable[[], object], *, tab_id: str,
            exemption: ScopedExemption | None = None, emergency_kind: str | None = None,
            actionable_now: bool = False, preflight_would_delay: bool = False,
            prior_visible_body: bool = False, prior_executable_actions: int = 0) -> dict:
        trace = {'turn_id': turn_id, 'events': [], 'first_executable_valid': prior_executable_actions == 0,
                 'prior_visible_body': prior_visible_body, 'emergency_bypass': False,
                 'scoped_admin_exemption': False}
        result = {'turn_id': turn_id, 'trace': trace, 'evidence_class': self.remote.evidence_class,
                  'independent_live_trace_verified': False, 'platform_hook_installed': False,
                  'work_result': None, 'receipt': None, 'no_late_promotion': True}
        urgent = emergency_kind in {'POLICE', 'AMBULANCE', 'IMMINENT_DANGER'} and actionable_now and preflight_would_delay
        if urgent or (exemption is not None and exemption.applies(tab_id)):
            trace['emergency_bypass' if urgent else 'scoped_admin_exemption'] = True
            result['work_result'] = work()
        elif trace['first_executable_valid'] and not prior_visible_body:
            try:
                stamp = self.clock()
                trace['capture_valid'] = valid_jst(stamp)
                trace['events'].append('TIME_CAPTURED')
                if not trace['capture_valid']:
                    raise BarrierError('clock did not return actual-provider JST receipt shape')
                result['receipt'] = stamp
                commit = self.local.append(turn_id, stamp, self.provider)
                result.update(ledger_seq=commit.ledger_seq, line_count=commit.line_count, idempotent=commit.idempotent)
                trace.update(local_commit=True, flushed=commit.flushed, fsynced=commit.fsynced)
                trace['events'].extend(('LOCAL_APPEND', 'FLUSH', 'FSYNC'))
                publication = self.remote.publish(commit.data, turn_id)
                result['publication'] = asdict(publication)
                trace['published'] = True
                trace['events'].append('PUBLISHED')
                read_id, data = self.remote.read_by_file_id(publication.file_id)
                trace['events'].append('NEW_FILE_ID_READBACK')
                trace['new_file_id_verified'] = read_id == publication.file_id and (
                    publication.version_after > publication.version_before and publication.file_id != publication.previous_file_id
                    or publication.idempotent and commit.idempotent)
                result['readback_sha256'] = digest(data)
                trace['payload_hash_verified'] = digest(data) == digest(commit.data) and data == commit.data
                records = records_from_bytes(data)
                trace['line_count_verified'] = len(records) == commit.line_count
                target = [r for r in records if r['idempotency_key'] == turn_id]
                trace['sequence_verified'] = len(target) == 1 and target[0]['ledger_seq'] == commit.ledger_seq and target[0]['user_turn_observed_at_jst'] == stamp
                trace['prior_bytes_preserved'] = data.startswith(commit.previous_data)
                if not all(trace.get(flag) for flag in VERIFY_FLAGS):
                    raise BarrierError('new-file-id, hash, line-count, sequence or prior-byte verification failed')
                trace['events'].append('HASH_AND_SEQUENCE_VERIFIED')
                if classify_outcome(trace, require_status_audit=False) != 'PASS':
                    raise BarrierError('invalid execution ordering')
                result['outcome_audit_sha256'] = self.outcome_audit.append({
                    'turn_id': turn_id, 'candidate_outcome': 'PASS', 'publication': asdict(publication),
                    'readback_sha256': result['readback_sha256'], 'ledger_seq': commit.ledger_seq,
                    'line_count': commit.line_count, 'receipt': stamp, 'evidence_class': self.remote.evidence_class})
                trace['status_audit_committed'] = True
                trace['events'].append('STATUS_AUDIT_COMMITTED')
                trace['events'].append('RESPONSE_BODY_AUTHORIZED')
                result['work_result'] = work()
            except (OSError, ValueError, KeyError, TypeError) as exc:
                trace['failure'] = str(exc)
        result['status'] = classify_outcome(trace)
        result['normal_response_authorized'] = result['status'] in {'PASS', 'PREPROCESS_ADMIN_EXEMPT', 'PREPROCESS_EMERGENCY_BYPASS'}
        return result


def render_receipt(result: dict) -> str:
    if result.get('receipt') is None:
        return result['status']
    return f"**USER_TURN_OBSERVED_AT_JST: {result['receipt']}** / {result['status']}"


def source_sync_restore() -> dict:
    return {'evidence_class': 'SOURCE_SUMMARY_REPORTED', 'source_ledger_count_before': 255,
            'source_ledger_count_after': 256, 'reported_sequence': ['PASS'] * 8 + ['FAIL'],
            'verified_live_streak': None, 'new_file_id': None, 'verified_ledger_sha256': None,
            'runtime_ready': False, 'replay_actions': [], 'private_ledger_reconstructed': False,
            'current_tab_status': 'PREPROCESS_ADMIN_EXEMPT', 'current_tab_pass_credit': 0,
            'source': 'PEOS_father_session_log_2026_10_21_024240.txt'}


def father_learning_spans(body: str) -> dict:
    direct, quoted = [], []
    for line in body.splitlines():
        (quoted if line.lstrip().startswith(('>', '＞')) else direct).append(line)
    return {'father_direct': direct, 'quoted_other_speaker_excluded': quoted}


def clinical_continuity() -> dict:
    return {'needle_emg': {'planned_date': '2026-10-26', 'source_class': 'SOURCE_SUMMARY_REPORTED', 'currently_reconfirmed': False},
            'lifelong_left_leg_concern': {'source_class': 'FATHER_SELF_PESSIMISTIC_INFERENCE', 'corrected_by_user_seq': '0013'},
            'clinician_prognosis': None,
            'candidate_muscles': {'values': ['大腿四頭筋', '腸腰筋'], 'source_class': 'ASSISTANT_DISCUSSION_REPORTED', 'clinical_order': False},
            'clinical_decision_owner': 'TREATING_CLINICIAN'}


def inspect_manifested_source(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != 3 or len(set(names)) != 3 or any('/' in n or '\\' in n for n in names) or archive.testzip() is not None:
            raise BarrierError('source must have three unique root files and valid CRC')
        payload = {name: archive.read(name) for name in names}
    log_name = next(n for n in names if n.startswith('PEOS_father_session_log_'))
    directive_name = next(n for n in names if n.startswith('PEOS_next_spec_directive_'))
    manifest_name = next(n for n in names if 'bundle_manifest_' in n)
    log, directive, manifest = (payload[n].decode('utf-8') for n in (log_name, directive_name, manifest_name))
    bodies = re.findall(r'^BODY_VERBATIM_BEGIN\n(.*?)\nBODY_VERBATIM_END$', log, re.M | re.S)
    seq = re.findall(r'^SEQ: (\d{4})$', log, re.M)
    if seq != [f'{n:04d}' for n in range(1, 18)] or len(bodies) != 17 or log.count('\nEND_OF_TURN') != 17 or 'USER_DIRECT_VERBATIM_COUNT: 17' not in log:
        raise BarrierError('source user sequence or body closure mismatch')
    entries = re.findall(r'^FILE=(\S+)\tSIZE=(\d+)\tSHA256=([0-9a-f]{64})$', manifest, re.M)
    if len(entries) != 2 or {n for n, _, _ in entries} != {log_name, directive_name}:
        raise BarrierError('manifest does not cover exactly log and directive')
    for name, size, sha in entries:
        if len(payload[name]) != int(size) or digest(payload[name]) != sha:
            raise BarrierError('file-level source manifest mismatch')
    if not log.rstrip().endswith('END_OF_LOG') or not directive.rstrip().endswith('END_OF_DIRECTIVE') or not manifest.rstrip().endswith('END_OF_MANIFEST'):
        raise BarrierError('closure marker missing')
    if 'SOURCE_GAP_DECLARATION' not in log or 'ENDPOINT_NOT_RECURSIVELY_EMBEDDED' not in manifest:
        raise BarrierError('gap declaration or endpoint marker missing')
    return {'crc': 'PASS', 'root_file_count': 3, 'verbatim_user_count': 17, 'file_manifest_entry_count': 2,
            'assistant_full_transcript_source_gap': True, 'pipeline_execution_order_independently_proven': False,
            'per_message_time_status': 'UNAVAILABLE_PER_MESSAGE', 'bodies': bodies,
            'artifact_class': 'MANIFESTED_SOURCE_COMMAND_BUNDLE', 'finished_revision': False}
