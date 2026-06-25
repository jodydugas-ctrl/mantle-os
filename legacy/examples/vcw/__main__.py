#!/usr/bin/env python3
"""python -m vcw -- back-compat entry. The v3 entry point is `python -m mantle`;
this forwards the old command names so muscle memory keeps working."""
import sys

import _repo_path  # noqa: F401
from mantle import cli

_MAP = {"demo": "demo", "audit": "audit", "prove": "prove", "mind": "mind",
        "audit-mind": "audit-mind", "audit_mind": "audit-mind", "tour": "demo"}

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = _MAP.get(args[0] if args else "demo", args[0] if args else "demo")
    sys.exit(cli.main([cmd] + (args[1:] if args else [])))
