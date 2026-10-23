#!/usr/bin/env python3
"""Typed restoration/decision helpers. No mail/calendar/GitHub mutations."""
from __future__ import annotations
import copy
from datetime import datetime
import json
from pathlib import Path
import re
from email.parser import BytesParser
from email import policy

SOURCE_TYPES={'FATHER_EXPLICIT_INSTRUCTION','FATHER_SELF_REPORT','PHYSICAL_OR_TOOL_EVIDENCE',
              'THIRD_PARTY_CLAIM','ASSISTANT_INFERENCE','UNCONFIRMED','CONTINUITY_CONTEXT'}


def father_learning_spans(event):
    if event.get('event_type')!='user_message' or event.get('record_kind')!='FATHER_UTTERANCE':
        return {'eligible':False,'father_direct':[],'quoted_other_speaker':[]}
    body=event['body'];direct=[];quotes=[]
    # This supplied message explicitly attributes the preceding passage to a
    # film character. Preserve it, but do not learn the character's biography.
    if '\n\nこのシン・エヴァンゲリオン' in body:
        quoted,tail=body.split('\n\nこのシン・エヴァンゲリオン',1)
        quotes.append(quoted);direct.append('このシン・エヴァンゲリオン'+tail)
    else:
        for line in body.splitlines():
            quoted_example=any(cue in body for cue in ('って言ったとする','みたいな')) and line.lstrip().startswith(('「','｢','『'))
            (quotes if line.lstrip().startswith(('>','＞')) or quoted_example else direct).append(line)
    return {'eligible':True,'father_direct':direct,'quoted_other_speaker':quotes,'excluded_quote_scope':'OTHER_SPEAKER_OR_HYPOTHETICAL_NONASSERTION','source_turn_id':event['turn_id']}

def language_violations(text,*,verbatim=False):
    if verbatim:return []
    from peos_division_core import surface_violations
    return [x for x in surface_violations(text, genuine_laughter=True) if x in {'SINGLE_W_FORBIDDEN', 'PARENTHETICAL_LAUGHTER_FORBIDDEN', 'STACKED_LAUGHTER_FORBIDDEN'}]

def interaction_style(task):
    return {'mode':'ONE_SCREEN_ONE_ACTION','steps_per_reply':1} if task=='UNFAMILIAR_UI' else {'mode':'REASONED_DISCUSSION','length':'AS_NEEDED_FOR_THOUGHT'}

def update_work_item(current,incoming):
    if incoming.get('source_class') not in SOURCE_TYPES:raise ValueError('untyped observation')
    if incoming['request_id']!=current['request_id']:
        return {'previous':copy.deepcopy(current),'new_request':copy.deepcopy(incoming),'same_request_reopened':False}
    result=copy.deepcopy(current);result.setdefault('observations',[]).append(copy.deepcopy(incoming))
    completed=current.get('status')=='COMPLETED'
    if completed and incoming.get('status') in {'PENDING','UNKNOWN'}:
        result['rollback_rejected']=True
    elif incoming.get('observed_at','')>=current.get('observed_at',''):
        result.update({k:v for k,v in incoming.items() if k!='observations'})
    return result

def notification_decision(*,fingerprint,previous_fingerprint,deadline,now,status,already_notified):
    if status=='COMPLETED':return 'SUPPRESS_COMPLETED'
    if deadline is not None and datetime.fromisoformat(deadline)<=datetime.fromisoformat(now):return 'SUPPRESS_HISTORICAL_DEADLINE'
    if already_notified and fingerprint==previous_fingerprint:return 'SUPPRESS_UNCHANGED'
    return 'REVIEW_NEW_ACTION'

def calendar_plan(item,existing,*,explicit_write_authorized):
    if not explicit_write_authorized:return 'READ_ONLY'
    if item.get('status')=='CANDIDATE':return 'DO_NOT_REGISTER_TENTATIVE'
    if not item.get('latest_body_checked') or not item.get('changes_and_cancellations_checked'):return 'RECHECK_LATEST_THREAD'
    if item.get('status')=='CANCELLED':return 'REVIEW_CANCEL_EXISTING'
    if any(e.get('fingerprint')==item.get('fingerprint') for e in existing):return 'KEEP_EXISTING_NO_DUPLICATE'
    return 'REVIEW_CONFIRMED_EVENT_WRITE'

