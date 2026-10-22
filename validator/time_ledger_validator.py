#!/usr/bin/env python3
"""Validate PEOS rev0.308 turn-time ledger JSONL without external packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} JST$")
PROVIDER = 'datetime.now(ZoneInfo("Asia/Tokyo"))'
PLACEHOLDER_VALUES = {"", "UNAVAILABLE", "N/A", "UNKNOWN"}
REQUIRED = {
    "record_type",
    "schema_version",
    "ledger_seq",
    "idempotency_key",
    "turn_id",
    "user_turn_observed_at_jst",
    "provider",
    "capture_attempts",
    "successful_executable_action_index",
    "pre_receipt_semantic_output",
    "runtime_order_valid",
    "canonical_for_log_reconstruction",
    "capture_status",
    "direct_append_status",
    "persistent_store_status",
    "persistence_status",
    "persistence_verified",
}


def load_jsonl(path: Path, allow_bootstrap: bool = False) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_no}: invalid JSON: {exc}") from exc
        if item.get("record_type") == "PEOS_TURN_TIME_LEDGER_BOOTSTRAP":
            if not allow_bootstrap:
                raise ValueError(f"line {line_no}: bootstrap record not allowed")
            if item.get("private_live_records_included") is not False:
                raise ValueError(f"line {line_no}: bootstrap privacy flag invalid")
            continue
        records.append(item)
    return records


def validate_records(records: Iterable[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_seq: set[int] = set()
    seen_keys: set[str] = set()
    previous_seq = 0
    for index, record in enumerate(records, 1):
        label = f"record[{index}]"
        missing = sorted(REQUIRED - record.keys())
        if missing:
            errors.append(f"{label}: missing fields: {','.join(missing)}")
            continue
        if record.get("record_type") != "TURN_TIME_RECORD":
            errors.append(f"{label}: record_type")
        if record.get("schema_version") != "rev0.308":
            errors.append(f"{label}: schema_version")
        seq = record.get("ledger_seq")
        if not isinstance(seq, int) or seq < 1:
            errors.append(f"{label}: ledger_seq")
        else:
            if seq in seen_seq:
                errors.append(f"{label}: duplicate ledger_seq {seq}")
            if seq <= previous_seq:
                errors.append(f"{label}: ledger_seq not strictly increasing")
            seen_seq.add(seq)
            previous_seq = seq
        key = record.get("idempotency_key")
        if not isinstance(key, str) or len(key) < 8:
            errors.append(f"{label}: idempotency_key")
        elif key in seen_keys:
            errors.append(f"{label}: duplicate idempotency_key {key}")
        else:
            seen_keys.add(key)
        timestamp = record.get("user_turn_observed_at_jst")
        if timestamp in PLACEHOLDER_VALUES or not isinstance(timestamp, str) or not TIMESTAMP_RE.fullmatch(timestamp):
            errors.append(f"{label}: invalid canonical JST timestamp")
        if record.get("provider") != PROVIDER:
            errors.append(f"{label}: provider")
        if not isinstance(record.get("capture_attempts"), int) or record["capture_attempts"] < 1:
            errors.append(f"{label}: capture_attempts")
        if not isinstance(record.get("successful_executable_action_index"), int) or record["successful_executable_action_index"] < 1:
            errors.append(f"{label}: successful_executable_action_index")
        order_valid = record.get("runtime_order_valid")
        canonical = record.get("canonical_for_log_reconstruction")
        pre_semantic = record.get("pre_receipt_semantic_output")
        action_class = record.get("pre_receipt_action_class", "NONE")
        if not isinstance(order_valid, bool) or not isinstance(canonical, bool) or not isinstance(pre_semantic, bool):
            errors.append(f"{label}: boolean state field")
        if order_valid and pre_semantic:
            errors.append(f"{label}: semantic output before valid receipt")
        if order_valid and action_class not in {"NONE", "HOST_CONTROL_PLANE_ACTION_VERIFIED_EXEMPT"}:
            errors.append(f"{label}: pre-receipt action before valid receipt")
        if not order_valid and canonical:
            errors.append(f"{label}: invalid order promoted to canonical")
        persistence = record.get("persistence_status")
        verified = record.get("persistence_verified")
        if persistence == "PERSISTED_VERIFIED" and verified is not True:
            errors.append(f"{label}: persisted without verification")
        if persistence == "PERSISTENCE_FAILED" and verified is not False:
            errors.append(f"{label}: failed persistence marked verified")
        if canonical and (not order_valid or persistence != "PERSISTED_VERIFIED" or verified is not True):
            errors.append(f"{label}: reconstruction authority without verified persistence")
        if record.get("coordinate") in {"FATHER", "MOTHER"}:
            if record.get("visible_timestamp") != timestamp:
                errors.append(f"{label}: visible timestamp fork")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--allow-bootstrap", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        records = load_jsonl(args.ledger, allow_bootstrap=args.allow_bootstrap)
        errors = validate_records(records)
    except Exception as exc:
        errors = [str(exc)]
        records = []
    result = {
        "validator": "PEOS_TIME_LEDGER_VALIDATOR_rev0.308",
        "records": len(records),
        "errors": errors,
        "result": "PASS" if not errors else "FAIL",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{result['result']} records={result['records']} errors={len(errors)}")
        for error in errors:
            print(f"ERROR {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
