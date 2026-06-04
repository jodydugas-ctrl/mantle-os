#!/usr/bin/env python3
"""
organs/heart.py  --  The Heart organ: clock, heartbeat, circulation (Mantle v2.3)

The Heart is the only organ whose Phase-1 state is unconditionally ACTIVE: the Body has a
heartbeat with NO brain. Each pulse is a complete moment of awareness (the doctrine's "native
tempo"). The Heart owns:

  tick         advance the clock (one beat)
  pulse-check  detect a stalled heartbeat -> immune event (never swallowed)
  circulate    flush dirty state durably (the staged-commit cadence; a sink is injected)
  dual-flush   persist on BOTH an explicit checkpoint AND an atexit handler

Phase 2 extension: the SAME heartbeat additionally invokes cognition (a callback). In Phase 1 the
cognition callback is None -- proving the loop runs with no LLM. Nothing here imports a model.
"""
from __future__ import annotations

import atexit
from typing import Any, Callable, Optional


class Heart:
    def __init__(self, organism: Any, circulate: Optional[Callable[[], None]] = None) -> None:
        self.org = organism
        self._circulate_cb = circulate          # the durable sink (e.g. Organism.save); injected
        self.beats = 0
        self.last_beat = 0
        self.flushes = 0
        self._atexit_installed = False

    # ---- reflexes ---------------------------------------------------------
    def tick(self) -> int:
        self.beats += 1
        return self.beats

    def pulse_check(self) -> bool:
        """A missed pulse is logged as an immune event, never swallowed (fail-open, not silent)."""
        if self.beats <= self.last_beat:
            self.org.immune_event("stalled_pulse", {"beats": self.beats, "last": self.last_beat})
            return False
        self.last_beat = self.beats
        return True

    def circulate(self) -> int:
        """Flush dirty bands durably. The injected sink performs the staged commit; a missing sink
        is a no-op (a headless Body still has a heartbeat). Fail-open."""
        try:
            if self._circulate_cb is not None:
                self._circulate_cb()
        except Exception:                        # a sick flush degrades; it never crashes the host
            self.org.immune_event("flush_failed", {"organ": "heart"})
        self.flushes += 1
        return self.flushes

    def beat(self, cognition: Optional[Callable[[Any], None]] = None) -> bool:
        """One pulse. In Phase 1, cognition is None: the Body lives with no brain. In Phase 2 the
        SAME pulse invokes the MIND -- an extension, never a replacement of the reflex."""
        self.tick()
        ok = self.pulse_check()
        self.circulate()
        if cognition is not None:                # Phase-2 extension only
            cognition(self.org)
        return ok

    def run(self, beats: int, cognition: Optional[Callable[[Any], None]] = None) -> int:
        for _ in range(beats):
            self.beat(cognition)
        return self.beats

    # ---- dual-flush (durability) -----------------------------------------
    def install_dual_flush(self) -> bool:
        """Persist on BOTH an explicit checkpoint (circulate) AND an atexit handler, so a cube is
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
