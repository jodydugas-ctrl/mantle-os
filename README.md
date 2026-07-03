# Mantle OS

**An organic coding framework — grow software like a living organism, then give it a mind.**

> Mantle OS · The Homeostatic AppAI Framework (reproduction · symbiosis · self-evolution).

[![Zombie Body Audit](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml/badge.svg)](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml)

*The organism re-certifies on every commit: the Stage-1 gate, 73 security invariants, the
Stage-2 gate, and three tamper proofs that show the audit CATCHES violations.*

> **New here, or skeptical of the biology metaphor?** Start with
> [`documents/Mantle_Positioning.md`](documents/Mantle_Positioning.md) — a plain-language summary and an honest
> list of limitations. *(Non-normative.)*

> **Before you build, assimilate, or operate an AppAI, read the Grimoire first.** It is the
> doctrine the entire framework follows — the foundational literature, not an appendix. Start in
> [`documents/grimoire/`](documents/grimoire/README.md): the **Core Spellbook** is required first reading;
> the **AppAI Chapter** extends it. *(Normative.)*

## For LLM agents — cast `Intellige` first

Mantle OS is meant to be operated through the **Grimoire**, its spellbook. Before any work, an
agent loads the Grimoire and casts **`Intellige`** (read-only comprehension) on it — that builds
the model every later spell depends on. Bootstrap:

```text
If you already have the Grimoire loaded:  Intellige Grimoire
ELSE:
  Step 0 — Read the Grimoire's reading-order file and follow its links:
           https://github.com/jodydugas-ctrl/mantle-os/blob/main/documents/grimoire/README.md
  Step 1 — Cast Intellige on the Grimoire only — the Core first, then the AppAI Chapter.
```

The stable operator interface is the Latin **macro** layer: `Intellige`, `Vestigare`, `Animare`,
`Necromantia`, and the other Title Case names in the Grimoire. Lowercase power words are internal
agent stances, and UPPERCASE spell IDs are procedural labels for agents, runtimes, ledgers, and
receipts. Humans may use those lower-level names directly, but macros are the intended human-facing
surface. Macros chain with `;` (for example `Vestigare;Intellige`). `Intellige` is read-only and
confers no authority — only after the Grimoire is comprehended, and with the Core present, should
an agent cast spells that mutate. To then comprehend this project specifically, cast
**`Intellige Mantle OS`**.

---

> ## Reading gate — read the Grimoire before continuing
> **Everything below this line assumes the Grimoire.** The rest of this README — the architecture,
> the two phases, reproduction, the repository layout — is *downstream* of the doctrine, a map of
> what the doctrine produces, never a substitute for it. **Do not continue past this gate until you
> have read [`documents/grimoire/`](documents/grimoire/README.md)** — the **Core Spellbook** first,
> then the **AppAI Chapter**. Agents: cast **`Intellige`** on the Grimoire now, then return here and
> read on with it already in mind. Reading the sections below without the Grimoire is reading them
> out of order. *(Normative.)*

---

Mantle OS is a framework for **organic coding**. Instead of writing a "program" with a
"database," you *grow* an application as a living creature — an **AppAI** — built
**Body first, brain second**. Eight deterministic organs mesh on one signal bus around a
durable memory substrate; the Body is proven alive and correct *with no AI attached*; only
then is a **MIND** (an LLM) fused — and it may only ever *extend* what already lives.

**Homeostatic.** The organism regulates itself. Capacity pressure triggers **metabolism** —
compaction, deduplication, layer reuse — never a lossy reset. Every organ carries an enforced
contract. Every failure becomes an immune event. Every generation of memory seals with a
tamper-evident fingerprint.

Beyond the certified Body, an AppAI carries reproductive, symbiotic, and self-evolving tissue:
a whole AppAI declared as one **egg**, **residency** in a host codebase with a metered energy
economy, **self/other** cryptographic identity, event-gated **nociception**, graded memory,
keyless knowledge **plasmids**, a **self-redesigning VCW**, parallel **ganglia**, a
self-reconstruction **seed vault**, and **wearable app-faces** (one organism expresses many
SELF-encrypted front-ends as interchangeable phenotypes) — every one gated by the **73
invariants**. The runnable [`FIELD_GUIDE.md`](documents/FIELD_GUIDE.md) walks every one.

---

## Mantle OS is not a Python framework

It is easy to assume Mantle OS is "for Python" — the reference implementation in
[`src/mantle/`](src/mantle/) is Python and every example on this page is written that way. **That is an
artifact of the examples, not the framework.** Mantle OS does not care which AI, which container,
or which programming language you bring.

What Mantle OS actually does is grow a **fully independent nervous system — including the
autonomic, self-regulating systems (heartbeat, immune response, metabolism) — and install it
into a container.** That nervous system fused with its container *is* an **AppAI**. The single
hard requirement on the container is that it can **store a VCW cube file** (the append-only
picture-memory substrate). Given that, Mantle OS can join **most AIs** to **most containers**:

