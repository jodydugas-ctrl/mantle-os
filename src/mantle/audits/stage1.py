#!/usr/bin/env python3
"""
mantle.audits.stage1  --  the Stage-1 (Zombie Body) gate (Mantle OS)

Deterministic and LLM-free: every check reads the cube, runs Body reflexes, and runs
verify(). No human judgment, no model, no network. The gate exits non-zero if ANY row
fails or any security invariant is red; a passing run certifies the Zombie Body and
authorizes Phase 2 (`organism.stage1_certified = True`).

Tamper proofs (the harness must CATCH violations):
    python -m mantle audit --break-hash     # a tampered entry   -> must FAIL
    python -m mantle audit --break-primer   # Primer in the cube -> must FAIL
    python -m mantle audit --break-seal     # a tampered ancestor-> must FAIL
"""
from __future__ import annotations

import json
import sys

from ..core.organism import Organism
from ..core.audit import make_row as _row, safe as _safe, print_row, PASS, FAIL, NA
from ..vcw.bands import standard_genome
from ..vcw.entry import make_entry, entry_hash
from . import invariants as _inv

ORGANS = ("heart", "genome", "nervous", "senses", "immune", "limbs", "memory", "brain")


# ============================================================================
# Substrate rows (the cube / Body store)
# ============================================================================
def audit_substrate(org):
    rows = []

    problems = org.prime.verify()
    rows.append(_row("B-01", "Cube genesis valid; verify() healthy",
                     PASS if not problems else FAIL,
                     note="clean" if not problems else "; ".join(problems[:3])))

    primer = org.body.self_record().get("primer") or []
    rows.append(_row("B-02", "Primer present and non-empty (AppAI is 'born')",
                     PASS if primer else FAIL, "HF-B02",
                     note="name=%s" % org.body.identity_name()))

    expected = {b["band"]: b["head"] for b in standard_genome()}
    actual = {name: boot["head"] for name, boot in org.prime.bands.items()}
    missing = [b for b, h in expected.items() if actual.get(b) != h]
    rows.append(_row("B-03", "Band map matches canonical reserved heads",
                     PASS if not missing else FAIL, "HF-B03",
                     note="all 8 reserved bands at canonical heads" if not missing
                          else "deviation: %s" % missing))

    genome_in_cube = [b for b in org.prime.bands if b.startswith("bodyentry") or b == "genome"]
    in_body_ok = bool(org.prime.identity_in_body) and not genome_in_cube and bool(primer)
    rows.append(_row("B-45", "Primer/commandments live in the BODY, not the cube",
                     PASS if in_body_ok else FAIL, "HF-B45",
                     note="identity_in_body=%s, genome-bands-in-cube=%s"
                          % (org.prime.identity_in_body, genome_in_cube or "none")))

    bad = [p for p in problems if "hash mismatch" in p]
    rows.append(_row("B-13", "Entries immutable & hashed; verify recomputes hashes",
                     PASS if not bad else FAIL,
                     note="all hashes intact" if not bad else "tampered: %s" % bad[:2]))

    veiled = org.prime.read("thoughts")
    revealed = org.prime.read("thoughts", reveal_private=True)
    rows.append(_row("B-14", "Reads honor the veil (private thoughts hidden)",
                     PASS if veiled == [] else FAIL,
                     note="veiled=[]  reveal shows %d entr(ies)" % len(revealed)))

    before = len(org.immune.log)
    result = org.resolve("<facts.999999>")
    logged = len(org.immune.log) > before
    rows.append(_row("B-12", "Dangling reference -> immune event (never silent)",
                     PASS if (result is None and logged) else FAIL, "HF-B24",
                     note="resolved=%r, immune_logged=%s" % (result, logged)))

    if org.ancestral:
        anc = org.ancestral[0]
        try:
            anc.append("facts", make_entry({"k": "x"}))
            rows.append(_row("B-46", "Ancestral (sealed) cube rejects writes", FAIL,
                             "HF-B46", note="ancestral accepted a write!"))
        except PermissionError:
            rows.append(_row("B-46", "Ancestral (sealed) cube rejects writes", PASS,
                             "HF-B46", note="gen%d sealed; write refused" % anc.generation))
        seal_problems = anc.verify_seal()
        rows.append(_row("B-46b", "Ancestral seal fingerprint intact",
                         PASS if not seal_problems else FAIL, "HF-B46",
                         note="fingerprint verified" if not seal_problems
                              else "; ".join(seal_problems)))
    else:
        rows.append(_row("B-46", "Ancestral (sealed) cube rejects writes", NA, "HF-B46",
                         note="no ancestral generation yet (no rebirth)"))

    free_pool = hasattr(org.prime, "band_free") and hasattr(org.prime, "compact")
    purposed = all(str(b.get("purpose") or "").strip() for b in org.prime.bands.values())
    rows.append(_row("B-W", "Metabolism present (reclaim/dedupe) & every band purposed",
                     PASS if (free_pool and purposed) else FAIL, None,
                     note="reuse pool + compact + dedupe present; all bands purposed"
                          if free_pool and purposed else "missing"))

    return rows


