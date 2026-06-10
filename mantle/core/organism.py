#!/usr/bin/env python3
"""
mantle.core.organism  --  the Organism: Body + Prime cube + ancestors + eight organs (Mantle v3)

    Organism = BODY        (the Primer + lineage index -- identity, outside every cube)
             + PRIME cube  (one, hot, takes all experiential writes)
             + ANCESTRAL   (sealed, fingerprinted, lazy-loaded, read-only)
             + the eight organs, meshed on one deterministic SignalBus

How an AppAI lives, in this one class's vocabulary:
  born      Organism.birth() -- the Primer seals into the Body; the Prime cube is genesis'd
  senses    organism.senses.inhale()/receive() -- the only inbound boundary
  remembers organism.memory.remember() -- immutable hashed entries, veiled reads
  reacts    reflex arcs + bus reflexes -- deterministic, no LLM
  protects  organism.immune -- every violation becomes an immune event; staged saves
  acts      organism.limbs -- dispatch lifecycle, ControlBridge, proofs
  learns    discoveries (inferred) -> facts only with cited evidence
  calcifies trial -> gates -> Cube.calcify -> limbs.invoke_reflex (instinct, no MIND)
  rebirths  organism.rebirth() -- CHOSEN reformat; ancestors sealed + fingerprinted
  thinks    Phase 2 only: a bounded MIND fused into organism.brain (extension, never
            replacement -- and never imported by anything in this package)
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .body import Body
from .events import SignalBus
from . import refs as _refs
from ..vcw.cube import Cube
from ..vcw.bands import standard_genome
from ..vcw.entry import make_entry
from ..organs.heart import Heart
from ..organs.genome import Genome
from ..organs.nervous import Nervous
from ..organs.senses import Senses
from ..organs.immune import Immune
from ..organs.limbs import Limbs
from ..organs.memory import Memory
from ..organs.brain import Brain

ORGAN_ORDER = ("heart", "genome", "nervous", "senses", "immune", "limbs", "memory", "brain")


class Organism:
    def __init__(self, body: Body, prime: Cube) -> None:
        self.body = body
        self.prime = prime
        self.ancestral: List[Cube] = []
        self.stage1_certified = False           # set by the Stage-1 gate; required for fusion

        # --- the mesh: one bus, eight organs, no hidden coupling -----------------
        self.bus = SignalBus()
        self.immune = Immune(self)
        self.bus.set_immune_sink(self.immune.event)      # reflex faults -> immune events
        self.heart = Heart(self)
        self.genome = Genome(self)
        self.nervous = Nervous(self)
        self.senses = Senses(self)
        self.limbs = Limbs(self)
        self.memory = Memory(self)
        self.brain = Brain(self)
        self.prime.pressure_hook = self.memory.on_pressure   # capacity -> metabolism record
        self._sync_lineage()

    # ---- birth ----------------------------------------------------------------
    @classmethod
    def birth(cls, identity: Dict[str, Any], truths: List[str], commandments: List[str],
              genome: Optional[List[Dict[str, Any]]] = None) -> "Organism":
        body = Body()
        body.birth(identity, truths, commandments)
        prime = Cube.genesis(genome or standard_genome(), generation=0)
        return cls(body, prime)

    # ---- the organ mesh, inspectable -------------------------------------------
    def organs(self) -> Dict[str, Any]:
        return {name: getattr(self, name) for name in ORGAN_ORDER}

    def manifests(self) -> Dict[str, Dict[str, Any]]:
        return {name: organ.manifest() for name, organ in self.organs().items()}

    # ---- lineage bookkeeping ------------------------------------------------------
    def _sync_lineage(self) -> None:
        self.body.prime_generation = self.prime.generation
        self.body.lineage_index[self.prime.generation] = {
            "role": "prime", "location": "prime", "seal_fingerprint": None}
        for c in self.ancestral:
            self.body.lineage_index[c.generation] = {
                "role": "ancestral", "location": "gen%03d" % c.generation,
                "seal_fingerprint": c.seal_fingerprint}

    def cube_for_generation(self, gen: int) -> Optional[Cube]:
        if gen == self.prime.generation:
            return self.prime
        for c in self.ancestral:
            if c.generation == gen:
                return c
        return None

    # ---- boundaries (delegations that keep old call-sites honest) ----------------
    def sense(self, signal: Any, opcode: str = "SENSE") -> str:
        """Back-compat inbound boundary: everything still enters through Senses."""
        if not isinstance(signal, dict):
            signal = {"value": signal}
        return self.senses.inhale(signal)

    def immune_event(self, kind: str, detail: Any) -> None:
        self.immune.event(kind, detail)

    @property
    def immune_log(self) -> List[Dict[str, Any]]:
        return self.immune.log

    def resolve(self, ref: str) -> Any:
        return _refs.resolve(self, ref)

    # ---- rebirth = CHOSEN reformat (never capacity-forced) -------------------------
    def rebirth(self, new_genome: Optional[List[Dict[str, Any]]] = None,
                reason: str = "reformat") -> "Organism":
        """Distill Prime -> seal + fingerprint it as ancestral -> new Prime with a
        (possibly new) genome. The Body keeps the Primer; nothing identity-bearing is
        copied between cubes. Rebirth is always a choice; capacity triggers metabolism,
        not this."""
        distillation = {"from_generation": self.prime.generation, "reason": reason,
                        "fact_count": len(self.prime.read("facts"))}
        fingerprint = self.prime.seal()                       # freeze + fingerprint
        self.ancestral.append(self.prime)
        new_gen = self.prime.generation + 1
        self.prime = Cube.genesis(new_genome or standard_genome(), generation=new_gen)
        self.prime.pressure_hook = self.memory.on_pressure
        self.genome.record_inheritance(
            dict(distillation, seal_fingerprint=fingerprint),
            source_ref="<gen%d.facts>" % distillation["from_generation"])
        self._sync_lineage()
        self.bus.emit("rebirth", {"generation": new_gen, "reason": reason})
        return self

    # ---- persistence (hot Prime; cold, write-once ancestors) ------------------------
    def save(self, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        self.prime.save(os.path.join(directory, "gen%03d.vcw" % self.prime.generation))
        for c in self.ancestral:
            target = os.path.join(directory, "gen%03d.vcw" % c.generation)
            if c.sealed and os.path.exists(target):
                continue                          # sealed = immutable = written once
            c.save(target)
        with open(os.path.join(directory, "body.json"), "w") as f:
            json.dump(self.body.to_dict(), f, indent=2)
        with open(os.path.join(directory, "organism.json"), "w") as f:
            json.dump({"prime_generation": self.prime.generation,
                       "ancestral_generations": [c.generation for c in self.ancestral],
                       "stage1_certified": self.stage1_certified}, f, indent=2)

    @classmethod
    def load(cls, directory: str, verify_seals: bool = False) -> "Organism":
        with open(os.path.join(directory, "organism.json")) as f:
            org_meta = json.load(f)
        with open(os.path.join(directory, "body.json")) as f:
            body = Body.from_dict(json.load(f))
        prime = Cube.load(os.path.join(directory,
                                       "gen%03d.vcw" % org_meta["prime_generation"]))
        o = cls(body, prime)
        o.stage1_certified = org_meta.get("stage1_certified", False)
        # ancestors load LAZY (the cold tier): no layer decodes until referenced
        o.ancestral = [Cube.load(os.path.join(directory, "gen%03d.vcw" % g), lazy=True)
                       for g in org_meta["ancestral_generations"]]
        if verify_seals:
            for c in o.ancestral:
                for problem in c.verify_seal():
                    o.immune_event("ancestor_tamper",
                                   {"generation": c.generation, "problem": problem})
        o._sync_lineage()
        return o
