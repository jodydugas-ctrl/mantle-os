#!/usr/bin/env python3
"""audit.py -- back-compat shim: the Stage-1 Zombie Body gate now lives in
mantle/audits/stage1.py. `python audit.py [--break-hash|--break-primer|--break-seal]`
keeps working from this directory exactly as it did in v2.3."""
import sys

import _repo_path  # noqa: F401
from mantle.audits import stage1

if __name__ == "__main__":
    sys.exit(stage1.main(sys.argv[1:]))
