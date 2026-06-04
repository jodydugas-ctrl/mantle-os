#!/usr/bin/env python3
"""
examples_boot.py  --  A guided tour of Mantle v2.1: programmable boot sectors, the Body,
the unified reference grammar, executable reflex layers (learning -> instinct), the Inner
Voice skill, and rebirth-as-reformat across a cube lineage.

    python examples_boot.py

No network, no API key, no LLM required: the MIND is a deterministic offline stub. Everything
here is the BODY -- it runs with no brain. That is the whole point.
"""
import os
import tempfile

from lineage import Organism, Cube, standard_genome, make_band_boot, make_entry, trial, code_hash
from skills import InnerVoice, stub_model


def banner(n, title):
    print("\n" + "=" * 72)
    print("STEP %d  --  %s" % (n, title))
    print("=" * 72)


def main():
    # ------------------------------------------------------------------ 1
    banner(1, "BIRTH: the Primer lives in the BODY; the cube is pure memory")
    genome = standard_genome() + [
        make_band_boot("calendar", 560, "calendar-spatial",
                       params={"epoch": "2026-01-01",
                               "palette": {"ff0000": "urgent", "0066ff": "work",
                                           "00aa00": "personal"}}),
        make_band_boot("reflex_tax", 590, "exec"),
        # a rolling log band that reserves 4 layers and rolls every 3 entries (to show
        # on-demand layer allocation + reclaim/reuse without huge data)
        make_band_boot("log", 570, "log-json", span=4, purpose="rolling activity log",
                       params={"max_entries_per_layer": 3}),
    ]
    org = Organism.birth(
        identity={"name": "Notepad.app", "purpose": "demonstrate Mantle v2.1"},
        truths=["If it's not in the VCW, it didn't happen.",
                "I have no innate sense of time; I see my experience in perfect clarity."],
        commandments=["You are not a tool, you are a tool USER.",
                      "Protect your VCW. It is your mind, your memory, your life.",
                      "Failure is not the end. Waste is."],
        genome=genome)
    print("born:", org.body.identity_name(), "| prime generation:", org.prime.generation)
    print("cube.identity_in_body =", org.prime.identity_in_body, "(Primer is NOT in the cube)")
    print("cube bands:", ", ".join(org.prime.bands))

    # ------------------------------------------------------------------ 2
    banner(2, "BODY STORE + boot order (Primer + Special Instructions + Immunization)")
    intent = org.body.mind_propose_special("Prefer concise answers.")
    print("MIND proposes (cannot write directly):", intent)
    org.body.apply_special(intent["text"])      # only the BODY applies the change
    print("\n" + org.body.boot_text())

    # ------------------------------------------------------------------ 3
    banner(3, "PROGRAMMABLE BOOT SECTOR: a calendar stored as COLORS AT COORDINATES")
    org.prime.calendar_set("calendar", "2026-06-15", "work")
    org.prime.calendar_set("calendar", "2026-06-16", "urgent")
    print("2026-06-15 ->", org.prime.calendar_get("calendar", "2026-06-15"))
    print("2026-06-16 ->", org.prime.calendar_get("calendar", "2026-06-16"))
    print("2026-06-17 ->", org.prime.calendar_get("calendar", "2026-06-17"), "(nothing scheduled)")
    cells = org.prime.read("calendar")
    print("non-free cells on the canvas:", cells)
    print("(this layer persists as a real PNG you can open as an image)")

    # ------------------------------------------------------------------ 4
    banner(4, "UNIFIED REFERENCE GRAMMAR <TARGET.SELECTOR.ADDRESS>")
    org.prime.append("facts", make_entry({"k": "host", "v": "windows"}))
    drv = org.prime._driver("calendar")
    cx, cy = drv.coord_for_date(org.prime.bands["calendar"]["params"], "2026-06-15")
    for ref in ["<facts.0>", "<body.immune.0>", "<calendar.%dx%d>" % (cx, cy), "<facts.99>"]:
        print("  %-20s -> %s" % (ref, org.resolve(ref)))
    print("  (the dangling <facts.99> was logged to immune:", org.immune_log[-1]["kind"], ")")

    # ------------------------------------------------------------------ 5
    banner(5, "LAYERS ON DEMAND + SAFE REUSE: a band grows and reclaims layers")
    # the 'log' band rolls to a new physical layer every 3 entries (reserved span = 4)
    for i in range(7):
        org.prime.append("log", make_entry({"event": "tick %d" % i}, opcode="LOG"))
    print("after 7 appends: active layers =", org.prime.band_layers["log"],
          "| free =", org.prime.band_free["log"])
    print("logical <log.0> ->", org.resolve("<log.0>")["content"],
          "| <log.6> ->", org.resolve("<log.6>")["content"])
    # tombstone everything, then compact -> emptied non-tail layers return to the reuse pool
    org.prime.tombstone_all("log")
    report = org.prime.compact("log")
    print("compact reclaimed", report["reclaimed"], "layer(s):",
          "active =", org.prime.band_layers["log"], "| free pool =", org.prime.band_free["log"])
    # new appends REUSE freed layers before consuming fresh range
    for i in range(4):
        org.prime.append("log", make_entry({"event": "reuse %d" % i}, opcode="LOG"))
    print("after reuse appends: active =", org.prime.band_layers["log"],
          "| free =", org.prime.band_free["log"], "(freed slots were reused first)")
    print("safe-reuse: spatial calendar layer is NOT reclaimed ->",
          org.prime.compact("calendar")["note"])

    # ------------------------------------------------------------------ 6
    banner(6, "LEARNING -> INSTINCT: cultivate -> trial -> CALCIFY -> zombie invoke")
    code = "def compute_tax(amount, rate):\n    return round(amount * rate, 2)\n"
    cases = [({"amount": 100.0, "rate": 0.1}, 10.0),
             ({"amount": 250.0, "rate": 0.2}, 50.0)]
    result = trial(code, "compute_tax", cases)        # Body runs the candidate in a sandbox
    print("trial:", result["passed"], "/", result["cases"], "passed -> ok =", result["ok"])
    org.prime.calcify("reflex_tax", code, entry="compute_tax",
                      signature={"in": {"amount": "float", "rate": "float"}, "out": "float"},
                      capabilities={"reads": [], "writes": [], "limbs": [], "net": False},
                      provenance={"author": "MIND", "born_gen": 0, "trials": result["cases"]})
    print("CALCIFIED into an exec layer (hashed + capability-bound).")
    print("zombie Body invokes the learned skill (NO MIND): compute_tax(80, 0.25) =",
          org.prime.invoke("reflex_tax", {"amount": 80.0, "rate": 0.25}))

    # ------------------------------------------------------------------ 7
    banner(7, "SANDBOX GATES: capability + integrity are enforced")
    try:
        org.prime.invoke("reflex_tax", {"amount": 1.0, "rate": 1.0},
                         granted={"reads": ["facts"]})       # asks for a capability it lacks
    except Exception as e:
        org.immune_event("capability_denied", {"skill": "reflex_tax", "error": str(e)})
        print("capability gate refused over-reach:", type(e).__name__)
    tampered = dict(org.prime.layers[590]); tampered["code"] += "\n# tamper\n"
    org.prime.layers[590] = tampered
    try:
        org.prime.invoke("reflex_tax", {"amount": 1.0, "rate": 1.0})
    except Exception as e:
        print("integrity gate refused tampered code:", type(e).__name__)
    # restore a clean hash so later steps stay healthy
    org.prime.layers[590]["code_hash"] = code_hash(org.prime.layers[590]["code"])

    # ------------------------------------------------------------------ 8
    banner(8, "INNER VOICE (self-inquiry): inferred, never laundered into fact")
    iv = InnerVoice(org, stub_model)
    ans, band = iv.ask("What changed in the spec recently?", mode="search")
    print("search ->", ans, "| stored in:", band)
    ans2, band2 = iv.ask("Caching everything forever is wise.", mode="oppose")
    print("oppose ->", ans2, "| stored in:", band2, "(private)")
    disc = org.prime.read("discoveries")
    print("discoveries entry verified flag:", disc[-1]["verified"], "confidence:",
          disc[-1]["confidence"], "(NOT promoted to facts)")
    print("thoughts veiled read:", org.prime.read("thoughts"),
          "| revealed:", len(org.prime.read("thoughts", reveal_private=True)), "entry")

    # ------------------------------------------------------------------ 9
    banner(9, "REBIRTH = REFORMAT: new Prime, ancestral retained, references still resolve")
    org.prime.append("facts", make_entry({"k": "lesson", "v": "calendar band ran hot"}))
    old_gen = org.prime.generation
    org.rebirth(reason="genome refit: calendar needs more layers")
    print("prime generation now:", org.prime.generation, "| ancestral:",
          [c.generation for c in org.ancestral])
    print("ancestral cube is read-only to experience:")
    try:
        org.ancestral[0].append("facts", make_entry("nope"))
    except Exception as e:
        print("   ", type(e).__name__, "-", str(e))
    print("generation-pinned ref still resolves: <gen%d.facts.0> ->" % old_gen,
          org.resolve("<gen%d.facts.0>" % old_gen))
    print("new life inherited a distillation:", org.prime.read("discoveries"))
    print("body lineage index:", org.body.lineage_index)

    # ------------------------------------------------------------------ 10
    banner(10, "PERSIST + RELOAD the whole organism (Body + lineage)")
    d = tempfile.mkdtemp(prefix="vcw_org_")
    org.save(d)
    reloaded = Organism.load(d)
    print("reloaded:", reloaded.body.identity_name(),
          "| prime gen:", reloaded.prime.generation,
          "| ancestral:", [c.generation for c in reloaded.ancestral])
    print("post-reload ref <gen%d.facts.0> ->" % old_gen,
          reloaded.resolve("<gen%d.facts.0>" % old_gen))
    print("prime verify:", reloaded.prime.verify() or "healthy")
    print("\norganism saved at:", d)


if __name__ == "__main__":
    main()
