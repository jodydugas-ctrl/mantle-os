# Mantle OS

**An organic coding framework — grow software like a living organism, then give it a mind.**

> Mantle OS v3.0 · The Homeostatic AppAI Framework.

[![Zombie Body Audit](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml/badge.svg)](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml)

*The organism re-certifies on every commit: the Stage-1 gate, 32 security invariants, the
Stage-2 gate, and three tamper proofs that show the audit CATCHES violations.*

> **New here, or skeptical of the biology metaphor?** Start with
> [`docs/Mantle_Positioning.md`](docs/Mantle_Positioning.md) — a plain-language summary and an honest
> list of limitations. *(Non-normative.)*

Mantle OS is a framework for **organic coding**. Instead of writing a "program" with a
"database," you *grow* an application as a living creature — an **AppAI** — built
**Body first, brain second**. Eight deterministic organs mesh on one signal bus around a
durable memory substrate; the Body is proven alive and correct *with no AI attached*; only
then is a **MIND** (an LLM) fused — and it may only ever *extend* what already lives.

**v3 ("homeostatic")**: the organism now regulates itself. Capacity pressure triggers
**metabolism** — compaction, deduplication, layer reuse — never a lossy reset. Every organ
carries an enforced contract. Every failure becomes an immune event. Every generation of
memory seals with a tamper-evident fingerprint.

---

## Quick start

```bash
# Phase 1 — a Body lives (not one model call anywhere on this path)
python -m mantle demo          # narrated life: born -> senses -> reflex -> remembers ->
                               #   protects -> acts -> calcifies -> metabolizes ->
                               #   rebirths -> persists
python -m mantle audit         # the Stage-1 Zombie Body gate (deterministic, LLM-free)
python -m mantle prove         # 32 security invariants, red/green

# the gate must CATCH tampering (all three MUST exit non-zero)
python -m mantle audit --break-hash
python -m mantle audit --break-primer
python -m mantle audit --break-seal

# Phase 2 — fuse a bounded MIND (offline stub; no key, no network)
python -m mantle mind          # narrated fusion: the same heartbeat now also thinks
python -m mantle audit-mind    # the Stage-2 gate: containment + FULL Stage-1 regression

# Path B — assimilate an existing app (read-only dissection)
python -m mantle assimilate examples/sample_app --dry-run

# the VCW cube, standalone — the format defined as one runnable, pure-stdlib file
python examples/vcw/vcw_cube.py selftest      # every format rule proven in one run
python examples/vcw/interop.py                # standalone <-> engine: identical bytes
```

Pure standard library. No dependencies, no network, no keys — for any of the above.

```python
from mantle import Organism
org = Organism.birth(identity={"name": "My.AppAI"},
                     truths=["if it is not in the VCW it did not happen"],
                     commandments=["protect your VCW", "you are a tool USER"])
org.senses.inhale({"action_id": "boot", "event_type": "start"})
org.heart.run(3)               # the Body lives -- no LLM in this loop, ever
```

---

## The architecture in one diagram

```
                          ┌─────────────────────────────┐
        inbound ──────►   │  SENSES   (the ONLY way in)  │
                          └──────────────┬──────────────┘
                                         ▼
   ┌──────────┐   pulse   ┌─────────────────────────────┐   ┌──────────────┐
   │  HEART   │ ────────► │     SignalBus (reflexes,     │◄──│   IMMUNE     │
   │ tick/scan│           │  deterministic, fail-open)   │   │ every fault  │
   │ checkpoint│          └──────┬───────────┬──────────┘   │ becomes an   │
   └──────────┘                  ▼           ▼              │ immune event │
                          ┌──────────┐ ┌──────────┐         └──────────────┘
                          │ NERVOUS  │ │  MEMORY  │
                          │ refs +   │ │ recall + │      BODY (outside every cube):
                          │ assembly │ │metabolism│      GENOME — Primer, sealed at birth
                          └────┬─────┘ └────┬─────┘
                               ▼            ▼
                          ┌─────────────────────────────┐
                          │   VCW CUBE  (PNG layers,     │   sealed ancestors:
                          │   bands, hashed entries,     │   gen0, gen1, ... lazy,
                          │   veil, staged atomic save)  │   read-only, fingerprinted
                          └──────────────┬──────────────┘
                                         ▼
                          ┌─────────────────────────────┐
        outbound ◄──────  │  LIMBS    (the ONLY way out) │
                          └─────────────────────────────┘

        BRAIN: a dormant socket in Phase 1. In Phase 2 a bounded MIND fuses into it —
        writes only thoughts+brain, proposes while the Body applies, never replaces a reflex.
```

