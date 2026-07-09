#!/usr/bin/env python3
"""
mantle.reproduction  --  the TWO ways an AppAI makes another AppAI (Mantle OS)

Doctrine of record: documents/Mantle_Reproduction.md.

The framework grew many propagation verbs over time -- egg, hatchery, vault, anchor,
symbiosis, graft, and (newest) the spore. They are not six ideas; they are two, wearing
different clothes. This module is the single seam that says so, and routes each old verb to
the method it always belonged to. It adds no new behaviour: every call delegates to the
canonical, already-audited module. It exists so that "how does an organism reproduce?" has a
two-word answer -- SEED or GRAFT -- instead of a glossary.

  SEED  --  INDEPENDENT reproduction. The organism condenses itself into a dormant,
            self-describing package of DATA (never programs) that grows into a certified Body
            on its own, needing no host. One substrate, three castings of the same act:
              * spore  -- the smallest seed: one PNG that IS a whole minimal agent
                          (mantle.spore); optionally a cache-ghost (mantle.ghost).
              * egg    -- a richer seed: a whole AppAI declared as one JSON document, grown
                          by the hatchery through the Stage-1 gate (mantle.egg / mantle.hatchery).
              * vault  -- a seed of an ALREADY-LIVING organism, sealed inside its own VCW, so a
                          corrupted body can be rebuilt from itself (mantle.vault).
            Whatever the size, a seed is data, and hatching it is always a BIRTH that faces the
            same gate -- a tampered seed cannot smuggle an uncertified Body into the world.

  GRAFT --  DEPENDENT reproduction. The organism propagates by taking up residence INSIDE a
            host it does not own, growing its nervous system around what already lives there,
            under a do-no-harm law and a metered energy economy. One act, three facets:
              * anchor    -- move in: dissect the host read-only, grow an additive `.mantle/`
                             nest, become the codebase's resident (mantle.anchor).
              * symbiosis -- earn its keep: the credit ledger that feeds metered cognition;
                             a starved graft falls back to a Zombie Body, never a corpse
                             (mantle.symbiosis).
              * graft-egg -- a NON-destructive patch against a NAMED host, applied in a
                             workspace copy; the original is census-proven byte-identical
                             (mantle.graft).
            A graft never modifies a host file; the census proves do-no-harm as an invariant.

The old distinction "grow from scratch vs. assimilate an existing app" is the SAME axis as
"seed vs. graft": a seed answers to no host, a graft lives in one. Two methods, both gated by
the 88 invariants, no standing law weakened.
"""
from __future__ import annotations

from typing import Any, Dict, Union

SEED_FORMS = ("spore", "egg", "vault")
GRAFT_FORMS = ("anchor", "graft")

#: The consolidation map -- every legacy verb under the method it always was. Used by the
#: docs, `python -m mantle reproduce`, and the Field Guide so the story stays single-sourced.
METHODS: Dict[str, Dict[str, Any]] = {
    "seed": {
        "kind": "independent",
        "biology": "spores / seeds -- dormant, self-contained, grows with no host",
        "forms": {
            "spore": "mantle.spore  -- one PNG that is a whole minimal agent (optional cache-ghost)",
            "egg":   "mantle.egg + mantle.hatchery  -- a whole AppAI declared as one JSON document",
            "vault": "mantle.vault  -- an organism's own sealed seed, for self-reconstruction",
        },
        "law": "hatching a seed is a BIRTH: it faces the same Stage-1 gate every Body faces",
    },
    "graft": {
        "kind": "dependent",
        "biology": "grafting / symbiosis -- propagate by living inside a host you do not own",
        "forms": {
            "anchor":    "mantle.anchor  -- take residence in a host codebase (additive nest)",
            "symbiosis": "mantle.symbiosis  -- the metered energy economy that sustains residency",
            "graft":     "mantle.graft  -- a non-destructive patch against a named host",
        },
        "law": "a graft never modifies a host file; the census proves do-no-harm byte-for-byte",
    },
}


class ReproductionError(Exception):
    """An unknown reproductive form, or a form given the wrong kind of seed/host."""


def describe() -> Dict[str, Any]:
    """Return the two-method consolidation map (for docs, the CLI, and `teach`)."""
    return METHODS


# ---------------------------------------------------------------------------
# SEED -- independent reproduction
# ---------------------------------------------------------------------------

def seed(form: str = "spore", **kwargs) -> Dict[str, Any]:
    """Reproduce INDEPENDENTLY. `form` selects the seed's size; kwargs pass through unchanged.

        seed("spore", name="Buddy", task="answer one question", path="buddy.png")
        seed("egg",   egg_path="examples/eggs/greeter.json", out_dir="nest/")
        seed("vault", seed=<egg-or-graft dict sealed in an organism>)

    Every path ends in a certified Body (or, for a spore, a verifiable minimal seed). This
    routes to the canonical module; it never re-implements the birth.
    """
    if form == "spore":
        from . import spore as _spore
        path = _spore.create_spore(**kwargs)
        return {"method": "seed", "form": "spore", "path": path,
                "verify": _spore.verify_spore(path)["ok"]}
    if form == "egg":
        from .hatchery import hatch
        return {"method": "seed", "form": "egg", "result": hatch(**kwargs)}
    if form == "vault":
        from . import vault
        return {"method": "seed", "form": "vault", "result": vault.reconstruct(**kwargs)}
    raise ReproductionError(
        f"unknown seed form {form!r}; expected one of {SEED_FORMS}")


# ---------------------------------------------------------------------------
# GRAFT -- dependent reproduction (residency in a host)
# ---------------------------------------------------------------------------

def graft(form: str = "anchor", **kwargs) -> Dict[str, Any]:
    """Reproduce DEPENDENTLY, inside a host. `form` selects the residency style.

        graft("anchor", host="path/to/app", starter_credits=5)
        graft("graft",  spec="examples/eggs/notes_graft.json", host="examples/sample_app")

    The `graft` form accepts `spec` as either a path (loaded for you) or an already-loaded
    graft dict. Both forms are do-no-harm: the host is never modified in place.
    """
    if form == "anchor":
        from .anchor import anchor
        return {"method": "graft", "form": "anchor", "result": anchor(**kwargs)}
    if form == "graft":
        from . import graft as _graft
        spec: Union[str, Dict[str, Any]] = kwargs.pop("spec")
        loaded = _graft.load_graft(spec) if isinstance(spec, str) else spec
        return {"method": "graft", "form": "graft", "result": _graft.apply(loaded, **kwargs)}
    raise ReproductionError(
        f"unknown graft form {form!r}; expected one of {GRAFT_FORMS}")
