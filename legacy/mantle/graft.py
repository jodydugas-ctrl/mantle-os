#!/usr/bin/env python3
"""
mantle.graft  --  the GRAFT EGG and LIVE RESIDENCY (Mantle OS · R1 + R2)

Doctrine of record: docs/grimoire/GRIMOIRE_APPAI_DOMAIN_v1_0.md (NECROMANCY -- operational
detail; "One substrate, two casts"). Graft reuses the single canonical organ-role table
(ROLES from assimilator.scanner) and delegates scanning to anchor(); it never re-classifies.

Two reframes the NEXT_MOLT roadmap demanded:

  R1 -- the egg as a PATCH SET, not a from-scratch spec.
        A normal egg (`mantle.egg`) declares a WHOLE new AppAI. A *graft* egg instead
        carries a NON-DESTRUCTIVE diff against a NAMED host: extra app bands, hook
        directives (which classified symbols to thread through the organism), and
        instincts. Applying a graft never touches the original host -- it copies the host
        into a WORKSPACE and grows the resident there. The original is census-proven
        byte-identical. If the host has DRIFTED from the census the graft was built
        against, the apply RAISES a GraftDrift interrupt (for the MIND to re-patch) rather
        than mis-applying silently -- "managing its own survival against source drift."

  R2 -- residency that WEAVES a live nervous system, not just a static map.
        `weave()` replaces a host namespace's classified callables with the assimilator's
        fail-open, reversible wrappers (`assimilator.Assimilation`): SENSOR_EVENTs become
        senses entries, ARM_ACTIONs get Limb proofs, exceptions become immune events --
        live, on every call, zero LLM. The host's behavior is preserved EXACTLY (same
        return, same exceptions). `unweave()` restores the originals; detach is clean.

Eggs carry DATA, not programs: a graft's hooks are role directives, and any instinct it
carries rides the same gauntlet as every skill. A malformed graft never applies.

    python -m mantle graft eggs/notes_graft.json <host-dir>
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Any, Callable, Dict, List, Optional

from .assimilator.scanner import ROLES
from .vcw.bands import make_band_boot

GRAFT_FORMAT = "mantle-graft-egg-v1"
NEST = ".mantle"


class GraftError(Exception):
    """A malformed graft egg. It never applies; the reason is the message."""


class GraftDrift(Exception):
    """The host has drifted from the census the graft was built against. The graft is NOT
    applied silently -- this interrupt is the signal for the MIND to re-patch."""


# ---------------------------------------------------------------------------
# the graft egg: a non-destructive diff, declared as data
# ---------------------------------------------------------------------------
def _need(d: Dict[str, Any], key: str, typ, where: str):
    if key not in d:
        raise GraftError("%s: missing %r" % (where, key))
    if not isinstance(d[key], typ):
        raise GraftError("%s: %r must be %s" % (where, key, typ.__name__))
    return d[key]


def validate_graft(graft: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a graft egg dict (structure only -- it carries data, not code)."""
    if graft.get("graft_format") != GRAFT_FORMAT:
        raise GraftError("not a graft egg (graft_format != %r)" % GRAFT_FORMAT)
    ident = _need(graft, "identity", dict, "graft")
    _need(ident, "name", str, "graft.identity")
    _need(graft, "host", str, "graft")               # the NAMED host (repo/url/label)
    for i, band in enumerate(graft.get("bands", [])):
        where = "graft.bands[%d]" % i
        _need(band, "band", str, where)
        head = _need(band, "head", int, where)
        if not (550 <= head <= 749):
            raise GraftError("%s: app bands live in 550-749 (head=%d)" % (where, head))
    for i, h in enumerate(graft.get("hooks", [])):
        where = "graft.hooks[%d]" % i
        _need(h, "symbol", str, where)
        role = _need(h, "role", str, where)
        if role not in ROLES:
            raise GraftError("%s: role %r not a known organ role" % (where, role))
    if "host_census" in graft and not isinstance(graft["host_census"], dict):
        raise GraftError("graft.host_census must be a map of path -> sha256")
    return graft


