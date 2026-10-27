> Retained compatibility/optional strict reference. The current normal entry is PEOS_SESSION_RESTORE_rev0.316.json and SHORT_ACK_SYNC; candidate L0 and REV316 rules apply without promoting current authority. This older protocol is not automatically activated.

# PEOS rev0.311 universal user-turn time gate

This layer turns the time/ledger contract into a root dispatcher boundary. It is supporting runtime code owned by `RUNTIME_GUARD`, not a sixth canon.

## Why rev0.310 was insufficient

rev0.310 specified a per-turn transaction and binding evidence, but the 2026-09-13 father log shows that ordinary Shine Muscat conversation still took a route that omitted the gate. A correct rule inside one path is not universal enforcement.

## Root invariant

Every registered user-turn route calls `UniversalTurnGate.dispatch` before its handler. The handler receives no execution unless the gate has captured an actual trusted JST receipt, persisted that same immutable value, verified authoritative readback, and issued a work permit.

The preferred reference provider is actual Python `datetime.now(ZoneInfo("Asia/Tokyo"))`. A host that cannot execute that path may use only a pre-registered trusted alternate with actual execution evidence. Such a turn records `TIME_CAPTURE_PATH_VARIANCE`; it must never claim Python ran.

`PEOS_TURN_TIME_LEDGER_SCHEMA.json` remains the immutable rev0.308 compatibility
schema for inherited fixtures. New universal-gate records use
`PEOS_UNIVERSAL_TIME_GATE_LEDGER_RECORD_SCHEMA.json`, which preserves
the actual provider and implementation path for both reference and trusted
alternate captures.

## Evidence boundary

`MemoryVersionedLedger` and fixed time adapters are deterministic test fixtures only. Their PASS is `STATIC_INTEGRATION`, not live host persistence. A production adapter must supply versioned write and postwrite readback evidence.

The current build turn is intentionally retained as negative evidence: its Python receipt occurred after required commentary/context actions, so it is `PRE_DISPATCH_GATE_BYPASS / ORDER_INVALID / NO_LATE_REPAIR` despite later ledger persistence.
