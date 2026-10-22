#!/usr/bin/env python3
"""Executable reference for the PEOS rev0.311 universal user-turn gate.

This module is deliberately host-neutral.  It proves the dispatcher contract
with deterministic adapters, but it cannot install a hook in the ChatGPT host
or promote static/integration evidence to live acceptance.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable
from zoneinfo import ZoneInfo

BUILD_ID = "PEOS-REV0.311-CANDIDATE-20260913-171938-JST"
REFERENCE_PROVIDER = 'Python datetime.now(ZoneInfo("Asia/Tokyo"))'
REFERENCE_PATH = 'datetime.now(ZoneInfo("Asia/Tokyo"))'
ALL_ROUTES = (
    "BOOT", "NORMAL_CONVERSATION", "CASUAL_CHAT", "SHORT_ACK", "FILE",
    "IMAGE", "WEB_TOOL", "AUTOMATION", "LOG_GENERATION", "SPECIFICATION",
    "PACKAGE_ZIP", "DEVICE", "TRAVEL",
)
TRANSITION_ORDER = (
    "LOCKED", "CAPTURE_ATTEMPTED", "CAPTURED", "PERSIST_ATTEMPTED",
    "PERSISTED", "READBACK_VERIFIED", "WORK_PERMITTED",
)


class GateError(RuntimeError):
    """Typed fail-closed transition."""


@dataclass(frozen=True)
class Capture:
    value_jst: str
    provider_id: str
    implementation_path: str
    path_class: str
    trusted: bool
    actual_execution_evidence: bool
    attempts: int = 1


class ReferencePythonProvider:
    provider_id = REFERENCE_PROVIDER
    implementation_path = REFERENCE_PATH
    trusted = True

    def __init__(self, observed: datetime | None = None, available: bool = True):
        self.observed = observed
        self.available = available

    def capture(self) -> Capture:
        if not self.available:
            raise GateError("TIME_CAPTURE_UNAVAILABLE")
        observed = self.observed or datetime.now(ZoneInfo("Asia/Tokyo"))
        if observed.tzinfo is None:
            raise GateError("TIME_CAPTURE_UNAVAILABLE")
        value = observed.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S JST")
        return Capture(value, self.provider_id, self.implementation_path,
                       "REFERENCE_PYTHON_PATH", True, True)


class TrustedAlternateProvider:
    """Fixture adapter for a registered trusted non-reference clock."""

    def __init__(self, value_jst: str, provider_id: str = "trusted.fixture.clock",
                 implementation_path: str = "fixture://trusted-current-time"):
        self.value_jst = value_jst
        self.provider_id = provider_id
        self.implementation_path = implementation_path
        self.trusted = True

    def capture(self) -> Capture:
        return Capture(self.value_jst, self.provider_id, self.implementation_path,
                       "TRUSTED_PATH_VARIANCE", True, True)


class UntrustedProvider(TrustedAlternateProvider):
    trusted = False

    def capture(self) -> Capture:
        item = super().capture()
        return Capture(item.value_jst, item.provider_id, item.implementation_path,
                       "UNTRUSTED", False, item.actual_execution_evidence)


class MemoryVersionedLedger:
    """Deterministic fixture store; never evidence of live host persistence."""

    def __init__(self, records: list[dict[str, Any]] | None = None, version: int = 0,
                 available: bool = True, corrupt_readback: bool = False):
        self.records = copy.deepcopy(records or [])
        self.version = version
        self.available = available
        self.corrupt_readback = corrupt_readback

    @property
    def locator(self) -> str:
        return "fixture://versioned-turn-ledger"

    def append_and_readback(self, record: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if not self.available:
            raise GateError("LEDGER_PERSIST_FAILED")
        before = copy.deepcopy(self.records)
        version_before = self.version
        candidate = before + [copy.deepcopy(record)]
        self.records = candidate
        self.version += 1
        readback = copy.deepcopy(self.records)
        if self.corrupt_readback:
            readback[-1]["user_turn_observed_at_jst"] = "CORRUPTED"
        evidence = {
            "store_locator": self.locator,
            "version_before": version_before,
            "version_after": self.version,
            "ledger_seq": record["ledger_seq"],
            "postwrite_readback_verified": readback == candidate,
            "prior_records_preserved": readback[:len(before)] == before,
        }
        return readback, evidence


def locked_state(turn_id: str, session_id: str, route: str) -> dict[str, Any]:
    if route not in ALL_ROUTES:
        raise GateError(f"UNREGISTERED_ROUTE:{route}")
    return {
        "schema_version": "rev0.311",
        "build_id": BUILD_ID,
        "turn_id": turn_id,
        "session_id": session_id,
        "route": route,
        "gate_state": "LOCKED",
        "work_permitted": False,
        "success_claim_authorized": False,
        "time_capture": {
            "success": False, "value_jst": None, "provider_id": None,
            "implementation_path": None, "path_class": "UNAVAILABLE",
            "trusted": False, "actual_execution_evidence": False,
            "attempts": 0, "peos_executable_action_index": 0,
        },
        "persistence": {
            "attempted": False, "success": False,
            "postwrite_readback_verified": False,
            "same_timestamp_verified": False, "store_locator": None,
            "version_before": None, "version_after": None, "ledger_seq": None,
        },
        "failure_classes": [],
        "variance_classes": [],
        "state_history": ["LOCKED"],
        "work_callback_invoked": False,
    }


def _transition(state: dict[str, Any], name: str) -> None:
    state["gate_state"] = name
    state["state_history"].append(name)


def _fail(state: dict[str, Any], *classes: str) -> dict[str, Any]:
    for item in classes:
        if item not in state["failure_classes"]:
            state["failure_classes"].append(item)
    state["gate_state"] = "DEGRADED"
    state["state_history"].append("DEGRADED")
    state["work_permitted"] = False
    state["success_claim_authorized"] = False
    return state


class UniversalTurnGate:
    """The only conforming root dispatcher for every eligible USER turn."""

    def __init__(self, ledger: MemoryVersionedLedger, session_id: str = "FIXTURE-SESSION"):
        self.ledger = ledger
        self.session_id = session_id

    def dispatch(
        self,
        route: str,
        turn_id: str,
        work: Callable[[dict[str, Any]], Any],
        reference_provider: Any,
        alternate_provider: Any | None = None,
        pre_dispatch_peos_actions: int = 0,
    ) -> tuple[dict[str, Any], Any | None]:
        state = locked_state(turn_id, self.session_id, route)
        if pre_dispatch_peos_actions:
            return _fail(state, "PRE_DISPATCH_GATE_BYPASS"), None

        # The gate-owned capture procedure is PEOS executable action index 1.
        _transition(state, "CAPTURE_ATTEMPTED")
        # Capability classification selects one adapter before capture. A
        # failed attempt may retry the same adapter internally; it may not
        # drift to another provider after failure.
        if getattr(reference_provider, "available", True) is False:
            selected_provider = alternate_provider
        else:
            selected_provider = reference_provider
        attempts = 1
        if selected_provider is None:
            state["time_capture"]["attempts"] = attempts
            state["time_capture"]["peos_executable_action_index"] = 1
            return _fail(state, "TIME_CAPTURE_UNAVAILABLE"), None
        try:
            capture = selected_provider.capture()
        except Exception:
            attempts += 1
            try:
                capture = selected_provider.capture()
            except Exception:
                state["time_capture"]["attempts"] = attempts
                state["time_capture"]["peos_executable_action_index"] = 1
                return _fail(state, "TIME_CAPTURE_UNAVAILABLE"), None

        capture = Capture(
            capture.value_jst, capture.provider_id, capture.implementation_path,
            capture.path_class, capture.trusted, capture.actual_execution_evidence,
            attempts,
        )
        state["time_capture"] = {
            "success": True, "value_jst": capture.value_jst,
            "provider_id": capture.provider_id,
            "implementation_path": capture.implementation_path,
            "path_class": capture.path_class, "trusted": capture.trusted,
            "actual_execution_evidence": capture.actual_execution_evidence,
            "attempts": capture.attempts, "peos_executable_action_index": 1,
        }
        if not capture.trusted or not capture.actual_execution_evidence:
            return _fail(state, "TIME_CAPTURE_UNAVAILABLE"), None
        if capture.path_class == "TRUSTED_PATH_VARIANCE":
            state["variance_classes"].append("TIME_CAPTURE_PATH_VARIANCE")
        _transition(state, "CAPTURED")

        immutable_timestamp = capture.value_jst
        seq = len(self.ledger.records) + 1
        record = {
            "record_type": "TURN_TIME_RECORD",
            "schema_version": "rev0.311",
            "ledger_seq": seq,
            "turn_id": turn_id,
            "session_id": self.session_id,
            "route": route,
            "user_turn_observed_at_jst": immutable_timestamp,
            "visible_timestamp": immutable_timestamp,
            "provider": capture.provider_id,
            "implementation_path": capture.implementation_path,
            "capture_path_class": capture.path_class,
            "capture_attempts": capture.attempts,
            "successful_peos_executable_action_index": 1,
            "runtime_order_valid": True,
            "persistence_status": "PERSISTED_VERIFIED",
            "canonical_for_log_reconstruction": True,
        }
        state["persistence"]["attempted"] = True
        _transition(state, "PERSIST_ATTEMPTED")
        try:
            readback, evidence = self.ledger.append_and_readback(record)
        except Exception:
            return _fail(state, "LEDGER_PERSIST_FAILED", "TIME_CAPTURED_BUT_NOT_PERSISTED"), None

        state["persistence"].update(evidence)
        state["persistence"]["success"] = True
        _transition(state, "PERSISTED")
        same = bool(readback and readback[-1].get("user_turn_observed_at_jst") == immutable_timestamp)
        state["persistence"]["same_timestamp_verified"] = same
        if not evidence["postwrite_readback_verified"] or not evidence["prior_records_preserved"] or not same:
            state["persistence"]["success"] = False
            return _fail(state, "LEDGER_PERSIST_FAILED"), None
        _transition(state, "READBACK_VERIFIED")

        state["work_permitted"] = True
        state["success_claim_authorized"] = True
        _transition(state, "WORK_PERMITTED")
        state["work_callback_invoked"] = True
        result = work(copy.deepcopy(state))
        return state, result


def canonical_log_time(record: dict[str, Any]) -> str | None:
    if (record.get("runtime_order_valid") is True
            and record.get("persistence_status") == "PERSISTED_VERIFIED"
            and record.get("canonical_for_log_reconstruction") is True):
        return record.get("user_turn_observed_at_jst")
    return None


def audit_coverage(turns: Iterable[dict[str, Any]], ledger: Iterable[dict[str, Any]]) -> dict[str, Any]:
    eligible = [item for item in turns if item.get("eligible") is True]
    canonical_ids = {
        item.get("turn_id") for item in ledger
        if item.get("canonical_for_log_reconstruction") is True
    }
    excluded = [
        item for item in eligible
        if item.get("runtime_order_valid") is False
        or item.get("capture_status") == "TIME_CAPTURE_UNAVAILABLE"
        or item.get("persistence_status") == "PERSISTENCE_FAILED"
    ]
    excluded_ids = {item.get("turn_id") for item in excluded}
    missing = [item for item in eligible if item.get("turn_id") not in canonical_ids | excluded_ids]
    result = {
        "ELIGIBLE_USER_TURN_COUNT": len(eligible),
        "CANONICAL_LEDGER_ENTRY_COUNT": len(canonical_ids),
        "EXCLUDED_FAILED_TURN_COUNT": len(excluded),
        "MISSING_LEDGER_ENTRY_COUNT": len(missing),
        "COVERAGE_STATUS": "PASS" if not missing and len(eligible) == len(canonical_ids) + len(excluded) else "FAIL",
        "EXCLUDED_TURNS": [item.get("turn_id") for item in excluded],
        "MISSING_TURNS": [item.get("turn_id") for item in missing],
    }
    return result


def user_operation_error_authorized(evidence: dict[str, Any]) -> bool:
    return all(bool(evidence.get(key)) for key in (
        "specific_user_action", "defined_different_action_contract", "direct_causal_path",
    ))


def success_narration_authorized(state: dict[str, Any]) -> bool:
    return bool(
        state.get("gate_state") == "WORK_PERMITTED"
        and state.get("work_permitted") is True
        and state.get("success_claim_authorized") is True
        and not state.get("failure_classes")
    )
