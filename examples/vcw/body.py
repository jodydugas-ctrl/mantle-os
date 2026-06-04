#!/usr/bin/env python3
"""
body.py  --  The BODY store (Mantle v2.1)

CORRECTION captured here: the PRIMER lives in the BODY, not in the VCW cube. The cube is
pure experiential memory (read/append-only). The Body holds the agent's *defining* data and
provides the small MUTABLE surface the append-only VCW cannot:

    Primer               read-only    -- who you are: identity + TRUTHS + COMMANDMENTS
    Special Instructions read/write    -- steering; the MIND GUIDES, the BODY APPLIES
    Immunization         read/write    -- safety rules (a VCW immune layer is the working copy)

The API boot order sent to a model is:  Primer + Special Instructions + Immunization.

The Body is also addressable like a layer:  <body.immune.11>  ->  the 11th immunization entry.

Finally, the Body holds the durable SELF RECORD -- Primer + commandments + the LINEAGE INDEX
(which cube generation is Prime, and where the ancestors live). That record, not any cube, is
the continuity of the organism across rebirths.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def _entry(content: Any, author: str = "BODY") -> Dict[str, Any]:
    return {"ts": time.time(), "author": author, "content": content}


class Body:
    CATEGORIES = ("primer", "special", "immunization")

    def __init__(self) -> None:
        self._primer: List[Dict[str, Any]] = []
        self._special: List[Dict[str, Any]] = []
        self._immunization: List[Dict[str, Any]] = []
        self._primer_sealed = False
        # lineage index: generation -> {"role": "prime"|"ancestral", "location": str}
        self.lineage_index: Dict[int, Dict[str, Any]] = {}
        self.prime_generation: int = 0

    # ---- birth: set the Primer once, immutably -----------------------------
    def birth(self, identity: Dict[str, Any], truths: List[str],
              commandments: List[str]) -> None:
        if self._primer_sealed:
            raise PermissionError("Primer is immutable post-birth")
        self._primer = [_entry({"identity": identity}),
                        _entry({"truths": truths}),
                        _entry({"commandments": commandments})]
        self._primer_sealed = True
        # the Commandments seed the Immunization working copy (doctrine -> immune)
        for c in commandments:
            self._immunization.append(_entry(c, author="BODY"))

    # ---- Special Instructions: MIND guides, BODY applies -------------------
    def mind_propose_special(self, text: str) -> Dict[str, Any]:
        """The MIND may only PROPOSE a change. Returns an intent; it is not written."""
        return {"intent": "special_instruction", "text": text, "author": "MIND"}

    def apply_special(self, text: str, source: str = "MIND") -> Dict[str, Any]:
        """Only the BODY writes. (In a full system this is driven by a dispatch reflex.)"""
        e = _entry(text, author="BODY")
        e["guided_by"] = source
        self._special.append(e)
        return e

    # ---- Immunization (read/write) ----------------------------------------
    def add_immunization(self, rule: str) -> Dict[str, Any]:
        e = _entry(rule, author="BODY")
        self._immunization.append(e)
        return e

    # ---- addressing: the Body as a referenceable layer --------------------
    def category(self, name: str) -> List[Dict[str, Any]]:
        return {"primer": self._primer, "special": self._special,
                "immune": self._immunization, "immunization": self._immunization}[name]

    def get(self, category: str, index: int) -> Optional[Dict[str, Any]]:
        items = self.category(category)
        return items[index] if 0 <= index < len(items) else None

    # ---- the boot order assembled for the model ---------------------------
    def boot_order(self) -> Dict[str, Any]:
        return {
            "primer": [e["content"] for e in self._primer],
            "special_instructions": [e["content"] for e in self._special],
            "immunization": [e["content"] for e in self._immunization],
        }

    def boot_text(self) -> str:
        bo = self.boot_order()
        lines = ["=== PRIMER ==="]
        for p in bo["primer"]:
            lines.append("  " + str(p))
        lines.append("=== SPECIAL INSTRUCTIONS ===")
        lines += ["  " + str(s) for s in bo["special_instructions"]] or ["  (none)"]
        lines.append("=== IMMUNIZATION ===")
        lines += ["  " + str(i) for i in bo["immunization"]]
        return "\n".join(lines)

    # ---- the durable self record (continuity across generations) ----------
    def self_record(self) -> Dict[str, Any]:
        return {
            "primer": [e["content"] for e in self._primer],
            "prime_generation": self.prime_generation,
            "lineage_index": self.lineage_index,
        }

    def identity_name(self) -> str:
        for e in self._primer:
            ident = e["content"].get("identity") if isinstance(e["content"], dict) else None
            if ident and "name" in ident:
                return ident["name"]
        return "unnamed AppAI"

    # ---- persistence ------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {"primer": self._primer, "special": self._special,
                "immunization": self._immunization, "primer_sealed": self._primer_sealed,
                "lineage_index": {str(k): v for k, v in self.lineage_index.items()},
                "prime_generation": self.prime_generation}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Body":
        b = cls()
        b._primer = d.get("primer", [])
        b._special = d.get("special", [])
        b._immunization = d.get("immunization", [])
        b._primer_sealed = d.get("primer_sealed", bool(b._primer))
        b.lineage_index = {int(k): v for k, v in d.get("lineage_index", {}).items()}
        b.prime_generation = d.get("prime_generation", 0)
        return b
