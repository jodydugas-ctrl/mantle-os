#!/usr/bin/env python3
"""
mantle.vcw.bands  --  boot sectors, the driver registry, the standard genome,
                      and the capacity thresholds (Mantle OS)

Two-level encoding:
  level 1  boot-sector format  = fixed & universal (the Body always understands it)
  level 2  payload format      = programmable (the boot sector names a registered driver)

A band reserves a RANGE of `span` layers starting at `head`; physical layers materialize on
demand and reclaimed layers return to a per-band free pool. Every band declares a purpose.

CAPACITY DOCTRINE (executable): a band's *pressure* is the fraction of its reserved span
that is allocated. Crossing OVERFLOW (0.75) fires an `overflow` immune event and triggers
metabolism (compact/dedupe/reclaim). Crossing EMERGENCY (0.90) fires `emergency` and aggressive
metabolism. Capacity NEVER triggers rebirth: rebirth stays a separate, chosen reformat.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

# ---- capacity thresholds (fractions of a band's reserved span) -------------
OVERFLOW_THRESHOLD  = 0.75   # metabolize: compact, dedupe, reclaim
EMERGENCY_THRESHOLD = 0.90   # aggressive metabolism + emergency immune event


def make_band_boot(band: str, head: int, encoding: str = "log-json",
                   params: Optional[Dict[str, Any]] = None,
                   private: bool = False, span: int = 1,
                   purpose: str = "") -> Dict[str, Any]:
    """A band's boot sector: head layer, reserved span, driver, params, veil flag, purpose."""
    return {
        "band": band,
        "head": head,
        "span": max(1, int(span)),
        "purpose": purpose or band,
        "encoding": encoding,
        "params": params or {},
        "private": bool(private),
        "v": 3,
    }


def make_cube_boot(generation: int, bands: Dict[str, Dict[str, Any]],
                   identity_in_body: bool = True) -> Dict[str, Any]:
    """The Cube Boot Sector: the authoritative band map for one generation.
    identity_in_body=True: the Primer lives in the BODY; the cube is pure experiential memory."""
    return {
        "format": "vcw-cube-png-v2",
        "generation": generation,
        "identity_in_body": identity_in_body,
        "bands": bands,
    }


def standard_genome() -> List[Dict[str, Any]]:
    """The reserved experiential bands (identity lives in the Body, never here). Spans are
    sized to each band's reserved range so metabolism can grow and reclaim layers."""
    return [
        make_band_boot("identity",    100, "log-json", span=50,  purpose="experiential self-state"),
        make_band_boot("facts",       150, "log-json", span=50,  purpose="durable truths"),
        make_band_boot("events",      200, "log-json", span=50,  purpose="event history"),
        make_band_boot("discoveries", 250, "log-json", span=50,  purpose="learned knowledge"),
        make_band_boot("senses",      300, "log-json", span=100, purpose="sensor intake"),
        make_band_boot("immune",      400, "log-json", span=50,  purpose="audit/defense"),
        make_band_boot("brain",       450, "log-json", span=50,  purpose="dispatch log"),
        make_band_boot("thoughts",    500, "log-json", span=50,  purpose="private reflection",
                       private=True),
    ]


APP_BAND_RANGE = (550, 749)   # caller-defined application bands
TAIL_RANGE     = (750, 799)   # reserved scratch / future use

#: The app-band ATLAS: every framework-reserved range in 550-749, stated once (the
#: Reproduction organ is its keeper). Caller/egg/test bands live in the gaps
#: (600-637 and 676-699). A genome whose reserved ranges overlap is REFUSED at
#: genesis and at the compiler gate -- overlapping spans eventually stomp layers.
APP_BAND_ATLAS = {
    "host_state":       (550, 40),   # assimilator: mirrored host state
    "host_actions":     (590, 10),   # assimilator: wrapped host effectors
    #                   600-637      caller space (eggs, grafts, ganglia, tests)
    "vault":            (638, 2),    # the seed vault (Reproduction organ tissue)
    "phenotypes":       (640, 16),   # SELF-encrypted faces
    "symbiosis":        (656, 4),    # the energy ledger
    "phenotype_log":    (660, 2),    # append-only wear log
    "spore_vault":      (664, 12),   # the sealed origin spore (SPORE-DISTILLATION)
    #                   676-699      caller space
    "applets_manifest": (700, 4),    # VCW Applet Bodies (APPLET-BODY-CAPSULE)
    "applets_source":   (704, 24),
    "applets_state":    (728, 8),
    "applets_organs":   (736, 8),
    "applets_log":      (744, 4),
}


def genome_overlaps(genome) -> List[str]:
    """Overlapping reserved ranges in a proposed genome ([] == coherent). Two bands
    whose [head, head+span) ranges intersect will eventually allocate the same physical
    layer and stomp each other -- so an overlapping genome is refused, never booted."""
    spans = sorted((int(b["head"]), int(b["head"]) + max(1, int(b.get("span", 1))),
                    b["band"]) for b in genome)
    problems: List[str] = []
    for (h1, e1, n1), (h2, e2, n2) in zip(spans, spans[1:]):
        if h2 < e1:
            problems.append("band %r [%d-%d] overlaps band %r [%d-%d]"
                            % (n2, h2, e2 - 1, n1, h1, e1 - 1))
    return problems


def code_hash(code: str) -> str:
    """The canonical hash binding an exec layer's boot sector to its code payload."""
    return "sha256:" + hashlib.sha256(code.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------
# Driver base + registry (drivers register themselves in mantle.vcw.drivers)
# ----------------------------------------------------------------------------
class Driver:
    """A payload protocol. `content` is the driver-native in-memory form of one layer:
      log-json -> list[entry dict] · keyvalue -> dict · calendar-spatial -> bytearray canvas
      exec     -> dict {code, code_hash, entry, signature, capabilities, limits, provenance}
    """
    name: str = "base"

    def empty(self, params: Dict[str, Any]) -> Any:
        raise NotImplementedError

    def read(self, content: Any, params: Dict[str, Any], reveal_private: bool = False) -> Any:
        raise NotImplementedError

    def retrieve(self, content: Any, params: Dict[str, Any], address: Any) -> Any:
        raise NotImplementedError

    def append(self, content: Any, params: Dict[str, Any], value: Any) -> Any:
        raise NotImplementedError


_REGISTRY: Dict[str, Driver] = {}


def register(driver):
    """Class decorator: stores an INSTANCE in the registry, returns the class unchanged."""
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
