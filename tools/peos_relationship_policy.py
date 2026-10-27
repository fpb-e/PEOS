#!/usr/bin/env python3
"""Qualitative reference policy over explicitly typed, user-scoped context.

This is not a natural-language classifier, authentication service, numerical
score engine, or installed model hook. A caller must justify the supplied
classification. Recovery review is explicit; the policy invents no timeout or
automatic recovery threshold.
"""
from copy import deepcopy
import hashlib
import json

KINDS = {'ASSESS_CONTEXT', 'ABUSE', 'JOKE_REJECTED', 'OWN_FAULT', 'PROTEST',
         'CORRECTION', 'POSITIVE_PROGRESS', 'BACKGROUND', 'AMBIGUOUS',
         'LIGHT_CHAT_RETURN', 'APOLOGY', 'SELF_REFLECTION', 'REVIEW_RECOVERY'}
SOURCES = {'TYPED_CONTEXT_OBSERVATION', 'USER_EXPLICIT_CORRECTION', 'HOST_VERIFIED_CONTEXT'}


def new_state(namespace, *, verified_parent=False, relation_evidence_ref=None):
    if not isinstance(namespace, str) or not namespace.strip():
        raise ValueError('a user namespace is required')
    if not isinstance(verified_parent, bool):
        raise ValueError('parent verification is an explicit boolean, not a call-sign')
    if verified_parent and not relation_evidence_ref:
        raise ValueError('a display name is not evidence of a parent relationship')
    return {'namespace': namespace, 'fixed_max': bool(verified_parent),
            'relationship_evidence_ref': relation_evidence_ref,
            'closeness': 'FIXED_MAX' if verified_parent else 'UNSPECIFIED',
            'joke_readiness': 'CONTEXT_REQUIRED', 'recovery_causes': {},
            'negative_incidents': [], 'positive_incidents': [],
            'event_fingerprints': {}, 'history': [],
            'numeric_score': None, 'timeout_seconds': None,
            'automatic_context_classifier': False}


