"""mantle.assimilator -- Path B: grow organs around existing code, non-destructively.

The prime directive: DO NO HARM. Dissect read-only (scanner), map host tissue to organs
(organ_map), produce the signed Phase-0 artifacts (report), and only then thread host
behavior through the organism with fail-open, reversible wrappers (wrappers). The host
runs exactly as before -- plus now it has a nervous system and a memory.
"""
from .scanner import scan_project, scan_file, classify_symbol, ROLES
from .organ_map import build_map, propose_genome, ROLE_TO_ORGAN, ORGANS
from .wrappers import Assimilation
from .report import dry_run, render_inventory, write_artifacts

__all__ = ["scan_project", "scan_file", "classify_symbol", "ROLES",
           "build_map", "propose_genome", "ROLE_TO_ORGAN", "ORGANS",
           "Assimilation", "dry_run", "render_inventory", "write_artifacts"]
