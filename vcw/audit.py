#!/usr/bin/env python3
"""
audit.py  --  Stage-1 (Zombie Body) audit harness (Mantle v2.3)

`Mantle_Part1_Body_Audit.md` declares itself deterministic and machine-checkable
("every check can be performed by reading the cube, running the Body's reflexes, and
running vcw_cube.py verify. No human judgment"). This script *is* that runner: it loads
an Organism, evaluates the substrate-checkable Stage-1 rows programmatically, folds in the
security invariants (test_invariants.py), prints the Stage-1 sign-off block filled in, and
exits non-zero if any hard-fail is open.

Honesty rules:
  * Rows that need a running HOST app (heartbeat, surface parity, dispatch proofs, dual-flush)
    are reported NEEDS-HOST -- never silently passed. The reference agent's in-browser self-audit
    covers those; here we certify the substrate.
  * Phase-2 (MIND) rows are out of scope here (NEEDS-MODEL).

Usage:
  python audit.py                 # audit a fresh demo Organism (self-contained)
  python audit.py <organism_dir>  # audit an Organism saved by Organism.save()
  python audit.py --break-hash    # demo with a tampered entry  -> B-13 must FAIL (proves the harness)
  python audit.py --break-primer  # demo with Primer forced into the cube -> HF-B45/HF-B02 FAIL
  python audit.py --json          # also print the JSON evidence record
"""
from __future__ import annotations

import json
import sys

from lineage import Organism, standard_genome
from drivers import make_entry, _entry_hash
import test_invariants

PASS, FAIL, NA = "PASS", "FAIL", "N/A"
NEEDS_HOST, NEEDS_MODEL = "NEEDS-HOST", "NEEDS-MODEL"

# Stage-1 rows that require a live host application, not the substrate (kept visible, not passed).
HOST_ROWS = [
    ("B-04", "Heartbeat loop runs with no LLM", "HF-B08"),
    ("B-05", "Dual-flush: checkpoint + atexit", "HF-B33"),
    ("B-16", "Senses classifier deterministic & LLM-free", "HF-B09"),
    ("B-25", "Every visible control in the Human Surface Map", "HF-B44"),
    ("B-26", "Each control has a ControlBridge + recorded proof", "HF-B44"),
    ("B-29", "Dispatch authorship present & immutable", "HF-B29"),
    ("B-38", "Imports as module and as script", "HF-B34"),
]


def _row(code, requirement, result, hf=None, note=""):
    return {"code": code, "requirement": requirement, "hf": hf, "result": result, "note": note}


