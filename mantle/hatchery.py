#!/usr/bin/env python3
"""
mantle.hatchery  --  incubate an egg into a CERTIFIED organism (Argonaut)

The hatchery is the brood shell. It takes a validated egg and performs the whole birth,
deterministically, with no LLM anywhere:

  1. BIRTH       Primer seals into the Body; the cube geneses (reserved 8 + app bands)
  2. WIRE        declarative reflex arcs, routines, and controls bind to the organs
  3. INSTINCTS   each candidate skill runs the gauntlet: static sandbox gate -> trial
                 (proving cases) -> calcify (hash/signature/capability/provenance)
  4. WARMUP      a few heartbeats: intake, assembly, scan, checkpoint
  5. THE GATE    the SAME Stage-1 audit every Body faces; a failed gate = no hatch
  6. HATCH       save the organism (staged atomic) + the hatch report + a self-portrait

An egg that fails any step does not hatch -- the hatchery refuses with evidence. The
gate's probes leave entries in the newborn's memory: the audit is the organism's first
remembered experience, which is exactly the doctrine ("if it's not in the VCW, it
didn't happen" -- including being born and being examined).
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .core.organism import Organism
from .vcw.bands import standard_genome, make_band_boot
from .vcw.drivers import trial
from .audits import stage1
from . import egg as _egg
from . import face as _face


class HatchError(Exception):
    """The egg did not hatch. The reason is the message; the evidence travels with it."""


def _bind_reflex(org: Organism, spec: Dict[str, Any]) -> None:
    """Turn a declarative response into a deterministic Body reflex arc. The vocabulary
    is FIXED (egg.REFLEX_KINDS): eggs declare behavior, they do not ship behavior."""
    resp = spec["response"]
    kind = resp["kind"]

    def arc(o, signal, _resp=dict(resp), _kind=kind):
        if _kind == "remember":
            o.memory.remember(_resp["band"], _resp.get("content", {"signal": True}),
                              opcode=_resp.get("opcode", "WRITE"), source="egg-reflex")
        elif _kind == "complete":
            o.limbs.complete(_resp.get("payload", {"done": True}))
        elif _kind == "notify":
            o.limbs.notify(_resp.get("payload", {"noted": True}))
        elif _kind == "operate":
            o.limbs.operate(_resp["control"], _resp.get("value", True))

    org.senses.bind_reflex(spec["action_id"], spec["event_type"], arc)


def incubate(egg: Dict[str, Any], *, warmup_beats: int = 3,
             run_gate: bool = True) -> Dict[str, Any]:
    """Egg -> living organism. Returns {organism, report}. Raises HatchError if any
    instinct is refused or the Stage-1 gate blocks."""
    egg = _egg.validate(egg)
    report: Dict[str, Any] = {"egg": egg["identity"]["name"], "stages": []}

    # 1. BIRTH
    genome = standard_genome() + [
        make_band_boot(b["band"], b["head"], b.get("encoding", "log-json"),
                       params=b.get("params"), private=bool(b.get("private")),
                       span=b.get("span", 1), purpose=b.get("purpose", b["band"]))
        for b in egg.get("genome", [])]
    org = Organism.birth(identity=egg["identity"], truths=list(egg["truths"]),
                         commandments=list(egg["commandments"]), genome=genome)
    report["stages"].append({"birth": {"bands": len(org.prime.bands),
                                       "name": org.body.identity_name()}})

    # 2. WIRE
    for rx in egg.get("reflexes", []):
        _bind_reflex(org, rx)
    for action_id, event_type in egg.get("routines", []):
        org.senses.mark_routine(action_id, event_type)
    for c in egg.get("controls", []):
        cid = c["id"]
        org.limbs.register_control(cid, {k: v for k, v in c.items() if k != "id"},
                                   lambda value, _cid=cid: None)   # stub bridge; proofs real
    report["stages"].append({"wire": {"reflexes": len(egg.get("reflexes", [])),
                                      "routines": len(egg.get("routines", [])),
                                      "controls": len(egg.get("controls", []))}})

    # 3. INSTINCTS (the gauntlet -- a refused candidate aborts the hatch)
    for sk in egg.get("instincts", []):
        cases = [(c["args"], c["expect"]) for c in sk["cases"]]
        result = trial(sk["code"], sk["entry"], cases)          # sandbox gate runs first
        if not result["ok"]:
            raise HatchError("instinct %r failed trial: %s"
                             % (sk["entry"], result["detail"]))
        org.prime.calcify(sk["band"], sk["code"], entry=sk["entry"],
                          signature={"by": "hatchery", "egg": egg["identity"]["name"]},
                          capabilities=sk.get("capabilities", {}),
                          provenance={"author": "BODY", "born_gen": 0,
                                      "egg": egg["identity"]["name"]})
        report["stages"].append({"instinct": {"entry": sk["entry"],
                                              "cases": result["passed"]}})

    # 4. WARMUP
    org.heart.run(warmup_beats, assemble=True)
    report["stages"].append({"warmup": {"beats": org.heart.beats,
                                        "immune_events": len(org.immune.log)}})

    # 5. THE GATE (the same Stage-1 audit every Body faces)
    if run_gate:
        passed, ev = stage1.run(org, include_invariants=False)
        report["stages"].append({"gate": {
            "passed": passed,
            "rows": len(ev["substrate_rows"]) + len(ev["mesh_rows"]),
            "fails": ev["fails"]}})
        if not passed:
            raise HatchError("Stage-1 gate BLOCKED the hatch: %s" % ev["fails"])
    report["certified"] = org.stage1_certified
    return {"organism": org, "report": report}


def hatch(egg_path: str, out_dir: Optional[str] = None,
          warmup_beats: int = 3) -> Dict[str, Any]:
    """The full ceremony: load -> incubate -> persist + report + self-portrait."""
    egg = _egg.load(egg_path)
    result = incubate(egg, warmup_beats=warmup_beats)
    org, report = result["organism"], result["report"]
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        org.save(out_dir)
        portrait = os.path.join(out_dir, "face.png")
        _face.render(org, portrait)
        with open(os.path.join(out_dir, "hatch_report.json"), "w") as f:
            json.dump(report, f, indent=2, default=str)
        report["saved_to"] = out_dir
        report["portrait"] = portrait
    return {"organism": org, "report": report}
