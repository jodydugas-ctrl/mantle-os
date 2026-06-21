#!/usr/bin/env python3
"""
mantle.egg  --  the EGG: a whole AppAI as one declarative spec (Mantle OS · Gen-4)

Mantle v3 grew the organism; generation 4 grows the vessel that carries new organisms.
The EGG is that vessel: a newborn AppAI declared entirely as data, so growing one no longer
means writing Python wiring.

An EGG is a single JSON document that declares everything a newborn AppAI is:

  identity / truths / commandments    -> the Primer (seals into the Body at hatch)
  genome                              -> extra app bands beyond the reserved eight
  reflexes                            -> declarative reflex arcs (NO arbitrary code:
                                         a fixed vocabulary of deterministic responses)
  routines                            -> signals classified ROUTINE
  controls                            -> the Human Surface Map + stub ControlBridges
  instincts                           -> candidate skills; each must still pass the
                                         static sandbox gate + trial + calcify gates

Eggs contain DATA, not programs. The only code an egg may carry is an instinct's
source, and that travels the same gauntlet as any skill: sandbox gate, proving cases,
hash/signature/capability/provenance. A malformed egg never hatches; a hatched egg is
never trusted until it passes the same Stage-1 gate as every other Body.

    python -m mantle hatch eggs/greeter.json --out nest/
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

EGG_FORMAT = "mantle-egg-v1"

# the fixed, deterministic vocabulary a declarative reflex may respond with
REFLEX_KINDS = ("remember", "complete", "notify", "operate")


class EggError(Exception):
    """A malformed egg. It never hatches; the hatchery refuses with the reason."""


def _need(d: Dict[str, Any], key: str, typ, where: str):
    if key not in d:
        raise EggError("%s: missing %r" % (where, key))
    if not isinstance(d[key], typ):
        raise EggError("%s: %r must be %s" % (where, key, typ))
    return d[key]


def validate(egg: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an egg dict. Returns it (normalized) or raises EggError."""
    if egg.get("egg_format") != EGG_FORMAT:
        raise EggError("not an mantle egg (egg_format != %r)" % EGG_FORMAT)
    ident = _need(egg, "identity", dict, "egg")
    _need(ident, "name", str, "egg.identity")
    _need(egg, "truths", list, "egg")
    _need(egg, "commandments", list, "egg")

    for i, band in enumerate(egg.get("genome", [])):
        where = "egg.genome[%d]" % i
        _need(band, "band", str, where)
        head = _need(band, "head", int, where)
        if not (550 <= head <= 749):
            raise EggError("%s: app bands live in 550-749 (head=%d)" % (where, head))

    for i, rx in enumerate(egg.get("reflexes", [])):
        where = "egg.reflexes[%d]" % i
        _need(rx, "action_id", str, where)
        _need(rx, "event_type", str, where)
        resp = _need(rx, "response", dict, where)
        kind = _need(resp, "kind", str, where + ".response")
        if kind not in REFLEX_KINDS:
            raise EggError("%s: response.kind %r not in %s (eggs carry data, not code)"
                           % (where, kind, REFLEX_KINDS))
        if kind == "remember" and resp.get("band") not in ("facts", "events",
                                                           "discoveries", "identity"):
            raise EggError("%s: remember.band must be a memory band" % where)
        if kind == "operate" and not resp.get("control"):
            raise EggError("%s: operate needs a control id" % where)

    for i, pair in enumerate(egg.get("routines", [])):
        if not (isinstance(pair, list) and len(pair) == 2):
            raise EggError("egg.routines[%d]: must be [action_id, event_type]" % i)

    for i, c in enumerate(egg.get("controls", [])):
        _need(c, "id", str, "egg.controls[%d]" % i)

    for i, sk in enumerate(egg.get("instincts", [])):
        where = "egg.instincts[%d]" % i
        _need(sk, "band", str, where)
        _need(sk, "code", str, where)
        _need(sk, "entry", str, where)
        cases = _need(sk, "cases", list, where)
        if not cases:
            raise EggError("%s: an instinct must carry proving cases (trial is the "
                           "gate that earns trust)" % where)
    return egg


def load(path: str) -> Dict[str, Any]:
    """Load + validate an egg file."""
    with open(path, "r", encoding="utf-8") as f:
        egg = json.load(f)
    return validate(egg)
