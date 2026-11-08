"""Typed, namespace-bound relationship values; no NLP or authentication.

The host supplies verified relationship/configuration/authorization evidence.
This reference does not discover identity, install a store, or invent numeric
increments. JSON snapshots preserve the supplied values and replay boundaries;
a host must retain its own latest epoch/revision guard when restoring them.
"""
from copy import deepcopy
import hashlib
import json
import re

from peos_relationship_policy import new_state as qualitative_state
from peos_relationship_policy import evaluate as qualitative_evaluate

KIND = 'SCOPED_NUMERIC_RELATIONSHIP_REFERENCE_STATE'
COORDINATES = {'FATHER', 'MOTHER', 'GENERAL'}
OBSERVATION_SOURCES = {'TYPED_CONTEXT_OBSERVATION', 'USER_EXPLICIT_CORRECTION',
                       'HOST_VERIFIED_CONTEXT'}


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be nonempty text')
    return value


def _number(value, low, high, label, *, unknown=False):
    if unknown and value is None:
        return value
    if type(value) is not int or not low <= value <= high:
        raise ValueError(label + ' is outside the explicitly adopted range')
    return value


def validate_state(state, *, namespace=None, coordinate=None):
    if not isinstance(state, dict) or state.get('kind') != KIND:
        raise ValueError('explicit numeric relationship state required')
    _text(state.get('namespace'), 'namespace')
    if namespace is not None and state['namespace'] != namespace:
        raise ValueError('another namespace cannot supply this relationship state')
    if state.get('coordinate') not in COORDINATES:
        raise ValueError('unknown relationship coordinate')
    if coordinate is not None and state['coordinate'] != coordinate:
        raise ValueError('relationship coordinate differs from the host binding')
    _number(state.get('affinity'), 1, 100, 'affinity', unknown=True)
    _number(state.get('stored_banter'), 1, 5, 'stored banter', unknown=True)
    _number(state.get('fixed_banter'), 1, 5, 'fixed banter', unknown=True)
    for name in ('epoch', 'revision'):
        value = state.get(name)
        if type(value) is not int or value < 0:
            raise ValueError('invalid monotonic ' + name)
    if state['coordinate'] in {'FATHER', 'MOTHER'}:
        _text(state.get('relation_evidence_ref'), 'verified parent relationship evidence')
        if state['affinity'] != 100:
            raise ValueError('a verified parent remains at fixed affinity 100')
    if state['fixed_banter'] is not None and state['stored_banter'] != state['fixed_banter']:
        raise ValueError('a fixed personal banter value cannot drift')
    configuration = state.get('personal_configuration')
    if configuration is not None:
        if (not isinstance(configuration, dict) or configuration.get('namespace') != state['namespace']
                or configuration.get('source_class') != 'HOST_VERIFIED_PERSONAL_CONFIGURATION'
                or ('initial_value' in configuration) == ('fixed_value' in configuration)):
            raise ValueError('restored personal configuration has no verified scoped basis')
        _text(configuration.get('evidence_ref'), 'personal configuration evidence')
        if 'fixed_value' in configuration:
            _number(configuration['fixed_value'], 1, 5, 'configured fixed banter')
            if state['fixed_banter'] != configuration['fixed_value']:
                raise ValueError('restored fixed value differs from its configuration')
        else:
            _number(configuration['initial_value'], 1, 5, 'configured initial banter')
            if state['fixed_banter'] is not None:
                raise ValueError('an initial personal value is not a fixed value')
    elif state['fixed_banter'] is not None:
        raise ValueError('a fixed personal value needs its verified source configuration')
    for name in ('event_fingerprints', 'jokes', 'reactions', 'qualitative'):
        if not isinstance(state.get(name), dict):
            raise ValueError('missing typed relationship ' + name)
    if state['qualitative'].get('namespace') != state['namespace']:
        raise ValueError('qualitative state belongs to another namespace')
    if (type(state['qualitative'].get('fixed_max')) is not bool
            or state['qualitative']['fixed_max'] != (state['coordinate'] != 'GENERAL')):
        raise ValueError('qualitative and numeric parent boundaries differ')
    if not isinstance(state.get('history'), list):
        raise ValueError('relationship history must be a list')
    return state


