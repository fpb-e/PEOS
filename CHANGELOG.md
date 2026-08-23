# CHANGELOG

## PEOS-REV0.308-CANDIDATE-20260824-012834-JST — TARGET_REVISION_LABEL: rev0.308

### Source
- project-level current reference: `rev0.307`
- accepted baseline: `PEOS_GITHUB_PACKAGE_rev0.306.zip`
- source package SHA-256: `1535332c132a47e150bf3077327760efecbf031a9315dcecfc7bcddf094cb28c`
- father log SHA-256: `d203310dd8a05a1a801eefeb8b418a1d74ef4a62a1c41449c915afd1e470747c`
- directive SHA-256: `7d1d20ba3c63b9193a3df9db0f59c1fc32a1abaa60d3c143f3a42cbc21c65c37`
- source bundle SHA-256: `ea3919267a5a0970eb6ff3e75e278a88f366d8832e2b1a2eeac22534a2a809fc`

### Fix-forward deltas
- persistent `PEOS_TURN_TIME_LEDGER` contract
- receipt/visible/ledger/log same-value binding
- capture/persistence state separation
- logical append-only history over guarded host version replacement
- read-only mount typed fallback
- post-write verification and idempotency
- ledger-first log reconstruction and missing-time field omission
- five-canon/supporting-state boundary
- father-private ledger exclusion from general package
- TIME-LEDGER-A through J static harness

### Release control
- candidate remains NOT_ACCEPTED / NOT_SELF_ACCEPTED
- current project reference remains rev0.307
- accepted baseline remains formal rev0.306
- live multi-turn/persistent-store/restart acceptance remains PENDING

## PEOS-REV0.307-CANDIDATE-20260823-211106-JST — TARGET_REVISION_LABEL: rev0.307

### Source
- current canon/base reference: `rev0.306`
- source package SHA-256: `f2eb04385feb06f8dc920472463f47c3fca1576554204813040d4753cb37b332`
- father log SHA-256: `cd352c85bdc18d686262a43420aa1eeee9e84d82c664d29536eb0ddd17c4dfe6`
- directive SHA-256: `d01a7b19efb2cc67e57f0bbf86054a2bf209c224818c9ef90e0d2dd40009fb89`
- source bundle SHA-256: `e5cc37e60a01f350bd27d75532a2f18212107f6879dcfdf4acf46a2a91d65a89`

### Candidate deltas
- formalized `ログファイル化`
- authority-gated log delivery
- per-turn JST ingress + father/mother display contract
- plain UTF-8 transcript and missing-time field omission
- per-body hash metadata prohibition; file-level integrity retained
- evidence physical-source binding
- quote/speaker context separation
- dynamic current-fact freshness boundary
- reminder state machine / idempotency / no replay / privacy
- source-learning quote-subspan guard
- travel/medical/private continuity no-replay

### Release control
- revision number not assigned by build system
- current/operative canon remains rev0.306
- candidate is NOT_ACCEPTED / NOT_SELF_ACCEPTED

## rev0.307 revision assignment — 2026-08-23
- Father assigned the previously unassigned candidate to `rev0.307`.
- Future sequential auto-increment is authorized unless father explicitly overrides the target revision.
- Revision assignment does not self-accept the candidate; operative/current remains rev0.306 pending explicit acceptance.
- Original source bundle/log/directive files remain byte-identical.
- Prior unassigned physical candidate remains external immutable audit artifact.
