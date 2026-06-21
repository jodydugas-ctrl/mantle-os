#!/usr/bin/env python3
"""
mantle.organs.memory  --  the Memory organ: recall & metabolism (Argonaut, of the Mantle lineage)

Owns the durable knowledge bands -- identity, facts, events, discoveries -- AND their
metabolism: the hot working-set -> durable flush cycle, on-demand layer allocation,
compaction, deduplication, and layer reclaim/reuse. "Every layer has a purpose; be
efficient."

CAPACITY DOCTRINE (executable here): the substrate fires the pressure hook when a band
crosses OVERFLOW (0.75) or EMERGENCY (0.90) of its reserved span; Memory's response is
METABOLISM (already run by the substrate) plus an immune event so the pressure is on the
record -- never a rebirth, never a silent reset. Promotion of inferred content into
`facts` requires external, cited evidence (verified=True + a source) -- self-inquiry can
never launder an inference into a fact.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .contract import Organ, OrganContract
from ..vcw.entry import make_entry
from ..vcw import metabolism as _met

MEMORY_BANDS = ("identity", "facts", "events", "discoveries")

CONTRACT = OrganContract(
    "memory", "recall & metabolism -- durable knowledge + keeping the working set lean",
    reads=list(MEMORY_BANDS),
    writes=list(MEMORY_BANDS),
    reflexes=[
        {"name": "remember", "trigger": "an organ records knowledge",
         "effect": "append one immutable, hashed entry to the owned band"},
        {"name": "recall", "trigger": "a read", "effect": "visible entries through the veil, "
         "ordered by weight (graded memory)"},
        {"name": "deweight", "trigger": "a value is contradicted/superseded",
         "effect": "lower its weight via an append-only event; it survives as a ghost, never "
                   "overwritten or deleted (M3)"},
        {"name": "allocate", "trigger": "a band tail fills",
         "effect": "grow onto the next layer in range, preferring the reuse pool"},
        {"name": "compact", "trigger": "metabolism / pressure",
         "effect": "drop tombstoned entries; emptied layers return to the free pool"},
        {"name": "dedupe", "trigger": "aggressive metabolism",
         "effect": "tombstone duplicate (opcode, content) entries; history preserved"},
        {"name": "overflow", "trigger": "pressure >= 0.75 (emergency >= 0.90)",
         "effect": "metabolize + immune event; may MOTIVATE a chosen rebirth, never force one"},
        {"name": "promote", "trigger": "external, cited evidence arrives",
         "effect": "an inferred discovery may become a fact ONLY with verified evidence"},
    ],
    phase1="active",
    phase2_extension="the MIND may REQUEST a write; the write is performed by this organ "
                     "into the correct band; metabolism stays pure Body",
    audit=[
        "entries are immutable + hashed; reads honor the veil; history never rewritten",
        "capacity != rebirth: thresholds trigger metabolism (0.75 overflow, 0.90 emergency)",
        "compaction preserves visible history",
        "inferred content is never auto-promoted to facts",
        "deweighting is graded + append-only: a ghost is hidden by default yet recoverable, "
        "and the original entry is never mutated",
    ],
)


class Memory(Organ):
    contract = CONTRACT

    # ---- remember / recall ---------------------------------------------------
    def remember(self, band: str, content: Any, opcode: str = "WRITE",
                 source: str = "", **extra) -> Dict[str, Any]:
        e = make_entry(content, opcode=opcode, author="BODY", source=source, **extra)
        return self.append(band, e)

    def recall(self, band: str) -> List[Dict[str, Any]]:
        """Visible entries through the veil, ordered by weight (ghosts hidden)."""
        return self.org.prime.read(band)

    # ---- graded memory (M3): deweight instead of delete -----------------------
    def deweight(self, band: str, entry_id: int, weight: float = 0.0) -> bool:
        """Lower an entry's weight (default: fully suppress) via an append-only event. The
        entry becomes a behavioral ghost -- hidden from `recall`, still recoverable and never
        overwritten. Restoring is the same call with a higher weight."""
        return self.org.prime.deweight(band, entry_id, weight)

    def recall_ghosts(self, band: str) -> List[Dict[str, Any]]:
        """Surface the suppressed ghosts of a band -- the latent values the heavy path hid."""
        return self.org.prime.read(band, ghosts=True)

    # ---- metabolism -------------------------------------------------------------
    def compact(self, band: str) -> Dict[str, Any]:
        return self.org.prime.compact(band)

    def dedupe(self, band: str) -> Dict[str, Any]:
        return self.org.prime.dedupe(band)

    def metabolize(self, band: str, aggressive: bool = False) -> Dict[str, Any]:
        return self.org.prime.reclaim(band, aggressive=aggressive)

    def pressure(self, band: str) -> float:
        return self.org.prime.pressure(band)

    def pressures(self) -> Dict[str, float]:
        return {b: self.org.prime.pressure(b) for b in self.org.prime.bands}

    def on_pressure(self, band: str, level: str, report: Dict[str, Any]) -> None:
        """The substrate's pressure hook: metabolism already ran; put it on the record.
        NOTE WHAT THIS DOES NOT DO: it never calls rebirth."""
        self.org.immune_event("capacity_" + level, {
            "band": band, "pressure_before": report.get("pressure_before"),
            "pressure_after": report.get("pressure_after"),
            "response": "metabolism (compact%s)" % ("+dedupe" if level == "emergency" else ""),
        })
        self.bus.emit("pressure", {"band": band, "level": level})

    # ---- honest promotion (inference -> fact requires evidence) ----------------
    def promote_to_fact(self, discovery_entry: Dict[str, Any],
                        evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Promote an inferred discovery into `facts` -- ONLY with external, cited
        evidence. Anything less is refused and recorded as an immune event."""
        if not evidence or not evidence.get("source") or not evidence.get("verified"):
            self.org.immune_event("promotion_refused", {
                "reason": "facts require external, cited, verified evidence",
                "discovery_id": discovery_entry.get("id")})
            raise PermissionError("inferred content cannot become a fact without "
                                  "external, cited, verified evidence")
        return self.remember("facts", discovery_entry.get("content"),
                             opcode="PROMOTED",
                             source=str(evidence.get("source")),
                             verified=True, evidence=evidence)