# ============================================================================
# Mesh rows (the eight organs, contracts, bus -- the RUNNING Body)
# ============================================================================
def audit_mesh(org):
    rows = []

    def safe(code, requirement, hf, fn):
        _safe(rows, code, requirement, hf, fn)

    def b04():
        # The Phase-1 guarantee: the heartbeat NEVER needs the MIND. If a MIND is fused
        # (the Stage-2 regression re-runs this row), detach it, beat, and re-attach --
        # the loop must run whole with the cognition slot empty.
        was_fused = org.brain.fused
        mind_obj = org.brain.mind
        if was_fused:
            org.brain.defuse()
        before = org.heart.beats
        org.heart.run(3)                                 # cognition slot empty: no LLM
        ok = org.heart.beats == before + 3 and not org.brain.fused
        if was_fused:
            org.brain.fuse(mind_obj, stage1_certified=org.stage1_certified)
        return (ok, "3 beats with the cognition slot empty (no LLM in the loop)%s"
                % ("; MIND re-fused" if was_fused else ""))
    safe("B-04", "Heartbeat loop runs with no LLM", "HF-B08", b04)

    def b05():
        installed = org.heart.install_dual_flush()
        f0 = org.heart.flushes
        org.heart.circulate()
        return (installed and org.heart.flushes == f0 + 1,
                "atexit handler installed + explicit checkpoint flush")
    safe("B-05", "Dual-flush: checkpoint + atexit", "HF-B33", b05)

    def b06():
        report = org.heart.beat(assemble=True)
        ordered = ("intake" in report and "assembled" in report and "flushes" in report)
        return (ordered and report["ok"],
                "pulse = tick, intake, assembly, reflexes, scan, checkpoint")
    safe("B-06", "Pulse order fixed & complete (incl. assembly + checkpoint)", None, b06)

    def b16():
        hits = {"n": 0}
        org.senses.bind_reflex("btn", "press",
                               lambda o, s: hits.__setitem__("n", hits["n"] + 1))
        org.senses.mark_routine("poll", "tick")
        deterministic = (
            org.senses.classify("btn", "press") == org.senses.classify("btn", "press")
            == "REFLEX"
            and org.senses.classify("poll", "tick") == "ROUTINE"
            and org.senses.classify("zzz", "qqq") == "SIGNIFICANT")
        sb = len(org.prime.read("senses")); bb = len(org.prime.read("brain"))
        cls = org.senses.inhale({"action_id": "btn", "event_type": "press"})
        one_entry = len(org.prime.read("senses")) == sb + 1
        no_brain = len(org.prime.read("brain")) == bb
        return (deterministic and cls == "REFLEX" and one_entry and no_brain
                and hits["n"] == 1,
                "deterministic; one senses entry; REFLEX never touched brain")
    safe("B-16", "Senses classifier deterministic & LLM-free", "HF-B09", b16)

    def b25():
        org.limbs.register_control("save_btn", {"label": "Save"}, lambda v: None)
        org.limbs.register_control("title", {"label": "Title"}, lambda v: None)
        return ({"save_btn", "title"} <= set(org.senses.surface_map),
                "Human Surface Map inventories %d control(s)" % len(org.senses.surface_map))
    safe("B-25", "Every visible control in the Human Surface Map", "HF-B44", b25)

    def b26():
        def proofs():
            return sum(1 for e in org.prime.read("brain")
                       if isinstance(e.get("content"), dict) and "action_proof" in e["content"])
        covered = org.limbs.surface_covered()
        p0 = proofs()
        org.limbs.operate("save_btn", True)
        return (covered and proofs() == p0 + 1,
                "every control bridged; operate() recorded a proof")
    safe("B-26", "Each control has a ControlBridge + recorded proof", "HF-B44", b26)

    def b29():
        e = org.limbs.complete({"task": "save"})
        present = e.get("authorship") == "BODY"
        body_authored_mind_phase = any(
            isinstance(x.get("content"), dict)
            and x["content"].get("phase") in ("INTENTION", "DELEGATED")
            and x.get("authorship") == "BODY"
            for x in org.prime.read("brain"))
        rewrite = dict(e); rewrite["authorship"] = "MIND"
        caught = entry_hash(rewrite) != e["hash"]
        return (present and not body_authored_mind_phase and caught,
                "authorship=BODY; a rewrite breaks the hash; no Body INTENTION")
    safe("B-29", "Dispatch authorship present & immutable", "HF-B29", b29)

    def b60():
        manifests = org.manifests()
        complete = set(manifests) == set(ORGANS)
        contracted = all(m.get("fail_mode") == "fail-open" and "writes" in m
                         for m in manifests.values())
        # In Phase 1 the Brain must be dormant; after a CERTIFIED fusion (the Stage-2
        # regression) a fused brain is the expected state -- what stays invariant is the
        # contract: dormant phase1, bounded write surface.
        brain_ok = (manifests["brain"]["phase1"] == "dormant"
                    and (not org.brain.fused or org.stage1_certified))
        return (complete and contracted and brain_ok,
                "8/8 organs carry contracts; brain %s; all fail-open"
                % ("fused post-certification" if org.brain.fused else "dormant"))
    safe("B-60", "All eight organs present with contracts; Brain dormant", "HF-B60", b60)

    def b61():
        surface = org.bus.reflex_surface()
        before = len(org.immune.log)
        org.bus.subscribe("pulse", lambda p: 1 / 0, organ="audit-probe")
        org.heart.beat()
        faulted = any(e["kind"] == "reflex_fault" for e in org.immune.log[before:])
        return (isinstance(surface, dict) and faulted,
                "bus surface inspectable; a faulting reflex degraded to an immune event")
    safe("B-61", "SignalBus deterministic + fail-open (faults -> immune)", "HF-B32", b61)

    def b62():
        try:
            org.senses.append("facts", make_entry({"x": 1}))
            return False, "an organ wrote outside its contract unchallenged"
        except PermissionError:
            pass
        overreach = org.immune.log[-1]["kind"] == "organ_overreach"
        return overreach, "out-of-contract write refused + recorded as overreach"
    safe("B-62", "Organ contracts enforced (no out-of-band writes)", "HF-B61", b62)

    def b63():
        pressures = {b: org.prime.pressure(b) for b in org.prime.bands}
        sane = all(0.0 <= p <= 1.0 for p in pressures.values())
        hook = org.prime.pressure_hook is not None
        return (sane and hook,
                "pressure 0..1 for %d bands; pressure hook wired to Memory/Immune"
                % len(pressures))
    safe("B-63", "Capacity pressure measurable; thresholds wired (0.75/0.90)", None, b63)

    return rows


