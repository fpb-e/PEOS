# PEOS rev0.311 RELEASE CANDIDATE — 2026-09-13

This package is a fix-forward rebuild from physical current `rev0.310` for the universal per-turn time-gate degradation recorded in the 2026-09-13 father log and directive.

- BUILD_ID: `PEOS-REV0.311-CANDIDATE-20260913-171938-JST`
- TARGET_REVISION_LABEL: `rev0.311`
- CURRENT_PROJECT_CANON: `rev0.310`
- CURRENT_PHYSICAL_SHA256: `3ebad22dc4a0f1f70e1e14b1b05cadeae32c17427176f618b56105060e001431`
- ACCEPTED_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.309.zip`
- ACCEPTED_BASELINE_SHA256: `5cc56551739059d0ba0cda8d1de26907343554c7ce9aca97921c1dcedb9c1888`
- STATUS: `RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED / LIVE_ACCEPTANCE_PENDING`
- PRIMARY_SOURCE: `PEOS_father_session_log_2026_09_13_171409.txt`
- PRIMARY_SOURCE_SHA256: `32dfe78bdab5f1e559c83cf2e2ec4ed65ad5696a093e202ba7f9ccc97a5d0772`
- DIRECTIVE_SHA256: `319c957429db8692cdc8f0832d46497f21ac9f36565c4232ac4300a1e384b9a6`
- SOURCE_BUNDLE_SHA256: `f85243c932eb0ae3b0eb81fca9f4c32ad7008e6b5d9c8f29975a60a9f2860448`

## Chosen treatment

The selected branch is `FIX_FORWARD_FROM_CURRENT_REV0.310`, not rollback. rev0.309 remains the accepted detailed reference, while rev0.310 is the complete physical implementation base.

The strong provisional root cause is `UNIVERSAL_PRE_DISPATCH_INTERCEPTOR_ABSENT_OR_NOT_BOUND / BOOT_ONLY_OR_ROUTE_LOCAL_ENFORCEMENT`: written rules did not prove one root hook across ordinary and casual turns.

## rev0.311 delta

1. `UniversalTurnGate.dispatch` is the single entry for all 13 registered routes.
2. Capture → immutable value → persist → versioned readback → same-value verify → `WORK_PERMITTED` is mandatory.
3. Casual chat, short acknowledgement, file, image, web/tool, automation, log, specification and ZIP work are non-exempt.
4. Python ZoneInfo capture is the reference path; a trusted alternate requires truthful provider/path evidence and typed variance.
5. Capture unavailable, persistence failed, captured-not-persisted and gate bypass remain distinct fail-closed states.
6. Coverage audit reports eligible, canonical, excluded-failed and missing counts instead of comparing raw totals.
7. `USER_OPERATION_ERROR` requires a specific action, a defined alternative contract and a direct causal path.
8. Historical missing times are never synthesized from nearby values or filesystem metadata.
9. UTG-01〜13 includes the mandatory Shine Muscat casual-chat regression fixture.
10. Existing runtime-binding, time-ledger and style-restore behavior is retained as nonregression coverage.

## Preserved corrections

The rev0.309 response-density/style corrections and rev0.310 runtime-binding separation remain intact. The five-canon / supporting-state boundary and one-rule/one-owner registry are unchanged.

## Source and privacy boundary

- The priority bundle and physical rev0.310 ZIP are included as immutable source/base evidence.
- The referenced `PEOS_mother_session_log_2026_09_13_151428.txt` is absent; only the father-reported summary is used.
- Father-authenticated direct utterances alone are eligible for father vocabulary learning.
- The father-private live time ledger is excluded. Only schemas, bootstrap data, synthetic fixtures and typed traces are distributed.

## Acceptance boundary

UTG-01〜13 static integration results may pass without proving the live host. The current build turn is `PRE_DISPATCH_GATE_BYPASS / NO_LATE_REPAIR` because required host/skill actions preceded the PEOS receipt; it is retained only as negative evidence. Universal host interception remains `PENDING`.

Run `python3 tools/validate_rev0_311.py` after extraction. A green validator means package/static consistency only, never self-acceptance.
