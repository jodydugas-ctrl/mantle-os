#!/usr/bin/env python3
"""examples_mind.py -- back-compat shim: the narrated Phase-2 fusion tour is now
`python -m mantle mind` (mantle/cli.py; offline stub, no key/network)."""
import sys

import _repo_path  # noqa: F401
from mantle import cli


def main():
    return cli.mind_demo([])


if __name__ == "__main__":
    sys.exit(main())
