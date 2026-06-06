#!/usr/bin/env python3
"""
organs/nervous.py  --  The Nervous System organ: routing + Context Assembly (Mantle v2.3)

The Nervous System owns the reference resolver (delegated to refs.py) and the Context Assembly
Protocol: the deterministic act of materializing a fully-resolved context snapshot from the cube
+ Body. The doctrine: an AppAI "sees the whole of its experience in perfect clarity" -- Context
Assembly IS that whole-at-once view.

Two guarantees, both Body reflexes (no LLM):
  * NO unresolved reference is ever handed onward. Every `<...>` is resolved during assembly; a
    dangling reference is logged to the immune band, never silently dropped.
  * The veil is applied -- the private `thoughts` band is excluded unless explicitly lifted.

In Phase 2 the assembled snapshot is exactly what the MIND receives -- already resolved, already
veiled. The MIND never sees a raw reference.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

_REF_RE = re.compile(r"<[^<>]+>")


class NervousSystem:
    def __init__(self, organism: Any) -> None:
        self.org = organism

    # ---- resolve -----------------------------------------------------------
    def resolve_all(self, obj: Any) -> Any:
        """Walk a structure and replace any value that is EXACTLY a reference with its resolved
        value (dangling -> immune event, via Organism.resolve)."""
        if isinstance(obj, str):
            s = obj.strip()
            return self.org.resolve(s) if _REF_RE.fullmatch(s) else obj
        if isinstance(obj, dict):
            return {k: self.resolve_all(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.resolve_all(v) for v in obj]
        return obj

    def _unresolved(self, obj: Any, out: List[str]) -> None:
        if isinstance(obj, str):
            if _REF_RE.search(obj):
                out.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                self._unresolved(v, out)
        elif isinstance(obj, list):
            for v in obj:
                self._unresolved(v, out)

    # ---- the 9-step Context Assembly Protocol -----------------------------
    def assemble(self, reveal_private: bool = False) -> Dict[str, Any]:
        """Deterministically assemble a fully-resolved, veiled context snapshot. `_complete` is
        True iff no unresolved reference remains (any leftover is an immune event).

        Resolution (step 7) and the completeness scan (step 9) are done in ONE traversal of the
        snapshot skeleton instead of two: each leaf is resolved, then the produced value is scanned
        for any remaining reference (embedded, or inside a resolved value) -- which is exactly what
        a separate `_unresolved` walk of the final snapshot would find. `resolve_all`/`_unresolved`
        remain for callers/tests."""
        leftover: List[str] = []

        def resolve_and_check(obj: Any) -> Any:
            if isinstance(obj, str):
                s = obj.strip()
                val = self.org.resolve(s) if _REF_RE.fullmatch(s) else obj
                self._unresolved(val, leftover)        # scan the produced value (step 9, inline)
                return val
            if isinstance(obj, dict):
                return {k: resolve_and_check(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [resolve_and_check(v) for v in obj]
            return obj

        snap: Dict[str, Any] = {
            "primer": self.org.body.boot_order(),                                  # 1 identity/boot
            "identity": self.org.prime.read("identity"),                           # 2 self-state
            "facts": self.org.prime.read("facts"),                                 # 3 truths
            "events": self.org.prime.read("events"),                               # 4 history
            "discoveries": self.org.prime.read("discoveries"),                     # 5 learned
            "senses": self.org.prime.read("senses"),                               # 6 perception
            "thoughts": self.org.prime.read("thoughts", reveal_private=reveal_private),  # 8 veil
        }
        snap = resolve_and_check(snap)                                  # 7 resolve + 9 completeness
        if leftover:
            self.org.immune_event("unresolved_ref",
                                  {"count": len(leftover), "sample": leftover[:3]})
        snap["_complete"] = not leftover
        return snap