## The two phases (non-negotiable order)

| Phase | Name | LLM? | Produces |
|-------|------|------|----------|
| **1** | **Body** | **No** | A certified **Zombie Body** — runs, persists, reacts, provably alive. |
| **2** | **MIND** | Yes | The same Body, now with cognition — fusion is *refused* without a passed Stage-1 gate. |

A Body that passes Stage 1 must keep passing it after fusion; the Stage-2 gate re-runs
every Stage-1 row to prove it.

## Repository layout

```
mantle/                  the v3 framework (start here)
  core/                  Body, SignalBus, references, redaction, the Organism
  vcw/                   the substrate: PNG codec, bands, drivers, cube, metabolism, indexes
  organs/                the eight organs, each with an enforced contract
  mind/                  Phase 2 only: transports, containment, the MIND, AppAIRuntime
  assimilator/           Path B: read-only dissection, organ map, fail-open wrappers
  audits/                Stage 1, Stage 2, and the 32 invariants
docs/
  Mantle_v3_Architecture.md     why the rewrite, and the shape of it
  Mantle_v3_Migration.md        old layout -> new layout, what tightened
  v3/                           VCW guide · organism lifecycle · organ contracts ·
                                assimilation guide · audit guide · visual guide
  assets/                       diagrams (SVG, agent-readable) + rendered art
  Mantle_Doctrine.md (+ the v2 doc set)   the living doctrine — still the creed
examples/
  vcw/                   THE standalone VCW cube: vcw_cube.py (the normative, runnable
                         format definition), interop proof, bench, back-compat shims
  sample_app/            the assimilation dry-run target
```

Reading order: [`docs/Mantle_Doctrine.md`](docs/Mantle_Doctrine.md) →
[`docs/Mantle_Organism_Lens.md`](docs/Mantle_Organism_Lens.md) →
[`docs/Mantle_v3_Architecture.md`](docs/Mantle_v3_Architecture.md) →
[`docs/v3/Organism_Lifecycle.md`](docs/v3/Organism_Lifecycle.md) → the code.
Prefer pictures? [`docs/v3/Visual_Guide.md`](docs/v3/Visual_Guide.md).
When prose and code disagree, **the working code in `mantle/` is ground truth** (and
`examples/vcw/vcw_cube.py` is the standalone, normative definition of the cube format).

## Design principles (binding)

Body before brain · Reflex before reasoning · Append before overwrite · Veil before
exposure · Immune event before silent failure · Audit before fusion · Capability before
action · Provenance before trust · **Metabolism before rebirth** · Harmony before cleverness.

## Two build paths

- **Path A — grow from scratch.** `Mantle_Part1_Body.md`, then the Stage-1 gate, then
  Phase 2. The `mantle/` package is the runnable skeleton.
- **Path B — assimilate existing code.** `Mantle_Assimilator.md` +
  [`docs/v3/Assimilation_Guide.md`](docs/v3/Assimilation_Guide.md): dissect read-only, map organs,
  sign the inventory, wrap fail-open. Both paths converge on the same certified Body and
  the same MIND fusion.

## Status & license

An open demonstration of an alternative coding structure — study it, critique it, build
on it ([`CONTRIBUTING.md`](CONTRIBUTING.md)). Released under the [MIT License](LICENSE).
