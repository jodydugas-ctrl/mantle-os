#!/usr/bin/env python3
"""
organs/senses.py  --  The Senses organ: perception (afferent I/O) (Mantle v2.3)

Senses is the organism's afferent boundary. It ingests external signals and CLASSIFIES their
significance deterministically -- with NO LLM -- on the compound key (action_id, event_type):

  REFLEX       a signal bound to an immediate Body response; handled WITHOUT reaching the brain
  ROUTINE      a known-mundane signal; recorded, no escalation
  SIGNIFICANT  anything unrecognized; recorded and (in Phase 2) surfaced to cognition

Every inbound signal produces EXACTLY ONE senses entry, written through the secret-redacting
boundary (Organism.sense), so a secret never burns into memory. A REFLEX runs its bound Body
response immediately and never touches the brain band -- that is what "the Body acts with no
mind" means, made concrete.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Set, Tuple


class Senses:
    REFLEX = "REFLEX"
    ROUTINE = "ROUTINE"
    SIGNIFICANT = "SIGNIFICANT"

    def __init__(self, organism: Any) -> None:
        self.org = organism
        # (action_id, event_type) -> Body response callable(org, signal)
        self.reflex_arcs: Dict[Tuple[Any, Any], Callable[[Any, Dict[str, Any]], None]] = {}
        self.routine_keys: Set[Tuple[Any, Any]] = set()

    # ---- wiring -----------------------------------------------------------
    def bind_reflex(self, action_id: Any, event_type: Any,
                    response: Callable[[Any, Dict[str, Any]], None]) -> None:
        """Bind a deterministic Body response to a signal key (the reflex arc)."""
        self.reflex_arcs[(action_id, event_type)] = response

    def mark_routine(self, action_id: Any, event_type: Any) -> None:
        self.routine_keys.add((action_id, event_type))

    # ---- reflexes ---------------------------------------------------------
    def classify(self, action_id: Any, event_type: Any) -> str:
        """Deterministic, LLM-free classification keyed on (action_id, event_type)."""
        key = (action_id, event_type)
        if key in self.reflex_arcs:
            return self.REFLEX
        if key in self.routine_keys:
            return self.ROUTINE
        return self.SIGNIFICANT

    def inhale(self, signal: Dict[str, Any]) -> str:
        """Ingest one signal: classify it, write EXACTLY ONE redacted senses entry, and -- if it is
        a REFLEX -- run the bound Body response immediately, WITHOUT touching the brain band.
        Returns the classification."""
        action_id = signal.get("action_id")
        event_type = signal.get("event_type")
        cls = self.classify(action_id, event_type)
        # Organism.sense redacts at the boundary and appends one entry to the senses band.
        self.org.sense({"signal": signal, "class": cls}, opcode="SENSE")
        if cls == self.REFLEX:
            self.reflex_arcs[(action_id, event_type)](self.org, signal)
        return cls
