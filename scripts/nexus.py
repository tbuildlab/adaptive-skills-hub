#!/usr/bin/env python3
"""Nexus command alias; delegates to the compatible hub.py entry point."""
from __future__ import annotations

import sys
from pathlib import Path

# The release-owned embedded Python deliberately omits the script directory.
# Add only this checked-in sibling directory so the compatibility alias remains
# usable without system Python, PATH changes, or user site packages.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from hub import main


if __name__ == "__main__":
    raise SystemExit(main())
