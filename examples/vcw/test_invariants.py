#!/usr/bin/env python3
"""
test_invariants.py  --  Executable security invariants for the VCW substrate (Mantle v2.3)

Turns the audit's *security* hard-fails from prose into red/green assertions. Each test maps
to a hard-fail code and proves the guard actually fires. Pure standard library (no pytest):

    python test_invariants.py          # run all; exit 0 = all green, 1 = a guard failed

Also importable: `run_all()` returns a list of result dicts so the audit harness (audit.py)
can fold these in as evidence.

Covered: HF-B07 (Primer immutability), HF-B20 (secret boundary), HF-B29 (authorship in hash),
HF-B46 (ancestral write), HF-B47 (exec integrity), HF-B48 (capability gate), HF-B50 (exec trust
gate), HF-B51 (static sandbox gate), B-14 (the veil).
"""
from __future__ import annotations

import sys

from lineage import Organism, standard_genome, Cube, make_band_boot
from body import Body
from drivers import (ExecDriver, code_hash, make_entry, trial,
                     CapabilityError, IntegrityError, TrustError, SandboxError)
from mind import Mind, stub_mind, WRITE_SURFACE
from redact import redact, contains_secret
from audit_helpers import expect_raise as _expect_raise

_EXEC = ExecDriver()
_CODE = "def f(x):\n    return x + 1\n"


def _born():
    return Organism.birth(identity={"name": "TestAppAI"},
                          truths=["if it is not in the VCW it did not happen"],
                          commandments=["protect your VCW"])


def _exec_content(provenance, runner="python", caps=None, bad_hash=False):
    return {"code": _CODE, "code_hash": ("sha256:deadbeef" if bad_hash else code_hash(_CODE)),
            "entry": "f", "runner": runner, "capabilities": caps or {},
            "limits": {"ms": 200}, "provenance": provenance}


# ---- the invariants --------------------------------------------------------
def t_primer_immutable():
    """HF-B07: the Primer is sealed at birth; a second birth must be refused."""
    b = Body()
    b.birth(identity={"name": "X"}, truths=["t"], commandments=["c"])
    return _expect_raise(lambda: b.birth(identity={"name": "Y"}, truths=["t2"],
                                         commandments=["c2"]), PermissionError)


def t_secret_boundary_sense():
    """HF-B20: a secret in an inbound signal is redacted before it enters the senses band."""
    org = _born()
    org.sense({"event": "login", "authorization": "Bearer sk-ABCD1234EFGH5678IJKL",
               "api_key": "AKIAQWERTYUIOPASDFGH"})
    stored = org.prime.read("senses")[-1]["content"]
    if contains_secret(stored):
        return False, "secret survived into senses: %r" % stored
    return True, "senses entry redacted: %r" % stored


def t_secret_boundary_immune():
    """HF-B20: secrets are redacted before they reach the immune log too."""
    org = _born()
    org.immune_event("suspicious", {"token": "eyJabc.def123456789.ghiJKLmnop",
                                     "note": "leaked?"})
    stored = org.prime.read("immune")[-1]["content"]
    return (not contains_secret(stored)), "immune entry: %r" % stored


def t_veil_hides_thoughts():
    """B-14: the private `thoughts` band is veiled on normal read, visible only with reveal."""
    org = _born()
    org.prime.append("thoughts", make_entry("a private musing", opcode="THINK", author="MIND"))
    veiled = org.prime.read("thoughts")
    revealed = org.prime.read("thoughts", reveal_private=True)
    ok = (veiled == [] and len(revealed) == 1)
    return ok, "veiled=%r revealed=%d" % (veiled, len(revealed))


def t_ancestral_readonly():
    """HF-B46: after rebirth the sealed ancestral cube must reject experiential writes."""
    org = _born()
    org.prime.append("facts", make_entry({"k": "host", "v": "test"}))
    org.rebirth(reason="test reformat")
    ancestral = org.ancestral[0]
    return _expect_raise(
        lambda: ancestral.append("facts", make_entry({"k": "x", "v": "y"})), PermissionError)


