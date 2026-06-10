#!/usr/bin/env python3
"""python -m mantle -- the v3 entry point. See mantle/cli.py for the commands."""
import sys

from .cli import main

sys.exit(main() or 0)
