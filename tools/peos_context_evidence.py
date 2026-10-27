#!/usr/bin/env python3
"""Typed evidence helpers. They do not infer modality or speaker from words."""
from copy import deepcopy
from datetime import datetime

MODES = {'ASSERTED', 'HYPOTHETICAL', 'METAPHOR', 'QUOTED_OTHER', 'APPROXIMATE_REENACTMENT'}
SOURCES = {'USER_REPORT', 'USER_CORRECTION', 'PHYSICAL_EVIDENCE', 'ASSISTANT_INFERENCE'}


def observe(record, item):
    required = {'subject_key', 'claim_id', 'mode', 'source_class', 'source_ref', 'value'}
    if not required <= item.keys() or item['mode'] not in MODES or item['source_class'] not in SOURCES:
        raise ValueError('typed claim, source and modality are required')
    result = deepcopy(record) if record is not None else {
        'subject_key': item['subject_key'], 'actual_status': 'UNREPORTED',
        'reported_value': None, 'actual_claim_id': None, 'actual_source_class': None,
        'observations': []}
    if result['subject_key'] != item['subject_key']:
        raise ValueError('a different subject cannot overwrite this record')
    result['observations'].append(deepcopy(item))
    if item['mode'] == 'ASSERTED' and item['source_class'] != 'ASSISTANT_INFERENCE':
        result.update(actual_status='EVIDENCED' if item['source_class'] == 'PHYSICAL_EVIDENCE' else 'USER_REPORTED',
                      reported_value=deepcopy(item['value']), actual_claim_id=item['claim_id'],
                      actual_source_class=item['source_class'])
    return result


def correct_inferred_modality(record, correction):
    """Retract a linked mistaken inference; do not erase independent evidence."""
    if (correction.get('source_class') != 'USER_CORRECTION'
            or correction.get('mode') not in MODES - {'ASSERTED'}
            or not correction.get('source_ref')
            or correction.get('subject_key') != record['subject_key']):
        raise ValueError('a linked explicit user correction is required')
    result = deepcopy(record)
    if correction.get('correction_of') != result.get('actual_claim_id'):
        raise ValueError('correction must identify the mistaken claim')
    result['observations'].append(deepcopy(correction))
    if result.get('actual_source_class') == 'ASSISTANT_INFERENCE':
        result.update(actual_status='UNREPORTED', reported_value=None,
                      actual_claim_id=None, actual_source_class=None)
    else:
        result['correction_status'] = 'REVIEW_CONFLICT_WITH_EXISTING_EVIDENCE'
    return result


def attribute_spans(text, spans):
    """Validate explicitly supplied partial attribution; never infer image authors."""
    output = []; end = 0
    for span in spans:
        start, stop = span.get('start'), span.get('end')
        if (not isinstance(start, int) or not isinstance(stop, int)
                or start < end or not 0 <= start < stop <= len(text)
                or span.get('speaker') not in {'USER_SELF_ATTRIBUTED', 'THIRD_PARTY', 'UNKNOWN'}
                or not span.get('source_ref')):
            raise ValueError('ordered nonoverlapping source-bound spans are required')
        output.append(dict(span, text=text[start:stop],
                           father_primary_eligible=span['speaker'] == 'USER_SELF_ATTRIBUTED'))
        end = stop
    return output


def clock_evidence(*, observed_at=None, persisted_at=None, capture_kind='MISSING', ingress_proven=False):
    allowed = {'MISSING', 'DIRECT_OBSERVATION', 'DEFERRED_AFTER_OUTAGE', 'RECONNECTED_REQUEST'}
    if capture_kind not in allowed:
        raise ValueError('unknown capture evidence kind')
    if not isinstance(ingress_proven, bool) or (ingress_proven and observed_at is None):
        raise ValueError('original ingress needs a supplied clock and explicit proof classification')
    if capture_kind == 'MISSING' and observed_at is not None:
        raise ValueError('missing clock cannot acquire a fabricated observation')
    if capture_kind == 'DEFERRED_AFTER_OUTAGE' and ingress_proven:
        raise ValueError('late observation does not prove original ingress')
    result = {'capture_kind': capture_kind, 'original_ingress_proven': bool(ingress_proven),
              'strict_pass_claimed': False}
    parsed = {}
    for key, value in [('observed_at_jst', observed_at), ('persisted_at_jst', persisted_at)]:
        if value is None:
            continue
        try:
            date = datetime.fromisoformat(value)
            if date.tzinfo is None or date.utcoffset().total_seconds() != 32400:
                raise ValueError('clock must be an actual supplied JST observation')
        except (TypeError, AttributeError) as exc:
            raise ValueError('invalid clock') from exc
        result[key] = value; parsed[key] = date
    if observed_at is None and capture_kind != 'MISSING':
        raise ValueError('a capture kind requires its supplied observation')
    if len(parsed) == 2 and parsed['persisted_at_jst'] < parsed['observed_at_jst']:
        raise ValueError('persistence cannot precede the supplied observation')
    return result
