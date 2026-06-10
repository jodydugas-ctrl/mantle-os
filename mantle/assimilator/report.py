#!/usr/bin/env python3
"""
mantle.assimilator.report  --  the assimilation artifacts (Mantle v3)

Produces the Phase 0 artifacts the Stage-1 audit consumes: the APP_INVENTORY markdown
(the read-only gate a human signs before any hook is inserted) and the machine-readable
assimilation map (JSON). A dry run = scan + map + report, ZERO writes to the host.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from .scanner import scan_project
from .organ_map import build_map, propose_genome, ORGANS


def dry_run(root: str) -> Dict[str, Any]:
    """The read-only assimilation pipeline: dissect -> map -> artifacts. Touches nothing."""
    dissection = scan_project(root)
    amap = build_map(dissection)
    return {"dissection": dissection, "map": amap,
            "inventory_md": render_inventory(amap, dissection)}


def render_inventory(amap: Dict[str, Any], dissection: Dict[str, Any]) -> str:
    """The APP_INVENTORY.md artifact (Appendix A of Mantle_Assimilator.md), pre-filled
    from the dissection. The READ-ONLY sign-off line stays unsigned -- a human signs it;
    only then may Phase 5+ insert any hook (HF-B42)."""
    L = []
    L.append("# APP INVENTORY & ORGAN MAP — %s" % os.path.basename(amap["host"]))
    L.append("")
    L.append("*Generated READ-ONLY by `mantle.assimilator` (Path B, Phase 0). No host file "
             "was modified. Hook insertion (Phase 5+) is authorized ONLY after the sign-off "
             "line below is signed.*")
    L.append("")
    L.append("## A.1 Host identity")
    L.append("- **Root:** `%s`" % amap["host"])
    L.append("- **Python files:** %d" % dissection["python_files"])
    L.append("")
    L.append("## A.3/A.4 Symbol-role summary")
    L.append("")
    L.append("| Role | Count |")
    L.append("|------|-------|")
    for role, n in sorted(amap["role_counts"].items(), key=lambda kv: -kv[1]):
        L.append("| %s | %d |" % (role, n))
    L.append("")
    L.append("## The organ map (host tissue -> organs)")
    L.append("")
    for organ in ORGANS:
        syms = amap["organs"][organ]
        L.append("### %s (%d symbol%s)" % (organ.capitalize(), len(syms),
                                           "" if len(syms) == 1 else "s"))
        for s in syms[:12]:
            L.append("- `%s:%d`  `%s`  (%s)" % (s["module"], s["line"], s["symbol"], s["role"]))
        if len(syms) > 12:
            L.append("- ... and %d more" % (len(syms) - 12))
        if not syms:
            L.append("- *none found — an app with no %s is information too*" % organ)
        L.append("")
    L.append("### Remains external host code (%d)" % len(amap["external_host_code"]))
    L.append("*INTERNAL_UTILITY symbols are wrapped only if they touch an organ surface.*")
    L.append("")
    if amap["missing_organs"]:
        L.append("> **Missing organs:** %s — fragile seams the assimilation should "
                 "compensate for." % ", ".join(amap["missing_organs"]))
        L.append("")
    L.append("## A.7 Proposed cube genome")
    L.append("")
    L.append("| Band | Head | Span | Encoding | Purpose |")
    L.append("|------|------|------|----------|---------|")
    for b in propose_genome(amap["role_counts"]):
        L.append("| %s | %d | %d | %s%s | %s |"
                 % (b["band"], b["head"], b["span"], b["encoding"],
                    " (private)" if b["private"] else "", b["purpose"]))
    L.append("")
    L.append("## A.9 Gap report")
    if amap["gap_report"]:
        for g in amap["gap_report"]:
            L.append("- `%s` — %s" % (g.get("module", g.get("symbol", "?")),
                                      g.get("why", "DEPRECATED")))
    else:
        L.append("- none")
    L.append("")
    L.append("## A.11 READ-ONLY sign-off (the Phase 0 gate)")
    L.append("```")
    L.append("APP INVENTORY COMPLETE — NO HOST CODE MODIFIED")
    L.append("  Host                 : %s" % amap["host"])
    L.append("  Files modified so far: 0   (MUST be 0)")
    L.append("  Approved to instrument (Phase 1+): [ ]  by ____________  date __________")
    L.append("")
    L.append("  >>> Hook insertion (Phase 5+) is authorized ONLY after this line is signed. <<<")
    L.append("```")
    return "\n".join(L)


def write_artifacts(result: Dict[str, Any], out_dir: str) -> Dict[str, str]:
    """Write APP_INVENTORY.md + assimilation_map.json NEXT TO the operator (never into
    the host tree). Returns the written paths."""
    os.makedirs(out_dir, exist_ok=True)
    md = os.path.join(out_dir, "APP_INVENTORY.md")
    js = os.path.join(out_dir, "assimilation_map.json")
    with open(md, "w", encoding="utf-8") as f:
        f.write(result["inventory_md"])
    with open(js, "w", encoding="utf-8") as f:
        json.dump(result["map"], f, indent=2)
    return {"inventory": md, "map": js}
