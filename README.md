# PEOS_GITHUB_PACKAGE rev0.245

This package adds a SPEC/RUNTIME_GUARD integration bridge to prevent definition drift.

## Status
- Latest operative package: rev0.245
- Source base: PEOS_GITHUB_PACKAGE_rev0.244.zip
- Previous operative baseline: rev0.244 balanced restore
- rev0.243 compact remains deprecated for runtime use.

## Core addition
SPEC and RUNTIME_GUARD are now coupled by an explicit bridge:

- SPEC owns semantic definitions: identity, relation coordinates, source-separation meaning, adoption/non-adoption.
- RUNTIME_GUARD owns enforcement: output precheck, fail-closed behavior, regression tests, SELF_AUDIT triggers.
- DESIGNDOC explains rationale.
- PAPER preserves philosophy.
- LOG_ANTHOLOGY preserves observation evidence and regression material.

## Drift rule
Do not let SPEC and RUNTIME_GUARD become separate definitions of the same rule. If they disagree, use the stricter/safest existing rule and record `SPEC_RUNTIME_DRIFT_CHECK`.

## File layout
- `prompt/PEOS_CURRENT_SPEC_JP.md`
- `prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md`
- `prompt/PEOS_CURRENT_DESIGNDOC_JP.md`
- `prompt/PEOS_CURRENT_PAPER_JP.md`
- `prompt/PEOS_CURRENT_LOG_ANTHOLOGY_JP.md`
- `papers/PEOS_ACADEMIC_PAPER_JP.md`
- `CHANGELOG.md`
- `PACKAGE_MANIFEST.txt`
- `README.md`

## Read order
SPEC -> RUNTIME_GUARD -> DESIGNDOC -> PAPER -> LOG_ANTHOLOGY

Execution primary remains RUNTIME_GUARD / BOOT_CANON, but RUNTIME_GUARD must enforce SPEC definitions rather than independently redefining them.
