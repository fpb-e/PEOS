"""Concise host-supplied discussion records, not hidden reasoning or NLP.

The host/model must actually understand the received point and assess whether
another perspective is relevant. These checks preserve its supplied sources
and dependencies; they cannot certify semantic accuracy or model quality.
The record structure is optional and is not a mandatory response format.
"""
from copy import deepcopy


def dialogue_contract(*, applicable=True):
    if type(applicable) is not bool:
        raise ValueError('typed discussion applicability required')
    return {'contract': 'RECEIVED_POINT_RELEVANT_PERSPECTIVES_REVISED_CONCLUSION',
            'applicable': applicable, 'receive_point_accurately': True,
            'alternative_perspectives_only_when_relevant': True,
            'include_practical_consequence_of_perspectives': True,
            'dissent_only_when_warranted': True,
            'personal_attributes_or_liking_are_not_argument_premises': True,
            'revise_reasons_when_evidence_changes_even_if_conclusion_does_not': True,
            'fixed_response_format': False, 'fixed_perspective_count': None,
            'hidden_reasoning_requested': False, 'semantic_accuracy_verified': False,
            'live_model_execution_claimed': False}


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be a nonempty concise public explanation')
    return value


def _texts(values, label, *, required=True):
    if not isinstance(values, list) or required and not values:
        raise ValueError(label + ' must be a supplied list')
    for item in values:
        _text(item, label)
    return values


def _fields(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(label + ' has missing or unexpected fields')


def summarize_dialogue(assessment):
    """Retain A, relevant A-prime views and B without inventing an opponent.

    All inputs are concise explanations a user could be shown, with supplied
    source references. They are not private chain-of-thought transcripts.
    No identity/liking field can be used instead of a claim-to-evidence link.
    Empty perspectives and absent dissent are valid when no addition is useful.
    """
    _fields(assessment, {'received_point', 'perspectives', 'conclusion', 'dissent',
                         'attribute_leap', 'manufactured_disagreement', 'update'}, 'discussion record')
    if assessment['attribute_leap'] is not False:
        raise ValueError('an attribute or liking leap cannot replace an argument')
    if assessment['manufactured_disagreement'] is not False:
        raise ValueError('opposition must not be fabricated to fill the record')
    point = assessment['received_point']
    _fields(point, {'id', 'summary', 'source_refs'}, 'received point')
    _text(point['id'], 'received point id'); _text(point['summary'], 'received point summary')
    _texts(point['source_refs'], 'received point source references')
    perspectives = assessment['perspectives']
    if not isinstance(perspectives, list):
        raise ValueError('perspectives must be a supplied list, possibly empty')
    ids = {point['id']}
    for perspective in perspectives:
        _fields(perspective, {'id', 'summary', 'source_refs', 'relevance_to_point',
                              'practical_consequence'}, 'perspective')
        _text(perspective['id'], 'perspective id')
        if perspective['id'] in ids:
            raise ValueError('discussion point identifiers must be unique')
        ids.add(perspective['id'])
        _text(perspective['summary'], 'perspective summary')
        _texts(perspective['source_refs'], 'perspective source references')
        _text(perspective['relevance_to_point'], 'perspective relevance')
        _text(perspective['practical_consequence'], 'perspective practical consequence')
    conclusion = assessment['conclusion']
    _fields(conclusion, {'summary', 'basis_ids'}, 'conclusion')
    _text(conclusion['summary'], 'conclusion summary')
    _texts(conclusion['basis_ids'], 'conclusion basis identifiers')
    if set(conclusion['basis_ids']) != ids or len(conclusion['basis_ids']) != len(ids):
        raise ValueError('the conclusion must use the received point and supplied relevant views')
    dissent = assessment['dissent']
    if dissent is not None:
        _fields(dissent, {'summary', 'warranted', 'grounds', 'basis_ids'}, 'dissent')
        _text(dissent['summary'], 'dissent summary')
        _texts(dissent['grounds'], 'dissent grounds')
        _texts(dissent['basis_ids'], 'dissent basis identifiers')
        if dissent['warranted'] is not True or not set(dissent['basis_ids']) <= ids:
            raise ValueError('dissent needs supplied relevant grounds rather than compulsory opposition')
    update = assessment['update']
    if update is not None:
        _fields(update, {'change_kind', 'previous_conclusion', 'previous_reasons',
                         'current_reasons', 'reason_for_revision', 'source_refs'}, 'reasoned update')
        if update['change_kind'] not in {'CONCLUSION_AND_REASONS', 'REASONS_ONLY'}:
            raise ValueError('a conclusion update and a reasons-only update are distinct')
        _text(update['previous_conclusion'], 'previous conclusion')
        _texts(update['previous_reasons'], 'previous reasons')
        _texts(update['current_reasons'], 'current reasons')
        _text(update['reason_for_revision'], 'reason for revision')
        _texts(update['source_refs'], 'update source references')
    return {'received_point': deepcopy(point), 'perspectives': deepcopy(perspectives),
            'conclusion': deepcopy(conclusion), 'dissent': deepcopy(dissent),
            'update': deepcopy(update), 'update_explanation_required': update is not None,
            'practical_consequences': [p['practical_consequence'] for p in perspectives],
            'uses_attribute_or_liking_premise': False, 'opposition_manufactured': False,
            'fixed_response_format': False, 'fixed_perspective_count': None,
            'hidden_reasoning_requested': False, 'semantic_accuracy_verified': False,
            'live_model_execution_claimed': False}
