#!/usr/bin/env python3
"""Regenerate the checked-in germ spores from the germ files in examples/eggs/.

A germ spore is THE one artifact that births an AppAI: a single PNG carrying the
complete build data (the germ) plus build instructions any coding agent can read.

    python examples/spores/make_spores.py          # rewrites the PNGs beside this file

Requires Pillow (pip install mantle-os[spore]).
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))

from mantle import spore  # noqa: E402

GERMS = ("greeter.json", "calculator.json", "notes_graft.json")


def main() -> int:
    for name in GERMS:
        germ_path = os.path.join(REPO, "examples", "eggs", name)
        with open(germ_path, encoding="utf-8") as f:
            germ = json.load(f)
        out = os.path.join(HERE, name.replace(".json", ".png"))
        spore.pack_germ(germ, out)
        report = spore.verify_spore(out)
        status = "ok" if report["ok"] else "PROBLEMS: %s" % report["problems"]
        print("%s -> %s  (%s)" % (name, os.path.basename(out), status))
        if not report["ok"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
