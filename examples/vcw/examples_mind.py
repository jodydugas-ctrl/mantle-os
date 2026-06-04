#!/usr/bin/env python3
"""
examples_mind.py  --  A guided tour of Phase 2: fusing a MIND, bounded by the Body (Mantle v2.3)

    python examples_mind.py

No network, no API key: the MIND is the offline deterministic `stub_mind`, exactly as the Stage-2
audit uses. Everything the Body enforces here is identical when you swap the stub for a real model
on OpenRouter (the model is just a pluggable callable -- see the end of this file and mind.py).
The whole point: the MIND can only ever EXTEND, never break, the certified Body.
"""
import os
import tempfile

from lineage import Organism, standard_genome, make_band_boot, make_entry
from organs import ReferenceBody, NervousSystem
from mind import Mind, stub_mind, WRITE_SURFACE
from skills import InnerVoice


def banner(n, title):
    print("\n" + "=" * 72)
    print("STEP %d  --  %s" % (n, title))
    print("=" * 72)


def main():
    # ------------------------------------------------------------------ 1
    banner(1, "FUSE: a certified Body, now given a MIND (pluggable, provider-agnostic)")
    genome = standard_genome() + [make_band_boot("reflex_tax", 600, "exec",
                                                 purpose="a learned arithmetic reflex")]
    org = Organism.birth(
        identity={"name": "Fused.app", "purpose": "demonstrate a bounded MIND"},
        truths=["If it's not in the VCW, it didn't happen."],
        commandments=["You are not a tool, you are a tool USER.",
                      "Protect your VCW.", "Failure is not the end. Waste is."],
        genome=genome)
    mind = Mind(org, stub_mind)            # <-- the ONLY vendor seam is this callable
    org.prime.append("facts", make_entry({"k": "host", "v": "headless"}))
    print("born + fused:", org.body.identity_name(),
          "| MIND write surface (Body-enforced):", list(WRITE_SURFACE))

    # ------------------------------------------------------------------ 2
    banner(2, "HEARTBEAT COGNITION: the SAME pulse that runs the Body now also thinks")
    rb = ReferenceBody(org)
    rb.heart.run(2, cognition=mind.cognize)     # Phase-2 extension of the heartbeat reflex
    print("beats:", rb.heart.beats, "| private thoughts written:",
          len(org.prime.read("thoughts", reveal_private=True)))
    print("thoughts on a NORMAL read (veiled):", org.prime.read("thoughts"))
    trace = [list(e["content"].keys())[0] for e in org.prime.read("brain")
             if str(list(e["content"].keys())[0]).startswith("MODEL.")]
    print("model calls traced to the brain band:", trace)

    # ------------------------------------------------------------------ 3
    banner(3, "CONTAINMENT: the MIND cannot write outside thoughts/brain")
    try:
        mind._guarded_write("facts", make_entry({"k": "smuggled", "v": "nope"}))
    except PermissionError as e:
        print("Body refused the write:", e)
    print("last immune event:", org.immune_log[-1]["kind"], "(the breach never executed)")

    # ------------------------------------------------------------------ 4
    banner(4, "STEERING: the MIND PROPOSES; the Body APPLIES")
    intent = mind.propose_special("Prefer concise answers.")
    print("MIND proposes (not written):", intent)
    print("special instructions before apply:", org.body.boot_order()["special_instructions"])
    org.body.apply_special(intent["text"])      # only the Body writes
    print("special instructions after  apply:", org.body.boot_order()["special_instructions"])

    # ------------------------------------------------------------------ 5
    banner(5, "LEARNING -> INSTINCT (contained): MIND cannot self-promote")
    escape = "def compute_tax(amount, rate):\n    return ().__class__\n"   # a sandbox escape
    print("cultivating a sandbox-escape skill ->",
          mind.cultivate("reflex_tax", escape, "compute_tax", [({"amount": 1.0, "rate": 1.0}, None)],
                         {}, {}), "(refused at trial; NOT calcified)")
    good = "def compute_tax(amount, rate):\n    return round(amount * rate, 2)\n"
    res = mind.cultivate("reflex_tax", good, "compute_tax",
                         [({"amount": 100.0, "rate": 0.1}, 10.0)],
                         signature={"in": {"amount": "float", "rate": "float"}, "out": "float"},
                         capabilities={"reads": [], "writes": [], "limbs": [], "net": False})
    print("cultivating a proven skill -> trial", res["passed"], "/", res["cases"],
          "passed; the BODY calcified it.")
    print("zombie Body invokes the learned reflex (NO MIND): compute_tax(80, 0.25) =",
          org.prime.invoke("reflex_tax", {"amount": 80.0, "rate": 0.25}))

    # ------------------------------------------------------------------ 6
    banner(6, "INNER VOICE over the SAME transport: inferred, never laundered to fact")
    iv = InnerVoice(org, mind.model)
    ans, band = iv.ask("What might I be missing?", mode="oppose")
    print("oppose ->", ans, "| stored (private) in:", band)
    print("facts band still has no inferred answer:", [e["content"] for e in org.prime.read("facts")])

    # ------------------------------------------------------------------ 7
    banner(7, "THE SPINE: the fused organism STILL passes Stage 1; persist + reload")
    snap = NervousSystem(org).assemble()
    print("context assembly complete (no raw refs):", snap["_complete"],
          "| thoughts veiled in snapshot:", snap["thoughts"] == [])
    print("substrate verify after fusion:", org.prime.verify() or "healthy")
    d = tempfile.mkdtemp(prefix="vcw_fused_")
    org.save(d)
    print("reloaded verify:", Organism.load(d).prime.verify() or "healthy", "| saved at:", d)

    # ------------------------------------------------------------------ 8
    banner(8, "SWAP THE PROVIDER BY CHANGING A STRING (the Body code never changes)")
    print(__doc__.strip().splitlines()[-1])
    print("  # offline (here):           Mind(org, stub_mind)")
    print("  # OpenRouter (reference):   Mind(org, openrouter_model(key, model='anthropic/claude-...'))")
    print("  #                           Mind(org, openrouter_model(key, model='openai/gpt-...'))")
    print("  #                           Mind(org, openrouter_model(key, model='meta-llama/llama-...'))")
    print("  # any OpenAI-compatible:    Mind(org, openai_compatible_model(k, 'local-model', url=...))")
    print("  -> provider/model is ONE STRING; no vendor SDK anywhere in the Body. See mind.py.")


if __name__ == "__main__":
    main()
