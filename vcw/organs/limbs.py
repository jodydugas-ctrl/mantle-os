#!/usr/bin/env python3
"""
organs/limbs.py  --  The Limbs organ: action & surface actuation (efferent I/O) (Mantle v2.3)

Limbs is the efferent boundary -- it OPERATES the surface the Senses perceived. It owns:

  the dispatch lifecycle    INTENTION -> DELEGATED -> NOTIFIED -> COMPLETED, each record carrying
                            an immutable `authorship` field (now INSIDE the entry hash, so a
                            rewrite is caught by verify()):
                              * the MIND owns INTENTION / DELEGATED   (Phase 2)
                              * the BODY owns NOTIFIED / COMPLETED     (Phase 1, permanently)
  the Human Surface Map     the inventory of every human-visible control (afferent, from Senses)
  the ControlBridge         an effector path for every control (efferent)
  Action Execution Proof    a record (attempted/ok/method/ref/reason) for every effector use

Phase 1 is dormant->active: effectors, surface actuation, and proofs are built and TESTABLE (the
Body can operate controls and record NOTIFIED/COMPLETED). INTENTION/DELEGATED await the MIND --
the Body never authors them. Authorship is never rewritten.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

try:                                   # run from vcw/ (sibling modules on the path)
    from drivers import make_entry
except ImportError:                    # imported as part of the `vcw` package
    from vcw.drivers import make_entry  # type: ignore

DISPATCH_PHASES = ("INTENTION", "DELEGATED", "NOTIFIED", "COMPLETED")
_MIND_PHASES = ("INTENTION", "DELEGATED")     # authored only by a fused MIND (Phase 2)
_BODY_PHASES = ("NOTIFIED", "COMPLETED")      # authored by the Body (Phase 1, permanently)


class Limbs:
    def __init__(self, organism: Any) -> None:
        self.org = organism
        self.surface_map: Dict[str, Dict[str, Any]] = {}   # control_id -> human-visible descriptor
        self.bridges: Dict[str, Callable[[Any], Any]] = {}  # control_id -> effector (ControlBridge)

    # ---- surface wiring ---------------------------------------------------
    def register_control(self, control_id: str, descriptor: Dict[str, Any],
                         bridge: Callable[[Any], Any]) -> None:
        """Map a human-visible control into the Human Surface Map AND give it a ControlBridge.
        Every visible control must have both halves (afferent map + efferent effector)."""
        self.surface_map[control_id] = descriptor
        self.bridges[control_id] = bridge

    def surface_covered(self) -> bool:
        """True iff every control in the Human Surface Map has a ControlBridge path."""
        return all(cid in self.bridges for cid in self.surface_map)

    # ---- dispatch lifecycle ----------------------------------------------
    def _dispatch(self, phase: str, payload: Any) -> Dict[str, Any]:
        authorship = "MIND" if phase in _MIND_PHASES else "BODY"
        e = make_entry({"phase": phase, "payload": payload}, opcode="DISPATCH",
                       author=authorship, authorship=authorship)
        self.org.prime.append("brain", e)
        return e

    # Phase-1 (Body-owned) -------------------------------------------------
    def notify(self, payload: Any) -> Dict[str, Any]:
        return self._dispatch("NOTIFIED", payload)

    def complete(self, payload: Any) -> Dict[str, Any]:
        return self._dispatch("COMPLETED", payload)

    # Phase-2 (MIND-owned) -- present so the lifecycle is whole; the Body must never call these.
    def intend(self, payload: Any) -> Dict[str, Any]:
        return self._dispatch("INTENTION", payload)

    def delegate(self, payload: Any) -> Dict[str, Any]:
        return self._dispatch("DELEGATED", payload)

    # ---- actuation + proof ------------------------------------------------
    def operate(self, control_id: str, value: Any) -> Dict[str, Any]:
        """Drive a human-visible control through its ControlBridge and record an Action Execution
        Proof for the effector use. Fail-open: a failing effector records a failed proof, it does
        not crash the host."""
        if control_id not in self.bridges:
            self.org.immune_event("unmapped_control", {"control_id": control_id})
            return self._prove(control_id, attempted=False, ok=False,
                               method=None, ref=None, reason="no ControlBridge")
        try:
            self.bridges[control_id](value)
            return self._prove(control_id, attempted=True, ok=True,
                               method="ControlBridge", ref=control_id, reason="ok")
        except Exception as ex:                  # noqa: BLE001 -- fail-open at the effector
            return self._prove(control_id, attempted=True, ok=False,
                               method="ControlBridge", ref=control_id, reason=type(ex).__name__)

    def _prove(self, control_id: str, **proof: Any) -> Dict[str, Any]:
        rec: Dict[str, Any] = {"control": control_id}
        rec.update(proof)
        self.org.prime.append("brain", make_entry({"action_proof": rec}, opcode="PROOF",
                                                  author="BODY", authorship="BODY"))
        return rec
