#!/usr/bin/env python3
"""
mantle.vcw.entry  --  the one entry hasher + the one entry maker (Mantle v3)

The rule is simple and total: the hash covers EVERY field of an entry EXCEPT the four
volatile ones the Body is allowed to flip after the fact -- `id` (assigned on append),
`tombstone`, `quarantined` (immune flags), and `hash` itself. So `authorship` and any other
content-bearing extra field are hash-protected by construction: "what your organ does, you
have done" is true in code, not just in prose.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict

# Fields the Body may set/flip after an entry is born; everything else is inside the hash.
VOLATILE_FIELDS = ("id", "tombstone", "quarantined", "hash")


def entry_hash(entry: Dict[str, Any]) -> str:
    """SHA-256 (first 16 hex chars) over every non-volatile field. Deterministic across
    processes and save/reload: keys sorted, separators fixed."""
    h = {k: v for k, v in entry.items() if k not in VOLATILE_FIELDS}
    blob = json.dumps(h, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def content_hash(content: Any) -> str:
    """A canonical hash of an entry's CONTENT alone -- the deduplication key used by
    metabolism (two entries with the same opcode + content hash are duplicates)."""
    blob = json.dumps(content, separators=(",", ":"), sort_keys=True,
                      default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def make_entry(content: Any, opcode: str = "WRITE", author: str = "BODY",
               source: str = "", **extra) -> Dict[str, Any]:
    """Create one immutable band entry record. Extra fields (e.g. `authorship`, `verified`,
    `confidence`) are INSIDE the hash."""
    e = {"id": None, "ts": time.time(), "opcode": opcode, "author": author,
         "source": source, "content": content, "tombstone": False, "quarantined": False}
    e.update(extra)
    e["hash"] = entry_hash(e)
    return e


def visible(entries) -> list:
    """The base visibility filter: tombstoned and quarantined entries never surface."""
    return [e for e in entries if not e.get("tombstone") and not e.get("quarantined")]
