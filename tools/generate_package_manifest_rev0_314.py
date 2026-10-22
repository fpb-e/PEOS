#!/usr/bin/env python3
"""Regenerate only the public tree's manifest; reject private inputs first."""
import json
from pathlib import Path
from peos_public_release import publication_errors, write_manifest

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    p = json.loads((root / 'admin/PUBLIC_EXPORT_PROVENANCE_rev0.314.json').read_text())
    errors = publication_errors(root, set(p['excluded_original_sha256']))
    if errors:
        raise SystemExit('\n'.join(errors))
    write_manifest(root)
    print('Public manifest generated; private corpus verification not claimed.')
