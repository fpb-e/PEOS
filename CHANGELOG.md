# CHANGELOG - PEOS_GITHUB_PACKAGE rev0.245

## rev0.245 - SPEC/RUNTIME integration bridge

### Source
- Built from: `PEOS_GITHUB_PACKAGE_rev0.244.zip`
- Previous operative baseline: rev0.244 balanced restore

### User instruction
- 「RUNTIME_GUARDとSPECの統合定義を挟もう。ドリフトはよくない」

### Action
- Added `PEOS_REV0_245_SPEC_RUNTIME_INTEGRATION_BRIDGE` to SPEC.
- Added `PEOS_REV0_245_SPEC_RUNTIME_EXECUTION_BRIDGE` to RUNTIME_GUARD.
- Added supporting notes to DESIGNDOC, PAPER, LOG_ANTHOLOGY, and academic paper.
- Kept rev0.244 semantic thickness; did not repeat rev0.243 over-compaction.

### Core rule
SPEC owns meaning. RUNTIME_GUARD owns enforcement. Neither should independently redefine the other.

### Preserved operative invariants
- BOOT_CANON
- CURRENT definition / rollback prevention
- 成生 / セイ
- `俺 / お母さん / 親父`
- MAGI always-on / visible-on-request
- source separation
- ORDER_ONLY_STRICT / no fake JST
- response density enforcement
- adult-child / food-care boundaries
- panic correction stop-repeat
- unilateral eye pain BODY_FIRST
- relationship privacy minimum
- external lookup source integrity
- redundancy / acceptance testing
- 宇宙屋SE I/F
- copyrighted-reference sensibility extraction

### New audit hook
`SPEC_RUNTIME_DRIFT_CHECK` records missing runtime enforcement, runtime weakening of SPEC, duplicate redefinition, imported wrong calling, stale-log rollback, and examples treated as definitions.
