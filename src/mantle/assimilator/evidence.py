#!/usr/bin/env python3
"""
mantle.assimilator.evidence -- resident host evidence index and consultation

Phase-0 dissection does not only produce a report for humans. A resident AppAI
needs a compact, machine-readable index it can consult before generic MIND chat.
This module keeps that shape canonical for assimilate, anchor, graft, spores, and
examples.
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List

from .surface_coverage import build_surface_coverage, flatten_dissection_symbols


STOP_WORDS = frozenset(
    "how do i the a an to of in is what where which my this app use run does can "
    "you it for with and or me about tell explain software host your".split()
)


def build_host_evidence_index(amap: Dict[str, Any],
                              dissection: Dict[str, Any]) -> Dict[str, Any]:
    """Build the resident's local-first consultation index from Phase-0 evidence."""
    substrate = dissection.get("substrate") or amap.get("substrate") or {}
    surface_coverage = amap.get("surface_coverage")
    if not isinstance(surface_coverage, dict):
        symbols = flatten_dissection_symbols(dissection)
        surface_coverage = build_surface_coverage(symbols)
    organ_summary: Dict[str, Any] = {}
    for organ, syms in (amap.get("organs") or {}).items():
        roles = sorted({s.get("role", "unknown") for s in syms})
        organ_summary[organ] = {
            "count": len(syms),
            "roles": roles,
            "samples": [
                {
                    "symbol": s.get("symbol"),
                    "module": s.get("module"),
                    "line": s.get("line"),
                    "role": s.get("role"),
                }
                for s in syms[:8]
            ],
        }

    control_surfaces = [
        {
            "control": s.get("symbol"),
            "module": s.get("module"),
            "line": s.get("line"),
            "role": s.get("role"),
            "proof_requirement": (
                "attempted action plus body-owned verification before ok=true"
            ),
        }
        for s in (amap.get("organs") or {}).get("limbs", [])[:12]
    ]
    for surface in (surface_coverage.get("surfaces") or []):
        if surface.get("surface_type") not in {"action", "dynamic_surface"}:
            continue
        control_surfaces.append({
            "control": surface.get("id"),
            "module": surface.get("module"),
            "line": surface.get("line"),
            "role": "GUI_SURFACE",
            "vcw_status": surface.get("vcw_status"),
            "risk": surface.get("risk"),
            "proof_requirement": surface.get("proof_requirement"),
        })

    deduped_controls = []
    seen_controls = set()
    for control in control_surfaces:
        cid = control.get("control")
        if not cid or cid in seen_controls:
            continue
        seen_controls.add(cid)
        deduped_controls.append(control)
    control_surfaces = deduped_controls

    gaps = [
        {
            "source": g.get("module", g.get("symbol", "unknown")),
            "why": g.get("why", "unknown"),
        }
        for g in amap.get("gap_report", [])
    ]
    limitations: List[str] = []
    missing = amap.get("missing_organs") or []
    if missing:
        limitations.append(
            "Missing organ evidence: %s." % ", ".join(missing)
        )
    unsupported = substrate.get("unsupported") or []
    if unsupported:
        limitations.append(
            "Some host surfaces need adaptive parser/observer/verifier tools before "
            "instrumentation."
        )
    if not control_surfaces:
        limitations.append(
            "No Limb control surface was observed; effectful actions need an explicit "
            "ControlBridge before use."
        )
    missing_surfaces = [
        item.get("surface")
        for item in surface_coverage.get("maintenance_findings", [])
        if item.get("status") == "maintenance_gap"
    ]
    if missing_surfaces:
        limitations.append(
            "GUI nerve maintenance gaps remain for %d surface(s); they must be proposed "
            "to Body before any operability claim." % len(missing_surfaces)
        )

    return {
        "kind": "HOST_EVIDENCE_INDEX",
        "schema_version": "mantle-host-evidence-v2",
        "local_first_consultation": True,
        "host": amap.get("host") or dissection.get("root"),
        "host_identity": {
            "name": os.path.basename(amap.get("host") or dissection.get("root", "")),
            "python_files": dissection.get("python_files", 0),
            "multilang": bool(dissection.get("multilang")),
            "substrate_languages": substrate.get("languages", []),
            "build_files": substrate.get("build_files", [])[:12],
        },
        "evidence_sources": [
            "APP_INVENTORY.md",
            "assimilation_map.json",
            "substrate census",
            "organ map",
            "gap report",
            "control surface map",
        ],
        "organ_summary": organ_summary,
        "control_surfaces": control_surfaces,
        "surface_coverage_summary": {
            "kind": surface_coverage.get("kind"),
            "schema_version": surface_coverage.get("schema_version"),
            "total_surfaces": surface_coverage.get("total_surfaces", 0),
            "status_counts": surface_coverage.get("status_counts", {}),
            "type_counts": surface_coverage.get("type_counts", {}),
            "maintenance_findings": len(surface_coverage.get("maintenance_findings", [])),
        },
        "gaps": gaps,
        "limitations": limitations,
        "consultation_contract": {
            "answer_host_questions_from": [
                "host_identity",
                "organ_summary",
                "control_surfaces",
                "surface_coverage_summary",
                "gaps",
                "limitations",
            ],
            "provider_mind_role": (
                "may reason over resident evidence after Phase-2 authorization; "
                "must not replace the evidence index"
            ),
            "missing_evidence_policy": "name the gap instead of guessing",
            "effectful_action_policy": (
                "imperative host-surface requests route to Body/Limbs and require "
                "Action Execution Proof"
            ),
        },
    }


