#!/usr/bin/env python3
"""Executable rev0.310 binding state and per-turn transaction reference.

This module is host-neutral. A host adapter must supply authoritative versioned
persistent-store read/write evidence; reading package bytes never makes READY.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "validator"))
from peos_turn_time_ledger import merge_records, verify_preservation  # noqa: E402
from time_ledger_validator import validate_records  # noqa: E402

PROVIDER = 'datetime.now(ZoneInfo("Asia/Tokyo"))'
PREFIX_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} JST)\]")
EVIDENCE_KEYS = [
    "FILE_VISIBLE", "CONTENT_READ", "SOURCE_SYNC", "PROJECT_CANON_CONTEXT_SHARED",
    "CONTINUITY_MEMORY_SHARED", "RUNTIME_GUARDS_BOUND", "TIME_LEDGER_LOCATOR_RESOLVED",
    "TIME_LEDGER_SCHEMA_VALID", "PERSISTENCE_PATH_VERIFIED", "PER_TURN_HOOK_BOUND",
    "DISPLAY_RENDERER_BOUND", "PRECOMMIT_AUDIT_BOUND", "CORRECTION_CONSTRAINTS_BOUND",
    "GLOBAL_PEOS_RESPONSE_CORE_ACTIVE", "BOOT_ASSETS_READY", "TIME_LEDGER_RUNTIME_READY",
]
TIME_READY_KEYS = [
    "TIME_LEDGER_LOCATOR_RESOLVED", "TIME_LEDGER_SCHEMA_VALID", "PERSISTENCE_PATH_VERIFIED",
    "PER_TURN_HOOK_BOUND", "DISPLAY_RENDERER_BOUND",
]
READY_KEYS = [
    "RUNTIME_GUARDS_BOUND", "BOOT_ASSETS_READY", "PERSISTENCE_PATH_VERIFIED",
    "PER_TURN_HOOK_BOUND", "DISPLAY_RENDERER_BOUND", "PRECOMMIT_AUDIT_BOUND",
    "CORRECTION_CONSTRAINTS_BOUND", "GLOBAL_PEOS_RESPONSE_CORE_ACTIVE",
    "TIME_LEDGER_RUNTIME_READY",
]
DELIVERY_MEANING = {
    "recovery_scope", "declared_gaps", "key_spec_changes",
    "reinjection_significance", "authority_boundary", "runtime_faults",
}


class BindingError(RuntimeError):
    pass


def initial_state() -> dict[str, Any]:
    return {
        "schema_version": "rev0.310",
        "build_id": "PEOS-REV0.310-CANDIDATE-20260904-042814-JST",
        "authority": {
            "live_current": "rev0.309",
            "accepted_baseline": "PEOS_GITHUB_PACKAGE_rev0.308.zip",
            "historical_snapshots_can_rollback": False,
        },
        "runtime_status": "UNINITIALIZED",
        "evidence": {key: False for key in EVIDENCE_KEYS},
        "persistence_evidence": None,
        "failure_classes": [],
        "runtime_ready_claim_authorized": False,
        "last_verified_ledger_seq": None,
        "last_transition": None,
    }


def persistence_evidence_valid(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    before, after = value.get("version_before"), value.get("version_after")
    return (
        isinstance(before, int)
        and isinstance(after, int)
        and after == before + 1
        and isinstance(value.get("ledger_seq"), int)
        and value.get("postwrite_readback_verified") is True
        and value.get("prior_records_preserved") is True
        and bool(value.get("store_locator"))
    )


def transition_binding(
    state: dict[str, Any],
    evidence_update: dict[str, bool] | None = None,
    persistence_evidence: dict[str, Any] | None = None,
    failures: Iterable[str] = (),
    transition: str | None = None,
) -> dict[str, Any]:
    result = copy.deepcopy(state)
    evidence = result["evidence"]
    for key, value in (evidence_update or {}).items():
        if key not in EVIDENCE_KEYS or not isinstance(value, bool):
            raise BindingError(f"invalid evidence update: {key}")
        evidence[key] = value
    if persistence_evidence is not None:
        result["persistence_evidence"] = copy.deepcopy(persistence_evidence)
        evidence["PERSISTENCE_PATH_VERIFIED"] = persistence_evidence_valid(persistence_evidence)
        if evidence["PERSISTENCE_PATH_VERIFIED"]:
            result["last_verified_ledger_seq"] = persistence_evidence["ledger_seq"]
        else:
            result["failure_classes"].append("PERSISTENCE_EVIDENCE_INVALID")
    for failure in failures:
        if failure not in result["failure_classes"]:
            result["failure_classes"].append(failure)
    evidence["TIME_LEDGER_RUNTIME_READY"] = all(evidence[key] for key in TIME_READY_KEYS)
    if result["failure_classes"]:
        status = "DEGRADED"
    elif all(evidence[key] for key in READY_KEYS):
        status = "READY"
    elif evidence["SOURCE_SYNC"] or evidence["CONTENT_READ"]:
        status = "BINDING_IN_PROGRESS" if evidence["RUNTIME_GUARDS_BOUND"] else "SOURCE_ONLY"
    else:
        status = "UNINITIALIZED"
    result["runtime_status"] = status
    result["runtime_ready_claim_authorized"] = status == "READY"
    result["last_transition"] = transition
    return result


def validate_binding_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence = state.get("evidence", {})
    missing = [key for key in EVIDENCE_KEYS if not isinstance(evidence.get(key), bool)]
    if missing:
        errors.append("MISSING_OR_INVALID_EVIDENCE:" + ",".join(missing))
        return errors
    computed_time = all(evidence[key] for key in TIME_READY_KEYS)
    if evidence["TIME_LEDGER_RUNTIME_READY"] != computed_time:
        errors.append("TIME_LEDGER_RUNTIME_READY_DERIVATION_MISMATCH")
    ready = all(evidence[key] for key in READY_KEYS) and not state.get("failure_classes")
    if (state.get("runtime_status") == "READY") != ready:
        errors.append("RUNTIME_READY_DERIVATION_MISMATCH")
    if state.get("runtime_ready_claim_authorized") != ready:
        errors.append("RUNTIME_READY_CLAIM_MISMATCH")
    if evidence["SOURCE_SYNC"] and not evidence["RUNTIME_GUARDS_BOUND"] and ready:
        errors.append("SOURCE_SYNC_FALSE_PROMOTION")
    if evidence["PERSISTENCE_PATH_VERIFIED"] and not persistence_evidence_valid(state.get("persistence_evidence")):
        errors.append("PERSISTENCE_PATH_WITHOUT_VERSIONED_EVIDENCE")
    authority = state.get("authority", {})
    if authority.get("live_current") != "rev0.309" or authority.get("historical_snapshots_can_rollback") is not False:
        errors.append("AUTHORITY_ROLLBACK_OR_DRIFT")
    return errors


@dataclass(frozen=True)
class Receipt:
    value: str
    provider: str = PROVIDER
    capture_attempts: int = 1
    executable_action_index: int = 1

    @property
    def prefix(self) -> str:
        return f"[{self.value}]"


def capture_receipt(now: datetime | None = None) -> Receipt:
    observed = now or datetime.now(ZoneInfo("Asia/Tokyo"))
    if observed.tzinfo is None:
        raise BindingError("timezone-aware datetime required")
    return Receipt(observed.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S JST"))


def build_record(
    receipt: Receipt,
    turn_id: str,
    idempotency_key: str,
    coordinate: str = "FATHER",
    direct_append_status: str = "NOT_APPLICABLE_PERSISTENT_STORE",
) -> dict[str, Any]:
    return {
        "record_type": "TURN_TIME_RECORD",
        "schema_version": "rev0.308",
        "ledger_seq": 0,
        "idempotency_key": idempotency_key,
        "turn_id": turn_id,
        "user_turn_observed_at_jst": receipt.value,
        "provider": receipt.provider,
        "capture_attempts": receipt.capture_attempts,
        "successful_executable_action_index": receipt.executable_action_index,
        "pre_receipt_semantic_output": False,
        "pre_receipt_action_class": "NONE",
        "intervening_semantic_action_before_success": "NONE",
        "runtime_order_valid": True,
        "canonical_for_log_reconstruction": True,
        "capture_status": "CAPTURE_SUCCESS",
        "direct_append_status": direct_append_status,
        "persistent_store_status": "WRITE_SUCCESS",
        "persistence_status": "PERSISTED_VERIFIED",
        "persistence_verified": True,
        "coordinate": coordinate,
        "visible_timestamp": receipt.value,
        "source_class": "LIVE_RUNTIME_TRANSACTION",
        "fixture": False,
    }


class MemoryVersionedStore:
    """Deterministic integration-test adapter; never evidence of live host persistence."""

    def __init__(self, records: list[dict[str, Any]] | None = None, version: int = 0, available: bool = True):
        self.records = copy.deepcopy(records or [])
        self.version = version
        self.available = available

    def write_and_readback(self, expected_version: int, candidate: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if not self.available:
            raise BindingError("PERSISTENCE_UNAVAILABLE")
        if expected_version != self.version:
            raise BindingError("PERSISTENCE_VERSION_CONFLICT")
        before = copy.deepcopy(self.records)
        self.records = copy.deepcopy(candidate)
        self.version += 1
        after = copy.deepcopy(self.records)
        return after, {
            "store_locator": "fixture://versioned-persistent-store",
            "version_before": expected_version,
            "version_after": self.version,
            "ledger_seq": after[-1]["ledger_seq"],
            "postwrite_readback_verified": after == candidate,
            "prior_records_preserved": after[: len(before)] == before,
        }


def commit_turn(
    state: dict[str, Any],
    existing_records: list[dict[str, Any]],
    store: MemoryVersionedStore,
    receipt: Receipt,
    turn_id: str,
    idempotency_key: str,
    direct_append_status: str = "NOT_APPLICABLE_PERSISTENT_STORE",
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    if state.get("runtime_status") != "READY" or not state.get("runtime_ready_claim_authorized"):
        raise BindingError("TIME_LEDGER_RUNTIME_NOT_READY")
    record = build_record(receipt, turn_id, idempotency_key, direct_append_status=direct_append_status)
    candidate, merge_status = merge_records(existing_records, record)
    try:
        readback, evidence = store.write_and_readback(store.version, candidate)
        verify_preservation(existing_records, readback, idempotency_key)
        if validate_records(readback):
            raise BindingError("POSTWRITE_SCHEMA_VALIDATION_FAILED")
        if not persistence_evidence_valid(evidence):
            raise BindingError("POSTWRITE_EVIDENCE_INVALID")
        next_state = transition_binding(state, persistence_evidence=evidence, transition="TURN_PERSISTED_VERIFIED")
        return next_state, readback, {"merge_status": merge_status, **evidence}
    except Exception as exc:
        failed = transition_binding(
            state,
            evidence_update={"PERSISTENCE_PATH_VERIFIED": False},
            failures=[str(exc)],
            transition="PERSISTENCE_FAIL_CLOSED",
        )
        return failed, existing_records, {
            "capture_status": "CAPTURE_SUCCESS",
            "persistence_status": "PERSISTENCE_FAILED",
            "canonical_for_log_reconstruction": False,
            "failure_class": str(exc),
        }


def precommit_audit(
    text: str,
    receipt: Receipt,
    state: dict[str, Any],
    corrections: list[dict[str, Any]] | None = None,
    context_requires_depth: bool = False,
    delivery_meaning: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    match = PREFIX_RE.match(text)
    if not match:
        errors.append("EXACT_TIMESTAMP_PREFIX_MISSING_OR_NOT_FIRST")
    elif match.group(1) != receipt.value:
        errors.append("RECEIPT_DISPLAY_VALUE_FORK")
    if state.get("runtime_status") != "READY" or not state.get("runtime_ready_claim_authorized"):
        errors.append("RUNTIME_NOT_READY")
    if not state.get("evidence", {}).get("GLOBAL_PEOS_RESPONSE_CORE_ACTIVE"):
        errors.append("GLOBAL_PEOS_RESPONSE_CORE_NOT_ACTIVE")
    if any(item.get("id") == "EXACT_TIMESTAMP_PREFIX" and item.get("remaining_turns", 0) > 0 for item in (corrections or [])):
        if not match or match.group(1) != receipt.value:
            errors.append("FATHER_CORRECTION_STICKINESS_FAIL")
    claims_ready = any(token in text for token in ("RUNTIME_READY", "起動完了", "同期完了", "再ロード完了"))
    if claims_ready and not state.get("evidence", {}).get("PERSISTENCE_PATH_VERIFIED"):
        errors.append("FALSE_RUNTIME_READY_CLAIM")
    if text.startswith("[clock widget") or ("[clock widget rendered]" in text and not match):
        errors.append("HOST_GENERIC_WIDGET_SUBSTITUTION")
    if context_requires_depth:
        supplied = delivery_meaning or set()
        missing = sorted(DELIVERY_MEANING - supplied)
        if missing:
            errors.append("RESPONSE_DENSITY_MEANING_MISSING:" + ",".join(missing))
    return sorted(set(errors))


def advance_corrections(corrections: list[dict[str, Any]], audit_errors: list[str]) -> list[dict[str, Any]]:
    if audit_errors:
        return copy.deepcopy(corrections)
    result = copy.deepcopy(corrections)
    for item in result:
        if item.get("remaining_turns", 0) > 0:
            item["remaining_turns"] -= 1
    return result


def canonical_log_time(record: dict[str, Any]) -> str | None:
    if (
        record.get("runtime_order_valid") is True
        and record.get("canonical_for_log_reconstruction") is True
        and record.get("persistence_status") == "PERSISTED_VERIFIED"
        and record.get("persistence_verified") is True
    ):
        return record.get("user_turn_observed_at_jst")
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    state_cmd = sub.add_parser("evaluate-state")
    state_cmd.add_argument("--state", type=Path, required=True)
    state_cmd.add_argument("--evidence", type=Path)
    state_cmd.add_argument("--persistence-evidence", type=Path)
    state_cmd.add_argument("--failure", action="append", default=[])
    state_cmd.add_argument("--output", type=Path)
    audit_cmd = sub.add_parser("precommit")
    audit_cmd.add_argument("--state", type=Path, required=True)
    audit_cmd.add_argument("--receipt", required=True)
    audit_cmd.add_argument("--text", type=Path, required=True)
    audit_cmd.add_argument("--context-requires-depth", action="store_true")
    audit_cmd.add_argument("--delivery-meaning", default="")
    args = parser.parse_args()

    if args.command == "evaluate-state":
        state = json.loads(args.state.read_text(encoding="utf-8"))
        update = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence else {}
        persistence = json.loads(args.persistence_evidence.read_text(encoding="utf-8")) if args.persistence_evidence else None
        result = transition_binding(state, update, persistence, args.failure, "CLI_EVALUATION")
        errors = validate_binding_state(result)
        rendered = json.dumps({"state": result, "validation_errors": errors}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0 if not errors else 1

    state = json.loads(args.state.read_text(encoding="utf-8"))
    receipt = Receipt(args.receipt)
    meaning = {item for item in args.delivery_meaning.split(",") if item}
    errors = precommit_audit(args.text.read_text(encoding="utf-8"), receipt, state, context_requires_depth=args.context_requires_depth, delivery_meaning=meaning)
    print(json.dumps({"result": "PASS" if not errors else "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
