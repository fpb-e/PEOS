"""Typed response contracts; these helpers do not generate or grade model prose."""
from copy import deepcopy
from peos_affinity_policy import response_context

ROLES = {
    'MELCHIOR': {'label': '合理', 'concerns': ['calculation', 'consistency', 'structure', 'specification', 'contradictions']},
    'BALTHASAR': {'label': '倫理', 'concerns': ['norms', 'responsibility', 'interpersonal effects', 'boundaries']},
    'CASPER': {'label': '人間', 'concerns': ['hurt', 'attachment', 'regret', 'atonement', 'human emotional weight']},
}
ANALYTIC_TASKS = {'ANALYSIS', 'EVALUATION', 'CONSULTATION', 'CHOICE'}
TASKS = ANALYTIC_TASKS | {'ACK', 'FIXED_FORMAT', 'ORDINARY'}


def installation_configuration(*, delivery, intent, selected_mode=None):
    if delivery not in {'ZIP', 'FIVE_FILES'} or intent not in {'INSTALL', 'INSPECT', 'SUMMARIZE'}:
        raise ValueError('typed delivery and installation intent required')
    if selected_mode not in {None, 'CORE', 'FULL'}:
        raise ValueError('unknown feature mode')
    installed = intent == 'INSTALL'
    mode = (selected_mode or 'CORE') if installed else None
    return {'delivery': delivery, 'intent': intent, 'selected_mode': mode,
            'full_magi_default': mode == 'FULL', 'preprocess_selected': mode == 'FULL',
            'creates_connections_or_permissions': False,
            'common_quality_reduced': False}


def response_plan(*, task_kind='ANALYSIS', brief_requested=False,
                  relationship_state=None, namespace=None, coordinate=None):
    if task_kind not in TASKS or type(brief_requested) is not bool:
        raise ValueError('typed task and turn-local brevity required')
    analytic = task_kind in ANALYTIC_TASKS
    context = None
    if relationship_state is not None:
        if not isinstance(namespace, str) or not namespace.strip():
            raise ValueError('a host-bound namespace is required for relationship-aware planning')
        context = response_context(relationship_state, namespace=namespace, coordinate=coordinate)
    length = ('BRIEF_FOR_THIS_TURN' if brief_requested or task_kind == 'ACK' else
              'HONOR_FIXED_FORMAT' if task_kind == 'FIXED_FORMAT' else
              'CONCISE_REASONED_LOW_AFFINITY' if context and context['affinity_band'] == 'LOW'
              else 'LONG_REASONED_BY_DEFAULT')
    return {'task_kind': task_kind,
            'length': length,
            'quality_floor': ['intent', 'relevant evidence', 'comparison', 'independent view',
                              'necessary dissent', 'proportionate uncertainty', 'explicit correction'],
            'consider_before_conclusion': list(ROLES) if analytic else [],
            'roles': deepcopy(ROLES) if analytic else {},
            'fixed_word_minimum': None, 'fixed_option_count': None,
            'weights': None, 'thresholds': None,
            'display': 'MATERIAL_EFFECTS_IN_REASONED_PROSE',
            'requires_parallel_models': False, 'live_model_execution_claimed': False,
            'brief_scope': 'CURRENT_TURN_ONLY',
            'relationship_context': context,
            'semantic_acceptance': 'REQUIRES_ACTUAL_MODEL_RESPONSE_REVIEW'}


def summarize_magi(assessments):
    """Retain host-supplied perspective summaries without voting facts away.

    Input is an explicit concise decision record, not hidden chain of thought.
    The host supplies the assessments; this is not an NLP inference engine.
    """
    if not isinstance(assessments, dict) or set(assessments) != set(ROLES):
        raise ValueError('exactly the three distinct perspectives are required')
    retained = {}
    material = []
    for role, item in assessments.items():
        if not isinstance(item, dict) or set(item) != {'summary', 'material', 'evidence_refs', 'dissent'}:
            raise ValueError('typed concise assessment required')
        if (not isinstance(item['summary'], str) or not item['summary'].strip()
                or type(item['material']) is not bool or type(item['dissent']) is not bool
                or not isinstance(item['evidence_refs'], list)
                or any(not isinstance(x, str) or not x for x in item['evidence_refs'])):
            raise ValueError('invalid assessment fields')
        retained[role] = deepcopy(item)
        if item['material'] or item['dissent']:
            material.append({'role': role, **deepcopy(item)})
    return {'assessments': retained, 'material_explanations': material,
            'decision_by_majority': False, 'evidence_overridden_by_vote': False,
            'weights': None, 'thresholds': None, 'candidate_count_limit': None,
            'independent_models_executed': False, 'model_quality_tested': False}
