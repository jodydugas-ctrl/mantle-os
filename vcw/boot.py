#!/usr/bin/env python3
"""
boot.py  --  Programmable boot sectors + the driver registry (Mantle v2.1)

The key idea: a layer (or cube) is self-describing. Its BOOT SECTOR declares HOW its
payload is encoded and how to read / retrieve / append it. The Body always knows how to
read a boot sector (fixed, universal format); the boot sector then names a PROGRAMMABLE
payload protocol -- a registered "driver".

    two-level encoding
      level 1  boot-sector format   = fixed & universal (the Body always understands it)
      level 2  payload format        = programmable (declared by the boot sector)

A driver implements three verbs -- read / retrieve / append -- exactly the operations the
boot sector promises. Drivers live in the Body (trusted, shipped code). The boot sector is
data that *selects* a driver and supplies parameters. That keeps memory declarative and the
Body in control of all storage mechanics -- the same Body/MIND split, one level down.

This module defines: the boot-sector schema helpers, the Driver base class, and the global
registry. Concrete drivers live in drivers.py and register themselves on import.
"""
from __future__ import annotations

import hashlib
from typing import Any, Callable, Dict, List, Optional


# ----------------------------------------------------------------------------
# Boot-sector schema
# ----------------------------------------------------------------------------
def make_band_boot(band: str, head: int, encoding: str = "log-json",
                   params: Optional[Dict[str, Any]] = None,
                   private: bool = False, span: int = 1,
                   purpose: str = "") -> Dict[str, Any]:
    """A band's boot sector: which head layer, which driver, with what params.

    A band reserves a RANGE of `span` layers starting at `head`. Physical layers within that
    range are allocated ON DEMAND as the band fills, and reclaimed for reuse after compaction
    (see lineage.Cube). `purpose` is a human-readable label for what this band/layer is for --
    every layer should have a purpose. `span=1` is the default (a single-layer band).
    """
    return {
        "band": band,
        "head": head,
        "span": max(1, int(span)),   # layers reserved for this band: [head, head+span-1]
        "purpose": purpose or band,  # every layer has a declared purpose
        "encoding": encoding,        # selects a registered driver
        "params": params or {},      # driver-specific configuration
        "private": bool(private),    # veiled on read unless the MIND lifts it
        "v": 2,
    }


def make_cube_boot(generation: int, bands: Dict[str, Dict[str, Any]],
                   identity_in_body: bool = True) -> Dict[str, Any]:
    """The Cube Boot Sector: the authoritative band map for one cube/generation.

    identity_in_body=True means the Primer/commandments do NOT live in this cube -- they
    live in the BODY (the corrected v2.1 architecture). The cube is pure experiential memory.
    """
    return {
        "format": "vcw-cube-png-v2",
        "generation": generation,
        "identity_in_body": identity_in_body,
        "bands": bands,
    }


def code_hash(code: str) -> str:
    """The canonical hash binding an exec layer's boot sector to its code payload."""
    return "sha256:" + hashlib.sha256(code.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------
# Driver base + registry
# ----------------------------------------------------------------------------
class Driver:
    """A payload protocol. Subclasses declare a `name` and implement the verbs.

    `content` is the driver-native in-memory representation of one layer:
      log-json   -> list[entry dict]
      keyvalue   -> dict
      calendar-spatial -> bytearray canvas (real RGBA pixels)
      exec       -> dict {code, code_hash, entry, signature, capabilities, limits, provenance}
    """
    name: str = "base"

    def empty(self, params: Dict[str, Any]) -> Any:
        """Return the empty/initial content for a freshly materialized layer."""
        raise NotImplementedError

    def read(self, content: Any, params: Dict[str, Any],
             reveal_private: bool = False) -> Any:
        """Return the whole layer, decoded (with the veil applied where relevant)."""
        raise NotImplementedError

    def retrieve(self, content: Any, params: Dict[str, Any], address: Any) -> Any:
        """Return one item by address (entry index, key, or coordinate tuple)."""
        raise NotImplementedError

    def append(self, content: Any, params: Dict[str, Any], value: Any) -> Any:
        """Add/derive a new state; return the updated content. (No effect for read-only.)"""
        raise NotImplementedError


_REGISTRY: Dict[str, Driver] = {}


def register(driver):
    """Register a driver. Usable as a class decorator: stores an INSTANCE in the registry
    but returns the class unchanged so `ClassName()` still works elsewhere."""
    inst = driver() if isinstance(driver, type) else driver
    _REGISTRY[inst.name] = inst
    return driver


def get_driver(encoding: str) -> Driver:
    if encoding not in _REGISTRY:
        raise KeyError("no driver registered for encoding %r (have: %s)"
                       % (encoding, ", ".join(sorted(_REGISTRY)) or "<none>"))
    return _REGISTRY[encoding]


def registered_encodings() -> List[str]:
    return sorted(_REGISTRY)
