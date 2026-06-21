#!/usr/bin/env python3
"""
mantle.mind.runtime  --  the AppAI runtime: how an agent thinks AS the organism (Argonaut, of the Mantle lineage)

A coding agent (or any LLM-driven operator) should experience the organism FROM INSIDE --
through Body APIs, never raw file mutation. AppAIRuntime is that surface. Everything it
exposes is mediated:

  inspect       the Body's boot order, organ contracts, lineage, band pressures, reflex
                surface -- the whole anatomy, read-only
  perceive      visible VCW memory through the veil (private/tombstoned/quarantined hidden)
  orient        assemble the deterministic context snapshot (what a MIND would receive)
  act           propose actions THROUGH Limbs (dispatch + proofs); never a private I/O path
  steer         propose Special Instructions; the Body applies them
  learn         request skill cultivation; the Body trials, gates, and calcifies
  wonder        self-inquiry via the Inner Voice; answers stay INFERRED, never facts

The runtime holds no privileged handles: every write it can cause goes through the same
organ reflexes and containment gates as any other caller. An agent with this runtime can
do everything an AppAI can do -- and nothing the Body forbids.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from .mind import Mind, fuse
from .inner_voice import InnerVoice
from .transport import stub_mind


class AppAIRuntime:
    def __init__(self, organism: Any, model: Optional[Callable[[str], str]] = None) -> None:
        self.org = organism
        self.model = model or stub_mind
        self._inner: Optional[InnerVoice] = None

    # ================= inspect: the anatomy, read-only ======================
    def inspect_body(self) -> Dict[str, Any]:
        """The whole anatomy at a glance: identity, boot order, lineage, organ contracts,
        reflex surface, band map + pressures, certification state."""
        prime = self.org.prime
        return {
            "identity": self.org.body.identity_name(),
            "boot_order": self.org.body.boot_order(),
            "prime_generation": prime.generation,
            "lineage_index": self.org.body.lineage_index,
            "stage1_certified": self.org.stage1_certified,
            "mind_fused": self.org.brain.fused,
            "organ_contracts": self.org.manifests(),
            "reflex_surface": self.org.bus.reflex_surface(),
            "bands": {name: {"head": boot["head"], "span": boot["span"],
                             "encoding": boot["encoding"], "private": boot["private"],
                             "purpose": boot["purpose"],
                             "pressure": round(prime.pressure(name), 3)}
                      for name, boot in prime.bands.items()},
        }

    # ================= perceive: visible memory, through the veil ============
    def read_band(self, band: str) -> Any:
        """Visible entries only -- the veil, tombstones, and quarantine always apply.
        (Lifting the veil on `thoughts` is a MIND privilege exercised via cognition, not
        a runtime bypass.)"""
        return self.org.prime.read(band)

    def resolve(self, ref: str) -> Any:
        """Resolve a `<...>` reference; a dangling reference becomes an immune event."""
        return self.org.resolve(ref)

    # ================= orient: the deterministic snapshot =====================
    def assemble_context(self) -> Dict[str, Any]:
        return self.org.nervous.assemble()

    # ================= act: through Limbs, with proofs ========================
    def sense(self, signal: Dict[str, Any]) -> str:
        """Feed an inbound signal through the ONLY inbound boundary (Senses)."""
        return self.org.senses.inhale(signal)

    def operate(self, control_id: str, value: Any) -> Dict[str, Any]:
        """Drive a mapped control through its ControlBridge (proof recorded)."""
        return self.org.limbs.operate(control_id, value)

    def invoke_skill(self, band: str, args: Dict[str, Any],
                     granted: Optional[Dict[str, Any]] = None) -> Any:
        """Run a calcified reflex through the Limb (gates + proof apply)."""
        return self.org.limbs.invoke_reflex(band, args, granted)

    # ================= steer: propose; the Body applies ========================
    def propose_special_instruction(self, text: str) -> Dict[str, Any]:
        """Returns the intent AND the Body's application of it -- the two-step made
        visible: the proposal is authored MIND, the applied entry is authored BODY."""
        intent = self.org.body.mind_propose_special(text)
        applied = self.org.body.apply_special(intent["text"])
        return {"intent": intent, "applied": applied}

    # ================= learn: request cultivation; the Body gates ==============
    def request_skill(self, band: str, code: str, entry: str,
                      cases: List[Tuple[Dict[str, Any], Any]],
                      signature: Optional[Dict[str, Any]] = None,
                      capabilities: Optional[Dict[str, Any]] = None
                      ) -> Optional[Dict[str, Any]]:
        """Propose a skill. The Body trials it (static sandbox first), then calcifies it
        behind the hash/signature/capability/provenance gates. A refused or failing
        candidate is an immune event and never becomes an instinct."""
        mind = self._require_mind()
        return mind.cultivate(band, code, entry, cases,
                              signature or {"by": "appai-runtime"},
                              capabilities or {})

    # ================= wonder: self-inquiry, honestly inferred ==================
    def self_inquire(self, question: str, mode: str = "neutral"):
        """Ask the Inner Voice. The answer is tagged inferred and lands in discoveries
        (or private thoughts for `oppose`) -- NEVER in facts."""
        if self._inner is None:
            self._inner = InnerVoice(self.org, self.model)
        return self._inner.ask(question, mode)

    # ================= cognition plumbing ========================================
    def _require_mind(self) -> Mind:
        if not self.org.brain.fused:
            raise PermissionError("no MIND fused: certify Stage 1, then fuse() "
                                  "(audit before fusion)")
        return self.org.brain.mind

    def fuse_mind(self, model: Optional[Callable[[str], str]] = None,
                  max_thoughts: int = 64) -> Mind:
        """Fuse a MIND (Phase 2). Refused unless the Stage-1 gate has been certified."""
        return fuse(self.org, model or self.model, max_thoughts=max_thoughts)
