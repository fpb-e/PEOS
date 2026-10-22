#!/usr/bin/env python3
"""Executable rev0.312 reference for typed continuity and truth guards.

This is deterministic supporting code. It does not diagnose, identify anonymous
authors, perform a live stock check, bind a host hook, or accept the candidate.
"""

from __future__ import annotations

import copy
import json
import re
import zipfile
from pathlib import Path
from typing import Any

BUILD_ID = "PEOS-REV0.312-CANDIDATE-20261007-105524-JST"
STATUS_CLASSES = {
    "CURRENT", "UNRESOLVED", "SUPERSEDED_CORRECTION",
}
SOURCE_CLASSES = {
    "FATHER_REPORTED", "CLINICIAN_CONFIRMED_VIA_FATHER",
    "DOCUMENT_OR_IMAGE_DERIVED", "ASSISTANT_INFERENCE", "UNRESOLVED",
}
COMPATIBILITY_KEYS = {
    "voltage", "chemistry", "connector", "bms", "physical_fit",
    "manufacturer_confirmation",
}
SESSION_LOG_RE = re.compile(r"^PEOS_father_session_log_\d{4}_\d{2}_\d{2}_\d{6}\.txt$")
DIRECTIVE_RE = re.compile(r"^PEOS_next_spec_directive_\d{4}_\d{2}_\d{2}_.+\.txt$")


class ContinuityError(RuntimeError):
    pass


def load_bootstrap(root: Path) -> dict[str, Any]:
    path = root / "runtime/PEOS_CONTINUITY_TRUTH_BOOTSTRAP.json"
    return json.loads(path.read_text(encoding="utf-8"))


def validate_authority(state: dict[str, Any]) -> list[str]:
    authority = state.get("authority", {})
    errors: list[str] = []
    if authority.get("project_current") != "rev0.311":
        errors.append("PROJECT_CURRENT_ROLLBACK_OR_DRIFT")
    if authority.get("accepted_baseline") != "PEOS_GITHUB_PACKAGE_rev0.310.zip":
        errors.append("ACCEPTED_BASELINE_DRIFT")
    if authority.get("historical_can_rollback") is not False:
        errors.append("HISTORICAL_ROLLBACK_ENABLED")
    return errors


