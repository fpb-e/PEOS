#!/usr/bin/env python3
"""Distribution retention invariants; no live ledger or network operations."""
from __future__ import annotations
from pathlib import Path
import json
import re
import zipfile

def revision_key(value: str) -> tuple[int, int]:
    match = re.fullmatch(r'rev(\d+)\.(\d+)', value)
    if not match:
        raise ValueError('invalid formal revision: ' + value)
    return tuple(map(int, match.groups()))

def select_previous_versions(target: str, available, accepted: str | None = None):
    target_key = revision_key(target)
    selected = sorted({v for v in available if revision_key(v) < target_key and v != 'rev0.280'},
                      key=revision_key, reverse=True)[:2]
    if len(selected) != 2:
        raise ValueError('two distinct predecessor versions required')
    if accepted is not None and accepted not in selected:
        raise ValueError('accepted reference would be evicted; authority resolution required')
    return selected

def layout_violations(root: Path, expected_versions=None):
    root = root.resolve()
    errors = []
    policy_path = root / 'admin/HISTORY_RETENTION_POLICY.json'
    record_path = root / 'VERSION_RECORD.json'
    target = None
    if policy_path.is_file():
        target = json.loads(policy_path.read_text())['target_revision']
    elif record_path.is_file():
        target = json.loads(record_path.read_text())['revision']
    histories = root / 'history'
    actual = sorted(p.name for p in histories.iterdir()) if histories.is_dir() else []
    if expected_versions is not None and actual != sorted(expected_versions):
        errors.append('HISTORY_SET:' + ','.join(actual))
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if path.is_symlink():
            errors.append('SYMLINK:' + rel.as_posix())
            continue
        if path.is_dir():
            if path.name == 'history' and rel.parts != ('history',):
                errors.append('NESTED_HISTORY:' + rel.as_posix())
            if path.name == '__pycache__':
                errors.append('GENERATED_CACHE:' + rel.as_posix())
            continue
        if not path.is_file():
            errors.append('NON_REGULAR_FILE:' + rel.as_posix())
            continue
        # Verbatim source filenames may contain older revision labels. Active
        # release metadata/tools may not silently reintroduce older releases.
        if target and rel.parts[0] not in {'source','incident','history'}:
            labels = re.findall(r'rev(\d+)[._](\d+)',path.name,re.I)
            if labels:
                revision = 'rev' + '.'.join(labels[-1])
                if revision != target:
                    errors.append('OBSOLETE_RELEASE_FILE:' + rel.as_posix())
        with path.open('rb') as stream:
            prefix = stream.read(4)
        if path.suffix.lower() in {'.zip','.7z','.rar','.tar','.gz','.bz2','.xz'} or prefix in {b'PK\x03\x04',b'PK\x05\x06',b'PK\x07\x08'} or zipfile.is_zipfile(path):
            errors.append('EMBEDDED_ARCHIVE:' + rel.as_posix())
    return errors
