#!/usr/bin/env python3
"""
mantle.organs.brain  --  the Brain organ: the dormant Phase-2 socket (Mantle OS)

The Brain is the only organ that is FULLY DORMANT in Phase 1: the cube has the bands
(`brain`, `thoughts`); nothing writes them. This module is deliberately just the SOCKET --
it holds a fused cognition object and never imports a model, a transport, or anything
from `mantle.mind`. That import direction is the architecture: Phase-1 code cannot reach
an LLM even by accident.

Fusion contract (what `fuse()` accepts): any object with
    cognize(snapshot) -> Optional[str]
The reference implementation is `mantle.mind.Mind`, which is bounded by the Body: it may
write only `thoughts` + `brain`, it proposes while the Body applies, and it cannot
self-promote a skill. Fusion is REFUSED unless the organism's Stage-1 gate has been
certified (audit before fusion).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .contract import Organ, OrganContract

CONTRACT = OrganContract(
    "brain", "cognition (Phase 2 only) -- the fused MIND's socket; dormant in Phase 1",
    reads=["*"],                       # via the assembled snapshot, never raw layers
    writes=["thoughts", "brain"],      # the ONLY MIND write surface, Body-enforced
    reflexes=[],                       # the Brain is the non-reflex organ; it reasons
    phase1="dormant",
    phase2_extension="receives the assembled context each pulse, thinks into `thoughts`, "
                     "authors INTENTION/DELEGATED dispatches, proposes to the Body",
    audit=[
        "Phase 1: the brain/thoughts bands exist and nothing cognitive writes them",
        "fusion requires a passed Stage-1 gate (audit before fusion)",
        "the fused MIND writes nowhere except thoughts + brain",
        "the fused MIND cannot touch the Genome or self-promote a skill",
    ],
)


class Brain(Organ):
    contract = CONTRACT

    def __init__(self, organism) -> None:
        super().__init__(organism)
        self._mind: Optional[Any] = None

    @property
    def fused(self) -> bool:
        return self._mind is not None

    @property
    def mind(self) -> Optional[Any]:
        return self._mind

    def fuse(self, mind: Any, stage1_certified: bool = False) -> None:
        """Attach a cognition object (Phase 2). Audit before fusion: the caller must
        attest a passed Stage-1 gate; an unattested fusion is refused + immune-logged."""
        if not stage1_certified:
            self.org.immune_event("fusion_refused",
                                  {"reason": "Stage-1 gate not certified"})
            raise PermissionError("audit before fusion: certify the Zombie Body "
                                  "(Stage 1) before fusing a MIND")
        if not callable(getattr(mind, "cognize", None)):
            raise TypeError("a fused MIND must provide cognize(snapshot)")
        self._mind = mind
        self.org.immune_event("fusion", {"mind": type(mind).__name__})

    def defuse(self) -> None:
        """Detach cognition. The Body keeps running -- Phase 1 never depended on it."""
        self._mind = None

    def cognize(self, snapshot: Dict[str, Any]) -> Optional[Any]:
        """The Phase-2 heartbeat extension: offer the assembled snapshot to the fused
        MIND. Fail-open: a sick MIND degrades to an immune event; the pulse completes."""
        if self._mind is None:
            return None
        try:
            return self._mind.cognize(snapshot)
        except Exception as e:                   # noqa: BLE001 -- cognition is fail-open
            self.org.immune_event("cognition_fault",
                                  {"error": "%s: %s" % (type(e).__name__, e)})
            return None