def new_state(namespace, *, coordinate='GENERAL', affinity=None, stored_banter=None,
              relation_evidence_ref=None, personal_banter=None):
    """Provision one explicit state, never migrate every user to neutral.

    Unknown GENERAL values stay unknown. A verified personal configuration can
    supply an initial value only when no stored value exists, or a fixed value.
    Personal names and owner-specific values belong in the host/private adapter.
    """
    _text(namespace, 'namespace')
    if coordinate not in COORDINATES:
        raise ValueError('unknown coordinate')
    parent = coordinate != 'GENERAL'
    if parent:
        _text(relation_evidence_ref, 'verified parent relationship evidence')
        if affinity is not None and (type(affinity) is not int or affinity != 100):
            raise ValueError('parent affinity cannot be changed from 100')
        affinity = 100
    _number(affinity, 1, 100, 'affinity', unknown=True)
    _number(stored_banter, 1, 5, 'stored banter', unknown=True)
    fixed = None
    if personal_banter is not None:
        if (not isinstance(personal_banter, dict)
                or personal_banter.get('namespace') != namespace
                or personal_banter.get('source_class') != 'HOST_VERIFIED_PERSONAL_CONFIGURATION'
                or not personal_banter.get('evidence_ref')):
            raise ValueError('personal configuration needs a verified namespace-bound source')
        if set(personal_banter) - {'namespace', 'source_class', 'evidence_ref', 'initial_value', 'fixed_value'}:
            raise ValueError('unknown personal configuration fields')
        if ('initial_value' in personal_banter) == ('fixed_value' in personal_banter):
            raise ValueError('choose one initial or fixed personal value')
        _text(personal_banter['evidence_ref'], 'personal configuration evidence')
        if 'fixed_value' in personal_banter:
            fixed = _number(personal_banter['fixed_value'], 1, 5, 'fixed banter')
            if stored_banter is not None and stored_banter != fixed:
                raise ValueError('stored state conflicts with the verified fixed value')
            stored_banter = fixed
        elif stored_banter is None:
            stored_banter = _number(personal_banter['initial_value'], 1, 5, 'initial banter')
        else:
            _number(personal_banter['initial_value'], 1, 5, 'initial banter')
    state = {'kind': KIND, 'namespace': namespace, 'coordinate': coordinate,
             'relation_evidence_ref': relation_evidence_ref,
             'affinity': affinity, 'stored_banter': stored_banter, 'fixed_banter': fixed,
             'personal_configuration': deepcopy(personal_banter),
             'epoch': 0, 'revision': 0, 'event_fingerprints': {},
             'jokes': {}, 'reactions': {}, 'history': [],
             'qualitative': qualitative_state(namespace, verified_parent=parent,
                                               relation_evidence_ref=relation_evidence_ref),
             'numeric_increment_policy': None, 'automatic_context_classifier': False,
             'live_persistence_claimed': False}
    validate_state(state)
    return state


def restore_state(snapshot, *, namespace, minimum_epoch, minimum_revision=0, coordinate=None):
    """Restore the complete snapshot without rerunning old command/history text."""
    validate_state(snapshot, namespace=namespace, coordinate=coordinate)
    for label, value in (('minimum epoch', minimum_epoch), ('minimum revision', minimum_revision)):
        if type(value) is not int or value < 0:
            raise ValueError(label + ' must be an actual nonnegative guard')
    if snapshot['epoch'] < minimum_epoch or snapshot['revision'] < minimum_revision:
        raise ValueError('snapshot is older than the retained relationship boundary')
    return deepcopy(snapshot)


def affinity_band(value):
    _number(value, 1, 100, 'affinity', unknown=True)
    return 'UNCONFIRMED' if value is None else ('LOW' if value < 25 else 'HIGH' if value >= 75 else 'MIDDLE')


def response_context(state, *, namespace=None, coordinate=None):
    validate_state(state, namespace=namespace, coordinate=coordinate)
    band = affinity_band(state['affinity'])
    effective = 1 if band == 'LOW' else (None if band == 'UNCONFIRMED' else state['stored_banter'])
    expression = {'LOW': 'DIRECT_REASONED_WITHOUT_CEREMONY',
                  'MIDDLE': 'RESPECTFUL_EQUAL_COOPERATION',
                  'HIGH': 'CONFIRMED_SHARED_CONTEXT_AND_CARE',
                  'UNCONFIRMED': 'CONTEXT_REQUIRED'}[band]
    return {'namespace': state['namespace'], 'coordinate': state['coordinate'],
            'affinity': state['affinity'], 'affinity_band': band,
            'neutral_value_matched': state['affinity'] == 50,
            'stored_banter': state['stored_banter'], 'effective_banter': effective,
            'relationship_expression': expression, 'epoch': state['epoch'],
            'revision': state['revision'], 'quality_reduced': False,
            'forced_endearments': False, 'invented_shared_memories': False}


