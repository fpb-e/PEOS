#!/usr/bin/env python3
"""Validation of the deliberately source-free public PEOS distribution.

This is an explicit publication policy, not a general secret scanner. It does
not recreate or verify the absent private conversation/image corpus.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tif',
                  '.tiff', '.svg', '.heic', '.heif', '.avif', '.ico'}
ARCHIVE_SUFFIXES = {'.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz'}
PRIVATE_ROOTS = {'source', 'incident', 'attachments', 'upload', 'uploads'}
PRIVATE_NAMES = {'peos_turn_time_ledger.jsonl', 'father_direct_ledger.jsonl',
                 'events.jsonl', 'attachment_ledger.json', 'source_coverage.json',
                 'peos_preprocess_restore_state.json',
                 'peos_continuity_truth_bootstrap.json'}
OWNERS = ('SPEC', 'RUNTIME_GUARD', 'DESIGNDOC', 'PAPER', 'LOG_ANTHOLOGY')
LIVE_ID = re.compile(r'(?<![A-Za-z0-9])(?:libfile_[0-9a-f]{16,}|file_[0-9a-f]{24,})')
# Immutable public package already published by PR #5. A filename alone does
# not permit an archive; different bytes or another path remain forbidden.
DISTRIBUTION_ARCHIVES = {
    'downloads/PEOS_GITHUB_PACKAGE_rev0.316.zip':
        '7a35699d30153ae8ce30234f20aa35bef7a2f1520060ff85af398da4e3016915',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files(root):
    root = Path(root)
    return sorted((p for p in root.rglob('*')
                   if '.git' not in p.relative_to(root).parts and (p.is_file() or p.is_symlink())),
                  key=lambda p: p.relative_to(root).as_posix())


def forbidden_file(relative, data, excluded_original_sha256=()):
    """Check publication scope and known excluded originals, including renames."""
    path = Path(relative)
    parts = [p.casefold() for p in path.parts]
    leaf = path.name.casefold()
    issues = []
    data_sha256 = digest(data)
    distribution_archive = DISTRIBUTION_ARCHIVES.get(path.as_posix()) == data_sha256
    if any(p in PRIVATE_ROOTS for p in parts):
        issues.append('PRIVATE_SOURCE_DIRECTORY')
    if (leaf in PRIVATE_NAMES or 'father_learning_projection' in leaf
            or (('session_log' in leaf or 'session_bundle' in leaf)
                and path.suffix.lower() != '.py' and not leaf.endswith('_schema.json'))
            or path.suffix.lower() == '.jsonl'):
        issues.append('RAW_CONVERSATION_OR_PRIVATE_STATE')
    if path.suffix.lower() in IMAGE_SUFFIXES:
        issues.append('IMAGE_EXTENSION')
    if (data.startswith((b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff', b'GIF87a', b'GIF89a', b'BM',
                         b'II*\x00', b'MM\x00*', b'\x00\x00\x01\x00'))
            or (data[:4] == b'RIFF' and data[8:12] == b'WEBP')
            or re.match(br'\s*(?:<\?xml[^>]*>\s*)?<svg(?:\s|>)', data)):
        issues.append('IMAGE_BYTES')
    if not distribution_archive and (path.suffix.lower() in ARCHIVE_SUFFIXES
            or data.startswith((b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08', b'7z\xbc\xaf\x27\x1c', b'Rar!'))):
        issues.append('EMBEDDED_ARCHIVE')
    if data_sha256 in excluded_original_sha256:
        issues.append('EXCLUDED_ORIGINAL_BYTES')
    if distribution_archive:
        return issues
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        issues.append('NON_UTF8_PUBLIC_CONTENT')
    else:
        if LIVE_ID.search(text):
            issues.append('LIVE_PRIVATE_FILE_IDENTIFIER')
    return issues


def distribution_errors(root):
    """Check the optional repository download shelf without changing the ZIP."""
    root = Path(root)
    if not (root / 'downloads').exists():
        return []
    errors = []
    for relative, sha in DISTRIBUTION_ARCHIVES.items():
        path = root / relative
        if not path.is_file() or path.is_symlink():
            errors.append('DISTRIBUTION_ARCHIVE_MISSING:' + relative)
        elif digest(path.read_bytes()) != sha:
            errors.append('DISTRIBUTION_ARCHIVE_BYTES_DIFFER:' + relative)
    expected = ''.join(f'{sha}  {Path(name).name}\n'
                       for name, sha in sorted(DISTRIBUTION_ARCHIVES.items()))
    sums = root / 'downloads/SHA256SUMS'
    if not sums.is_file() or sums.read_bytes() != expected.encode('ascii'):
        errors.append('DISTRIBUTION_CHECKSUMS_DIFFER')
    return errors


def publication_errors(root, excluded_original_sha256=()):
    root = Path(root)
    issues = []
    for path in files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            issues.append(relative + ':SYMLINK')
            continue
        issues.extend(relative + ':' + code for code in
                      forbidden_file(relative, path.read_bytes(), excluded_original_sha256))
    return issues


def manifest_rows(root):
    root = Path(root)
    entries = []
    for path in files(root):
        name = path.relative_to(root).as_posix()
        if name != 'PACKAGE_MANIFEST.txt':
            data = path.read_bytes()
            entries.append((name, digest(data), len(data)))
    return entries


def write_manifest(root):
    root = Path(root)
    names = {p.relative_to(root).as_posix() for p in files(root)}
    names.update({'DIRECTORY_AND_FILE_LIST.txt', 'PACKAGE_MANIFEST.txt'})
    (root / 'DIRECTORY_AND_FILE_LIST.txt').write_text(
        'PEOS rev0.316 candidate public tree (Git metadata excluded)\n\n'
        + '\n'.join(sorted(names)) + '\n', encoding='utf-8')
    entries = manifest_rows(root)
    text = ('PEOS_PUBLIC_PACKAGE_MANIFEST_V1\n'
            'TARGET_REVISION: rev0.316\n'
            'STATUS: RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED\n'
            'PROJECT_LEVEL_CURRENT_REFERENCE: rev0.315\n'
            'ACCEPTED_BASELINE: PEOS_GITHUB_PACKAGE_rev0.314.zip\n'
            'DETAILED_REFERENCE: rev0.315\n'
            'PUBLICATION_SCOPE: SPECIFICATIONS_CODE_SYNTHETIC_TESTS_WITHOUT_RAW_CONVERSATIONS_OR_IMAGES\n'
            'PRIVATE_SOURCE_VALIDATION: NOT_PERFORMED_BY_PUBLIC_VALIDATOR\n'
            f'FILE_COUNT_EXCLUDING_MANIFEST: {len(entries)}\n\nFILES:\n')
    text += ''.join(f'{sha} {size} {name}\n' for name, sha, size in entries)
    (root / 'PACKAGE_MANIFEST.txt').write_text(text, encoding='utf-8')


def manifest_errors(root):
    root = Path(root)
    path = root / 'PACKAGE_MANIFEST.txt'
    if not path.is_file():
        return ['MISSING_PUBLIC_MANIFEST']
    text = path.read_text(encoding='utf-8')
    if not text.startswith('PEOS_PUBLIC_PACKAGE_MANIFEST_V1\n'):
        return ['NOT_A_PUBLIC_MANIFEST']
    try:
        count = int(re.search(r'^FILE_COUNT_EXCLUDING_MANIFEST: (\d+)$', text, re.M)[1])
        entries = {}
        for row in text.split('\nFILES:\n', 1)[1].splitlines():
            match = re.fullmatch(r'([0-9a-f]{64}) (\d+) (.+)', row)
            if not match or match[3] in entries:
                return ['INVALID_OR_DUPLICATE_MANIFEST_ROW']
            entries[match[3]] = (match[1], int(match[2]))
    except (IndexError, TypeError, ValueError):
        return ['INVALID_PUBLIC_MANIFEST_HEADER']
    actual = {name: (sha, size) for name, sha, size in manifest_rows(root)}
    errors = []
    if count != len(entries) or entries != actual:
        errors.append('PUBLIC_MANIFEST_BYTES_OR_PATHS_DIFFER')
    expected = {p.relative_to(root).as_posix() for p in files(root)}
    listing = (root / 'DIRECTORY_AND_FILE_LIST.txt').read_text().split('\n\n', 1)[1].splitlines()
    if len(listing) != len(set(listing)) or set(listing) != expected:
        errors.append('PUBLIC_DIRECTORY_LIST_DIFFERS')
    return errors


def specification_errors(root):
    root = Path(root)
    errors = []
    provenance = json.loads((root / 'admin/PUBLIC_EXPORT_PROVENANCE_rev0.316.json').read_text())
    for item in provenance['canonical_documents']:
        path = root / item['path']
        if not path.is_file() or digest(path.read_bytes()) != item['source_sha256']:
            errors.append('CANON_BYTES_DIFFER:' + item['path'])
    ids, owners, blocks = [], {}, {}
    for owner in OWNERS:
        text = (root / f'prompt/PEOS_CURRENT_{owner}_JP.md').read_text()
        if '- 文書revision: `rev0.316`' not in text:
            errors.append('CURRENT_DOCUMENT_REVISION:' + owner)
        for block in re.split(r'(?=^### )', text, flags=re.M):
            match = re.search(r'^- RULE_ID: `([^`]+)`', block, re.M)
            if match:
                ids.append(match[1]); owners[match[1]] = owner; blocks[match[1]] = block
    if len(ids) != 443 or len(set(ids)) != 443:
        errors.append('443_UNIQUE_RULES_REQUIRED')
    registry = (root / 'admin/RULE_OWNERSHIP_REGISTRY.yaml').read_text()
    if not all(line in registry.splitlines() for line in ('revision: rev0.316', 'current_project_canon: rev0.315', 'accepted_baseline: rev0.314', 'rule_count: 443')):
        errors.append('RULE_REGISTRY_AUTHORITY_OR_COUNT_DIFFERS')
    pairs = re.findall(r'^- RULE_ID: (\S+)\n  OWNER: (\S+)', registry, re.M)
    if len(pairs) != 443 or dict(pairs) != owners:
        errors.append('RULE_OWNER_REGISTRY_DIFFERS')
    trace = json.loads((root / 'admin/REV0.314_REQUIREMENT_TRACEABILITY.json').read_text())
    requirements = trace['requirements']
    if trace['requirement_count'] != 91 or len(requirements) != 91 or len({r['id'] for r in requirements}) != 91:
        errors.append('91_DERIVED_REQUIREMENTS_REQUIRED')
    normalize = lambda value: re.sub(r'\s+', ' ', value).strip()
    for item in requirements:
        if (owners.get(item['rule_id']) != item['owner']
                or normalize(item['requirement']) not in normalize(blocks.get(item['rule_id'], ''))
                or item['public_verification'] != 'CANON_TEXT_AND_UNIQUE_OWNER'):
            errors.append('REQUIREMENT_BINDING:' + item['id'])
    latest = json.loads((root / 'admin/REV0.315_REQUIREMENT_TRACEABILITY.json').read_text())
    if latest.get('requirement_count') != 18 or len(latest['requirements']) != 18:
        errors.append('18_NEW_DERIVED_REQUIREMENTS_REQUIRED')
    for item in latest['requirements']:
        if owners.get(item['rule_id']) != item['owner'] or normalize(item['requirement']) not in normalize(blocks.get(item['rule_id'], '')):
            errors.append('LATEST_REQUIREMENT_BINDING:' + item['id'])
    source = json.loads((root / 'admin/REV0.316_REQUIREMENT_TRACEABILITY.json').read_text())
    from collections import Counter
    required = {'NEW_CANDIDATE_RULE':13, 'CLARIFY_EXISTING_RULE':4, 'REAFFIRM_EXISTING_RULE':1, 'PRIVATE_STATE_ONLY':6, 'UNADOPTED_PROPOSAL':1}
    if source.get('requirement_count') != 25 or len(source['requirements']) != 25 or len({x['id'] for x in source['requirements']}) != 25 or dict(Counter(x['disposition'] for x in source['requirements'])) != required:
        errors.append('SOURCE_DISPOSITIONS_DIFFER')
    inherited = set()
    for owner in OWNERS:
        old = (root / f'history/rev0.315/prompt/PEOS_CURRENT_{owner}_JP.md').read_text()
        inherited.update(re.findall(r'^- RULE_ID: `([^`]+)`', old, re.M))
    added = {x['rule_id'] for x in source['requirements'] if x['disposition'] == 'NEW_CANDIDATE_RULE'}
    if len(inherited) != 430 or not inherited <= set(ids) or set(ids) - inherited != added:
        errors.append('INHERITED_RULE_LOSS_OR_UNDECLARED_ADDITION')
    for item in source['requirements']:
        if item['disposition'] in {'NEW_CANDIDATE_RULE','CLARIFY_EXISTING_RULE','REAFFIRM_EXISTING_RULE'}:
            if owners.get(item['rule_id']) != item['owner']:
                errors.append('SOURCE_OWNER:' + item['id'])
            if item['disposition'] != 'REAFFIRM_EXISTING_RULE' and normalize(item['requirement']) not in normalize(blocks.get(item['rule_id'], '')):
                errors.append('SOURCE_REQUIREMENT:' + item['id'])
        elif item.get('rule_id') is not None:
            errors.append('NONOPERATIVE_ITEM_HAS_ACTIVE_RULE:' + item['id'])
        elif item['disposition'] == 'UNADOPTED_PROPOSAL' and not (root / item['proposal_document']).is_file():
            errors.append('UNADOPTED_PROPOSAL_DOCUMENT_MISSING')
    if any('.REV316.PRAG_004' in rid for rid in ids):
        errors.append('UNADOPTED_PROPOSAL_PROMOTED')
    readme = (root / 'README.md').read_text()
    if '## インストールマニュアル\n' not in readme:
        errors.append('INSTALL_MANUAL_MISSING')
    else:
        before, manual = readme.split('## インストールマニュアル\n', 1)
        if '## 公開範囲' not in before or '## 検証' not in before:
            errors.append('README_OVERVIEW_BEFORE_INSTALL_REQUIRED')
        if len(re.findall(r'^\| `prompt` \| `PEOS_CURRENT_[^`]+` \|$', manual, re.M)) != 5:
            errors.append('EXACTLY_FIVE_INSTALL_ATTACHMENTS')
        if 'ユーザー名：〈呼んでほしいユーザー名〉' not in manual or 'お母さん' in manual:
            errors.append('GENERIC_USER_NAME_REQUIRED')
    if restore_candidate_promoted(root):
        errors.append('CANDIDATE_SELF_PROMOTION')
    history = root / 'history'
    if sorted(p.name for p in history.iterdir()) != ['rev0.314', 'rev0.315']:
        errors.append('HISTORY_MUST_HAVE_EXACTLY_TWO_PREDECESSORS')
    for p in history.rglob('history'):
        errors.append('NESTED_HISTORY:' + p.relative_to(root).as_posix())
    policy = json.loads((root / 'admin/HISTORY_RETENTION_POLICY.json').read_text())
    for value in policy['snapshots'].values():
        for name, sha in value['canons'].items():
            if digest((root / value['path'] / name).read_bytes()) != sha:
                errors.append('HISTORICAL_CANON_HASH:' + value['path'] + '/' + name)
    return errors


def restore_candidate_promoted(root):
    r = json.loads((Path(root) / 'runtime/PEOS_SESSION_RESTORE_rev0.316.json').read_text())
    return r.get('candidate_revision') != 'rev0.316' or r.get('candidate_accepted') is not False

def authority_errors(root):
    root = Path(root)
    restore = json.loads((root / 'runtime/PEOS_SESSION_RESTORE_rev0.316.json').read_text())
    value = restore['authority']
    expected = ('rev0.315', 'PEOS_GITHUB_PACKAGE_rev0.314.zip', 'rev0.315')
    errors = []
    if tuple(value[k] for k in ('current_canon', 'accepted_baseline', 'detailed_reference')) != expected:
        errors.append('CURRENT_AUTHORITY_DIFFERS')
    if (restore.get('source_sync_receipt') is not None or restore.get('current_turn_receipt') is not None
            or restore.get('replay_actions') != [] or restore.get('runtime_ready')
            or restore.get('preprocessing', {}).get('ledger_library_file_id') is not None
            or restore.get('mail_states') or restore.get('job_priorities') or restore.get('corrections')):
        errors.append('PRIVATE_OR_LIVE_STATE_IN_PUBLIC_RESTORE')
    return errors


def validate(root, *, check_manifest=True):
    root = Path(root)
    provenance = json.loads((root / 'admin/PUBLIC_EXPORT_PROVENANCE_rev0.316.json').read_text())
    return (publication_errors(root, set(provenance['excluded_original_sha256']))
            + distribution_errors(root)
            + (manifest_errors(root) if check_manifest else [])
            + specification_errors(root) + authority_errors(root))
