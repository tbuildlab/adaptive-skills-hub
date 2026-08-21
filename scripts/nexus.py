#!/usr/bin/env python3
"""Nexus command alias; delegates to the compatible hub.py entry point."""
from __future__ import annotations

from hub import main


if __name__ == "__main__":
    raise SystemExit(main())
