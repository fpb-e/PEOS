#!/usr/bin/env python3
"""Host-neutral PEOS turn-time ledger merge and verification helper.

The helper never treats its local output as persistence proof. A host adapter
must write the merged bytes to persistent storage and independently verify the
result before declaring PERSISTED_VERIFIED.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validator"))
from time_ledger_validator import load_jsonl, validate_records  # noqa: E402


def render(records: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in records)


def load_record(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("empty record input")
    if "\n" in text:
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) != 1:
            raise ValueError("record input must contain exactly one JSON object")
        text = lines[0]
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("record input must be an object")
    return value


def merge_records(existing: list[dict[str, Any]], new_record: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    errors = validate_records(existing)
    if errors:
        raise ValueError("existing ledger invalid: " + "; ".join(errors))
    key = new_record.get("idempotency_key")
    matches = [record for record in existing if record.get("idempotency_key") == key]
    if matches:
        comparable_new = dict(new_record)
        comparable_new["ledger_seq"] = matches[0]["ledger_seq"]
        if comparable_new != matches[0]:
            raise ValueError("idempotency key collision with different record")
        return list(existing), "IDEMPOTENT_ALREADY_PRESENT"
    expected_seq = (existing[-1]["ledger_seq"] if existing else 0) + 1
    candidate = dict(new_record)
    candidate["ledger_seq"] = expected_seq
    merged = list(existing) + [candidate]
    errors = validate_records(merged)
    if errors:
        raise ValueError("merged ledger invalid: " + "; ".join(errors))
    return merged, "APPENDED_ONE_LOGICAL_RECORD"


def verify_preservation(before: list[dict[str, Any]], after: list[dict[str, Any]], key: str) -> None:
    if after[: len(before)] != before:
        raise ValueError("prior record preservation failure")
    matches = [record for record in after if record.get("idempotency_key") == key]
    if len(matches) != 1:
        raise ValueError("idempotency key must appear exactly once")
    errors = validate_records(after)
    if errors:
        raise ValueError("persisted ledger invalid: " + "; ".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    merge = sub.add_parser("merge")
    merge.add_argument("--existing", type=Path, required=True)
    merge.add_argument("--record", type=Path, required=True)
    merge.add_argument("--output", type=Path, required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--before", type=Path, required=True)
    verify.add_argument("--after", type=Path, required=True)
    verify.add_argument("--idempotency-key", required=True)

    lookup = sub.add_parser("lookup")
    lookup.add_argument("--ledger", type=Path, required=True)
    selector = lookup.add_mutually_exclusive_group(required=True)
    selector.add_argument("--turn-id")
    selector.add_argument("--idempotency-key")

    args = parser.parse_args()
    if args.command == "merge":
        if args.output.resolve() == args.existing.resolve():
            raise SystemExit("refusing in-place mutation; use a writable candidate output")
        existing = load_jsonl(args.existing)
        record = load_record(args.record)
        merged, status = merge_records(existing, record)
        args.output.write_text(render(merged), encoding="utf-8")
        print(json.dumps({
            "capture_status": record.get("capture_status"),
            "merge_status": status,
            "local_candidate_written": True,
            "persistent_store_status": "NOT_ATTEMPTED_BY_HOST_NEUTRAL_HELPER",
            "persistence_status": "PENDING",
            "records": len(merged),
        }, ensure_ascii=False))
        return 0

    if args.command == "verify":
        before = load_jsonl(args.before)
        after = load_jsonl(args.after)
        verify_preservation(before, after, args.idempotency_key)
        print(json.dumps({
            "verification": "PASS",
            "idempotency_key_count": 1,
            "prior_records_preserved": True,
            "persistence_status": "PERSISTED_VERIFIED_IF_AFTER_IS_AUTHORITATIVE_HOST_READ",
        }, ensure_ascii=False))
        return 0

    records = load_jsonl(args.ledger)
    errors = validate_records(records)
    if errors:
        raise SystemExit("ledger invalid: " + "; ".join(errors))
    matches = [
        record for record in records
        if (args.turn_id and record.get("turn_id") == args.turn_id)
        or (args.idempotency_key and record.get("idempotency_key") == args.idempotency_key)
    ]
    canonical = [
        record for record in matches
        if record.get("canonical_for_log_reconstruction") is True
        and record.get("persistence_status") == "PERSISTED_VERIFIED"
        and record.get("persistence_verified") is True
    ]
    if len(canonical) == 1:
        print(json.dumps({
            "field_present": True,
            "field_name": "USER_TURN_OBSERVED_AT_JST",
            "value": canonical[0]["user_turn_observed_at_jst"],
            "ledger_seq": canonical[0]["ledger_seq"],
        }, ensure_ascii=False))
        return 0
    print(json.dumps({
        "field_present": False,
        "omission_reason": "NO_UNIQUE_PERSISTED_VERIFIED_CANONICAL_RECORD",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
