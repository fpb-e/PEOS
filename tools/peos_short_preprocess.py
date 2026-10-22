#!/usr/bin/env python3
"""One-append/one-ACK-sync reference. No live adapter or host hook is installed.

Tests inject clocks and stores and write temporary files only. Import does not
capture time, open a private ledger, or contact an external service.
"""
from __future__ import annotations
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Protocol

class PreprocessError(ValueError): pass
class VersionConflict(PreprocessError): pass

def digest(data): return hashlib.sha256(data).hexdigest()
def encode(obj): return (json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def actual_jst(): return datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds')
def valid_jst(stamp):
    try:
        value=datetime.fromisoformat(stamp)
        return value.tzinfo is not None and value.utcoffset().total_seconds()==32400 and stamp.endswith('+09:00')
    except (ValueError,TypeError,AttributeError): return False

def validate_learning(updates):
    if not isinstance(updates,list): raise PreprocessError('learning delta must be a list; empty is valid')
    for item in updates:
        if not isinstance(item,dict) or item.get('source_class') not in {'FATHER_EXPLICIT_INSTRUCTION','FATHER_SELF_REPORT','FATHER_CORRECTION'}:
            raise PreprocessError('non-father material cannot be a father learning delta')
        if not item.get('source_turn_id') or not item.get('source_span'):
            raise PreprocessError('learning update must bind an original turn and span')
        if item.get('quoted_other_speaker',False): raise PreprocessError('quoted speaker is not father')

class DurableTurnJournal:
    """A time ledger entry also preserves raw source and its typed learning delta."""
    def __init__(self,path): self.path=Path(path);self.append_count=0
    def _records(self,data):
        if data and not data.endswith(b'\n'):raise PreprocessError('truncated journal')
        rows=[json.loads(line) for line in data.splitlines()]
        if [r.get('seq') for r in rows]!=list(range(1,len(rows)+1)):raise PreprocessError('journal sequence mismatch')
        if len({r.get('turn_id') for r in rows})!=len(rows):raise PreprocessError('duplicate turn identity')
        return rows
    def find(self,turn_id):
        if not self.path.exists():return None
        return next((r for r in self._records(self.path.read_bytes()) if r['turn_id']==turn_id),None)
    def append(self,turn_id,stamp,raw,updates,provider='EXPLICIT_TEST_PROVIDER'):
        if not turn_id or not valid_jst(stamp) or not isinstance(raw,str):raise PreprocessError('invalid turn receipt/body')
        validate_learning(updates)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('a+b') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX);stream.seek(0);before=stream.read();rows=self._records(before)
            existing=next((r for r in rows if r['turn_id']==turn_id),None)
            if existing:
                if (existing['observed_at_jst'],existing['body_verbatim'],existing['learning_updates'])!=(stamp,raw,updates):
                    raise PreprocessError('immutable retry receipt/body/delta differs')
                stream.flush();os.fsync(stream.fileno())
                return existing,before,False
            row={'seq':len(rows)+1,'turn_id':turn_id,'observed_at_jst':stamp,'body_verbatim':raw,
                 'learning_updates':copy.deepcopy(updates),'source_class':'CURRENT_TURN_OBSERVED',
                 'clock_evidence':provider}
            data=encode(row);stream.seek(0,2)
            if stream.write(data)!=len(data):raise OSError('incomplete durable append')
            stream.flush();os.fsync(stream.fileno())
            directory_fd=os.open(self.path.parent,os.O_RDONLY)
            try:os.fsync(directory_fd)
            finally:os.close(directory_fd)
            self.append_count+=1
            return row,before+data,True

class SyncAdapter(Protocol):
    def replace(self,identity:str,expected_version:int,payload:bytes)->dict: ...

class SyntheticAckStore:
    """Test-only store, explicitly not a live Library implementation."""
    def __init__(self,identity='SYNTHETIC_LEDGER',version=0,fail=False):
        self.identity=identity;self.version=version;self.fail=fail;self.sync_calls=[];self.readback_calls=0;self.data=b''
    def replace(self,identity,expected_version,payload):
        self.sync_calls.append({'identity':identity,'expected_version':expected_version,'sha256':digest(payload)})
        if self.fail:raise OSError('synthetic sync unavailable')
        if identity!=self.identity or expected_version!=self.version:raise VersionConflict('concrete expected version differs')
        self.data=payload;self.version+=1
        return {'status':'succeeded','library_file_id':identity,'version':self.version,'file_id':f'SYNTHETIC_FILE_{self.version}'}

