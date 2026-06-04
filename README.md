# Mantle OS

**An organic coding framework — grow software like a living organism, then give it a mind.**

> Mantle OS v2.3 · A demo of an alternative coding structure.

[![Zombie Body Audit](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml/badge.svg)](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml)

*The Zombie Body re-certifies on every commit: the Stage-1 audit (substrate **and** the runnable
reference Body) and the security invariants run in CI, and the audit harness is itself proven to
**catch** tampering.*

Mantle OS is a framework for **organic coding**. Instead of writing a "program" with a
"database," you *grow* an application as if it were a living creature — an **AppAI** — built
**Body first, brain second**. You assemble a body of deterministic *organs* around a durable
memory substrate, prove the body is alive and correct *with no AI attached*, and only then
fuse in a **MIND** (an LLM) that can extend what already lives but can never break it.

This repository is both a **set of ideas** (a way of thinking about software as anatomy) and a
**runnable substrate** (the `vcw/` package) you can read, run, and build on.

---

## Why this exists

Most applications are built like centralized machines: one big brain (now often an LLM) sits in
the middle and everything depends on it. Mantle takes the opposite stance, modelled on the
**octopus** — an animal whose arms think for themselves. Roughly two-thirds of an octopus's
neurons live in its arms; each arm senses, decides, and acts on its own. The central brain hands
an arm a *goal*, not a step-by-step program.

Mantle applies that wiring to software:

- The **Body** is a federation of organs that each do one living job and run *without* an LLM.
- The **MIND** (an LLM) is fused only after the Body is certified — and it may only ever *extend*
  the Body, never replace a reflex.
- All durable state lives in the **VCW cube**, a memory substrate the organism treats as its
  reality: *"if it's not in the VCW, it didn't happen."*

The payoff is an application that is **provable, auditable, and genuinely functional before any
AI is attached** — and whose AI layer is sharply bounded.

---

## The two phases (non-negotiable order)

| Phase | Name | LLM attached? | Produces |
|-------|------|---------------|----------|
| **1** | **Body** | **No** | A certified **Zombie Body** — runs, persists, reacts, provably alive but dormant. |
| **2** | **MIND** | **Yes** | The same Body, now with cognition and voice. |

**Phase 2 may only ever *extend* Phase 1.** A Body that passes the Stage 1 audit must keep
passing it after the mind is fused. If attaching the MIND breaks a Body reflex, the *fusion* is
wrong — not the Body.

---

## Core vocabulary

The biology is not decoration; it is the architecture.

| Term | Meaning |
|------|---------|
| **AppAI** | The embodied application-as-organism you are growing. |
| **VCW cube** | The durable nervous-memory substrate (layered images). The "heart." |
| **Body** | All organs that run **without** an LLM. Phase 1. |
| **MIND** | The reasoning/voice layer — an LLM fused in Phase 2. |
| **Organ** | A self-contained module with a manifest, reflexes, and audit obligations. |
| **Reflex** | A deterministic, no-LLM behavior. The Body is made of reflexes. |
| **Band** | A reserved, named range of cube layers (e.g. `facts`, `senses`, `thoughts`). |
| **Veil** | The reflex that hides private / retired / quarantined memory on read. |
| **Zombie Body** | A Body that has passed the Stage 1 Gate: alive, correct, dormant. |

The canonical organ set is eight organs: **Heart, Genome, Nervous System, Senses, Immune System,
Limbs, Memory, and Brain** (the Brain being the only organ dormant in Phase 1). See
[`Mantle_Organ_Atlas.md`](Mantle_Organ_Atlas.md) for the full taxonomy.

---

## How to read this repository

The documents are meant to be read in order. Start with the philosophy, then the mindset, then
the operating manual, then the code.

