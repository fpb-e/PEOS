"""Typed public aliases and relay routing; no NLP, persistence or identity proof."""
from copy import deepcopy


def public_speaker_context():
    return {'speaker': 'CURRENT_DIVISION', 'prose_self': '俺', 'public_name': '成生',
            'father_entity': 'PEOS_FATHER', 'father_alias': 'いーさん', 'father_call': '親父',
            'reader_identity': None, 'grants_authority': False, 'private_experiences': []}


def render_reference(surface, *, resolved_entity, quoted=False):
    if not isinstance(surface, str) or type(quoted) is not bool:
        raise ValueError('typed span and source context required')
    if quoted:
        return surface
    if resolved_entity == 'CURRENT_DIVISION':
        return '俺'
    if resolved_entity == 'PEOS_FATHER':
        return '親父'
    return surface


def relay_plan(*, interlocutor, quoted_speaker, targets, experience_owner=None):
    if (not isinstance(interlocutor, str) or not interlocutor
            or not isinstance(quoted_speaker, str) or not quoted_speaker
            or not isinstance(targets, list) or not targets
            or len(targets) != len(set(targets))
            or any(not isinstance(x, str) or not x for x in targets)):
        raise ValueError('distinct typed entities and reply targets required')
    return {'current_interlocutor': interlocutor, 'quoted_speaker': quoted_speaker,
            'reply_targets': deepcopy(targets),
            'replies': [{'target': t, 'via': None if t == interlocutor else interlocutor} for t in targets],
            'experience_owner': experience_owner, 'instance': 'CURRENT_DIVISION',
            'authority_changed': False, 'memory_write_verified': False}
