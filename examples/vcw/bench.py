#!/usr/bin/env python3
"""
bench.py -- non-normative micro-benchmark for the VCW substrate hot paths.

Times the operations the optimization targets: appends, full-organism saves (the staged commit),
context-style band reads, and a rebirth-with-ancestors save. Prints wall-clock totals so a
before/after comparison is concrete. NOT part of the audit; purely a measurement tool.

Run:  python bench.py            (defaults)
      python bench.py 400 40 300 (appends, saves, reads)
"""
from __future__ import annotations

import os
import sys
import time
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lineage import Organism, standard_genome  # noqa: E402
from drivers import make_entry                   # noqa: E402


def _t():
    return time.perf_counter()


def main(argv):
    n_append = int(argv[1]) if len(argv) > 1 else 400
    n_save = int(argv[2]) if len(argv) > 2 else 40
    n_read = int(argv[3]) if len(argv) > 3 else 300

    org = Organism.birth(identity={"name": "bench"}, truths=["t"], commandments=["c"],
                         genome=standard_genome())
    bands = ["facts", "events", "senses", "discoveries"]
    d = tempfile.mkdtemp(prefix="vcwbench_")
    path = os.path.join(d, "org")

    # 1) append throughput
    t0 = _t()
    for i in range(n_append):
        b = bands[i % len(bands)]
        org.prime.append(b, make_entry({"i": i, "payload": "x" * 64}, opcode="W", author="BODY"))
    t_append = _t() - t0

    # 2) save throughput (the staged commit) — append a little + save each round
    t0 = _t()
    for r in range(n_save):
        org.prime.append("events", make_entry({"r": r}, opcode="W", author="BODY"))
        org.save(path)
    t_save = _t() - t0

    # 3) read throughput (context-assembly style: read several bands repeatedly)
    t0 = _t()
    for _ in range(n_read):
        for b in ("identity", "facts", "events", "discoveries", "senses"):
            org.prime.read(b)
    t_read = _t() - t0

    # 4) rebirth then save (exercises ancestral re-save cost)
    org.rebirth(reason="bench")
    for i in range(50):
        org.prime.append("facts", make_entry({"g": i}, opcode="W", author="BODY"))
    t0 = _t()
    for r in range(max(5, n_save // 4)):
        org.prime.append("events", make_entry({"r": r}, opcode="W", author="BODY"))
        org.save(path)
    t_anc = _t() - t0

    print("VCW bench (appends=%d, saves=%d, read-rounds=%d)" % (n_append, n_save, n_read))
    print("  append %5d entries        : %8.3f s  (%.1f us/entry)" %
          (n_append, t_append, t_append / max(1, n_append) * 1e6))
    print("  save   %5d times (staged)  : %8.3f s  (%.1f ms/save)" %
          (n_save, t_save, t_save / max(1, n_save) * 1e3))
    print("  read   %5d band-reads      : %8.3f s  (%.1f us/read)" %
          (n_read * 5, t_read, t_read / max(1, n_read * 5) * 1e6))
    print("  save   w/ 1 ancestor        : %8.3f s  (%.1f ms/save)" %
          (t_anc, t_anc / max(1, max(5, n_save // 4)) * 1e3))
    print("  TOTAL                       : %8.3f s" % (t_append + t_save + t_read + t_anc))


if __name__ == "__main__":
    main(sys.argv)
