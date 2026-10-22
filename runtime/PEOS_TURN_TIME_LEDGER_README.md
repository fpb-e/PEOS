> Retained compatibility/optional strict reference. The current normal entry is PEOS_SESSION_RESTORE_rev0.314.json and SHORT_ACK_SYNC; current L0 and REV314 rules control. This older protocol is not automatically activated.

# PEOS turn-time ledger supporting runtime asset

- Revision: `rev0.308`
- Canonical logical name: `PEOS_TURN_TIME_LEDGER`
- Canonical persistent target: `/PEOS/Runtime/PEOS_TURN_TIME_LEDGER.jsonl`
- Authority: supporting runtime state; not a sixth canon
- Logical mutation model: append-only JSONL
- Physical host model: guarded version replacement is allowed when native append is unavailable

Required write sequence:

1. Read the latest persistent version.
2. Validate every existing record and preserve its bytes/meaning.
3. Reject or collapse a duplicate idempotency key.
4. Append exactly one new logical record.
5. Write through the host persistent-store route with a retained version guard when available.
6. Re-read or use an equivalent authoritative result and verify prior-record preservation plus the new record.
7. Mark `PERSISTED_VERIFIED` only after step 6.

An attached or mounted file may be read-only and must not be treated as the writable canonical target. Direct-append failure is typed separately from capture. The package contains no father-private live ledger data; it contains only this contract, schema, bootstrap metadata, validators, and synthetic fixtures.
