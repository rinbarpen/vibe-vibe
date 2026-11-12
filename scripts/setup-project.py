#!/usr/bin/env python3
"""Project setup without globally installing vibe, uv, or Bash (Python 3.10+)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/vibe_tool/src'))
from vibe_tool.setup import main

if __name__ == '__main__':
    raise SystemExit(main(repo=ROOT))