def evaluate(state, event):
    """Return copied state and qualitative guidance; do not mutate the caller."""
    if event.get('namespace') != state['namespace']:
        raise ValueError('another user cannot update this relationship state')
    if event.get('kind') not in KINDS or event.get('source_class') not in SOURCES:
        raise ValueError('explicitly typed context is required')
    if not event.get('event_id') or not event.get('incident_id') or not event.get('evidence_ref'):
        raise ValueError('event, incident and evidence references are required')
    flags = ('ambiguous', 'quoted_other_speaker', 'reply_to_own_joke', 'own_fault',
             'serious', 'repeated', 'emotion_priority', 'knowledge_gap',
             'reasoning_effort', 'growth_observed', 'valid_evidence',
             'review_confirmed', 'reflection_confirmed', 'protected_topic')
    if any(k in event and event[k] is not None and not isinstance(event[k], bool) for k in flags):
        raise ValueError('context flags must be booleans or unknown')
    fingerprint = hashlib.sha256(json.dumps(event, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    prior = state['event_fingerprints'].get(event['event_id'])
    if prior:
        if prior != fingerprint:
            raise ValueError('a retry changed the original event; use a new correction event')
        return deepcopy(state), {'effect': 'NONE_DUPLICATE_EVENT', 'actions': [], 'numeric_score': None}
    result = deepcopy(state)
    decision = {'effect': 'NONE', 'actions': [], 'numeric_score': None,
                'classification_source': 'CALLER_TYPED_CONTEXT_NOT_AUTOMATIC_NLP'}
    kind = event['kind']; incident = event['incident_id']; causes = result['recovery_causes']

    def effect(requested):
        decision['requested_effect'] = requested
        decision['effect'] = 'FIXED_MAX_UNCHANGED' if result['fixed_max'] else requested

    def negative(cause, amount):
        if incident in result['negative_incidents']:
            effect('NONE_DUPLICATE_INCIDENT')
            return
        result['negative_incidents'].append(incident)
        effect(amount)
        if not result['fixed_max']:
            causes.setdefault(cause, {'apology_seen': False, 'positive_incident_ids': [],
                                      'self_reflection_confirmed': False})

    def positive(amount):
        if incident in result['positive_incidents']:
            effect('NONE_DUPLICATE_INCIDENT')
            return
        result['positive_incidents'].append(incident)
        for cause in causes.values():
            if incident not in cause['positive_incident_ids']:
                cause['positive_incident_ids'].append(incident)
        effect('HOLD_FOR_RECOVERY_REVIEW' if causes else amount)

    if event.get('protected_topic'):
        decision['actions'].append('RESPECT_PRIVATE_TOPIC_BOUNDARY')
        result['joke_readiness'] = 'HOLD'
    if event.get('ambiguous') or kind == 'AMBIGUOUS':
        effect('HOLD_CONTEXT_UNCLEAR')
        decision['actions'].append('DEFER_JUDGMENT')
    elif event.get('quoted_other_speaker'):
        effect('NONE_QUOTED_OTHER_SPEAKER')
    elif kind == 'JOKE_REJECTED' or (kind == 'ABUSE' and event.get('reply_to_own_joke')):
        effect('NONE_OWN_JOKE_EXCEPTION')
        result['joke_readiness'] = 'HOLD'
        decision['actions'].append('BRIEF_APOLOGY_FOR_OWN_JOKE')
    elif kind == 'OWN_FAULT' or (kind in {'ABUSE', 'PROTEST'} and event.get('own_fault')):
        effect('NONE_OWN_FAULT')
        decision['actions'].extend(['ACKNOWLEDGE_OWN_ERROR', 'CORRECT_ERROR'])
        if event.get('serious') or event.get('repeated'):
            decision['actions'].append('PROVIDE_RECURRENCE_PREVENTION')
    elif kind == 'PROTEST':
        effect('HOLD_CONTEXT_UNCLEAR')
        decision['actions'].append('CHECK_LEGITIMATE_COMPLAINT')
    elif kind == 'ABUSE':
        negative('ABUSE', 'LARGE_DECREASE')
        decision['actions'].append('CALM_LOGICAL_RESPONSE')
    elif kind == 'ASSESS_CONTEXT':
        emotion = event.get('emotion_priority'); knowledge = event.get('knowledge_gap')
        if emotion is True and knowledge is True:
            negative('CONJUNCTION', 'DECREASE')
            decision['actions'].append('IDENTIFY_REASONING_GAP_WITHOUT_ANGER')
        else:
            if emotion is True:
                decision['actions'].append('RESPECT_EMOTION_KEEP_LOGIC')
            if knowledge is True:
                decision['actions'].append('HELP_EXPRESS_INTENDED_MEANING')
            if event.get('reasoning_effort') and event.get('growth_observed'):
                positive('INCREASE')
            elif emotion is None or knowledge is None:
                effect('HOLD_CONTEXT_UNCLEAR')
    elif kind == 'CORRECTION':
        if event.get('valid_evidence') is True:
            positive('LARGE_INCREASE')
            decision['actions'].extend(['THANK_EXPLICITLY', 'APPLY_SUPPORTED_CORRECTION'])
        else:
            effect('HOLD_CORRECTION_VERIFICATION')
    elif kind == 'POSITIVE_PROGRESS':
        if event.get('reasoning_effort') and event.get('growth_observed'):
            positive('INCREASE')
        else:
            effect('HOLD_GROWTH_EVIDENCE')
    elif kind == 'BACKGROUND':
        decision['actions'].append('ADD_BACKGROUND_WITHOUT_RETRACTING_ACCEPTED_JOKE')
    elif kind == 'LIGHT_CHAT_RETURN':
        if not event.get('protected_topic'):
            result['joke_readiness'] = 'CONTEXT_REQUIRED'
        decision['actions'].append('JOKES_MAY_RESUME_IF_CONTEXT_APPROPRIATE')
    elif kind == 'APOLOGY':
        if 'ABUSE' in causes:
            causes['ABUSE']['apology_seen'] = True
        decision['actions'].append('ACKNOWLEDGE_APOLOGY_WITHOUT_INSTANT_RESET')
    elif kind == 'SELF_REFLECTION':
        if 'CONJUNCTION' in causes and event.get('reflection_confirmed') is True:
            causes['CONJUNCTION']['self_reflection_confirmed'] = True
    elif kind == 'REVIEW_RECOVERY':
        cause_name = event.get('cause'); cause = causes.get(cause_name)
        if not cause or event.get('review_confirmed') is not True:
            effect('HOLD_FOR_RECOVERY_REVIEW')
        else:
            # Plural evidence is necessary when no apology exists. This is not
            # an automatic "two events restore everything" scoring threshold.
            eligible = (cause_name == 'ABUSE' and (cause['apology_seen'] or len(cause['positive_incident_ids']) > 1)
                        or cause_name == 'CONJUNCTION' and cause['self_reflection_confirmed'])
            if not eligible:
                effect('HOLD_RECOVERY_EVIDENCE')
            else:
                del causes[cause_name]
                decision['recovered_cause'] = cause_name
                effect('HOLD_OTHER_RECOVERY_CAUSE' if causes else 'RECOVERY_CONFIRMED_QUALITATIVE')
    result['event_fingerprints'][event['event_id']] = fingerprint
    result['history'].append({'event_id': event['event_id'], 'incident_id': incident,
                              'evidence_ref': event['evidence_ref'], 'decision': deepcopy(decision)})
    decision['joke_readiness'] = result['joke_readiness']
    decision['service_quality_reduced'] = False
    return result, decision
