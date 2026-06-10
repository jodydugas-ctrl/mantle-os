#!/usr/bin/env python3
"""
mantle.organs.heart  --  the Heart organ: clock, heartbeat, circulation (Mantle v3)

The Heart is the only organ whose Phase-1 state is unconditionally ACTIVE: the Body has a
heartbeat with NO brain. Each pulse is a complete moment of awareness, in a fixed,
deterministic order (the organism's native tempo):

    1. tick                 advance the clock; emit `pulse` on the bus
    2. sense intake         Senses drains its inbox (all inbound enters here)
    3. context assembly     the Nervous System materializes the whole-at-once snapshot
    4. reflex execution     bus subscribers fire (registration order, fail-open)
    5. immune scan          the Immune System verifies the cube (every scan_every beats)
    6. checkpoint           circulate: flush dirty state durably (staged atomic commit)

Phase 2 extension: the SAME pulse offers the assembled snapshot to the fused Brain
(cognition) -- an extension of the reflex, never a replacement. In Phase 1 the Brain slot
is empty and the identical loop runs whole. Nothing here imports a model.
"""
from __future__ import annotations

import atexit
from typing import Any, Callable, Dict, Optional

from .contract import Organ, OrganContract

CONTRACT = OrganContract(
    "heart", "circulation & pulse -- the clock that drives every periodic Body reflex",
    reads=[],
    writes=[],          # the Heart drives; it owns no band (its faults go to Immune)
    reflexes=[
        {"name": "tick", "trigger": "each beat", "effect": "advance the clock; emit `pulse`"},
        {"name": "pulse-check", "trigger": "each beat",
         "effect": "a stalled heartbeat becomes an immune event, never swallowed"},
        {"name": "circulate", "trigger": "each beat / checkpoint / atexit",
         "effect": "flush dirty state durably via the staged-commit sink (fail-open)"},
        {"name": "dual-flush", "trigger": "install",
         "effect": "persist on BOTH explicit checkpoint AND an atexit handler"},
    ],
    phase1="active",
    phase2_extension="the same pulse additionally offers the assembled snapshot to cognition",
    audit=[
        "heartbeat runs without an LLM (cognition slot empty in Phase 1)",
        "pulse order is fixed: tick, intake, assembly, reflexes, scan, checkpoint",
        "dual-flush persists on checkpoint and atexit",
        "a missed pulse is logged, never swallowed",
    ],
)


class Heart(Organ):
    contract = CONTRACT

    def __init__(self, organism, circulate: Optional[Callable[[], None]] = None,
                 scan_every: int = 4) -> None:
        super().__init__(organism)
        self._circulate_cb = circulate          # the durable sink (e.g. Organism.save)
        self.scan_every = max(1, int(scan_every))
        self.beats = 0
        self.last_beat = 0
        self.flushes = 0
        self._atexit_installed = False

    def set_circulate(self, sink: Optional[Callable[[], None]]) -> None:
        self._circulate_cb = sink

    # ---- reflexes ---------------------------------------------------------
    def tick(self) -> int:
        self.beats += 1
        return self.beats

    def pulse_check(self) -> bool:
        """A missed pulse is logged as an immune event, never swallowed."""
        if self.beats <= self.last_beat:
            self.org.immune_event("stalled_pulse",
                                  {"beats": self.beats, "last": self.last_beat})
            return False
        self.last_beat = self.beats
        return True

    def circulate(self) -> int:
        """Flush dirty state durably. The injected sink performs the staged commit; a
        missing sink is a no-op (a headless Body still has a heartbeat). Fail-open."""
        try:
            if self._circulate_cb is not None:
                self._circulate_cb()
        except Exception:                        # a sick flush degrades, never crashes
            self.org.immune_event("flush_failed", {"organ": "heart"})
        self.flushes += 1
        return self.flushes

    # ---- the pulse ---------------------------------------------------------
    def beat(self, assemble: bool = False) -> Dict[str, Any]:
        """One complete pulse in the fixed order. Returns a beat report. `assemble`
        forces context assembly even with no fused Brain (it is deterministic and free
        of LLMs either way); with a fused Brain it always runs, and the SAME snapshot
        is offered to cognition."""
        report: Dict[str, Any] = {"beat": self.tick()}
        self.bus.emit("pulse", {"beat": self.beats})                    # 1 tick
        report["ok"] = self.pulse_check()
        report["intake"] = self.org.senses.drain()                      # 2 sense intake
        snapshot = None
        fused = self.org.brain.fused
        if assemble or fused:
            snapshot = self.org.nervous.assemble()                      # 3 context assembly
            report["assembled"] = snapshot.get("_complete", False)
        # 4 reflex execution: bus subscribers fired during emit (registration order)
        if self.beats % self.scan_every == 0:
            report["scan_problems"] = len(self.org.immune.scan())       # 5 immune scan
        report["flushes"] = self.circulate()                            # 6 checkpoint
        if fused:                                                       # Phase-2 extension
            report["cognition"] = self.org.brain.cognize(snapshot)
        self.bus.emit("checkpoint", {"beat": self.beats})
        return report

    def run(self, beats: int, assemble: bool = False) -> int:
        for _ in range(beats):
            self.beat(assemble=assemble)
        return self.beats

    # ---- dual-flush (durability) -----------------------------------------
    def install_dual_flush(self) -> bool:
        """Persist on BOTH an explicit checkpoint AND an atexit handler, so a cube is
        never lost to an ungraceful shutdown."""
        if not self._atexit_installed:
            atexit.register(self._safe_flush)
            self._atexit_installed = True
        return self._atexit_installed

    def _safe_flush(self) -> None:
        try:                                     # atexit must never raise on the way down
            self.circulate()
        except Exception:
            pass
