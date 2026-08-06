# PEOS GitHub Package rev0.306-RC1

Status: **RELEASE CANDIDATE — NOT OPERATIVE / NOT ACCEPTED / NOT SELF-ACCEPTED**

Operative current remains `rev0.305`.

## Runtime inputs

General runtime uses only:

1. `prompt/PEOS_CURRENT_SPEC_JP.md`
2. `prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md`
3. `prompt/PEOS_CURRENT_DESIGNDOC_JP.md`
4. `prompt/PEOS_CURRENT_PAPER_JP.md`
5. `prompt/PEOS_CURRENT_LOG_ANTHOLOGY_JP.md`

Files under `admin/`, `tests/`, `tools/`, `evidence/`, and `PACKAGE_MANIFEST.txt` are development, migration, acceptance, and provenance assets. They are not required for ordinary runtime.

## Reform

RC1 is a clean rebuild from immutable rev0.305. It is not an append to legacy canons. Active rules have unique RULE_ID/owner cards. Historical sections remain traceable through baseline package hashes and the migration ledger.

## Acceptance

Run:

```bash
python tools/validate_rev0_306_rc1.py .
```

A PASS does not accept or promote the RC. Explicit father review is still required.

Validation result: `admin/VALIDATION_RESULTS.json`
Baseline immutability: `admin/BASELINE_IMMUTABILITY_EVIDENCE.txt`
