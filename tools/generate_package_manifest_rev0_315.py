#!/usr/bin/env python3
from pathlib import Path
from peos_public_release import write_manifest
if __name__ == '__main__':
    write_manifest(Path(__file__).resolve().parents[1])