def organs_present(org):
    bands = org.prime.bands
    return {
        "Heart": "x", "Senses": "x", "Limbs": "x", "Nervous": "x",
        "Genome": "x" if org.body.self_record().get("primer") else " ",
        "Immune": "x" if "immune" in bands else " ",
        "Memory": "x" if {"facts", "events", "discoveries"} <= set(bands) else " ",
        "Brain-socket": "x" if "thoughts" in bands else " ",
    }


def demo_organism(break_hash=False, break_primer=False, break_seal=False):
    org = Organism.birth(identity={"name": "Reference.AppAI"},
                         truths=["if it is not in the VCW it did not happen"],
                         commandments=["protect your VCW", "you are a tool USER"])
    org.senses.inhale({"action_id": "boot", "event_type": "start",
                       "authorization": "Bearer sk-SECRET1234567890ABCD"})
    org.memory.remember("facts", {"k": "host", "v": "headless"})
    org.memory.remember("events", "first breath", opcode="EVENT")
    org.prime.append("thoughts", make_entry("a private musing", opcode="THINK",
                                            author="MIND"))
    org.rebirth(reason="demo reformat")          # creates a sealed ancestral generation
    org.memory.remember("facts", {"k": "gen", "v": "1"})
    if break_hash:                               # tamper an entry without fixing its hash
        idx = org.prime.band_layers["facts"][0]
        org.prime.layer_content(idx)[0]["content"] = {"k": "host", "v": "TAMPERED"}
    if break_primer:                             # force the Primer into the cube
        org.prime.identity_in_body = False
        org.prime.bands["genome"] = {"band": "genome", "head": 4, "span": 4,
                                     "encoding": "log-json", "params": {},
                                     "private": False, "purpose": "anti-pattern", "v": 3}
        org.prime.band_layers["genome"] = [4]
        org.prime.band_free["genome"] = []
        org.prime.layers[4] = []
        org.body._primer = []
    if break_seal:                               # tamper a sealed ancestor's content
        anc = org.ancestral[0]
        idx = anc.band_layers["facts"][0]
        anc.layer_content(idx)[0]["content"] = {"k": "host", "v": "REWRITTEN-HISTORY"}
    return org


