#!/usr/bin/env python3
"""
mantle.check  --  the whole certification, one command (Mantle OS)

    python -m mantle check          run every gate, proof, demo, and test
    python -m mantle check --fast   skip the narrated demos (gates + proofs only)

This is the same sequence the CI workflow runs, made local and singular: the
Stage-1 Zombie Body gate, the three tamper proofs (which must FAIL to pass),
the executable security invariants, the Stage-2 MIND gate, both narrated demos, the
assimilation dry-run, the standalone cube codec conformance (selftest +
interop), the SPORE purity gates, and the multi-language parity test.

Repo-only steps (everything under examples/) are skipped honestly when the
package is installed without the repository checkout. Steps that need an
optional extra (Pillow for the spore gates) are skipped honestly when the
extra is absent -- a skip is named, never silent.

Exit code 0 = every executed step green; non-zero = at least one failure.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

from .paths import EXAMPLES_DIR, SAMPLE_APP_DIR, SRC_DIR

_LINE = "=" * 74


def _has_pillow() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def _steps(fast: bool):
    """Yield (name, argv, cwd, expect_fail, skip_reason) tuples in gate order."""
    py = sys.executable
    mantle = [py, "-m", "mantle"]
    repo = os.path.isdir(EXAMPLES_DIR)
    no_repo = None if repo else "examples/ not present (installed without the repo checkout)"
    no_pil = None if _has_pillow() else "Pillow not installed (pip install 'mantle-os[spore]')"

    yield ("Stage-1 Zombie Body gate", mantle + ["audit"], None, False, None)
    for flag in ("--break-hash", "--break-primer", "--break-seal"):
        yield ("tamper proof %s (must be CAUGHT)" % flag,
               mantle + ["audit", flag, "--fast"], None, True, None)
    yield ("security invariants", mantle + ["prove"], None, False, None)
    yield ("Stage-2 MIND gate", mantle + ["audit-mind"], None, False, None)
    if not fast:
        yield ("narrated Phase-1 demo", mantle + ["demo"], None, False, None)
        yield ("narrated Phase-2 fusion", mantle + ["mind"], None, False, None)
    yield ("assimilation dry-run", mantle + ["assimilate", SAMPLE_APP_DIR, "--dry-run"],
           None, False, no_repo)
    vcw_dir = os.path.join(EXAMPLES_DIR, "vcw")
    yield ("standalone cube codec selftest", [py, "vcw_cube.py", "selftest"],
           vcw_dir, False, no_repo)
    yield ("cube interop (standalone <-> engine)", [py, os.path.join(vcw_dir, "interop.py")],
           None, False, no_repo)
    spore_dir = os.path.join(EXAMPLES_DIR, "spore")
    yield ("SPORE purity gate", [py, os.path.join(spore_dir, "audit_spore.py")],
           None, False, no_repo or no_pil)
    yield ("SPORE VCW conformance", [py, os.path.join(spore_dir, "vcw_conformance.py")],
           None, False, no_repo or no_pil)
    yield ("multi-language parity (skips without tree-sitter)",
           [py, os.path.join(EXAMPLES_DIR, "tests", "test_multilang_parity.py")],
           None, False, no_repo)


def main(argv=None):
    argv = list(argv or [])
    fast = "--fast" in argv
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    print(_LINE)
    print("MANTLE OS CHECK  ·  the whole certification, one command%s"
          % ("  (--fast)" if fast else ""))
    print(_LINE)

    results = []
    for name, cmd, cwd, expect_fail, skip in _steps(fast):
        if skip:
            print("  [SKIP] %-45s %s" % (name, skip))
            results.append((name, "SKIP"))
            continue
        t0 = time.time()
        proc = subprocess.run(cmd, cwd=cwd, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        failed = (proc.returncode == 0) if expect_fail else (proc.returncode != 0)
        verdict = "FAIL" if failed else "PASS"
        print("  [%s] %-45s %5.1fs" % (verdict, name, time.time() - t0))
        if failed:
            tail = proc.stdout.decode(errors="replace").splitlines()[-12:]
            for line in tail:
                print("         | " + line)
        results.append((name, verdict))

    passed = sum(1 for _, v in results if v == "PASS")
    skipped = sum(1 for _, v in results if v == "SKIP")
    failures = [n for n, v in results if v == "FAIL"]
    print(_LINE)
    print("RESULT: %d passed, %d skipped, %d failed"
          % (passed, skipped, len(failures)))
    if failures:
        for n in failures:
            print("  FAILED: %s" % n)
        print(_LINE)
        return 1
    print("EVERY EXECUTED GATE GREEN. The organism is certified.")
    print(_LINE)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
