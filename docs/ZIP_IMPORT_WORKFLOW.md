> 公開版: 現行正本 rev0.314 / accepted baseline rev0.313。本文中の旧authorityと原文資料参照は元buildの記録。非公開の原文資料・画像は同梱せず、公開版の検証範囲はREADMEを参照。

# PEOS ZIP import workflow

This workflow prepares a ZIP supplied in a conversation for a reviewed GitHub update. The Python helper automates archive inspection, path mapping, change detection, and local placement. The assistant performs the GitHub commit using the connected GitHub integration.

This is a conversation-triggered workflow. Receiving an unrelated attachment is not an instruction to publish it. Scheduled polling, upload detection, GitHub Actions, and unattended publishing are outside this implementation.

## Normal operation

1. Identify the ZIP and the requested destination/revision. Read the repository's current branch and file layout.
2. Obtain a local working copy at the intended base commit. Run the import helper in its default dry-run mode.
3. Review the resulting paths, wrapper removal, mappings, hashes, and add/modify counts. Confirm that they match the requested update.
4. Apply the same ZIP and mapping to the isolated local working copy.
5. Run the applicable project validators against that imported candidate. Resolve any missing required validation before treating a release as validated.
6. Inspect the resulting diff, then create a GitHub commit on a working branch and report the commit/PR link.

For example, when the package uses `prompts/` and the destination repository uses `prompt/`:

```sh
python3 tools/peos_zip_import.py package.zip checkout --map prompts=prompt
python3 tools/peos_zip_import.py package.zip checkout --map prompts=prompt --apply
```

The first command is a dry run and leaves the working copy unchanged. The second writes the planned files. The helper does not run Git, create a commit, or access GitHub credentials.

## Paths and existing files

- A single common wrapper directory can be removed automatically; the report records the selected prefix. Inspect that choice before applying. Use `--strip-prefix ''` to retain the archive's exact relative paths, or provide an explicit prefix.
- Prefix mappings are explicit. The helper does not infer where a file belongs from its name or revision.
- Existing unrelated repository files are retained. An archive's omission of a file is not a deletion instruction.
- Unsafe paths, output collisions, symlinks, Git metadata paths, and the private `PEOS_TURN_TIME_LEDGER.jsonl` are rejected.
- Archive CRC checking, SHA-256 change detection, and path checks validate the import operation. They do not validate the meaning of the imported PEOS specifications.

## Validation and historical inspection

Validate the current public tree with `python3 -B tools/validate_rev0_315.py`. Its scope is the public manifest, canonical specification bindings, publication exclusions, and synthetic tests; original conversations and images are intentionally outside this public tree.

At the earlier repository inspection recorded in the canonical source, `tool/validate_rev0_305.py` existed while the referenced `tools/validate_rev0_311.py` and `tools/validate_rev0_313.py` were absent. The obsolete rev0.305 script has now been removed because it is not the current validation entry. That historical observation is retained in the immutable canons and does not require restoring the old script. The cleanup audit is `admin/OBSOLETE_FILE_CLEANUP_rev0.314.json`.

The importer does not change the project's authoritative revision or accepted baseline. Embedded candidate metadata and historical CURRENT labels must be interpreted against the owner's explicit revision instructions.

## Tests

```sh
python3 -m unittest discover -s tests -p 'test_peos_zip_import.py'
```

These tests cover archive import behavior using synthetic packages. They are not evidence of PEOS live-runtime acceptance or a successful deployment of a real release archive.
