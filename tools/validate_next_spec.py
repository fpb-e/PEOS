#!/usr/bin/env python3
"""Validate the unnumbered public candidate, not live model acceptance."""
import runpy
from pathlib import Path
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('validate_rev0_316.py')), run_name='__main__')
