#!/usr/bin/env python3
"""
examples.py  --  A guided tour of a VCW cube, runnable end to end.

    python examples.py

Each numbered step prints what it is doing and why. Read the output alongside
this source: together they teach how a Mantle AppAI's nervous-memory substrate
is born, written, read (with the veil), audited, and grown.

Nothing here needs a network or an LLM. This is the *Body* substrate -- it works
perfectly with no brain attached. That is the whole point of Phase 1.
"""
import json
import os
import tempfile

from vcw_cube import (
    Cube, make_entry, build_layer_rgba, LAYER_BYTES, RESERVED_BANDS,
    BODY_ENTRIES,
)


def banner(n, title):
    print("\n" + "=" * 70)
    print("STEP %d  --  %s" % (n, title))
    print("=" * 70)


def main():
    workdir = tempfile.mkdtemp(prefix="vcw_demo_")
    path = os.path.join(workdir, "organism.vcw")

    # ------------------------------------------------------------------ 1
    banner(1, "GENESIS: bring a cube into being")
    cube = Cube.genesis(
        primer_content={
            "name": "Demo AppAI",
            "purpose": "demonstrate the VCW substrate",
            "born": "phase-1, no brain attached",
        },
        immunization={"rules": ["verify before commit", "never overwrite the Primer"]},
    )
    cube.save(path)
    print("born at:", path)
    print("the Primer (bodyentry.000) is now immutable.")

    # ------------------------------------------------------------------ 2
    banner(2, "GENOME: read the four body entries")
    cube = Cube.load(path)
    for name in BODY_ENTRIES:
        entries = cube.read_body_entry(name)
        shown = entries[0]["content"] if entries else "(empty)"
        print("  %-16s -> %s" % (name, shown))
    print("\nLoad order is fixed: .000 Primer -> .001 Immunization -> "
          ".002 Special -> .003 Inheritance -> prime -> bands.")

    # ------------------------------------------------------------------ 3
    banner(3, "WRITE: append entries into reserved bands")
    cube.append("facts", make_entry("WRITE", {"k": "sky", "v": "blue"}))
    cube.append("facts", make_entry("WRITE", {"k": "grass", "v": "green"}))
    cube.append("events", make_entry("LOG", "user opened the app"))
    cube.append("senses", make_entry("SENSE", {"signal": "click", "class": "ROUTINE"}))
    cube.append("thoughts", make_entry("NOTE", "this is a private thought", author="MIND"))
    cube.save(path)
    print("appended to facts, events, senses, thoughts.")

    # ------------------------------------------------------------------ 4
    banner(4, "READ + THE VEIL: private layers are hidden by default")
    cube = Cube.load(path)
    print("facts (public):")
    for e in cube.read("facts"):
        print("   ", e["content"])
    print("thoughts (private), default read -> %d entries (veiled)"
          % len(cube.read("thoughts")))
    print("thoughts with reveal_private=True -> %d entries"
          % len(cube.read("thoughts", reveal_private=True)))
    print("\nThe veil is a Body reflex: only a fused MIND may lift it on the "
          "thoughts band. No LLM is needed to ENFORCE it.")

    # ------------------------------------------------------------------ 5
    banner(5, "IMMUNE REFLEXES: tombstone vs quarantine")
    # tombstone a fact that is no longer true; quarantine a suspicious one.
    facts = cube.read("facts")
    cube.tombstone("facts", facts[0]["id"])     # retire 'sky is blue'
    cube.append("facts", make_entry("WRITE", {"k": "moon", "v": "??", "suspect": True}))
    suspect = cube.read("facts")[-1]
    cube.quarantine("facts", suspect["id"])
    cube.save(path)
    cube = Cube.load(path)
    print("facts now visible (tombstoned + quarantined hidden):")
    for e in cube.read("facts"):
        print("   ", e["content"])

    # ------------------------------------------------------------------ 6
    banner(6, "CONTEXT ASSEMBLY (deterministic, NO LLM)")
    # A miniature of the 9-step Context Assembly Protocol: gather a fully
    # materialized snapshot from fixed bands in fixed order. No references are
    # left unresolved; nothing here calls a model.
    assembled = {
        "identity": [e["content"] for e in cube.read("identity")],
        "facts":    [e["content"] for e in cube.read("facts")],
        "events":   [e["content"] for e in cube.read("events")],
        "senses":   [e["content"] for e in cube.read("senses")],
    }
    print(json.dumps(assembled, indent=2))
    print("\nThis dict is what a Phase-2 MIND would receive -- already resolved.")

    # ------------------------------------------------------------------ 7
    banner(7, "DISPATCH LIFECYCLE in brain.vcw (authorship matters)")
    # In Phase 1 the Body can record NOTIFIED/COMPLETED; INTENTION/DELEGATED are
    # owned by the MIND in Phase 2. We illustrate the record shape here.
    cube.append("brain", make_entry("DISPATCH", {
        "state": "NOTIFIED", "action": "render_welcome", "authorship": "BODY"}))
    cube.append("brain", make_entry("DISPATCH", {
        "state": "COMPLETED", "action": "render_welcome", "authorship": "BODY"}))
    cube.save(path)
    for e in cube.read("brain"):
        print("   ", e["content"]["state"], "by", e["content"]["authorship"])

    # ------------------------------------------------------------------ 8
    banner(8, "METABOLISM: how overflow is detected (0.75 threshold)")
    head_boot, head_payload = cube.layers[Cube.band_head("events")]
    raw = build_layer_rgba(head_boot, head_payload)
    used = len(raw.rstrip(b"\x00"))
    print("events band head: %d / %d bytes used (%.4f%% of layer capacity)"
          % (used, LAYER_BYTES, 100.0 * used / LAYER_BYTES))
    print("overflow reflex fires at 0.75 capacity, emergency at 0.90.")
    print("Reaching capacity triggers compaction/tiering -- NOT rebirth.")

    # ------------------------------------------------------------------ 9
    banner(9, "VERIFY + STAGED COMMIT guarantee a healthy cube on disk")
    problems = cube.verify()
    print("verify ->", "healthy" if not problems else problems)
    print("every save() writes <path>.stage, re-loads it, verifies, then "
          "os.replace()s atomically. A half-written cube can never be committed.")

    print("\nDone. Cube lives at:", path)
    print("Open any layer as an image:  layers/150.png inside the .vcw zip.")


if __name__ == "__main__":
    main()
