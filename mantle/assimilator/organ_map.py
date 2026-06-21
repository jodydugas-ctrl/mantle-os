#!/usr/bin/env python3
"""
mantle.assimilator.organ_map  --  fold a dissection into the assimilation map (Argonaut, of the Mantle lineage)

Takes the scanner's raw symbol classification and produces the ASSIMILATION MAP: which
host tissue is which organ, what stays external host code, and the proposed cube genome
sized to the host's observed shape. Pure data transformation -- still read-only.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..vcw.bands import make_band_boot

ROLE_TO_ORGAN = {
    "REFLEX": "senses",
    "SENSOR_EVENT": "senses",
    "ARM_ACTION": "limbs",
    "DISPLAY_RENDER": "limbs",
    "STATE_TRANSITION": "memory",
    "PERSISTENCE_WRITE": "memory",
    "HEARTBEAT": "heart",
    "MIND_AFFORDANCE": "brain",
    "SECRET_BOUNDARY": "immune",
    "ERROR_DEFENSE": "immune",
    "INTERNAL_UTILITY": None,        # remains external host code
    "DEPRECATED": None,              # recorded in the gap report; never instrumented
}

ORGANS = ("heart", "senses", "limbs", "memory", "immune", "brain")


def build_map(dissection: Dict[str, Any]) -> Dict[str, Any]:
    """The assimilation map: organ -> [symbols], external host code, gap report, role
    counts, and a proposed genome sized to the host."""
    organ_symbols: Dict[str, List[Dict[str, Any]]] = {o: [] for o in ORGANS}
    external: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []
    role_counts: Dict[str, int] = {}

    for f in dissection["files"]:
        if f.get("error"):
            gaps.append({"module": f["module"], "why": f["error"]})
            continue
        for s in f["symbols"]:
            role = s["role"]
            role_counts[role] = role_counts.get(role, 0) + 1
            rec = dict(s, module=f["module"])
            organ = ROLE_TO_ORGAN.get(role)
            if organ is None:
                (gaps if role == "DEPRECATED" else external).append(rec)
            else:
                organ_symbols[organ].append(rec)

    missing_organs = [o for o in ORGANS if not organ_symbols[o]]
    return {
        "host": dissection["root"],
        "organs": organ_symbols,
        "external_host_code": external,
        "gap_report": gaps,
        "role_counts": role_counts,
        "missing_organs": missing_organs,    # information too: no immune = fragile, etc.
        "proposed_genome": [b["band"] for b in propose_genome(role_counts)],
    }


def propose_genome(role_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    """Propose a cube genome sized to the host's observed shape: high-churn surfaces get
    more span; every band declares a purpose. Always includes the eight reserved bands."""
    sensor_heavy = role_counts.get("SENSOR_EVENT", 0) + role_counts.get("REFLEX", 0) > 20
    persist_heavy = role_counts.get("PERSISTENCE_WRITE", 0) > 20
    genome = [
        make_band_boot("identity",    100, "log-json", span=50,  purpose="experiential self-state"),
        make_band_boot("facts",       150, "log-json", span=50,  purpose="durable truths"),
        make_band_boot("events",      200, "log-json", span=50 if not persist_heavy else 50,
                       purpose="event history (sized to host event rate)"),
        make_band_boot("discoveries", 250, "log-json", span=50,  purpose="learned knowledge"),
        make_band_boot("senses",      300, "log-json", span=100,
                       purpose="sensor intake%s" % (" (high-churn host)" if sensor_heavy else "")),
        make_band_boot("immune",      400, "log-json", span=50,  purpose="audit/defense"),
        make_band_boot("brain",       450, "log-json", span=50,  purpose="dispatch log"),
        make_band_boot("thoughts",    500, "log-json", span=50,  purpose="private reflection",
                       private=True),
        make_band_boot("host_state",  550, "log-json", span=100,
                       purpose="mirrored host state transitions (app band)"),
        make_band_boot("host_actions", 650, "log-json", span=50,
                       purpose="wrapped host effector calls (app band)"),
    ]
    return genome
