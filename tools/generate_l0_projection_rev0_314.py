#!/usr/bin/env python3
"""Generate a non-authoritative current-profile projection from its sole owner."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    source=ROOT/'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md';raw=source.read_bytes();text=raw.decode()
    begin='<!-- L0_BOOT_SHIM_SOURCE_BEGIN -->';end='<!-- L0_BOOT_SHIM_SOURCE_END -->'
    block=text[text.index(begin):text.index(end)+len(end)]+'\n'
    projection=('PEOS L0 BOOT SHIM\nREVISION: rev0.314\nIS_CANON: FALSE\nIS_SIXTH_CANON: FALSE\nRULE_OWNER: RUNTIME_GUARD\nSOURCE_CANON_SHA256: '+sha(raw)+'\nPROFILE: SHORT_ACK_SYNC\n\n'+block).encode()
    (ROOT/'bootstrap/PEOS_L0_BOOT_SHIM.txt').write_bytes(projection)
    binding={'revision':'rev0.314','source_canon_revision':'rev0.314','authority':'NON_AUTHORITATIVE_PROJECTION','is_sixth_canon':False,
      'source_canon':'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md','source_canon_sha256':sha(raw),'source_block_sha256':sha(block.encode()),
      'projection_sha256':sha(projection),'default_profile':'SHORT_ACK_SYNC','boot_priority':True,
      'optional_profile':'STRICT_READBACK_AUDIT','live_hook_installed':False,'live_adapter_installed':False}
    (ROOT/'bootstrap/PEOS_L0_BOOT_SHIM_BINDING.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps(binding,ensure_ascii=False))
if __name__=='__main__':main()
