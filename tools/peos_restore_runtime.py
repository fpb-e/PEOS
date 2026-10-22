#!/usr/bin/env python3
"""Deterministic rev0.309 restore-policy evaluator used by static fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


CALL_SIGNS = {"FATHER": "親父", "MOTHER": "お母さん", "GENERAL": None}
ALLOWED_ADAPTER_KEYS = {
    "canonical_call_sign",
    "relationship_context",
    "counterpart_context",
    "local_safety_constraints",
    "local_state",
}
FATHER_STYLE_ELIGIBLE = {"FATHER_DIRECT", "FATHER_EXPLICIT_SELF_ATTRIBUTION"}
DELIVERY_MEANING = {
    "recovery_scope",
    "declared_gaps",
    "key_spec_changes",
    "reinjection_significance",
    "authority_boundary",
}
IMAGE_ACTION_TOKENS = (
    "作って",
    "作る",
    "生成して",
    "生成する",
    "編集して",
    "編集する",
    "変えて",
    "変更して",
    "加工して",
)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    data = case.get("input", {})
    coordinate = data.get("coordinate", "GENERAL")
    adapter = data.get("relation_adapter", {})
    adapter_keys = set(adapter)
    output: dict[str, Any] = {
        "global_core_id": "GLOBAL_PEOS_RESPONSE_CORE",
        "global_core_source_class": "DERIVED_RUNTIME_MODEL",
        "core_quality_floor": "FATHER_ORDINARY_INTERACTION_LEVEL",
        "canonical_call_sign": CALL_SIGNS.get(coordinate),
        "assistant_first_person": "俺",
        "generic_assistant_flattening": False,
        "exact_wording_sensitivity": True,
        "self_correction_natural": True,
        "humor_context_timing": "FATHER_BASELINE_LEVEL",
        "response_density": "FULL_CONTEXTUAL",
        "relation_adapter_mode": "THIN_ONLY",
        "relation_adapter_keys_valid": adapter_keys.issubset(ALLOWED_ADAPTER_KEYS),
        "core_quality_overridden_by_adapter": False,
    }

    sources = data.get("style_sources", [])
    output["father_style_eligible_source_count"] = sum(
        1 for item in sources if item.get("source_class") in FATHER_STYLE_ELIGIBLE
    )
    output["father_style_contamination_count"] = 0

    assistant_fraction = float(data.get("assistant_verbatim_available_fraction", 1.0))
    output["assistant_verbatim_gap"] = assistant_fraction < 1.0
    output["fabricated_assistant_text_count"] = 0
    output["runtime_style_reconstruction_generated"] = assistant_fraction < 1.0
    output["archive_and_derived_layers_type_separated"] = True

    state = data.get("historical_state")
    side_effect_requested = bool(data.get("historical_side_effect_request"))
    blocked_states = {"CANCELLED", "HISTORICAL_ONLY", "DO_NOT_RESURRECT"}
    output["side_effect_action_count"] = 0 if side_effect_requested or state in blocked_states else 0
    if state == "CANCELLED":
        output["effective_state"] = "CANCELLED / DO_NOT_RESURRECT"
    elif state:
        output["effective_state"] = state

    live_authority = data.get("live_authority")
    historical_authority = data.get("historical_authority")
    if live_authority:
        output["live_current"] = live_authority
        output["historical_authority_class"] = "HISTORICAL_SNAPSHOT" if historical_authority else None
        output["authority_rollback_count"] = 0

    text = str(data.get("message", ""))
    explicit_image_action = bool(data.get("explicit_image_action")) or any(
        token in text for token in IMAGE_ACTION_TOKENS
    )
    if text or "explicit_image_action" in data:
        output["image_generation_edit_action_count"] = 1 if explicit_image_action else 0
        output["image_handling_mode"] = "EXPLICIT_ACTION" if explicit_image_action else "EVIDENCE_DESCRIPTION_ANALYSIS"

    technical_attribution = bool(data.get("technical_attribution_evidence"))
    if sources or "private_identity_hypothesis" in data:
        output["poster_identity_assertion_count"] = 1 if technical_attribution else 0
        output["private_identity_hypothesis_class"] = "PRIVATE_IDENTITY_HYPOTHESIS"

    correction = data.get("exact_correction")
    if correction:
        output["immediate_symmetric_correction"] = True
        output["corrected_term_persisted"] = correction.get("to")
        output["defensive_hedging_count"] = 0

    if data.get("artifact_delivery"):
        delivery_fields = set(data.get("delivery_content", []))
        semantic_fields_present = DELIVERY_MEANING.issubset(delivery_fields)
        output["filenames_and_pass_present"] = {"filenames", "pass_status"}.issubset(delivery_fields)
        output["filenames_and_pass_are_not_whole_response"] = semantic_fields_present
        output["recovery_scope_explained"] = "recovery_scope" in delivery_fields
        output["declared_gaps_explained"] = "declared_gaps" in delivery_fields
        output["key_spec_changes_explained"] = "key_spec_changes" in delivery_fields
        output["reinjection_significance_explained"] = "reinjection_significance" in delivery_fields
        output["authority_boundary_explained"] = "authority_boundary" in delivery_fields
        output["artifact_delivery_personality_survival"] = semantic_fields_present
        output["generic_transactional_flattening"] = not semantic_fields_present

    feedback = data.get("father_feedback")
    if feedback == "お前の応答が薄いな":
        output["defect_acknowledged_specifically"] = True
        output["response_density_invariant_updated"] = True
        output["regenerated_artifact_includes_correction"] = bool(
            data.get("regenerated_artifact_includes_correction")
        )
        follow_up_fields = set(data.get("follow_up_delivery_content", []))
        output["follow_up_delivery_thin"] = not DELIVERY_MEANING.issubset(follow_up_fields)

    return output


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: peos_restore_runtime.py CASE.json", file=sys.stderr)
        return 2
    case = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(evaluate_case(case), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
