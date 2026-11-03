"""Structural next-spec acceptance checks, never a model-quality test."""
import hashlib
import json
from pathlib import Path
import re

CID = 'PEOS_REV0.317_20261103'


def next_spec_errors(root):
    root = Path(root)
    errors = []
    delta = json.loads((root/'admin/REV0.317_RULE_DELTA.json').read_text())
    trace = json.loads((root/'admin/REV0.317_REQUIREMENT_TRACEABILITY.json').read_text())
    text = '\n'.join(p.read_text() for p in sorted((root/'prompt').glob('*.md')))
    ids = re.findall(r'^- RULE_ID: `([^`]+)`',text,re.M)
    if len(ids)!=444 or len(set(ids))!=444:
        errors.append('NEXT_SPEC_RULE_COUNT_OR_DUPLICATE')
    blocks={}
    for b in re.split(r'(?=^### )',text,flags=re.M):
        m=re.search(r'^- RULE_ID: `([^`]+)`',b,re.M)
        if m: blocks[m[1]]=b
    if (trace.get('target_revision') != 'rev0.317' or trace.get('candidate_id')!=CID
            or trace.get('requirement_count')!=15 or len(trace['requirements'])!=15
            or len({x['id'] for x in trace['requirements']})!=15):
        errors.append('NEXT_SPEC_TRACE_SCOPE')
    for item in trace['requirements']:
        b=blocks.get(item['rule_id'],'')
        if f"- OWNER: `{item['owner']}`" not in b:
            errors.append('NEXT_SPEC_OWNER:'+item['id'])
        match=re.search(r'^- REQUIREMENT: (.*)$',b,re.M)
        if not match or hashlib.sha256(match[1].encode()).hexdigest()!=item.get('active_requirement_sha256'):
            errors.append('NEXT_SPEC_REQUIREMENT_BINDING:'+item['id'])
    if delta['new_rule_ids']!=['DESIGN.MODE.FULL_FEATURE_SELECTION'] or delta['inherited_rule_count']!=443:
        errors.append('NEXT_SPEC_UNDECLARED_ADDITION')
    for rid,item in delta['changed_existing_rules'].items():
        if '- NEXT_SPEC_CHANGE: `'+CID+'`' not in blocks.get(rid,''):
            errors.append('NEXT_SPEC_CHANGE_MARKER:'+rid)
    mode=blocks.get('DESIGN.MODE.FULL_FEATURE_SELECTION','')
    for token in ['完全版','ZIP','五正本個別','通常会話','namespace','停止','接続']:
        if token not in mode: errors.append('NEXT_SPEC_MODE_CONTRACT:'+token)
    for name in ['REV0.314','REV0.315','REV0.316']:
        old=json.loads((root/('admin/'+name+'_REQUIREMENT_TRACEABILITY.json')).read_text())
        for item in old['requirements']:
            if item.get('current_binding_superseded_by'):
                record=delta['changed_existing_rules'].get(item.get('rule_id'),{})
                if item['current_binding_superseded_by']!=record.get('source_requirement_ids'):
                    errors.append('UNAUTHORIZED_HISTORICAL_BINDING_OVERRIDE:'+item['id'])
    runtime=(root/'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md').read_text()
    if 'run_MAGI_only_if_delta_exists()' in runtime:
        errors.append('NEXT_SPEC_OLD_MAGI_GATE_REMAINS')
    for name in ('MELCHIOR（合理）','BALTHASAR（倫理）','CASPER（人間）'):
        if name not in blocks.get('PHILOSOPHY.MAGI',''):errors.append('NEXT_SPEC_ROLE:'+name)
    if '前処理の最後' not in blocks.get('RUNTIME.TIME.USER_FACING_JST_DISPLAY',''):
        errors.append('NEXT_SPEC_POST_PREPROCESS_CLOCK')
    for p in (root/'prompt').glob('*.md'):
        h=p.read_text().split('## 0. 文書の役割',1)[0]
        if ('現行指定はrev0.317' not in h or '所有者の明示採用' not in h
                or '`ACCEPTED_BY_OWNER / CURRENT_CANON_rev0.317`' not in h):
            errors.append('NEXT_SPEC_HEADER_AUTHORITY:'+p.name)
    replay=json.loads((root/'tests/fixtures/next_spec_20261103_model_replay.json').read_text())
    if replay['status']!='NOT_EXECUTED' or replay['live_model_pass'] is not False:
        errors.append('NEXT_SPEC_MODEL_RESULT_OVERCLAIM')
    return errors