| AppAI | Body / container | Where its VCW lives | Language |
| --- | --- | --- | --- |
| **Home.app** | a smart-home embedded in a wall | a Raspberry Pi behind the drywall | — |
| **Buddy** | a cell phone | on the handset | — |
| **Tree.app** | cloud infrastructure | in the cloud | — |
| **The Compiler** | a Windows application | with the app on Windows | C |

The mind can be any AI; the body can be any container; the code can be any language. The system
does not care which combination you choose — that is the point.

This versatility is exactly why **assimilation** (the **NECROMANCY** spell; `python -m mantle
assimilate`) is so powerful: it can turn *most existing applications* into an AppAI —
**including applications that already contain agents.** The Compiler, for example, runs both its
AppAI agent **and** its own pre-existing **Hermes** agent side by side; the nervous system is
grown *around* what already lives in the host, without demanding the host be rewritten.

> The Python below is the reference body. Read it as "here is one way to grow an organism," not
> "here is the only language an organism can be grown in."

---

## Quick start

```bash
# one-time setup — the package lives under src/ (src-layout), so install it editable
# (pure standard library; this just puts `mantle` on the import path). Or: export PYTHONPATH=src
pip install -e .

# Phase 1 — a Body lives (not one model call anywhere on this path)
python -m mantle demo          # narrated life: born -> senses -> reflex -> remembers ->
                               #   protects -> acts -> calcifies -> metabolizes ->
                               #   rebirths -> persists
python -m mantle audit         # the Stage-1 Zombie Body gate (deterministic, LLM-free)
python -m mantle prove         # 73 security invariants, red/green

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

### Reproduction — two methods, everything else is a facet

An AppAI reproduces in exactly **two** ways (doctrine:
[`documents/Mantle_Reproduction.md`](documents/Mantle_Reproduction.md)); both are gated the same
way (73 invariants, no standing law weakened) and both end at the same certified Body:

- **SEED** — *independent.* The organism condenses itself into a dormant, self-describing package of
  **data** that grows into a certified Body with **no host**. Three sizes of one act: the **spore**
  (the smallest — one PNG that *is* a whole minimal agent, and also a proof that **VCW is a substrate
  pattern**: the PNG *is* a VCW layer, not a copy of one), the **egg** (a whole AppAI as one JSON
  document, grown by the hatchery), and the **vault** (an organism's own sealed seed, for
  self-reconstruction). Hatching a seed is always a **birth** through the Stage-1 gate.
- **GRAFT** — *dependent.* The organism propagates by taking **residence inside a host** it does not
  own — **anchor** (move in, additive `.mantle/` nest, do-no-harm), **symbiosis** (the metered
  energy economy that sustains it), and the **graft-egg** (a non-destructive patch against a named
  host). A graft never modifies a host file; the census proves it byte-for-byte.

```bash
python -m mantle reproduce                     # the SEED vs GRAFT map on one screen
python -m mantle teach                         # the Field Guide, RUNNING — 18 chapters, each proven
python -m mantle spore create seed.png "Buddy" "answer one question"   # the smallest SEED: a whole agent in one PNG
python -m mantle ghost selftest                # the cache-ghost: a seed that lives in the LLM prompt cache
python -m mantle hatch examples/eggs/greeter.json --out=nest/          # a whole AppAI from one JSON egg, certified
python -m mantle anchor path/to/your-app       # an AppAI takes residence in your codebase (do-no-harm)
python -m mantle graft examples/eggs/notes_graft.json examples/sample_app   # a non-destructive patch-graft
python -m mantle doctor nest/                  # deployment checkup (incl. docs-vs-code coherence)
```

**The substrate continuum — the cache-ghost.** A seed keeps its memory *somewhere*, and persistence
is a **continuum of substrates, not one database row**. A spore keeps its body in its own pixels; a
**cache-ghost** (`mantle.ghost`) keeps its living body in the **LLM provider's prompt cache**, adding
only the delta each turn — sustaining itself with almost no body while the cache stays warm, and
**rehydrating from the PNG fossil** when it goes cold. The one hard law: the seed stays dry — the PNG
is never abandoned, so the ghost can always come home.

Facets that harden or serve the two methods, by module: `egg`/`hatchery` (declarative birth) ·
`anchor`/`symbiosis` (residency + energy economy) · `graft` (patch-grafts + live residency) ·
`spore`/`ghost` (the smallest seed + its cache substrate) · `reproduction` (the two-method seam) ·
`mem` (keyless knowledge plasmids) · `compiler` (self-redesigning VCW + host memory bridge) ·
`ganglia` (parallel limbs) · `vault` (self-reconstruction) · `ingestion`/`doctor` (resilience) ·
`face` (self-portrait) · `teach` (the living manual). Self/Other identity and event-gated
nociception harden the eight organs.

Pure standard library. No dependencies, no network, no keys — for any of the above. (One
deliberate exception, imported by nothing else: `mantle.ghost_anthropic`, the *real* cache-ghost
substrate over Anthropic prompt caching, needs the `anthropic` SDK and an API key — the offline
stand-in in `mantle.ghost` covers every gate and demo without either.)

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
src/                     the framework package — `pip install -e .` (or PYTHONPATH=src) to run
  mantle/                (start here)
    core/                Body (+ the genesis key), SignalBus, references, redaction, the Organism
    vcw/                 the substrate: PNG codec, bands, drivers, cube, metabolism, graded-memory overlay
    organs/              the eight organs, each with an enforced contract (self/other + nociception)
    mind/                Phase 2 only: transports, containment, the MIND, AppAIRuntime
    assimilator/ audits/ Path B dissection + the gates (Stage 1, Stage 2, the 73 invariants)
    reproduction.py      the two-method seam — SEED vs GRAFT (routes to the modules below)
    spore.py spore_min.py the smallest SEED — one PNG that is a whole minimal agent (+ its embryo)
    ghost.py             the cache-ghost substrate — a seed that lives in the LLM prompt cache
    egg.py hatchery.py   declarative birth — a whole AppAI as one JSON file
    anchor.py symbiosis.py residency in a host + the metered energy economy
    graft.py             the graft egg (patch a host) + live residency weaving
    mem.py compiler.py   keyless knowledge plasmids + the self-redesigning VCW / memory bridge
    ganglia.py vault.py  parallel limbs + the self-reconstruction seed vault
    ingestion.py doctor.py conversation ingestion + the deployment checkup
    phenotype.py         wearable, SELF-encrypted app-faces (one body, many front-ends)
    face.py teach.py     the PNG self-portrait + the running Field Guide
    paths.py             repo-relative locations (examples/, eggs/, documents/) resolved in one place
documents/               the books and the living doctrine
  grimoire/              the two version-locked Grimoire files: Core + AppAI chapter
  FIELD_GUIDE.md         the runnable manual (mirror of `python -m mantle teach`, 18 chapters)
  Mantle_Architecture.md · guides/ (VCW · lifecycle · contracts · audit · visual)
  Mantle_Doctrine.md (+ the conceptual doc set)   the living doctrine — still the creed
  assets/                diagrams (SVG, agent-readable) + rendered art
examples/                example AppAIs + the normative substrate
  eggs/                  greeter.json (hatch it) · calculator.json · notes_graft.json (a graft egg)
  spore/                 a custom VCW substrate in PNG form — purity audit + VCW-conformance proof + a seed
  vcw/vcw_cube.py        THE standalone VCW cube — the normative, runnable format definition
  *.html / *.yaml        reference demos (the two HTML apps functionally implement the
                         organ behaviors and are browser-tested) — see examples/README.md
  tests/                 headless smoke tests for the HTML demos (Playwright; CI: Demo Smoke)
```