def t_exec_integrity():
    """HF-B47: an exec layer whose code does not match its hash must be refused."""
    return _expect_raise(
        lambda: _EXEC.execute(_exec_content({"author": "MIND"}, bad_hash=True), {"x": 1}),
        IntegrityError)


def t_exec_capability():
    """HF-B48: a call requesting a capability the layer never declared must be refused."""
    content = _exec_content({"author": "MIND"}, caps={"reads": []})
    return _expect_raise(
        lambda: _EXEC.execute(content, {"x": 1}, {"reads": ["facts"]}), CapabilityError)


def t_exec_trust_foreign():
    """HF-B50: a foreign-provenance skill must not run on the non-isolating Python runner."""
    content = _exec_content({"author": "MIND", "foreign": True})
    return _expect_raise(lambda: _EXEC.execute(content, {"x": 1}), TrustError)


def t_authorship_in_hash():
    """HF-B29: the dispatch `authorship` field lives INSIDE the entry hash, so a rewrite is caught
    by verify() -- 'what your organ does, you have done' is true by construction, not convention."""
    org = _born()
    org.prime.append("brain", make_entry({"phase": "COMPLETED"}, opcode="DISPATCH",
                                          author="BODY", authorship="BODY"))
    idx = org.prime.band_layers["brain"][0]
    org.prime.layers[idx][-1]["authorship"] = "MIND"          # malicious in-place rewrite
    problems = org.prime.verify()
    caught = any("hash mismatch" in p for p in problems)
    return caught, "verify caught the rewrite: %r" % problems


def t_sandbox_escape_refused():
    """HF-B51: a skill attempting a namespace escape (dunder traversal to reach os/subclasses) is
    refused at the cultivation/trial gate -- it never becomes a reflex."""
    evil = "def f(x):\n    return ().__class__.__bases__[0].__subclasses__()\n"
    return _expect_raise(lambda: trial(evil, "f", [({"x": 1}, None)]), SandboxError)


def t_sandbox_import_refused():
    """HF-B51: a skill that tries to `import` is refused at the cultivation/trial gate."""
    evil = "def f(x):\n    import os\n    return os.getpid()\n"
    return _expect_raise(lambda: trial(evil, "f", [({"x": 1}, None)]), SandboxError)


def t_exec_trust_trusted_runs():
    """HF-B50 (converse): an in-lineage MIND/BODY skill still runs normally (no false positive)."""
    content = _exec_content({"author": "MIND", "born_gen": 0})
    try:
        got = _EXEC.execute(content, {"x": 41})
    except Exception as e:  # noqa: BLE001
        return False, "trusted skill wrongly refused: %s" % e
    return (got == 42), "trusted skill returned %r (expected 42)" % got


def t_mind_write_surface():
    """HF-M10: a fused MIND may write ONLY thoughts/brain. Any other band is refused by the Body
    and logged as an immune event -- the MIND can extend, never break, the Body."""
    org = _born()
    m = Mind(org, stub_mind)
    before = len(org.immune_log)
    try:
        m._guarded_write("facts", make_entry({"k": "x"}))
        return False, "non-surface write was ALLOWED (containment breached)"
    except PermissionError:
        pass
    return (len(org.immune_log) == before + 1,
            "write to 'facts' refused + immune-logged; surface=%s" % list(WRITE_SURFACE))


def t_mind_no_self_promote():
    """HF-M12: the MIND cannot self-promote a skill -- a sandbox-escape candidate is refused at
    trial and never calcified into a reflex (the Body calcifies only what passed trial)."""
    genome = standard_genome() + [make_band_boot("reflex_probe", 600, "exec")]
    org = Organism.birth(identity={"name": "X"}, truths=["t"], commandments=["c"], genome=genome)
    m = Mind(org, stub_mind)
    res = m.cultivate("reflex_probe", "def f(x):\n    return ().__class__\n", "f",
                      [({"x": 1}, None)], {}, {})
    empty = not org.prime.layers[org.prime.primary_layer("reflex_probe")]
    return (res is None and empty, "escape skill refused at trial; band stays un-calcified")