def answer_from_host_evidence(question: str, amap: Dict[str, Any]) -> str:
    """Deterministic resident answer from the canonical host evidence index."""
    index = amap.get("host_evidence_index")
    if not isinstance(index, dict):
        index = build_host_evidence_index(amap, {
            "root": amap.get("host"),
            "python_files": 0,
            "multilang": False,
            "substrate": amap.get("substrate") or {},
        })

    lowered = question.lower()
    if any(word in lowered for word in ("limit", "cannot", "gap", "unsupported")):
        lines = ["Known host evidence limits:"]
        for item in index.get("limitations") or ["No limitations recorded."]:
            lines.append("- %s" % item)
        for gap in index.get("gaps", [])[:6]:
            lines.append("- %s: %s" % (gap.get("source"), gap.get("why")))
        return "\n".join(lines)

    if any(word in lowered for word in ("control", "action", "limb", "body", "can you do")):
        controls = index.get("control_surfaces") or []
        if not controls:
            return (
                "I have no verified Limb controls in my Phase-0 evidence yet. A Body "
                "operation needs a ControlBridge and post-action proof before ok=true."
            )
        surface_summary = index.get("surface_coverage_summary") or {}
        lines = ["Observed Body/Limb controls from local evidence:"]
        if surface_summary:
            lines.append("- GUI surfaces: %s; statuses: %s" % (
                surface_summary.get("total_surfaces", 0),
                surface_summary.get("status_counts", {}),
            ))
        for c in controls[:8]:
            status = c.get("vcw_status") or c.get("role")
            lines.append("- `%s` at %s:%s [%s]" % (
                c.get("control"), c.get("module"), c.get("line"), status))
        lines.append("Every control must produce Action Execution Proof before success.")
        return "\n".join(lines)

    tokens = [t for t in re.findall(r"[a-z_]+", lowered) if t not in STOP_WORDS]
    scored: List[tuple] = []
    for organ, summary in (index.get("organ_summary") or {}).items():
        for sample in summary.get("samples", []):
            hay = ("%s %s %s %s" % (
                organ, sample.get("symbol"), sample.get("module"), sample.get("role")
            )).lower()
            score = sum(2 if t in str(sample.get("symbol", "")).lower() else 1
                        for t in tokens if t in hay)
            if score:
                scored.append((score, organ, sample))
    scored.sort(key=lambda item: -item[0])

    lines: List[str] = []
    if scored:
        lines.append("From my host evidence index (observed, not guessed):")
        for _score, organ, sample in scored[:6]:
            lines.append("- %s: `%s` at %s:%s [%s]" % (
                organ,
                sample.get("symbol"),
                sample.get("module"),
                sample.get("line"),
                sample.get("role"),
            ))
    else:
        host_identity = index.get("host_identity") or {}
        languages = host_identity.get("substrate_languages") or ["unknown substrate"]
        lines.append("A structural overview of my host from local evidence:")
        lines.append("- host: %s" % (host_identity.get("name") or index.get("host")))
        lines.append("- substrate: %s" % ", ".join(languages))
        for organ, summary in (index.get("organ_summary") or {}).items():
            count = summary.get("count", 0)
            samples = ", ".join(
                str(s.get("symbol")) for s in summary.get("samples", [])[:4]
                if s.get("symbol")
            )
            lines.append("- %s: %d symbol(s)%s" % (
                organ, count, (": " + samples) if samples else ""))
    if index.get("limitations"):
        lines.append("Limits: %s" % " ".join(index["limitations"][:2]))
    return "\n".join(lines)
