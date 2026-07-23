#!/usr/bin/env python3
"""GUI/control surface coverage for assimilation evidence.

The surface inventory is the AppAI's nerve map: every visible affordance should
be known, connected to evidence when possible, and left as an explicit
maintenance finding when it is not yet proven.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List


SURFACE_KINDS = {"ui-action", "ui-widget", "ui-menu", "ui-toolbar"}
DESTRUCTIVE_HINTS = (
    "delete", "trash", "remove", "clear", "close", "exit", "quit", "print",
    "save", "reload", "rename", "update", "install",
)


def normalize_surface_id(value: Any) -> str:
    text = str(value or "").strip()
    for prefix in ("&", "ui->"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    if "::" in text:
        text = text.rsplit("::", 1)[-1]
    if "." in text and text.split(".", 1)[0].startswith("Q"):
        text = text.split(".", 1)[1]
    return text.strip()


def flatten_dissection_symbols(dissection: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for file_rec in dissection.get("files", []):
        module = file_rec.get("module")
        for sym in file_rec.get("symbols", []):
            rec = dict(sym)
            rec.setdefault("module", module)
            out.append(rec)
    return out


def _surface_type(kind: str, class_name: str = "") -> str:
    if kind == "ui-action":
        return "action"
    if kind == "ui-menu":
        return "menu"
    if kind == "ui-toolbar":
        return "toolbar"
    if class_name:
        return "widget:%s" % class_name
    return "widget"


def _edge_surface_id(edge: Dict[str, Any]) -> str:
    return normalize_surface_id(edge.get("sender") or edge.get("surface"))


def _is_not_implemented(surface_id: str, label: str, edges: List[Dict[str, Any]]) -> bool:
    low = ("%s %s %s" % (
        surface_id,
        label,
        " ".join(str(edge.get("slot", "")) for edge in edges),
    )).lower()
    return "not implemented" in low or "not_currently_implemented" in low


def _is_risky(surface_id: str, label: str) -> bool:
    low = ("%s %s" % (surface_id, label)).lower()
    return any(hint in low for hint in DESTRUCTIVE_HINTS)


def build_surface_coverage(symbols: Iterable[Dict[str, Any]],
                           edges: Iterable[Dict[str, Any]] | None = None,
                           *,
                           verified_controls: Iterable[str] | None = None,
                           observer_controls: Iterable[str] | None = None) -> Dict[str, Any]:
    """Return a machine-readable GUI nerve coverage matrix."""
    verified = {normalize_surface_id(c) for c in (verified_controls or [])}
    observed = {normalize_surface_id(c) for c in (observer_controls or [])}
    by_id: Dict[str, Dict[str, Any]] = {}
    all_edges = list(edges or [])

    for sym in symbols:
        kind = sym.get("kind")
        if kind not in SURFACE_KINDS:
            continue
        sid = normalize_surface_id(sym.get("surface_id") or sym.get("symbol"))
        if not sid:
            continue
        rec = by_id.setdefault(sid, {
            "id": sid,
            "surface_type": _surface_type(kind, sym.get("class", "")),
            "label": sym.get("label") or sym.get("text") or sid,
            "module": sym.get("module"),
            "line": sym.get("line"),
            "kind": kind,
            "class": sym.get("class"),
            "shortcut": sym.get("shortcut", ""),
            "placements": [],
            "connection_evidence": [],
        })
        for placement in sym.get("placements", []):
            if placement and placement not in rec["placements"]:
                rec["placements"].append(placement)

    for edge in all_edges:
        sid = _edge_surface_id(edge)
        if not sid:
            continue
        rec = by_id.setdefault(sid, {
            "id": sid,
            "surface_type": "dynamic_surface",
            "label": sid,
            "module": edge.get("module"),
            "line": edge.get("line"),
            "kind": "dynamic-signal",
            "class": "",
            "shortcut": "",
            "placements": [],
            "connection_evidence": [],
        })
        proof = {
            "kind": edge.get("kind", "connection"),
            "module": edge.get("module"),
            "line": edge.get("line"),
            "signal": edge.get("signal"),
            "slot": edge.get("slot"),
            "raw": edge.get("raw"),
        }
        if proof not in rec["connection_evidence"]:
            rec["connection_evidence"].append(proof)
        observed.add(sid)

    surfaces = []
    maintenance_findings = []
    for sid in sorted(by_id):
        rec = by_id[sid]
        edges_for_surface = rec["connection_evidence"]
        if sid in verified:
            status = "verified_body_operation"
        elif _is_not_implemented(sid, rec.get("label", ""), edges_for_surface):
            status = "not_implemented"
        elif sid in observed or edges_for_surface:
            status = "observer_registered"
        elif rec["surface_type"].startswith(("menu", "toolbar", "widget")):
            status = "sense_only"
        else:
            status = "maintenance_gap"
        rec["vcw_status"] = status
        rec["risk"] = "guarded" if _is_risky(sid, rec.get("label", "")) else "low"
        rec["proof_requirement"] = (
            "observed in surface inventory plus connection evidence; ok=true requires "
            "Body operation and post-action readback"
        )
        surfaces.append(rec)
        if status != "verified_body_operation":
            maintenance_findings.append({
                "surface": sid,
                "status": status,
                "risk": rec["risk"],
                "proposal": (
                    "MIND may propose a Body nerve or verifier; Body must implement and "
                    "prove it before this surface is claimed as operable."
                ),
            })

    status_counts = Counter(s["vcw_status"] for s in surfaces)
    type_counts = Counter(s["surface_type"].split(":", 1)[0] for s in surfaces)
    return {
        "kind": "GUI_NERVE_COVERAGE",
        "schema_version": "mantle-gui-nerve-coverage-v1",
        "total_surfaces": len(surfaces),
        "status_counts": dict(status_counts),
        "type_counts": dict(type_counts),
        "surfaces": surfaces,
        "maintenance_findings": maintenance_findings,
        "contract": {
            "no_silent_gui_omission": True,
            "known_surface_policy": (
                "every discovered GUI surface is classified as verified, observer-only, "
                "sense-only, not implemented, or a maintenance gap"
            ),
            "effectful_claim_policy": (
                "resident may claim operation only with Body-owned Action Execution Proof"
            ),
        },
    }


def render_surface_coverage_markdown(coverage: Dict[str, Any],
                                     title: str = "GUI Nerve Coverage") -> str:
    lines = [
        "# %s" % title,
        "",
        "- **Schema:** `%s`" % coverage.get("schema_version", "unknown"),
        "- **Total GUI surfaces:** %s" % coverage.get("total_surfaces", 0),
        "- **No silent GUI omission:** `%s`" % str(
            coverage.get("contract", {}).get("no_silent_gui_omission", False)
        ).lower(),
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted((coverage.get("status_counts") or {}).items()):
        lines.append("| %s | %s |" % (status, count))
    lines += [
        "",
        "## Type Counts",
        "",
        "| Type | Count |",
        "|---|---:|",
    ]
    for typ, count in sorted((coverage.get("type_counts") or {}).items()):
        lines.append("| %s | %s |" % (typ, count))
    lines += [
        "",
        "## Surface Samples",
        "",
        "| Surface | Type | Status | Risk | Evidence |",
        "|---|---|---|---|---:|",
    ]
    for surface in (coverage.get("surfaces") or [])[:60]:
        lines.append("| `%s` | %s | %s | %s | %d |" % (
            surface.get("id"),
            surface.get("surface_type"),
            surface.get("vcw_status"),
            surface.get("risk"),
            len(surface.get("connection_evidence") or []),
        ))
    findings = coverage.get("maintenance_findings") or []
    lines += [
        "",
        "## Maintenance Findings",
        "",
        "Unverified surfaces are explicit DREAM/MAINTENANCE work items. The MIND may",
        "propose a Body nerve or verifier, but Body must implement and prove it before",
        "the surface is claimed as operable.",
        "",
    ]
    if findings:
        for finding in findings[:80]:
            lines.append("- `%s`: %s (%s)" % (
                finding.get("surface"),
                finding.get("status"),
                finding.get("risk"),
            ))
        if len(findings) > 80:
            lines.append("- ... and %d more" % (len(findings) - 80))
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"
