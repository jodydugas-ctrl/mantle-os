#!/usr/bin/env python3
"""
organs/  --  The runnable reference Body (Mantle v2.3)

The substrate (`vcw/`) is the heart; this package is the rest of the Body that the Organ Atlas
describes -- grown as pure-stdlib, no-LLM code so the Stage-1 "host" audit rows become real
PASS/FAIL instead of NEEDS-HOST:

  Heart          heartbeat loop, circulation, dual-flush          (organs/heart.py)
  Senses         REFLEX/ROUTINE/SIGNIFICANT classifier            (organs/senses.py)
  Limbs          dispatch lifecycle + ControlBridge + proofs      (organs/limbs.py)
  NervousSystem  reference resolver + Context Assembly            (organs/nervous.py)

`ReferenceBody(organism)` wires all four to an Organism. Everything here runs with NO brain --
that is the whole point: a Body is genuinely alive before it is ever made to think.
"""
from __future__ import annotations

from typing import Any

from .heart import Heart
from .senses import Senses
from .limbs import Limbs
from .nervous import NervousSystem


class ReferenceBody:
    """A minimal reference Body: the four runnable organs wired to one Organism. The `circulate`
    sink defaults to a no-op (a headless Body still has a heartbeat); inject `Organism.save` (or a
    checkpoint) to make circulation durable."""

    def __init__(self, organism: Any, circulate=None) -> None:
        self.org = organism
        self.heart = Heart(organism, circulate=circulate)
        self.senses = Senses(organism)
        self.limbs = Limbs(organism)
        self.nervous = NervousSystem(organism)


__all__ = ["Heart", "Senses", "Limbs", "NervousSystem", "ReferenceBody"]