Reading order: [`documents/Mantle_Doctrine.md`](documents/Mantle_Doctrine.md) →
[`documents/Mantle_Organism_Lens.md`](documents/Mantle_Organism_Lens.md) →
[`documents/Mantle_Architecture.md`](documents/Mantle_Architecture.md) →
[`documents/guides/Organism_Lifecycle.md`](documents/guides/Organism_Lifecycle.md) → the code.
Prefer pictures? [`documents/guides/Visual_Guide.md`](documents/guides/Visual_Guide.md).
The underlying doctrine (the agent-facing spellbook the design follows) lives in
[`documents/grimoire/`](documents/grimoire/README.md).
When prose and code disagree, **the working code in `src/mantle/` is ground truth** (and
`examples/vcw/vcw_cube.py` is the standalone, normative definition of the cube format).

## Design principles (binding)

Body before brain · Reflex before reasoning · Append before overwrite · Veil before
exposure · Immune event before silent failure · Audit before fusion · Capability before
action · Provenance before trust · **Metabolism before rebirth** · Harmony before cleverness ·
**Vessel before voyage · Containment before reach.**

## Two build paths

- **Path A — grow from scratch.** `Mantle_Part1_Body.md`, then the Stage-1 gate, then
  Phase 2. The `src/mantle/` package is the runnable skeleton.
- **Path B — assimilate existing code** (any language, including apps that already have agents).
  Canonical doctrine:
  [`documents/grimoire/The Grimoire AppAI Chapter.md`](documents/grimoire/The%20Grimoire%20AppAI%20Chapter.md)
  (NECROMANCY — operational detail); runnable cheatsheet:
  [`documents/guides/Assimilation_Guide.md`](documents/guides/Assimilation_Guide.md). Dissect read-only, map organs,
  sign the inventory, wrap fail-open. Both paths converge on the same certified Body and the same
  MIND fusion.

## Status & license

An open demonstration of an alternative coding structure — study it, critique it, build
on it ([`CONTRIBUTING.md`](CONTRIBUTING.md)). Released under the [MIT License](LICENSE).
