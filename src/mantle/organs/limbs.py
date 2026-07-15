#!/usr/bin/env python3
"""
mantle.organs.limbs  --  the Limbs organ: action, the ONLY outbound boundary (Mantle OS)

ALL outbound actions leave the organism through Limbs. It owns:

  the dispatch lifecycle   INTENTION -> DELEGATED -> NOTIFIED -> COMPLETED, each record
                           carrying an immutable `authorship` field (INSIDE the entry hash):
                             * the MIND owns INTENTION / DELEGATED   (Phase 2)
                             * the BODY owns NOTIFIED / COMPLETED     (Phase 1, permanently)
  the ControlBridge        an effector path for every human-visible control
  Action Execution Proof   a record (attempted/ok/method/ref/reason) for every effector use
  calcified reflexes       Limbs runs `exec` skills behind the hash/capability/trust gates

Phase 1 is dormant->active: effectors, actuation, proofs, and reflex invocation are built
and testable with no MIND. INTENTION/DELEGATED await the Brain; the Body never authors them.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from .contract import Organ, OrganContract
from ..vcw.drivers import trial
from ..vcw.entry import make_entry

DISPATCH_PHASES = ("INTENTION", "DELEGATED", "NOTIFIED", "COMPLETED")
_MIND_PHASES = ("INTENTION", "DELEGATED")     # authored only by a fused MIND (Phase 2)
_BODY_PHASES = ("NOTIFIED", "COMPLETED")      # authored by the Body (Phase 1, permanently)
MIND_SPECIAL_CONTROL = "mind.special_instruction"
MIND_DISCOVERY_CONTROL = "mind.discovery"
MIND_CULTIVATE_CONTROL = "mind.cultivate"

CONTRACT = OrganContract(
    "limbs", "action & surface actuation (efferent I/O) -- the only outbound boundary",
    reads=["brain"],
    writes=["brain"],
    reflexes=[
        {"name": "notify", "trigger": "a limb reports back", "effect": "Body records NOTIFIED"},
        {"name": "complete", "trigger": "a task finishes", "effect": "Body records COMPLETED"},
        {"name": "operate", "trigger": "a control must be driven",
         "effect": "ControlBridge actuation + an Action Execution Proof, fail-open"},
        {"name": "prove", "trigger": "every effector use",
         "effect": "record attempted/ok/method/ref/reason"},
        {"name": "invoke-reflex", "trigger": "a calcified skill is called",
         "effect": "run the exec layer behind hash/capability/provenance/trust gates + proof"},
    ],
    phase1="dormant->active",
    phase2_extension="the MIND authors INTENTION/DELEGATED; the Body keeps NOTIFIED/COMPLETED "
                     "and all actuation permanently (no private MIND I/O path)",
    audit=[
        "authorship field present and immutable (inside the entry hash)",
        "the Body never authors INTENTION/DELEGATED",
        "every effector use has an Action Execution Proof",
        "every human-visible control has a working ControlBridge path with a recorded proof",
    ],
)


class Limbs(Organ):
    contract = CONTRACT

    def __init__(self, organism) -> None:
        super().__init__(organism)
        self.bridges: Dict[str, Callable[[Any], Any]] = {}  # control_id -> effector

    # ---- surface wiring (efferent half; Senses holds the afferent map) -----
    def register_control(self, control_id: str, descriptor: Dict[str, Any],
                         bridge: Callable[[Any], Any]) -> None:
        """Every human-visible control gets both halves: Senses perceives it into the
        Surface Map (afferent); Limbs gets its ControlBridge (efferent)."""
        self.org.senses.map_control(control_id, descriptor)
        self.bridges[control_id] = bridge

    def surface_covered(self) -> bool:
        """True iff every control in the Human Surface Map has a ControlBridge path."""
        return all(cid in self.bridges for cid in self.org.senses.surface_map)

    # ---- dispatch lifecycle ---------------------------------------------------
    def _dispatch(self, phase: str, payload: Any) -> Dict[str, Any]:
        authorship = "MIND" if phase in _MIND_PHASES else "BODY"
        e = make_entry({"phase": phase, "payload": payload}, opcode="DISPATCH",
                       author=authorship, authorship=authorship)
        self.append("brain", e)
        self.bus.emit("dispatch", {"phase": phase, "authorship": authorship})
        return e

    def _mind_dispatch(self, phase: str, payload: Any) -> Dict[str, Any]:
        if not self.org.brain.fused:
            self.org.immune_event("mind_dispatch_refused", {
                "phase": phase, "reason": "no MIND fused"})
            raise PermissionError("%s requires a fused MIND" % phase)
        return self._dispatch(phase, payload)

    # Phase-1 (Body-owned)
    def notify(self, payload: Any) -> Dict[str, Any]:
        return self._dispatch("NOTIFIED", payload)

    def complete(self, payload: Any) -> Dict[str, Any]:
        return self._dispatch("COMPLETED", payload)

    # Phase-2 (MIND-owned) -- present so the lifecycle is whole; the Body never calls these.
    def intend(self, payload: Any) -> Dict[str, Any]:
        return self._mind_dispatch("INTENTION", payload)

    def delegate(self, payload: Any) -> Dict[str, Any]:
        return self._mind_dispatch("DELEGATED", payload)

    # ---- actuation + proof -------------------------------------------------------
    def operate(self, control_id: str, value: Any) -> Dict[str, Any]:
        """Drive a human-visible control through its ControlBridge and record an Action
        Execution Proof. Fail-open: a failing effector records a failed proof."""
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
                               method="ControlBridge", ref=control_id,
                               reason=type(ex).__name__)

    def _prove(self, control_id: str, **proof: Any) -> Dict[str, Any]:
        rec: Dict[str, Any] = {"control": control_id}
        rec.update(proof)
        self.append("brain", make_entry({"action_proof": rec}, opcode="PROOF",
                                        author="BODY", authorship="BODY"))
        return rec

    # ---- model-caused mutation ceremonies ---------------------------------------
    def _require_fused_mind(self, control_id: str) -> None:
        if self.org.brain.fused:
            return
        self.org.immune_event(
            "mind_mutation_refused",
            {"control_id": control_id, "reason": "no MIND fused"},
        )
        raise PermissionError("%s requires a fused MIND" % control_id)

    def apply_mind_special(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a MIND steering proposal, apply it as Body, and prove the mutation."""
        self._require_fused_mind(MIND_SPECIAL_CONTROL)
        text = intent.get("text") if isinstance(intent, dict) else None
        valid = (
            isinstance(intent, dict)
            and intent.get("intent") == "special_instruction"
            and intent.get("author") == "MIND"
            and isinstance(text, str)
            and bool(text.strip())
            and len(text) <= 4096
            and not any(ord(character) < 32 and character not in "\n\t" for character in text)
        )
        if not valid:
            self._prove(
                MIND_SPECIAL_CONTROL, attempted=False, ok=False,
                method="BodyMutationBridge", ref="body.special", reason="invalid proposal",
            )
            raise ValueError("invalid MIND special-instruction proposal")
        applied = self.org.body.apply_special(text, source="MIND")
        proof = self._prove(
            MIND_SPECIAL_CONTROL, attempted=True, ok=True,
            method="BodyMutationBridge", ref="body.special", reason="ok",
        )
        return {"intent": intent, "applied": applied, "proof": proof}

    def record_mind_discovery(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Persist one inferred inner-voice result through Limbs, never as a fact."""
        self._require_fused_mind(MIND_DISCOVERY_CONTROL)
        valid = (
            isinstance(record, dict)
            and record.get("author") == "MIND"
            and record.get("verified") is False
            and record.get("confidence") == "inferred"
            and record.get("opcode") == "INNER_VOICE"
        )
        if not valid:
            self._prove(
                MIND_DISCOVERY_CONTROL, attempted=False, ok=False,
                method="BodyMutationBridge", ref="discoveries", reason="invalid proposal",
            )
            raise ValueError("invalid inferred-discovery proposal")
        self.org.memory.append("discoveries", record)
        return self._prove(
            MIND_DISCOVERY_CONTROL, attempted=True, ok=True,
            method="BodyMutationBridge", ref="discoveries", reason="ok",
        )

    def cultivate_mind_skill(
        self,
        band: str,
        code: str,
        entry: str,
        cases: List[Tuple[Dict[str, Any], Any]],
        signature: Dict[str, Any],
        capabilities: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Trial and calcify one MIND proposal as a proven Body mutation."""
        self._require_fused_mind(MIND_CULTIVATE_CONTROL)
        try:
            result = trial(code, entry, cases)
            if not result["ok"]:
                raise ValueError("skill trial failed")
            self.org.prime.calcify(
                band,
                code,
                entry=entry,
                signature=signature,
                capabilities=capabilities,
                provenance={"author": "MIND", "born_gen": self.org.prime.generation},
            )
        except Exception as exc:  # noqa: BLE001 -- refusal is a proved, fail-open outcome
            self.org.immune_event(
                "skill_refused", {"entry": entry, "reason": type(exc).__name__}
            )
            self._prove(
                MIND_CULTIVATE_CONTROL, attempted=True, ok=False,
                method="BodyMutationBridge", ref=band, reason=type(exc).__name__,
            )
            return None
        self._prove(
            MIND_CULTIVATE_CONTROL, attempted=True, ok=True,
            method="BodyMutationBridge", ref=band, reason="ok",
        )
        return result

    # ---- calcified reflex invocation (zombie-state capability) -----------------
    def invoke_reflex(self, band: str, args: Dict[str, Any],
                      granted: Optional[Dict[str, Any]] = None) -> Any:
        """Run a calcified exec-layer skill through the Limb (with a proof). Works with NO
        MIND; the substrate's hash/capability/provenance/trust gates apply unchanged."""
        try:
            result = self.org.prime.invoke(band, args, granted)
            self._prove(band, attempted=True, ok=True, method="exec-reflex",
                        ref=band, reason="ok")
            return result
        except Exception as ex:
            self._prove(band, attempted=True, ok=False, method="exec-reflex",
                        ref=band, reason=type(ex).__name__)
            self.org.immune_event("reflex_invoke_failed",
                                  {"band": band, "error": type(ex).__name__})
            raise