def audit_organism(org):
    rows = []

    # B-01 — substrate verify healthy
    problems = org.prime.verify()
    rows.append(_row("B-01", "Cube genesis valid; verify() healthy", PASS if not problems else FAIL,
                     note="clean" if not problems else "; ".join(problems)))

    # B-02 / HF-B02 — the AppAI is born (Primer present & non-empty)
    primer = org.body.self_record().get("primer") or []
    rows.append(_row("B-02", "Primer present and non-empty (AppAI is 'born')",
                     PASS if primer else FAIL, "HF-B02",
                     note="name=%s" % org.body.identity_name()))

    # B-03 / HF-B03 — canonical reserved band map
    expected = {b["band"]: b["head"] for b in standard_genome()}
    actual = {name: boot["head"] for name, boot in org.prime.bands.items()}
    missing = [b for b, h in expected.items() if actual.get(b) != h]
    rows.append(_row("B-03", "Band map matches canonical RESERVED_BANDS ranges",
                     PASS if not missing else FAIL, "HF-B03",
                     note="all 8 reserved bands at canonical heads" if not missing
                          else "deviation: %s" % missing))

    # HF-B45 — Primer lives in the BODY, not the cube
    genome_in_cube = [b for b in org.prime.bands if b.startswith("bodyentry") or b == "genome"]
    in_body_ok = bool(org.prime.identity_in_body) and not genome_in_cube and bool(primer)
    rows.append(_row("B-45", "Primer/commandments live in the BODY, not the cube",
                     PASS if in_body_ok else FAIL, "HF-B45",
                     note="identity_in_body=%s, genome-bands-in-cube=%s"
                          % (org.prime.identity_in_body, genome_in_cube or "none")))

    # B-13 — every entry immutable & correctly hashed (recompute)
    bad = []
    for band in org.prime.bands:
        if org.prime.encoding(band) != "log-json":
            continue
        for idx in org.prime.band_layers[band]:
            for e in org.prime.layers[idx]:
                if isinstance(e, dict) and "hash" in e and _entry_hash(e) != e["hash"]:
                    bad.append("%s#%s" % (band, e.get("id")))
    rows.append(_row("B-13", "Entries immutable & hashed; verify recomputes hash",
                     PASS if not bad else FAIL, note="all hashes intact" if not bad
                     else "tampered: %s" % bad))

    # B-14 / B-32 — the veil hides the private thoughts band
    veiled = org.prime.read("thoughts")
    revealed = org.prime.read("thoughts", reveal_private=True)
    rows.append(_row("B-14", "Reads honor the veil (private thoughts hidden)",
                     PASS if veiled == [] else FAIL,
                     note="veiled=[]  reveal_private shows %d entr(ies)" % len(revealed)))

    # B-11/B-12 / HF-B24 — a dangling reference becomes an immune event (never silently dropped)
    before = len(org.immune_log)
    result = org.resolve("<facts.999999>")
    logged = len(org.immune_log) > before
    rows.append(_row("B-12", "Dangling reference -> immune event (none reaches output)",
                     PASS if (result is None and logged) else FAIL, "HF-B24",
                     note="resolved=%r, immune_logged=%s" % (result, logged)))

    # HF-B46 — sealed ancestral cube rejects experiential writes (if any ancestor exists)
    if org.ancestral:
        try:
            org.ancestral[0].append("facts", make_entry({"k": "x", "v": "y"}))
            rows.append(_row("B-46", "Ancestral (sealed) cube rejects writes", FAIL, "HF-B46",
                             note="ancestral accepted a write!"))
        except PermissionError:
            rows.append(_row("B-46", "Ancestral (sealed) cube rejects writes", PASS, "HF-B46",
                             note="gen%d sealed; write refused" % org.ancestral[0].generation))
    else:
        rows.append(_row("B-46", "Ancestral (sealed) cube rejects writes", NA, "HF-B46",
                         note="no ancestral generation yet (no rebirth)"))

    # B-W (waste axis) — Memory's metabolism is present on THIS organism: bands allocate layers
    # on demand (a reuse pool exists) and every band declares a purpose ("be efficient").
    free_pool = hasattr(org.prime, "band_free") and hasattr(org.prime, "compact")
    purposed = all(str(b.get("purpose") or "").strip() for b in org.prime.bands.values())
    rows.append(_row("B-W", "Layers on-demand + reusable (Memory metabolism) & every band purposed",
                     PASS if (free_pool and purposed) else FAIL, None,
                     note=("reuse pool + compact present; " if free_pool else "no reclaim API; ") +
                          ("all bands purposed" if purposed else "a band lacks a purpose")))

    return rows


def organs_present(org):
    """Which organs the SUBSTRATE can attest to (host-level organs are marked [host])."""
    bands = org.prime.bands
    return {
        "Heart": "host", "Limbs": "host", "Nervous": "host",
        "Genome": "x" if org.body.self_record().get("primer") else " ",
        "Senses": "x" if "senses" in bands else " ",
        "Immune": "x" if "immune" in bands else " ",
        "Memory": "x" if {"facts", "events", "discoveries"} <= set(bands) else " ",
        "Brain-stub": "x" if "thoughts" in bands else " ",
    }