def validate_fact_graph(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    incidents = state.get("incidents", {})
    gero = incidents.get("下呂急変")
    if not isinstance(gero, dict) or gero.get("fixed_label") != "下呂急変":
        return ["GERO_FIXED_LABEL_MISSING"]
    facts = gero.get("facts", [])
    by_id = {item.get("fact_id"): item for item in facts if isinstance(item, dict)}
    if len(by_id) != len(facts):
        errors.append("FACT_ID_DUPLICATE")
    for item in facts:
        if item.get("source_class") not in SOURCE_CLASSES:
            errors.append(f"SOURCE_CLASS_INVALID:{item.get('fact_id')}")
        if item.get("status_class") not in STATUS_CLASSES:
            errors.append(f"STATUS_CLASS_INVALID:{item.get('fact_id')}")
        if item.get("status_class") == "SUPERSEDED_CORRECTION" and item.get("current") is not False:
            errors.append(f"SUPERSEDED_STILL_CURRENT:{item.get('fact_id')}")
        if item.get("status_class") in {"CURRENT", "UNRESOLVED"} and item.get("current") is not True:
            errors.append(f"CURRENT_FLAG_MISMATCH:{item.get('fact_id')}")
        prior = item.get("supersedes")
        if prior is not None:
            old = by_id.get(prior)
            if old is None or old.get("status_class") != "SUPERSEDED_CORRECTION" or old.get("current") is not False:
                errors.append(f"SUPERSESSION_EDGE_INVALID:{item.get('fact_id')}")
    expected = {
        "cardiac_arrest": ("CONFIRMED", "CLINICIAN_CONFIRMED_VIA_FATHER"),
        "intubation": ("FAILED_AFTER_REPEATED_ATTEMPTS_WITH_ORAL_NASAL_BLEEDING_REPORTED", "FATHER_REPORTED"),
        "bathing": ("APPARENTLY_DID_NOT_BATHE", "FATHER_REPORTED"),
    }
    for fact_id, (value, source) in expected.items():
        item = by_id.get(fact_id, {})
        if item.get("value") != value or item.get("source_class") != source or item.get("current") is not True:
            errors.append(f"CURRENT_CORRECTION_INVALID:{fact_id}")
    for fact_id in ("initial_arrest_rhythm", "rosc_time"):
        item = by_id.get(fact_id, {})
        if item.get("status_class") != "UNRESOLVED" or item.get("value") is not None:
            errors.append(f"UNRESOLVED_PROMOTED:{fact_id}")
    return errors


def apply_correction(
    state: dict[str, Any], incident_key: str, old_fact_id: str,
    new_fact: dict[str, Any],
) -> dict[str, Any]:
    result = copy.deepcopy(state)
    facts = result["incidents"][incident_key]["facts"]
    old = next((item for item in facts if item.get("fact_id") == old_fact_id), None)
    if old is None:
        raise ContinuityError("OLD_FACT_NOT_FOUND")
    old["current"] = False
    old["status_class"] = "SUPERSEDED_CORRECTION"
    candidate = copy.deepcopy(new_fact)
    candidate["current"] = True
    candidate["status_class"] = "CURRENT"
    candidate["supersedes"] = old_fact_id
    if candidate.get("source_class") not in SOURCE_CLASSES:
        raise ContinuityError("SOURCE_CLASS_INVALID")
    facts.append(candidate)
    return result


def medical_claim_authorized(source_class: str, claim_kind: str) -> bool:
    if claim_kind in {"FINAL_DIAGNOSIS", "EXACT_RESUSCITATION_SEQUENCE", "EXACT_LUNG_PATHOLOGY"}:
        return source_class in {"CLINICIAN_CONFIRMED_VIA_FATHER", "DOCUMENT_OR_IMAGE_DERIVED"}
    return source_class in SOURCE_CLASSES


def interpret_billing(categories: list[str]) -> dict[str, Any]:
    return {
        "supported_treatment_categories": list(categories),
        "exact_bedside_chronology": None,
        "exact_intubation_method": None,
        "chronology_claim_authorized": False,
        "evidence_class": "BILLING_RECORD_CATEGORY_ONLY",
    }


def classify_anonymous_cluster(posts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "domain": "NEETMAN_EVIDENCE",
        "posts": [dict(item, authorship="UNKNOWN") for item in posts],
        "named_authorship_authorized": False,
        "father_vocabulary_eligible": False,
        "medical_incident_link": None,
    }


def commerce_state(
    *, product_exists: bool, listing_exists: bool,
    live_stock: str | None, current_price_confirmed: bool = False,
) -> dict[str, Any]:
    stock_map = {"in_stock": "IN_STOCK_CONFIRMED", "out_of_stock": "OUT_OF_STOCK_CONFIRMED"}
    stock_state = stock_map.get(live_stock, "STOCK_UNKNOWN")
    return {
        "product_state": "PRODUCT_EXISTS" if product_exists else "PRODUCT_UNKNOWN",
        "listing_state": "LISTING_EXISTS" if listing_exists else "LISTING_UNKNOWN",
        "price_state": "CURRENT_PRICE_CONFIRMED" if current_price_confirmed else "CURRENT_PRICE_UNKNOWN",
        "stock_state": stock_state,
        "buyable_now_claim_authorized": stock_state == "IN_STOCK_CONFIRMED",
    }


def compatibility_state(evidence: dict[str, bool]) -> str:
    if set(evidence) != COMPATIBILITY_KEYS:
        return "COMPATIBILITY_UNKNOWN"
    return "COMPATIBILITY_CONFIRMED" if all(evidence.values()) else "COMPATIBILITY_UNKNOWN"


def inspect_session_handoff(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        names = archive.namelist()
        if bad is not None:
            raise ContinuityError(f"ZIP_CRC_FAILED:{bad}")
        if len(names) != 2 or any("/" in name or "\\" in name for name in names):
            raise ContinuityError("SESSION_HANDOFF_ROOT_TOPOLOGY_INVALID")
        logs = [name for name in names if SESSION_LOG_RE.fullmatch(name)]
        directives = [name for name in names if DIRECTIVE_RE.fullmatch(name)]
        if len(logs) != 1 or len(directives) != 1:
            raise ContinuityError("SESSION_HANDOFF_FILENAME_PATTERN_INVALID")
        log_text = archive.read(logs[0]).decode("utf-8")
        directive_text = archive.read(directives[0]).decode("utf-8")
        if not log_text.rstrip().endswith("END OF SESSION LOG"):
            raise ContinuityError("SESSION_LOG_TERMINATOR_MISSING")
        if not directive_text.rstrip().endswith("END OF DIRECTIVE"):
            raise ContinuityError("DIRECTIVE_TERMINATOR_MISSING")
    return {
        "artifact_class": "FATHER_SESSION_NEXT_SPEC_HANDOFF",
        "crc": "PASS",
        "root_file_count": 2,
        "log": logs[0],
        "directive": directives[0],
        "inspection_receipt": True,
    }


def resolve_fixture(artifact_class: str) -> dict[str, Any]:
    mapping = {
        "FATHER_SESSION_NEXT_SPEC_HANDOFF": {
            "fixture": "PEOS_father_session_bundle_2026_09_13_171409_for_next_spec.zip",
            "two_txt_only": True,
        },
        "GITHUB_PACKAGE": {
            "fixture": "PEOS_GITHUB_PACKAGE_rev0.311.zip",
            "two_txt_only": False,
        },
        "ATTACHMENT_BEARING_LOG_PIPELINE": {
            "fixture": "PEOS_GITHUB_PACKAGE_rev0.310.zip",
            "two_txt_only": False,
        },
    }
    if artifact_class not in mapping:
        raise ContinuityError("ARTIFACT_CLASS_UNREGISTERED")
    return {"artifact_class": artifact_class, **mapping[artifact_class]}


def mobility_state_valid(value: dict[str, Any]) -> bool:
    return (
        value.get("certificate_status") == "NOT_OBTAINED_FIXED_PERIOD_INSUFFICIENT"
        and value.get("hg_ewc9000") == "PURCHASED_INTERIM_POWERED_WHEELCHAIR"
        and value.get("amazon_ovoggpan_return") == "UNCONFIRMED"
        and value.get("official_spare_battery") == "OUT_OF_STOCK_WHEN_CHECKED"
        and value.get("spare_battery_acquired") is False
    )