def load_graft(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return validate_graft(json.load(f))


def graft_bands(graft: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The graft's extra app bands as boot sectors, ready for the resident's genome."""
    return [make_band_boot(b["band"], b["head"], b.get("encoding", "log-json"),
                           params=b.get("params"), private=bool(b.get("private")),
                           span=b.get("span", 1), purpose=b.get("purpose", b["band"]))
            for b in graft.get("bands", [])]


# ---------------------------------------------------------------------------
# R1: apply the graft -- non-destructively, in a workspace
# ---------------------------------------------------------------------------
def _drift(graft: Dict[str, Any], host: str) -> List[str]:
    """Which census-recorded host files have drifted from the graft's expectation.
    Empty list == the host still matches what the graft was built against."""
    from .anchor import census
    recorded = graft.get("host_census") or {}
    if not recorded:
        return []                                # no census recorded -> nothing to check
    now = census(host)
    return sorted(p for p, h in recorded.items() if now.get(p) != h)


def apply(graft: Dict[str, Any], host: str, workspace: Optional[str] = None,
          starter_credits: float = 5.0, allow_drift: bool = False) -> Dict[str, Any]:
    """Apply a graft egg to `host` WITHOUT touching it: copy the host into a workspace,
    grow the resident there (with the graft's extra bands), and return
    {organism, workspace, report, hooks}. The original host is census-verified unchanged.
    A drifted host raises GraftDrift unless `allow_drift=True`."""
    from .anchor import anchor, census
    graft = validate_graft(graft)
    host = os.path.abspath(host)
    if not os.path.isdir(host):
        raise GraftError("host %r is not a directory" % host)

    drifted = _drift(graft, host)
    if drifted and not allow_drift:
        raise GraftDrift("host drifted from the graft's census (%d file(s): %s); the MIND "
                         "must re-patch" % (len(drifted), ", ".join(drifted[:5])))

    before = census(host)                        # the ORIGINAL, must stay byte-identical
    ws_root = workspace or tempfile.mkdtemp(prefix="mantle-graft-")
    ws_host = os.path.join(ws_root, os.path.basename(host.rstrip("/\\")) or "host")
    shutil.copytree(host, ws_host, dirs_exist_ok=True)

    # the resident grows in the WORKSPACE copy; the graft's bands ride into its genome
    result = anchor(ws_host, name=graft["identity"]["name"],
                    starter_credits=starter_credits, extra_bands=graft_bands(graft))
    org = result["organism"]

    # remember the hook directives as observed facts (R2 reads these to weave a host)
    hooks = list(graft.get("hooks", []))
    org.memory.remember("facts", {"graft_hooks": hooks, "graft_host": graft["host"]},
                        opcode="OBSERVED", source="graft", verified=True)
    org.save(os.path.join(ws_host, NEST))

    after = census(host)                         # prove the ORIGINAL host untouched
    if before != after:
        raise GraftError("GRAFT MODIFIED THE ORIGINAL HOST -- this must never happen")

    report = {"graft": graft["identity"]["name"], "host": graft["host"],
              "workspace": ws_host, "original_unchanged": before == after,
              "drifted": drifted, "extra_bands": [b["band"] for b in graft.get("bands", [])],
              "hooks": len(hooks), "certified": org.stage1_certified}
    return {"organism": org, "workspace": ws_host, "report": report, "hooks": hooks}


# ---------------------------------------------------------------------------
# R2: weave a live nervous system into a running host namespace
# ---------------------------------------------------------------------------
def weave(namespace: Dict[str, Any], hooks: List[Dict[str, Any]],
          assimilation: Any) -> List[str]:
    """Replace each hooked callable in `namespace` with its fail-open organ wrapper. The
    host's behavior is preserved EXACTLY; every call now also perceives/proves/mirrors
    through the organism. Returns the symbols woven. Reversible via `unweave`."""
    woven: List[str] = []
    for h in hooks:
        sym, role = h["symbol"], h["role"]
        fn = namespace.get(sym)
        if callable(fn) and not getattr(fn, "mantle_role", None):   # not already woven
            namespace[sym] = assimilation.wrap(role, fn, sym)
            woven.append(sym)
    return woven


def unweave(namespace: Dict[str, Any], symbols: List[str], assimilation: Any) -> List[str]:
    """Detach: restore each woven symbol to its original callable (byte-for-byte behavior).
    Returns the symbols restored."""
    restored: List[str] = []
    for sym in symbols:
        fn = namespace.get(sym)
        if getattr(fn, "mantle_role", None):
            namespace[sym] = assimilation.unwrap(fn)
            restored.append(sym)
    return restored