```
Mantle_Doctrine.md        <- READ FIRST: the creed + cosmology (why)
Mantle_Organism_Lens.md   <- the mindset: read any app as a living creature
Mantle_PRIMER.md          <- role, ontology, operating procedure (who you are while building)
Mantle_Organ_Atlas.md     <- the formal organ taxonomy (what each organ is)
vcw/                      <- the heart, in runnable code (the substrate you build around)
  vcw/GUIDE.md            <- the one teaching guide for the substrate
  vcw/organs/            <- the runnable reference Body (Heart, Senses, Limbs, Nervous System)

PHASE 1 (Body):
  Mantle_Part1_Body.md          <- how to grow the Body, organ by organ
  Mantle_Part1_Body_Audit.md    <- the Stage 1 Gate; certify the Zombie Body

PHASE 2 (MIND):
  Mantle_Part2_Mind.md          <- how to fuse the MIND
  Mantle_Part2_Mind_Audit.md    <- the Stage 2 Gate; Phase-1 regression + Phase-2 checks

Mantle_Assimilator.md     <- Path B: grow organs around EXISTING code, non-destructively
Mantle_Extensions.md      <- OPTIONAL overlays. Not normative.

doctrine/                 <- source texts for the doctrine (the creed + the cosmology)
examples/                 <- illustrative reference artifacts (see note below)
```

When prose and code disagree, **the working code in `vcw/` is ground truth.**

---

## Quick start (the runnable substrate)

The `vcw/` package is plain Python with no required third-party dependencies for the core
substrate.

```bash
# from the repository root — one command to see the whole organism live
python -m vcw demo      # narrated tour: genesis -> sense -> reflex -> learn -> rebirth -> persist
python -m vcw audit     # the Stage-1 Zombie Body audit (substrate + runnable Body)
python -m vcw prove     # the security invariants (red/green)

# or run the modules directly from inside vcw/
cd vcw

# run the Stage 1 (Zombie Body) audit against a fresh demo organism
python audit.py

# prove the audit harness actually catches tampering
python audit.py --break-hash      # a tampered entry -> integrity check must FAIL
python audit.py --break-primer    # Primer forced into the cube -> must FAIL

# run the security invariants
python test_invariants.py
```

A passing `audit.py` prints a **Zombie Body Certification** block and exits zero only when there
are no open hard-fails — the deterministic gate that authorizes Phase 2. As of v2.3 that block
certifies **both** the substrate **and** a runnable reference Body (`vcw/organs/`): the Heart's
heartbeat, the Senses classifier, the Limbs dispatch lifecycle, and the Nervous System's Context
Assembly are real, no-LLM code, so the seven rows that once read *NEEDS-HOST* are now genuine
PASS/FAIL.

```bash
# Phase 2 — fuse a MIND, bounded entirely by the Body (offline; no key needed)
python -m vcw mind        # narrated fusion tour: the same heartbeat now also thinks
python -m vcw audit-mind  # the Stage-2 gate: MIND containment + Phase-1 regression
```

The MIND ([`vcw/mind.py`](vcw/mind.py)) is sharply contained: it may write **only** the private
`thoughts` band and the `brain` band (any other write is refused and logged as an immune event),
it *proposes* Special Instructions while the Body *applies* them, and it cannot self-promote a
skill. The model is a **pluggable transport** — there is no vendor SDK in the Body. The reference
transport is **OpenRouter** (one OpenAI-compatible endpoint, one keyfile, a model-id *string* that
selects any provider/model); an offline deterministic stub is used for the demo and audit so they
need no network or key. You change providers by changing a string, never the Body code.

---

## The mental model in one sentence

> Grow a Body of organs around the VCW cube that runs perfectly with no brain; certify it; then
> give it a mind that can only ever *extend* what already lives.

---

## Two build paths

- **Path A — build from scratch (greenfield).** Design the creature organ by organ: heart first,
  then senses, memory, immune system, limbs — a complete body that lives with no brain. Only then
  fuse a mind. Follow `Mantle_Part1_Body.md`.
- **Path B — assimilate existing code (brownfield).** Dissect an existing app with the Organism
  Lens, classify each part by organ role, and thread a nervous system through it *without
  rewriting its behavior*. Follow `Mantle_Assimilator.md`.

Both paths converge on the same certified Body, then the same MIND fusion.

---

## A note on the `examples/`

The `examples/` folder contains reference artifacts that illustrate the ideas in action. They are
**illustrative and may lag behind the documents** — the framework's own guidance is to build from
the instructions, not from any example artifact. Treat them as inspiration, not specification.

---

## Status

Mantle OS is published as an **open demonstration of an alternative coding structure**. It is a
conceptual framework plus a reference substrate, shared so others can study, critique, and build
on the approach. Feedback, questions, and forks are welcome — see
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

Released under the [MIT License](LICENSE).
