#!/usr/bin/env python3
"""
entry.py  --  The one entry hasher (Mantle v2.3)

The VCW had TWO copies of the entry-hash routine -- one in `vcw_cube.py` (the base codec) and one
in `drivers.py` (the v2.1 runtime) -- and they disagreed. The codec hashed exactly
(ts, opcode, author, source, content); the runtime's `make_entry` accepted `**extra` fields
(e.g. `authorship`, `verified`, `confidence`) and then hashed only that same fixed set -- so every
EXTRA field lived OUTSIDE the hash. That quietly broke a doctrine guarantee: the PRIMER calls the
dispatch `authorship` field "permanent ... never rewritten" and the Organ Atlas audits it as
"present and immutable" -- yet a mutated `authorship` would not break the entry hash, so `verify()`
could never catch it.

This module is the single source of truth for the entry hash. The rule is simple and total:

    the hash covers EVERY field of an entry EXCEPT the four volatile ones the Body is allowed to
    flip after the fact -- `id` (assigned on append), `tombstone`, `quarantined` (immune flags),
    and `hash` itself.

So `authorship` and any other content-bearing field are now hash-protected by construction:
"what your organ does, you have done" becomes true in code, not just in prose. For an entry with
no extra fields, this reproduces the legacy codec hash exactly (the non-volatile set is then
{ts, opcode, author, source, content}), so the base codec keeps verifying unchanged.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

# Fields the Body is permitted to set/flip after an entry is born; everything else is covered
# by the hash. `id` is assigned on append; `tombstone`/`quarantined` are immune reflexes; `hash`
# is the digest itself.
VOLATILE_FIELDS = ("id", "tombstone", "quarantined", "hash")


def entry_hash(entry: Dict[str, Any]) -> str:
    """SHA-256 (first 16 hex chars) over every non-volatile field of an entry.

    Deterministic across processes and save/reload: keys are sorted and separators fixed.
    """
    h = {k: v for k, v in entry.items() if k not in VOLATILE_FIELDS}
    blob = json.dumps(h, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


# Backward-compatible alias: existing code imports `_entry_hash`.
_entry_hash = entry_hash