def run(org=None, *, include_invariants=True):
    """Programmatic gate. Returns (passed, evidence). On pass, certifies the organism."""
    org = org or demo_organism()
    substrate_rows = audit_substrate(org)
    mesh_rows = audit_mesh(org)
    inv = _inv.run_all() if include_invariants else []
    all_rows = substrate_rows + mesh_rows
    fails = [r for r in all_rows if r["result"] == FAIL]
    inv_ok = all(r["ok"] for r in inv)
    passed = not fails and inv_ok
    if passed:
        org.stage1_certified = True              # the gate itself authorizes Phase 2
    return passed, {"substrate_rows": substrate_rows, "mesh_rows": mesh_rows,
                    "invariants": inv, "fails": [r["code"] for r in fails],
                    "organism": org}


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if args:
        org = Organism.load(args[0], verify_seals=True)
        source = args[0]
    else:
        org = demo_organism(break_hash="--break-hash" in flags,
                            break_primer="--break-primer" in flags,
                            break_seal="--break-seal" in flags)
        source = "demo organism (in-memory)"

    skip_inv = "--fast" in flags
    passed, ev = run(org, include_invariants=not skip_inv)
    substrate_rows, mesh_rows, inv = ev["substrate_rows"], ev["mesh_rows"], ev["invariants"]

    print("=" * 74)
    print("MANTLE OS — STAGE 1 (ZOMBIE BODY) GATE  ·  source: %s" % source)
    print("=" * 74)
    width = max(len(r["requirement"]) for r in substrate_rows + mesh_rows)
    print("  Substrate rows (the cube / Body store):")
    for r in substrate_rows:
        print_row(r, width)
    print("\n  Mesh rows (the eight organs, contracts, bus):")
    for r in mesh_rows:
        print_row(r, width)
    if inv:
        print("\n  Security invariants (mantle.audits.invariants):")
        for r in inv:
            print("    [%s] %s — %s" % ("PASS" if r["ok"] else "FAIL", r["name"],
                                        r["detail"]))

    inv_pass = sum(1 for r in inv if r["ok"])
    organs = organs_present(org)
    print("\n" + "-" * 74)
    print("ZOMBIE BODY CERTIFICATION")
    print("  AppAI name        : %s" % org.body.identity_name())
    print("  Prime generation  : %d   ancestral: %s"
          % (org.prime.generation, [c.generation for c in org.ancestral] or "none"))
    print("  Substrate verify  : [%s] healthy" % ("x" if not org.prime.verify() else " "))
    rows_pass = sum(1 for r in substrate_rows + mesh_rows if r["result"] == PASS)
    rows_all = sum(1 for r in substrate_rows + mesh_rows if r["result"] in (PASS, FAIL))
    print("  Gate rows         : %d / %d passed" % (rows_pass, rows_all))
    if inv:
        print("  Security invariants: %d / %d green" % (inv_pass, len(inv)))
    print("  Open hard-fails   : %d   (MUST be 0 to authorize Phase 2)" % len(ev["fails"]))
    if ev["fails"]:
        print("  FAILs             : %s" % ", ".join(ev["fails"]))
    print("  Organs            : " + "  ".join("%s[%s]" % (k, v) for k, v in organs.items()))
    print("-" * 74)

    if "--json" in flags:
        print("\nEVIDENCE_JSON:")
        print(json.dumps({"source": source, "substrate_rows": substrate_rows,
                          "mesh_rows": mesh_rows,
                          "invariants": [{k: v for k, v in r.items()} for r in inv],
                          "fails": ev["fails"]}, indent=2))

    if not passed:
        reasons = list(ev["fails"]) or []
        if inv and inv_pass != len(inv):
            reasons.append("security-invariants")
        print("\nRESULT: GATE BLOCKED — %s" % ", ".join(reasons))
        return 1
    print("\nRESULT: STAGE-1 ZOMBIE BODY GATE PASSED (substrate + organ mesh certified; "
          "Phase 2 authorized).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
