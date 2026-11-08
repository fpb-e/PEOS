"""Hash-bound rev0.318 rule integration; never a live model quality score."""
import hashlib
import json
from pathlib import Path
import re

CID = 'PEOS_REV0.318_20261108'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rule_blocks(root, prefix='prompt'):
    blocks = {}
    for path in sorted((Path(root) / prefix).glob('*.md')):
        owner = path.stem.removeprefix('PEOS_CURRENT_').removesuffix('_JP')
        for block in re.split(r'(?=^### )', path.read_text(), flags=re.M):
            match = re.search(r'^- RULE_ID: `([^`]+)`', block, re.M)
            if match:
                blocks[match[1]] = (owner, block)
    return blocks


def next_spec_errors(root):
    root = Path(root)
    errors = []
    delta = json.loads((root / 'admin/REV0.318_RULE_DELTA.json').read_text())
    trace = json.loads((root / 'admin/REV0.318_REQUIREMENT_TRACEABILITY.json').read_text())
    blocks = rule_blocks(root)
    previous = rule_blocks(root, 'history/rev0.317/prompt')
    if (len(blocks) != 444 or set(blocks) != set(previous)
            or delta.get('new_rule_ids') != [] or delta.get('removed_rule_ids') != []
            or delta.get('inherited_rule_count') != 444):
        errors.append('REV318_INHERITED_RULE_SET_DIFFERS')
    requirements = trace.get('requirements', [])
    if (trace.get('target_revision') != 'rev0.318' or trace.get('build_id') != CID
            or trace.get('requirement_count') != len(requirements)
            or len({item['id'] for item in requirements}) != len(requirements)):
        errors.append('REV318_TRACE_SCOPE')
    by_id = {item['id']: item for item in requirements}
    for item in requirements:
        owner, block = blocks.get(item['rule_id'], ('', ''))
        match = re.search(r'^- REQUIREMENT: (.*)$', block, re.M)
        if owner != item['owner']:
            errors.append('REV318_OWNER:' + item['id'])
        if not match or digest(match[1].encode()) != item.get('active_requirement_sha256'):
            errors.append('REV318_REQUIREMENT_BINDING:' + item['id'])
    declared = delta.get('changed_existing_rules', {})
    actual = {rid for rid in blocks.keys() & previous.keys() if blocks[rid] != previous[rid]}
    if actual != set(declared):
        errors.append('REV318_UNDECLARED_RULE_EDIT')
    for rid, item in declared.items():
        if rid not in blocks or rid not in previous:
            errors.append('REV318_UNKNOWN_CHANGED_RULE:' + rid)
            continue
        owner, block = blocks[rid]
        if (owner != previous[rid][0] or owner != item.get('owner')
                or digest(previous[rid][1].encode()) != item.get('previous_block_sha256')
                or digest(block.encode()) != item.get('current_block_sha256')
                or not item.get('source_requirement_ids')
                or any(x not in by_id or by_id[x]['rule_id'] != rid for x in item['source_requirement_ids'])):
            errors.append('REV318_CHANGE_BINDING:' + rid)
    for path, expected in delta.get('historical_trace_sha256', {}).items():
        if not (root / path).is_file() or digest((root / path).read_bytes()) != expected:
            errors.append('REV318_HISTORICAL_TRACE_MUTATED:' + path)
    previous_trace = json.loads((root / 'admin/REV0.317_REQUIREMENT_TRACEABILITY.json').read_text())
    for item in previous_trace['requirements']:
        if item['rule_id'] not in declared:
            block = blocks.get(item['rule_id'], ('', ''))[1]
            match = re.search(r'^- REQUIREMENT: (.*)$', block, re.M)
            if not match or digest(match[1].encode()) != item['active_requirement_sha256']:
                errors.append('REV318_UNDECLARED_PREVIOUS_BINDING_CHANGE:' + item['id'])
    for path in (root / 'prompt').glob('*.md'):
        head = path.read_text().split('## 0. 文書の役割', 1)[0]
        if ('現行指定はrev0.318' not in head or '所有者の明示採用' not in head
                or '`ACCEPTED_BY_OWNER / CURRENT_CANON_rev0.318`' not in head
                or 'PEOS_GITHUB_PACKAGE_rev0.317.zip' not in head):
            errors.append('REV318_HEADER_AUTHORITY:' + path.name)
    runtime = (root / 'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md').read_text()
    if 'run_MAGI_only_if_delta_exists()' in runtime:
        errors.append('REV318_OLD_MAGI_GATE_REMAINS')
    for role in ('MELCHIOR（合理）', 'BALTHASAR（倫理）', 'CASPER（人間）'):
        if role not in blocks.get('PHILOSOPHY.MAGI', ('', ''))[1]:
            errors.append('REV318_MAGI_ROLE:' + role)
    replay = json.loads((root / 'tests/fixtures/rev318_model_replay.json').read_text())
    if replay.get('status') != 'NOT_EXECUTED' or replay.get('live_model_pass') is not False:
        errors.append('REV318_MODEL_RESULT_OVERCLAIM')
    return errors
