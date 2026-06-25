#!/usr/bin/env python3
"""test_invariants.py -- back-compat shim: the security invariants now live in
mantle/audits/invariants.py (32 red/green guards; the v2.3 sixteen all kept)."""
import sys

import _repo_path  # noqa: F401
from mantle.audits import invariants

run_all = invariants.run_all      # importable, as before

if __name__ == "__main__":
    sys.exit(invariants.main())
