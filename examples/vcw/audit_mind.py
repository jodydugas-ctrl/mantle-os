#!/usr/bin/env python3
"""audit_mind.py -- back-compat shim: the Stage-2 MIND gate now lives in
mantle/audits/stage2.py (offline stub transport; containment + full Stage-1 regression)."""
import sys

import _repo_path  # noqa: F401
from mantle.audits import stage2

if __name__ == "__main__":
    sys.exit(stage2.main(sys.argv[1:]))
