#!/usr/bin/env python3
"""examples_boot.py -- back-compat shim: the narrated Phase-1 tour is now
`python -m mantle demo` (mantle/cli.py)."""
import sys

import _repo_path  # noqa: F401
from mantle import cli


def main():
    return cli.demo([])


if __name__ == "__main__":
    sys.exit(main())
