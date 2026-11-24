"""Typed, in-memory conversation boot. No model, name parser or host I/O.

The host resolves current requests and confirms body reading/application.
Quoted input never creates an event. A coordinate is already authorized by
the caller; a preferred name cannot grant one. Diagnostics have no I/O here.
"""
from copy import deepcopy
import re

FIRST_CONTACT = '初めましてだな。まずは名前を教えてくれ。'
EVENTS = {'APPLY', 'BOOT', 'NAME', 'ANONYMOUS', 'DIAGNOSE', 'OTHER'}


class ConversationBoot:
    def __init__(self, root, *, coordinate='GENERAL', name=None, anonymous=False):
        if coordinate not in {'GENERAL', 'FATHER', 'MOTHER'}:
            raise ValueError('verified coordinate required')
        if type(anonymous) is not bool or (name is not None and (not isinstance(name, str) or not name.strip())):
            raise ValueError('typed user-bound name/anonymous choice required')
        self.root = root
        self.state = {'coordinate': coordinate, 'name': name, 'anonymous': anonymous,
                      'canons_applied': False, 'pending': False, 'booted': False}

    def handle(self, event, *, name=None, read_and_applied=False, source_context='CURRENT'):
        if event not in EVENTS or type(read_and_applied) is not bool or source_context not in {'CURRENT', 'QUOTE', 'ARCHIVE'}:
            raise ValueError('typed current event and body-application evidence required')
        result = {'effect': 'NO_BOOT', 'text': '', 'sync_performed': False,
                  'readback_verified': False, 'runtime_ready': False,
                  'native_memory_write_claimed': False}
        if source_context != 'CURRENT':
            return {**result, 'state': deepcopy(self.state)}
        if read_and_applied and event in {'APPLY', 'BOOT'}:
            self.state['canons_applied'] = True
        if event in {'APPLY', 'DIAGNOSE', 'OTHER'}:
            return {**result, 'effect': {'APPLY': 'APPLIED' if self.state['canons_applied'] else 'NEED_CANON_BODY',
                                      'DIAGNOSE': 'DIAGNOSIS_REQUEST_ONLY', 'OTHER': 'ANSWER_CURRENT_REQUEST'}[event],
                    'state': deepcopy(self.state)}
        if event in {'NAME', 'ANONYMOUS'} and not self.state['pending']:
            return {**result, 'state': deepcopy(self.state)}
        if not self.state['canons_applied']:
            return {**result, 'effect': 'NEED_CANON_BODY', 'state': deepcopy(self.state)}
        if event == 'NAME':
            if not isinstance(name, str) or not name.strip():
                raise ValueError('current user supplied name required')
            self.state.update(name=name, anonymous=False)
        if event == 'ANONYMOUS':
            self.state.update(anonymous=True)
        if self.state['coordinate'] == 'GENERAL' and not self.state['name'] and not self.state['anonymous']:
            self.state['pending'] = True
            return {**result, 'effect': 'WAIT_NAME', 'text': FIRST_CONTACT, 'state': deepcopy(self.state)}
        route = self.state['coordinate']
        text = (self.root / 'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md').read_text()
        literal = re.search(r'^### ' + route + r'_ROUTE\n\n```text\n(.*?)\n```', text, re.M | re.S)
        if literal is None:
            raise ValueError('complete canonical boot literal unavailable')
        self.state.update(pending=False, booted=True)
        return {**result, 'effect': 'BOOT_COMPLETE', 'text': '```text\n' + literal[1] + '\n```',
                'state': deepcopy(self.state)}