def _fingerprint(event):
    return hashlib.sha256(json.dumps(event, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _current_epoch(state, value):
    return type(value) is int and value == state['epoch']


def _duplicate(state, event_id, event):
    _text(event_id, 'event id')
    fingerprint = _fingerprint(event)
    old = state['event_fingerprints'].get(event_id)
    if old is not None and old != fingerprint:
        raise ValueError('an event retry changed its original contents')
    return old is not None


def _finish(state, event_id, event, decision):
    state['event_fingerprints'][event_id] = _fingerprint(event)
    state['revision'] += 1
    state['history'].append({'event_id': event_id, **deepcopy(decision)})
    validate_state(state)
    return state, {**decision, 'state_changed': True, 'live_persistence_claimed': False}


def _unchanged(state, effect, **fields):
    return deepcopy(state), {'effect': effect, 'state_changed': False,
                              'live_persistence_claimed': False, **fields}


def process_command(state, raw, *, actor_namespace, event_id, source_class,
                    admin_authorization=None, applied_at=None):
    """Use host-typed current intent; quoted/archive strings never execute.

    Admin target tokens are exact host-resolved namespace identifiers. The
    authorization object represents an already verified host grant, not a
    textual claim inside the user's message and not a new permission service.
    """
    validate_state(state)
    if not isinstance(raw, str):
        raise ValueError('command input must be text')
    _text(actor_namespace, 'actor namespace')
    if source_class != 'CURRENT_USER_COMMAND':
        return _unchanged(state, 'NO_EXECUTION_NONCURRENT_OR_QUOTED_SOURCE')
    text = raw.strip()
    reset = text == '親密度リセット'
    admin = text.startswith('親密度設定')
    if not reset and not admin:
        return _unchanged(state, 'NOT_A_STANDALONE_RELATIONSHIP_COMMAND')
    event = {'operation': 'SELF_RESET' if reset else 'ADMIN_SET', 'raw': text,
             'actor_namespace': actor_namespace, 'source_class': source_class}
    if _duplicate(state, event_id, event):
        original = next((deepcopy(row) for row in state['history'] if row['event_id'] == event_id), None)
        return _unchanged(state, 'NONE_DUPLICATE_EVENT', original_operation=original)
    before = state['affinity']
    if reset:
        if actor_namespace != state['namespace']:
            return _unchanged(state, 'RESET_NAMESPACE_REJECTED')
        if state['coordinate'] != 'GENERAL':
            return _unchanged(state, 'RESET_DISABLED_FOR_VERIFIED_PARENT')
        value = 50
        grant = 'CURRENT_USER_OWN_NAMESPACE'
    else:
        match = re.fullmatch(r'親密度設定\s+(\S+)\s+([0-9]+)', text)
        if not match:
            return _unchanged(state, 'ADMIN_COMMAND_INVALID')
        if match[1] != state['namespace']:
            return _unchanged(state, 'ADMIN_TARGET_UNKNOWN_OR_DIFFERENT')
        digits = match[2].lstrip('0') or '0'
        if len(digits) > 3:
            return _unchanged(state, 'ADMIN_VALUE_OUT_OF_RANGE')
        value = int(digits)
        if not 1 <= value <= 100:
            return _unchanged(state, 'ADMIN_VALUE_OUT_OF_RANGE')
        grant = admin_authorization
        if (not isinstance(grant, dict) or grant.get('verified') is not True
                or grant.get('source_class') != 'HOST_VERIFIED_ADMIN_AUTHORIZATION'
                or grant.get('actor_namespace') != actor_namespace
                or not isinstance(grant.get('target_namespaces'), list)
                or state['namespace'] not in grant['target_namespaces']
                or not isinstance(grant.get('evidence_ref'), str) or not grant['evidence_ref'].strip()):
            return _unchanged(state, 'ADMIN_AUTHORIZATION_REQUIRED')
        if state['coordinate'] != 'GENERAL':
            return _unchanged(state, 'ADMIN_SET_DISABLED_FOR_VERIFIED_PARENT')
    result = deepcopy(state)
    result['affinity'] = value
    # Keep original events/incident identities while closing old evaluation
    # causes. The old history remains evidence, not scores to add again.
    if reset:
        result['epoch'] += 1
        result['qualitative']['recovery_causes'] = {}
    decision = {'effect': 'RESET_TO_NEUTRAL' if reset else 'ADMIN_VALUE_APPLIED',
                'operation': event['operation'], 'actor_namespace': actor_namespace,
                'target_namespace': state['namespace'], 'before': before,
                'requested_value': value, 'after': value,
                'authorization': deepcopy(grant), 'applied_at': applied_at,
                'applied_at_source': 'HOST_SUPPLIED_NOT_INDEPENDENTLY_VERIFIED' if applied_at else 'NOT_CAPTURED',
                'stored_banter_unchanged': True, 'epoch': result['epoch']}
    return _finish(result, event_id, event, decision)


def evaluate_context(state, event):
    """Keep adopted qualitative conditions without inventing score amounts."""
    validate_state(state)
    if not isinstance(event, dict) or event.get('namespace') != state['namespace']:
        raise ValueError('typed current observation must belong to this namespace')
    if not _current_epoch(state, event.get('epoch')):
        return _unchanged(state, 'NO_EVALUATION_OUTSIDE_CURRENT_EPOCH')
    if _duplicate(state, event.get('event_id'), event):
        return _unchanged(state, 'NONE_DUPLICATE_EVENT')
    result = deepcopy(state)
    qualitative, decision = qualitative_evaluate(state['qualitative'], event)
    result['qualitative'] = qualitative
    decision = deepcopy(decision)
    decision.update(numeric_change_applied=False, numeric_increment_policy=None,
                    affinity_before=state['affinity'], affinity_after=state['affinity'],
                    epoch=state['epoch'])
    return _finish(result, event['event_id'], event, decision)


def register_joke(state, *, joke_id, event_id, source_class, evidence_ref, epoch):
    """Record the effective value at the actual, host-attributed joke event."""
    validate_state(state)
    _text(joke_id, 'joke id'); _text(evidence_ref, 'evidence reference')
    if source_class not in OBSERVATION_SOURCES or not _current_epoch(state, epoch):
        return _unchanged(state, 'NO_JOKE_REGISTRATION_OUTSIDE_CURRENT_TYPED_SCOPE')
    event = {'joke_id': joke_id, 'source_class': source_class,
             'evidence_ref': evidence_ref, 'epoch': epoch}
    if _duplicate(state, event_id, event):
        return _unchanged(state, 'NONE_DUPLICATE_EVENT')
    if joke_id in state['jokes']:
        return _unchanged(state, 'NONE_DUPLICATE_JOKE')
    result = deepcopy(state)
    context = response_context(state)
    result['jokes'][joke_id] = {'epoch': epoch, 'effective_banter_at_joke': context['effective_banter'],
                               'affinity_at_joke': state['affinity'], 'evidence_ref': evidence_ref}
    return _finish(result, event_id, event, {'effect': 'JOKE_CONTEXT_RECORDED',
                                           'joke_id': joke_id, **result['jokes'][joke_id]})


def react_to_joke(state, event):
    """Produce an adopted direction; an unspecified numeric step is not run."""
    validate_state(state)
    if not isinstance(event, dict) or event.get('namespace') != state['namespace']:
        raise ValueError('another namespace cannot supply this reaction')
    if (event.get('source_class') not in OBSERVATION_SOURCES
            or event.get('quoted_other_speaker') or event.get('hypothetical')
            or not _current_epoch(state, event.get('epoch'))):
        return _unchanged(state, 'NO_REACTION_OUTSIDE_CURRENT_TYPED_SCOPE')
    _text(event.get('evidence_ref'), 'reaction evidence')
    if _duplicate(state, event.get('event_id'), event):
        return _unchanged(state, 'NONE_DUPLICATE_EVENT')
    joke_id = _text(event.get('joke_id'), 'reaction joke id')
    joke = state['jokes'].get(joke_id)
    if not joke or joke['epoch'] != state['epoch']:
        return _unchanged(state, 'REACTION_JOKE_CONTEXT_UNAVAILABLE')
    reaction = event.get('reaction')
    if reaction not in {'TAKEN_LITERAL', 'JOINED'}:
        return _unchanged(state, 'HOLD_REACTION_UNCONFIRMED')
    if joke_id in state['reactions']:
        old = state['reactions'][joke_id]
        return _unchanged(state, 'NONE_DUPLICATE_REACTION' if old['reaction'] == reaction
                          else 'HOLD_CONFLICTING_REACTION')
    result = deepcopy(state)
    direction = None
    if joke['effective_banter_at_joke'] == 3 and state['fixed_banter'] is None:
        direction = 'DECREASE' if reaction == 'TAKEN_LITERAL' else 'INCREASE'
    result['reactions'][joke_id] = {'reaction': reaction, 'evidence_ref': event['evidence_ref'],
                                    'requested_direction': direction, 'epoch': state['epoch']}
    actions = ['BRIEF_APOLOGY_FOR_OWN_JOKE'] if reaction == 'TAKEN_LITERAL' and joke['effective_banter_at_joke'] == 3 else []
    decision = {'effect': 'BANTER_DIRECTION_PENDING_UNSPECIFIED_AMOUNT' if direction else 'NO_DEFINED_BANTER_TRANSITION',
                'joke_id': joke_id, 'requested_direction': direction, 'actions': actions,
                'stored_banter_before': state['stored_banter'], 'stored_banter_after': state['stored_banter'],
                'effective_banter_at_joke': joke['effective_banter_at_joke'],
                'affinity_unchanged': True, 'numeric_change_applied': False,
                'numeric_increment_policy': None}
    return _finish(result, event['event_id'], event, decision)
