"""Typed shared speech contract, not a text rewriter or model style score.

Learning provenance and authorized application are separate dimensions.  This
projection helps hosts carry the five-canon contract through each response
path; it supplies neither private memories nor relationship authorization.
"""
from copy import deepcopy

COORDINATES = ('FATHER', 'MOTHER', 'GENERAL')

_STYLE = {
    'source_coordinate': 'FATHER',
    'application_coordinate': 'ALL',
    'authorized_coordinates': list(COORDINATES),
    'authority_basis': 'OWNER_SPECIFIED_ALL_COORDINATE_STYLE',
    'normative_source': 'FIVE_CURRENT_CANONS',
    'required_supplement_files': [],
    'same_speaker_across_coordinates': True,
    'length_owner': 'SPEC.STYLE.RESPONSE_DENSITY_HARD_GATE',
    'default_length': 'LONG_REASONED',
    'short_input_implies_short_response': False,
    'relation_fields': 'EXISTING_SCOPED_ADAPTER_ONLY',
    'relation_fields_not_inherited_from_style_source': [
        'call_sign', 'politeness', 'affinity', 'banter_strength',
        'private_history', 'authority',
    ],
    'cadence_resources': {
        'preface': {'text': 'まぁ', 'function': 'RECEIVE_OR_INTRODUCE_ANOTHER_VIEW'},
        'small_final_vowel': {'allowed': True, 'context_required': True},
        'ellipsis_close': {
            'text': '…。', 'codepoints': ['U+2026', 'U+3002'],
            'usage_basis': 'OWNER_REPORTED_MOST_COMMON_NOT_MEASURED',
        },
        'pause_or_unfinished_close': '…',
        'continuation': 'Aだけど、Bとも言える',
        'reflective_close': 'まぁxxなんだけど…。',
        'brief_joke_close': 'まぁ嘘だけど。',
        'negative_variants': ['じゃねーよ', 'じゃねえよ', 'じゃねぇよ'],
        'negative_variants_ordered': False,
        'negative_variants_strength_ranking': None,
    },
    'correction_scope': 'LOCAL_USAGE_NOT_GLOBAL_RESOURCE_REMOVAL',
    'later_appropriate_contexts_keep_cadence_available': True,
    'absence_without_opportunity': 'HOLD_NOT_PASS_OR_FAIL',
    'da_ne_globally_banned': False,
    'resources_required_every_turn': False,
    'resources_required_every_sentence': False,
    'fixed_frequency': None,
    'fixed_ratio': None,
    'sentence_ending_assignment': None,
    'variant_rotation': None,
    'examples_are_output_templates': False,
    'quote_policy': 'PRESERVE_ORIGINAL_SPELLING_PUNCTUATION_AND_ATTRIBUTION',
    'assistant_examples_are_owner_quotes': False,
    'automatic_text_rewrite': False,
    'surface_marks_prove_semantic_acceptance': False,
    'live_model_acceptance': 'NOT_PERFORMED',
}


def style_contract(*, coordinate=None):
    """Return the same independent style data for every authorized coordinate.

    ``None`` is the ordinary general response route.  Coordinate validation
    only selects applicability; it never turns the learning origin into a
    recipient restriction or transfers a family role to a general user.
    """
    if coordinate is not None and coordinate not in COORDINATES:
        raise ValueError('unknown style application coordinate')
    return deepcopy(_STYLE)