class ShortPreprocessor:
    def __init__(self,journal,adapter,identity,known_version,*,version_basis='CURRENT_ENVIRONMENT_RESOLVED',clock=actual_jst):
        self.journal=journal;self.adapter=adapter;self.identity=identity;self.version=known_version
        self.version_basis=version_basis;self.clock=clock;self.mode='ACTIVE';self.exempt_turn=None
        self.ack_path=journal.path.with_suffix('.ack.json')
    def control(self,action,turn_id=None):
        if action=='ONE_TURN_EXEMPT':
            if not turn_id:raise PreprocessError('one-turn exemption requires the current turn identity')
            self.exempt_turn=turn_id
        elif action=='PAUSE':self.mode='PAUSED'
        elif action=='RESUME':self.mode='ACTIVE';self.exempt_turn=None
        else:raise PreprocessError('unknown scope transition')
    def _save_ack(self,value):
        temp=self.ack_path.with_suffix('.tmp')
        with temp.open('wb') as stream:stream.write(encode(value));stream.flush();os.fsync(stream.fileno())
        os.replace(temp,self.ack_path)
        fd=os.open(self.ack_path.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    def _cached(self,turn_id):
        if self.ack_path.exists():
            value=json.loads(self.ack_path.read_text())
            if value['turn_id']==turn_id:return value
        return None
    def dispatch(self,turn_id,raw,updates,work=lambda:None,*,route='NORMAL'):
        # Startup and urgent assistance never wait for ledger I/O. These outcomes
        # are not synchronization successes or legacy acceptance streak credit.
        special='BOOT_PRIORITY' if route=='BOOT' else ('EMERGENCY_BYPASS' if route=='URGENT_SAFETY' else None)
        exempt=self.exempt_turn==turn_id
        if exempt:self.exempt_turn=None
        if not special and exempt:special='ONE_TURN_EXEMPT'
        if not special and self.mode=='PAUSED':special='PAUSED'
        if special:return {'status':special,'receipt':None,'prefix':'','work_result':work(),'sync_performed':False,'legacy_streak_credit':0}
        result={'status':'FAIL','receipt':None,'sync_performed':False,'readback_performed':False,
                'readback_verified':False,'legacy_streak_credit':0,'verified_live_streak':None,'work_authorized':False}
        try:
            validate_learning(updates)
            if any(u['source_turn_id']!=turn_id or u['source_span'] not in raw for u in updates):
                raise PreprocessError('learning delta must bind this exact raw turn span')
            previous=self.journal.find(turn_id)
            stamp=previous['observed_at_jst'] if previous else self.clock()
            provider='PYTHON_DATETIME_ZONEINFO_ASIA_TOKYO' if self.clock is actual_jst else 'EXPLICIT_INJECTED_PROVIDER'
            row,payload,added=self.journal.append(turn_id,stamp,raw,updates,provider)
            result.update(receipt=stamp,local_sha256=digest(payload),local_seq=row['seq'],local_lines=len(payload.splitlines()),local_append_added=added)
            result['status']='DEGRADED'
            cached=self._cached(turn_id)
            if cached:
                if cached['local_sha256']!=digest(payload):raise PreprocessError('retry payload changed')
                ack=cached['ack'];result['duplicate_retry']=True
            else:
                if self.version_basis!='CURRENT_ENVIRONMENT_RESOLVED' or isinstance(self.version,bool) or not isinstance(self.version,int) or self.version<0:
                    raise PreprocessError('resolve current identity/version before normal sync; captured version is historical')
                ack=self.adapter.replace(self.identity,self.version,payload)
                if ack.get('status')!='succeeded' or ack.get('library_file_id')!=self.identity or ack.get('version')!=self.version+1 or not ack.get('file_id'):
                    raise PreprocessError('ACK identity/version/success mismatch')
                self._save_ack({'turn_id':turn_id,'local_sha256':digest(payload),'local_seq':row['seq'],'ack':ack,'readback_performed':False})
                result['sync_performed']=True
            self.version=ack['version'];result.update(status='SYNC_ACKNOWLEDGED',ack=ack,work_authorized=True)
            result['prefix']=render_prefix(result)
            result['work_result']=work()
        except (OSError,ValueError,KeyError,TypeError) as exc:
            result['failure']=str(exc);result['prefix']=render_prefix(result)
        return result

def render_prefix(result):
    if result.get('receipt') is None:return ''
    label={'SYNC_ACKNOWLEDGED':'同期済','DEGRADED':'同期要復旧','FAIL':'前処理失敗'}.get(result['status'],result['status'])
    return f"**USER_TURN_OBSERVED_AT_JST: {result['receipt']}｜前処理：{label}**"

def assert_success_wording(result,text):
    """Inspect the sync status label only, not unrelated artifact-test claims."""
    if not result.get('readback_verified') and any(word in text for word in ('照合済','検証済','readback PASS','SHA256 PASS')):
        raise PreprocessError('unperformed readback cannot be claimed')
    if result['status']!='SYNC_ACKNOWLEDGED' and '同期済' in text:raise PreprocessError('no successful ACK')
    return True
