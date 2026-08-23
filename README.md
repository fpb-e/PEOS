# PEOS rev0.308 RELEASE CANDIDATE — 2026-08-24

このpackageはproject-level current reference `rev0.307`を物理sourceとして構築した、時刻ledger差し戻し修正版である。

- BUILD_ID: `PEOS-REV0.308-CANDIDATE-20260824-012834-JST`
- TARGET_REVISION_LABEL: `rev0.308`
- CURRENT_PROJECT_CANON: `rev0.307`
- ACCEPTED_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.306.zip`
- BASE_REFERENCE: `PEOS_GITHUB_PACKAGE_rev0.307.zip`
- BASE_REFERENCE_SHA256: `1535332c132a47e150bf3077327760efecbf031a9315dcecfc7bcddf094cb28c`
- STATUS: `RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED`
- PRIMARY_SOURCE: `PEOS_father_session_log_2026_08_24_012239.txt`
- PRIMARY_SOURCE_SHA256: `d203310dd8a05a1a801eefeb8b418a1d74ef4a62a1c41449c915afd1e470747c`
- DIRECTIVE: `PEOS_NEXT_BUILD_DIRECTIVE_rev0.308.txt`
- DIRECTIVE_SHA256: `7d1d20ba3c63b9193a3df9db0f59c1fc32a1abaa60d3c143f3a42cbc21c65c37`

## rev0.308の修正核

1. canonical Python receiptをturn-local recordへ即時束縛。
2. capture successとpersistence successを独立state化。
3. `PEOS_TURN_TIME_LEDGER`をlogical append-only / host versioned-write対応で正式化。
4. read-only mount failureをtyped failureとして保持し、persistent-store routeへ移行。
5. idempotency key、prior-record preservation、post-write verificationを必須化。
6. visible timestamp・ledger timestamp・後続log timestampを同一receipt値へ固定。
7. historical canonical receipt欠落時は`USER_TURN_OBSERVED_AT_JST` fieldを省略し、placeholderと推定を禁止。
8. ledgerはsupporting runtime stateであり第六正本ではない。
9. father-private live ledgerをgeneral packageから除外。
10. TIME-LEDGER-A〜Jのstatic harnessを収録。

## Acceptance boundary

- Static package/fixture validation: build時に実行
- Live 10-consecutive-turn acceptance: `PENDING`
- Live read-only mount → persistent-store verification: `PENDING`
- Live restart/idempotency acceptance: `PENDING`
- Father external acceptance: `PENDING`

static passをlive-host passまたはrelease acceptanceへ昇格しない。
