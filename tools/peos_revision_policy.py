"""Plan owner-authorized specification releases; no I/O, authentication or publication.

The caller supplies the verified owner scope, current authority and stable
request identity. A plan records adoption intent; it does not claim a build,
model evaluation, installation or repository mutation has already succeeded.
"""
from copy import deepcopy
import hashlib
import json
import re

POLICY_ID = 'PEOS_OWNER_SPECIFICATION_RELEASE_20261125'
CONTEXTS = {'CURRENT', 'ARCHIVE', 'QUOTE'}
ACTIONS = {'SPECIFY', 'REGISTER_POLICY', 'DISCUSS', 'INSPECT', 'LOAD', 'BOOT'}


def normalize_revision(value):
    if not isinstance(value, str):
        raise ValueError('revision must be text')
    match = re.fullmatch(r'rev(?:(\d+))?\.(\d+)', value)
    if not match:
        raise ValueError('formal revision or owner shorthand required')
    return f'rev{int(match[1] or 0)}.{int(match[2]):03d}'


def key(value):
    match = re.fullmatch(r'rev(\d+)\.(\d+)', value)
    return tuple(map(int, match.groups()))


def authority_value(value):
    if not isinstance(value, dict):
        raise ValueError('current authority required')
    result = deepcopy(value)
    current = normalize_revision(result.get('current_canon'))
    if not isinstance(result.get('accepted_baseline'), str):
        raise ValueError('previous accepted baseline must be text')
    baseline = re.fullmatch(r'PEOS_GITHUB_PACKAGE_(rev\d+\.\d+)\.zip',
                            result.get('accepted_baseline', ''))
    if (not baseline or normalize_revision(baseline[1]) == 'rev0.280'
            or key(normalize_revision(baseline[1])) >= key(current)
            or normalize_revision(result.get('detailed_reference')) != current):
        raise ValueError('current, detailed and previous accepted baseline must agree')
    result.update(current_canon=current, detailed_reference=current,
                  accepted_baseline='PEOS_GITHUB_PACKAGE_' + normalize_revision(baseline[1]) + '.zip')
    return result


def specification_plan(authority, *, action, owner_authorized, request_id,
                       source_digest, source_context='CURRENT',
                       explicit_revision=None, candidate_only=False, previous=None):
    """Assign once and record canonical adoption for a real specification command.

    source_digest binds the current command plus its specification inputs; the
    host must retain this decision under request_id for a resumed operation.
    Neither an actor label nor this Boolean authenticates a real-world owner.
    """
    current = authority_value(authority)
    if (action not in ACTIONS or source_context not in CONTEXTS
            or type(owner_authorized) is not bool or type(candidate_only) is not bool):
        raise ValueError('typed action, context and owner scope required')
    if not owner_authorized or source_context != 'CURRENT' or action != 'SPECIFY':
        return {'effect': 'NO_SPECIFICATION_BUILD', 'current_authority': current,
                'target_authority': None, 'release_accepted': False,
                'reason': 'ONLY_A_CURRENT_OWNER_SPECIFICATION_COMMAND_TRIGGERS'}
    if (not isinstance(request_id, str) or not request_id.strip()
            or not isinstance(source_digest, str)
            or not re.fullmatch('[0-9a-f]{64}', source_digest)):
        raise ValueError('stable request ID and source digest required')
    explicit = normalize_revision(explicit_revision) if explicit_revision is not None else None
    identity = {'request_id': request_id, 'source_digest': source_digest,
                'explicit_revision': explicit, 'candidate_only': candidate_only}
    fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    if previous is not None and previous.get('request_id') == request_id:
        if previous.get('request_fingerprint') != fingerprint:
            raise ValueError('request ID reused with changed specification input')
        target = normalize_revision(previous.get('target_revision'))
        result = deepcopy(previous)
        result.update(retry_reuses_assignment=True, current_authority=current,
                      effect='SUPERSEDED_NO_ROLLBACK' if key(current['current_canon']) > key(target)
                      else 'REUSE_ASSIGNED_RELEASE')
        if result['effect'] == 'SUPERSEDED_NO_ROLLBACK':
            result['historical_target_authority'] = result['target_authority']
            result['target_authority'] = None
        return result
    major, minor = key(current['current_canon'])
    target = explicit or f'rev{major}.{minor + 1:03d}'
    if key(target) < key(current['current_canon']):
        raise ValueError('a historical revision cannot silently roll back current authority')
    target_authority = deepcopy(current)
    target_authority.update(current_canon=target, detailed_reference=target)
    if key(target) > key(current['current_canon']):
        target_authority['accepted_baseline'] = 'PEOS_GITHUB_PACKAGE_' + current['current_canon'] + '.zip'
    return {'effect': 'PLAN_SPECIFICATION_RELEASE', **identity,
            'request_fingerprint': fingerprint, 'policy_id': POLICY_ID,
            'current_authority': current, 'target_revision': target,
            'target_authority': None if candidate_only else target_authority,
            'release_accepted': not candidate_only,
            'release_status': 'CANDIDATE_ONLY' if candidate_only else 'ACCEPTED_BY_OWNER',
            'acceptance_basis': 'EXPLICIT_CANDIDATE_SCOPE' if candidate_only else
                                'OWNER_STANDING_INSTRUCTION_AND_CURRENT_SPECIFICATION_COMMAND',
            'revision_assignment': 'OWNER_EXPLICIT' if explicit else 'NEXT_ACCEPTED_REVISION',
            'retry_reuses_assignment': False,
            'build_status': 'PLANNED_NOT_EXECUTED', 'live_model_acceptance': 'NOT_PERFORMED',
            'external_actions_performed': False}
