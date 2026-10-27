#!/usr/bin/env python3
"""Rebuild the optional L0 projection from its five-canon owner."""
from pathlib import Path
import hashlib, json, re
ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    name = 'prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md'
    data = (ROOT/name).read_bytes()
    block = re.search(r'<!-- L0_BOOT_SHIM_SOURCE_BEGIN -->.*?<!-- L0_BOOT_SHIM_SOURCE_END -->', data.decode(), re.S)[0]
    sha = hashlib.sha256(data).hexdigest()
    text = 'PEOS L0 BOOT SHIM\nREVISION: rev0.316\nIS_CANON: FALSE\nIS_SIXTH_CANON: FALSE\nRULE_OWNER: RUNTIME_GUARD\nSOURCE_CANON_SHA256: '+sha+'\n\n'+block+'\n'
    (ROOT/'bootstrap/PEOS_L0_BOOT_SHIM.txt').write_text(text)
    (ROOT/'bootstrap/PEOS_L0_BOOT_SHIM_BINDING.json').write_text(json.dumps({'source_canon': name, 'source_sha256': sha, 'projection_sha256': hashlib.sha256(text.encode()).hexdigest(), 'is_canon': False, 'required_install_attachment': False}, ensure_ascii=False, indent=2)+'\n')