def _demo_organism(break_hash=False, break_primer=False):
    org = Organism.birth(identity={"name": "Reference.AppAI"},
                         truths=["if it is not in the VCW it did not happen"],
                         commandments=["protect your VCW", "you are a tool USER"])
    org.sense({"event": "boot", "authorization": "Bearer sk-SECRET1234567890ABCD"})
    org.prime.append("facts", make_entry({"k": "host", "v": "browser"}))
    org.prime.append("events", make_entry("first breath", opcode="EVENT"))
    org.prime.append("thoughts", make_entry("a private musing", opcode="THINK", author="MIND"))
    org.rebirth(reason="demo reformat")          # create an ancestral generation
    org.prime.append("facts", make_entry({"k": "gen", "v": "1"}))
    if break_hash:                               # tamper an entry without fixing its hash
        idx = org.prime.band_layers["facts"][0]
        org.prime.layers[idx][0]["content"] = {"k": "host", "v": "TAMPERED"}
    if break_primer:                             # force the Primer into the cube (the anti-pattern)
        org.prime.identity_in_body = False
        org.prime.bands["genome"] = {"band": "genome", "head": 4, "span": 4,
                                     "encoding": "log-json", "params": {}, "private": False, "v": 2}
        org.prime.band_layers["genome"] = [4]
        org.prime.band_free["genome"] = []
        org.prime.layers[4] = []
        org.body._primer = []                    # and empty the Body's primer
    return org


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if args:
        org = Organism.load(args[0])
        source = args[0]
    else:
        org = _demo_organism(break_hash="--break-hash" in flags,
                             break_primer="--break-primer" in flags)
        source = "demo organism (in-memory)"

    rows = audit_organism(org)
    invariants = test_invariants.run_all()

    print("=" * 72)
    print("MANTLE OS — PART 1 (ZOMBIE BODY) AUDIT  ·  source: %s" % source)
    print("=" * 72)
    width = max(len(r["requirement"]) for r in rows)
    for r in rows:
        hf = (" [%s]" % r["hf"]) if r["hf"] else ""
        print("  %-4s %-9s %-*s %s%s" % (r["code"], r["result"], width, r["requirement"],
                                         r["note"], hf))
    print("\n  Host-dependent rows (certify against the running app, not the substrate):")
    for code, req, hf in HOST_ROWS:
        print("    %-4s %-10s %s [%s]" % (code, NEEDS_HOST, req, hf))

    print("\n  Security invariants (test_invariants.py):")
    for r in invariants:
        print("    [%s] %s — %s" % ("PASS" if r["ok"] else "FAIL", r["name"], r["detail"]))

    checkable = [r for r in rows if r["result"] in (PASS, FAIL)]
    passed = sum(1 for r in checkable if r["result"] == PASS)
    substrate_fails = [r for r in checkable if r["result"] == FAIL]
    open_hf = [r for r in rows if r["hf"] and r["result"] == FAIL]
    inv_pass = sum(1 for r in invariants if r["ok"])
    # The gate blocks on ANY substrate FAIL (an integrity/verify failure is disqualifying even
    # when the audit table tags it "—") or any failing security invariant.
    blocked = bool(substrate_fails) or inv_pass != len(invariants)

    organs = organs_present(org)
    print("\n" + "-" * 72)
    print("ZOMBIE BODY CERTIFICATION")
    print("  AppAI name        : %s" % org.body.identity_name())
    print("  Prime generation  : %d   ancestral: %s"
          % (org.prime.generation, [c.generation for c in org.ancestral] or "none"))
    print("  Substrate verify  : [%s] healthy" % ("x" if not org.prime.verify() else " "))
    print("  Substrate rows    : %d / %d passed" % (passed, len(checkable)))
    print("  Security invariants: %d / %d green" % (inv_pass, len(invariants)))
    print("  Open hard-fails   : %d   (MUST be 0 to authorize Phase 2)" % len(open_hf))
    if substrate_fails:
        print("  Substrate FAILs   : %s" % ", ".join(r["code"] for r in substrate_fails))
    print("  Organs (substrate): " + "  ".join("%s[%s]" % (k, v) for k, v in organs.items()))
    print("-" * 72)

    if "--json" in flags:
        print("\nEVIDENCE_JSON:")
        print(json.dumps({"source": source, "rows": rows, "invariants": invariants,
                          "open_hardfails": [r["code"] for r in open_hf]}, indent=2))

    if blocked:
        reasons = [r["code"] for r in substrate_fails]
        if inv_pass != len(invariants):
            reasons.append("security-invariants")
        print("\nRESULT: GATE BLOCKED — %s" % ", ".join(reasons))
        return 1
    print("\nRESULT: STAGE-1 SUBSTRATE GATE PASSED (Phase 2 authorized once host rows certify).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