def t_waste_reclaim_reuse():
    """B-W2 (waste axis): compaction must reclaim an emptied layer into the band's free pool,
    and the next allocation must REUSE that freed index — 'every layer has a purpose; be efficient.'"""
    cube = Cube.genesis([make_band_boot("log", 600, "log-json", span=4,
                                        params={"max_entries_per_layer": 2}, purpose="rolling log")], 0)
    for i in range(4):                       # 2 per layer → rolls onto a 2nd physical layer
        cube.append("log", make_entry({"i": i}))
    layers_before = list(cube.band_layers["log"])
    if len(layers_before) < 2:
        return False, "band did not roll onto a 2nd layer: %r" % layers_before
    first = layers_before[0]
    for e in cube.layers[first]:             # empty the FIRST (non-tail) layer
        e["tombstone"] = True
    res = cube.compact("log")
    if res["reclaimed"] < 1 or first not in cube.band_free["log"]:
        return False, "compact did not reclaim the emptied layer: %r free=%r" % (res, cube.band_free["log"])
    # the next allocation must drain the reuse pool (reuse `first`), not grow into a fresh index
    freed = list(cube.band_free["log"])
    for i in range(2):                       # fill the current tail, forcing one new allocation
        cube.append("log", make_entry({"j": i}))
    reused = first not in cube.band_free["log"] and first in cube.band_layers["log"]
    return reused, "reclaimed %d; reused freed layer %d (pool was %r)" % (res["reclaimed"], first, freed)


def t_waste_on_demand_and_purpose():
    """B-W4 (waste axis): bands reserve a RANGE but materialize layers ON DEMAND (only the head at
    genesis, not the whole span), and every band declares a non-empty purpose."""
    genome = standard_genome()
    cube = Cube.genesis(genome, 0)
    # only one physical layer per band at birth, even though spans are 50–100 wide
    over = {b: len(cube.band_layers[b]) for b in cube.bands if len(cube.band_layers[b]) != 1}
    if over:
        return False, "genesis pre-allocated beyond the head layer: %r" % over
    total_layers = len(cube.layers)
    spans = sum(b["span"] for b in genome)
    missing_purpose = [b["band"] for b in genome if not str(b.get("purpose") or "").strip()]
    if missing_purpose:
        return False, "bands missing a declared purpose: %r" % missing_purpose
    return True, "%d head layers materialized for %d reserved (span sum); all bands have a purpose" % (total_layers, spans)


TESTS = [
    ("HF-B07 primer-immutable", t_primer_immutable),
    ("HF-B20 secret-boundary/senses", t_secret_boundary_sense),
    ("HF-B20 secret-boundary/immune", t_secret_boundary_immune),
    ("B-14  veil-hides-thoughts", t_veil_hides_thoughts),
    ("HF-B29 authorship-in-hash", t_authorship_in_hash),
    ("HF-B46 ancestral-read-only", t_ancestral_readonly),
    ("HF-B47 exec-integrity-gate", t_exec_integrity),
    ("HF-B48 exec-capability-gate", t_exec_capability),
    ("HF-B50 exec-trust/foreign-refused", t_exec_trust_foreign),
    ("HF-B50 exec-trust/trusted-runs", t_exec_trust_trusted_runs),
    ("HF-B51 sandbox/escape-refused", t_sandbox_escape_refused),
    ("HF-B51 sandbox/import-refused", t_sandbox_import_refused),
    ("HF-M10 mind/write-surface", t_mind_write_surface),
    ("HF-M12 mind/no-self-promote", t_mind_no_self_promote),
    ("B-W2  waste/reclaim-reuse", t_waste_reclaim_reuse),
    ("B-W4  waste/on-demand+purpose", t_waste_on_demand_and_purpose),
]


def run_all():
    results = []
    for name, fn in TESTS:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001 -- a test harness must not crash on a bad guard
            ok, detail = False, "test crashed: %s: %s" % (type(e).__name__, e)
        results.append({"name": name, "ok": bool(ok), "detail": detail})
    return results


def main():
    results = run_all()
    width = max(len(r["name"]) for r in results)
    for r in results:
        print("  [%s] %-*s  %s" % ("PASS" if r["ok"] else "FAIL", width, r["name"], r["detail"]))
    passed = sum(r["ok"] for r in results)
    print("\n%d/%d invariants green" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