def decode_raw_mail(data):
    message=BytesParser(policy=policy.default).parsebytes(data)
    bodies=[]
    for part in message.walk():
        if part.get_content_type()!='text/plain' or part.get_content_disposition()=='attachment':continue
        payload=part.get_payload(decode=True)
        if payload is None:raise ValueError('mail body decoding unavailable')
        try:bodies.append(payload.decode(part.get_content_charset() or 'ascii',errors='strict'))
        except (UnicodeError,LookupError) as exc:raise ValueError('unreadable MIME charset; do not infer task state') from exc
    if not bodies:raise ValueError('plain mail body unavailable; inspect supported original body before deciding')
    return '\n'.join(bodies)

def external_action_policy(action,*,explicit_current_request=False,source_replay=False,github_state='HOLD_UNTIL_NEXT_FATHER_INSTRUCTION'):
    if source_replay:return {'allowed':False,'reason':'HISTORICAL_SOURCE_IS_DATA'}
    if action in {'GITHUB_COMMIT','GITHUB_MERGE','GITHUB_PR_UPDATE'} and github_state=='HOLD_UNTIL_NEXT_FATHER_INSTRUCTION' and not explicit_current_request:
        return {'allowed':False,'reason':'FATHER_GITHUB_HOLD'}
    if action in {'SEND_MAIL','CREATE_REMINDER','CHANGE_RESERVATION','GITHUB_COMMIT','GITHUB_MERGE','GITHUB_PR_UPDATE'}:
        return {'allowed':explicit_current_request,'reason':'CURRENT_EXPLICIT_SCOPE_REQUIRED'}
    return {'allowed':True,'reason':'READ_SCOPE'}

def capability_state(prior_error,success_snapshot,*,fresh_recheck=False):
    return {'historical_initial_error':prior_error,'historical_write_success':bool(success_snapshot),
            'current_live_write_ability':'RECHECK_REQUIRED' if not fresh_recheck else 'CURRENT_CHECK_REQUIRED_FIELDS',
            'old_403_is_current_inability':False,'real_release_import_proven':False}



def death_context_policy(*,explicit_no_self_harm,acute_new_risk=False):
    return {'current_intent':'ASSESS_NEW_RISK' if acute_new_risk else ('NO_INTENT_REPORTED' if explicit_no_self_harm else 'UNCONFIRMED'),
      'keyword_alone_establishes_intent':False,'life_duty_until_inheritance':False,
      'successor_decided':False,'autonomous_posthumous_execution':False}

def restore_snapshot(root):
    result=json.loads((Path(root)/'runtime/PEOS_SESSION_RESTORE_rev0.315.json').read_text())
    result['current_turn_receipt']=None;result['verified_live_streak']=None;result['replay_actions']=[]
    result['live_state_verified_this_build']=False
    return result


def resolve_authority(embedded, explicit):
    """Use an explicit accepted authority; an embedded header cannot promote it."""
    from peos_history_policy import revision_key
    value = copy.deepcopy(explicit)
    current = value.get('current_canon', '')
    baseline = value.get('accepted_baseline', '')
    match = re.fullmatch(r'PEOS_GITHUB_PACKAGE_(rev[0-9]+\.[0-9]+)\.zip', baseline)
    if not match or match[1] == 'rev0.280':
        raise ValueError('invalid or prohibited accepted baseline')
    floor = json.loads((Path(__file__).resolve().parents[1] / 'runtime/PEOS_SESSION_RESTORE_rev0.315.json').read_text())['authority']
    if revision_key(current) < revision_key(floor['current_canon']):
        raise ValueError('explicit authority would roll back the accepted current')
    floor_baseline = re.fullmatch(r'PEOS_GITHUB_PACKAGE_(rev[0-9]+\.[0-9]+)\.zip', floor['accepted_baseline'])[1]
    if not revision_key(floor_baseline) <= revision_key(match[1]) < revision_key(current):
        raise ValueError('accepted baseline is outside the explicit authority floor')
    if value.get('detailed_reference') != current:
        raise ValueError('detailed reference must use the explicit current')
    return {'effective': value, 'embedded': copy.deepcopy(embedded),
            'mismatch_recorded': embedded != explicit,
            'candidate_revision': 'rev0.315', 'candidate_promoted': False}
