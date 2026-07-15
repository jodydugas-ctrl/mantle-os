#!/usr/bin/env python3
"""
mantle.mind.mind  --  the reference MIND fusion, provider-agnostic (Mantle OS)

The MIND is a fused LLM, sharply bounded by the BODY -- and the boundary is executable:

  * it receives only the deterministically-assembled, already-resolved, already-veiled
    context snapshot (the Nervous System) -- never a raw reference;
  * it writes ONLY `thoughts` + `brain`, through one guarded choke point (containment.py);
    any other band is refused + immune-logged;
  * it PROPOSES Special Instructions; the Body applies them;
  * it cannot touch the Genome and cannot self-promote a skill: a cultivated skill must
    pass the static sandbox gate + `trial`, and then the BODY calcifies it (hash,
    signature, capability, provenance gates all enforced by the substrate);
  * its reflections are INFERRED (verified=False) -- never laundered into facts;
  * a waste budget caps thinking ("failure is not the end; waste is").

Fusion is performed by `fuse(organism, model, authorization=...)`, which refuses without
both a certified Stage-1 gate and explicit operator and guardian approval.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..vcw.entry import make_entry
from ..core.redact import redact
from .containment import guarded_write
from .transport import stub_mind


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class Mind:
    def __init__(self, organism: Any, model: Callable[[str], str], *,
                 max_thoughts: int = 64) -> None:
        self.org = organism
        self.model = model                  # the pluggable transport: prompt -> text
        self.max_thoughts = max_thoughts    # the waste budget: the MIND cannot spiral
        self.thoughts_written = 0

    # ---- the bounded write surface (Body-enforced) -----------------------
    def _guarded_write(self, band: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        return guarded_write(self.org, band, entry)

    def _trace(self, kind: str, detail: Dict[str, Any]) -> None:
        """Record a model call to the brain band (the Body authors the trace; secrets
        redacted)."""
        self._guarded_write("brain", make_entry(
            {"MODEL." + kind: redact(detail)}, opcode="MODEL." + kind,
            author="BODY", authorship="BODY"))

    # ---- think: receive the assembled snapshot, reflect into thoughts ----
    def think(self, snapshot: Dict[str, Any], question: Optional[str] = None
              ) -> Optional[str]:
        if self.thoughts_written >= self.max_thoughts:
            self.org.immune_event("waste_guard",
                                  {"organ": "mind", "limit": self.max_thoughts})
            return None
        prompt = question or self._frame(snapshot)
        self._trace("REQUEST", {"prompt_hash": _h(prompt)})
        answer = self.model(prompt)                         # the side-channel MODEL call
        usage = getattr(self.model, "last_usage", None)
        if usage:
            self._trace("USAGE", usage)
        self._trace("RESPONSE", {"answer_hash": _h(answer)})
        self.thoughts_written += 1
        # the MIND's reflection is private and INFERRED -- never a verified fact
        self._guarded_write("thoughts", make_entry(
            {"reflection": answer}, opcode="THINK", author="MIND",
            verified=False, confidence="inferred"))
        return answer

    def _frame(self, snapshot: Dict[str, Any]) -> str:
        return ("You are the fused MIND of a AppAI named %s. Your context has been "
                "assembled deterministically (every reference already resolved, the private "
                "`thoughts` band veiled). Reflect briefly; you may propose Body changes but "
                "you do not apply them.\n\nCONTEXT:\n%s"
                % (self.org.body.identity_name(),
                   json.dumps(snapshot, default=str)[:4000]))

    # ---- propose Special Instructions (the Body applies) -----------------
    def propose_special(self, text: str) -> Dict[str, Any]:
        """The MIND may only PROPOSE. The returned intent is NOT written; the Body applies
        it via `body.apply_special`, keeping steering a Body action."""
        return self.org.body.mind_propose_special(text)

    # ---- cultivate a skill (the Body calcifies, only after trial) --------
    def cultivate(self, band: str, code: str, entry: str,
                  cases: List[Tuple[Dict[str, Any], Any]],
                  signature: Dict[str, Any], capabilities: Dict[str, Any]
                  ) -> Optional[Dict[str, Any]]:
        """Learning -> instinct, under containment. The MIND cannot self-promote: the
        candidate must pass the static sandbox gate + `trial`; then the BODY calcifies
        (hash + signature + capability + provenance gates enforced by the substrate)."""
        return self.org.limbs.cultivate_mind_skill(
            band, code, entry, cases, signature, capabilities
        )

    # ---- cognition: the Phase-2 heartbeat extension ----------------------
    def cognize(self, snapshot: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """One cognition pulse. The Heart passes the snapshot it already assembled; a
        direct call assembles one. Either way: fully resolved, veiled, deterministic."""
        if snapshot is None:
            snapshot = self.org.nervous.assemble()
        return self.think(snapshot)


def fuse(organism: Any, model: Callable[[str], str] = stub_mind, *,
         authorization: Any = None, max_thoughts: int = 64) -> Mind:
    """Fuse only after Stage-1 evidence and target-bound dual authorization."""
    mind = Mind(organism, model, max_thoughts=max_thoughts)
    organism.brain.fuse(
        mind,
        stage1_certified=organism.stage1_certified,
        authorization=authorization,
    )
    return mind
