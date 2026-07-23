# Mantle OS

**An organic coding framework — grow software like a living organism, then give it a mind.**

> Mantle OS · The Homeostatic AppAI Framework (reproduction · symbiosis · self-evolution).

[![Zombie Body Audit](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml/badge.svg)](https://github.com/jodydugas-ctrl/mantle-os/actions/workflows/audit.yml)

*The organism re-certifies on every commit: the Stage-1 gate, the security invariant
suite, the Stage-2 gate, and three tamper proofs that show the audit CATCHES violations.*

**Current certification count:** run `python -m mantle prove` -- the count is derived
from the code, never hardcoded in prose (the doctor's docs-vs-code gate enforces this).

Release history: [`CHANGELOG.md`](CHANGELOG.md) · Security reporting: [`SECURITY.md`](SECURITY.md)

> **New here, or skeptical of the biology metaphor?** Start with the plain-language
> on-ramp in [`documents/PRIMER.md`](documents/PRIMER.md) §0 — a one-idea summary and an
> honest list of limitations.

> **For LLM agents.** Mantle OS is operated through the **Grimoire**, its spellbook —
> load it when the work needs doctrine, AppAI operation, assimilation, or mutation of
> Mantle tissue, and cast **`Intellige`** (read-only comprehension) on it first. It is
> doctrine, not a toll booth: routine code reading and small mechanical fixes proceed
> from the README, nearby docs, and working code. Start at
> [`documents/grimoire/`](documents/grimoire/README.md); §7 and §9 of the single
> canonical **Grimoire 2.0** file are the Mantle-binding sections. The organic language
> is scoped — Body, MIND, Senses, VCW, SELF/OTHER name *Mantle tissue*, not ordinary
> host/application code. *(Normative when used.)*

---

Mantle OS is a framework for **organic coding**. Instead of writing a "program" with a
"database," you *grow* an application as a living creature — an **AppAI** — built
**Body first, brain second**. Nine deterministic organs mesh on one signal bus around a
durable memory substrate; the Body is proven alive and correct *with no AI attached*; only
then is a **MIND** (an LLM) fused — and it may only ever *extend* what already lives.

**Homeostatic.** The organism regulates itself. Capacity pressure triggers **metabolism** —
compaction, deduplication, layer reuse — never a lossy reset. Every organ carries an enforced
contract. Every failure becomes an immune event. Every generation of memory seals with a
tamper-evident fingerprint.

Beyond the certified Body, an AppAI carries reproductive, symbiotic, and self-evolving tissue:
a whole AppAI travelling as one **spore** (a PNG carrying its **germ** — the complete build
data — plus instructions any coding agent can read), **residency** in a host codebase with a
metered energy economy, **self/other** cryptographic identity, baseline ten-minute cognition
plus additional **nociceptive interrupts**, graded memory,
keyless knowledge **plasmids**, a **self-redesigning VCW**, parallel **ganglia**, a
self-reconstruction **seed vault**, and **wearable app-faces** (one organism expresses many
SELF-encrypted front-ends as interchangeable phenotypes) — every one gated by the **full
invariant suite** and, where an operation creates a new resident or activates cognition,
separate target-bound authority. The runnable [`FIELD_GUIDE.md`](documents/FIELD_GUIDE.md)
walks every one.

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
**including applications that already contain agents.** The Compiler, for example, wraps its
pre-existing **Hermes** agent with an additive Mantle autonomic nervous system. Hermes remains
the cognitive host; Mantle grows *around* what already lives there without demanding a rewrite.

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
python -m mantle prove         # the security invariant suite, red/green

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

### Reproduction — one artifact, two methods

An AppAI travels as **ONE artifact — the spore** — and reproduces in exactly **two** ways
(doctrine: [`documents/REPRODUCTION.md`](documents/REPRODUCTION.md)); both require the same
technical evidence (the full invariant suite, no standing law weakened), but evidence is not
authority: birth, reconstruction, or activation also requires the applicable fresh
operator/guardian decision. Both methods end at the same certified Body:

- **SEED** — *independent.* A spore whose **germ** declares a whole new AppAI: one PNG
  carrying the complete build document plus instructions any coding agent can read (with
  Mantle: `mantle hatch <spore.png>`; without: decode the pixels and grow from the germ).
  The spore is also a proof that **VCW is a substrate pattern**: the PNG *is* a VCW layer.
  Hatching a seed is always a **birth** through the Stage-1 gate; the genesis key is
  **minted at birth, never derived from the spore** — a public PNG must never be able to
  forge SELF.
- **GRAFT** — *dependent.* A spore **aimed at a host** the organism does not own —
  **anchor** (move in, additive `.mantle/` nest, do-no-harm), **symbiosis** (the metered
  energy economy that sustains it), and the **graft germ** (a non-destructive patch
  against a named host). A graft never modifies a host file; the census proves it
  byte-for-byte. And assimilation closes the loop: `mantle assimilate <app> --spore=out.png`
  scans an existing app and **emits its spore**.

The ceremonies have a Body-resident owner: the **Reproduction organ** (the ninth organ) —
it keeps the app-band atlas, vaults every organism's own germ at birth, and carries the
sealed heirlooms across every rebirth (or raises an immune event, never a silent loss).

```bash
python -m mantle reproduce                     # the map on one screen
python -m mantle hatch examples/spores/greeter.png --out=nest/   # THE birth command
python -m mantle spore pack my_germ.json my_app.png              # germ -> one spore
python -m mantle assimilate path/to/app --spore=out.png          # existing app -> spore
python -m mantle teach                         # the Field Guide, RUNNING — 18 chapters, each proven
python -m mantle spore create seed.png "Buddy" "answer one question"   # the minimal seed
python -m mantle ghost selftest                # the cache-ghost: a seed that lives in the LLM prompt cache
python -m mantle anchor path/to/your-app       # an AppAI takes residence in your codebase (do-no-harm)
python -m mantle graft examples/spores/notes_graft.png examples/sample_app   # a spore aimed at a host
python -m mantle doctor nest/                  # deployment checkup (incl. docs-vs-code coherence)
```

**The substrate continuum — the cache-ghost.** A seed keeps its memory *somewhere*, and persistence
is a **continuum of substrates, not one database row**. A spore keeps its body in its own pixels; a
**cache-ghost** (`mantle.ghost`) keeps its living body in the **LLM provider's prompt cache**, adding
only the delta each turn — sustaining itself with almost no body while the cache stays warm, and
**rehydrating from the PNG fossil** when it goes cold. The one hard law: the seed stays dry — the PNG
is never abandoned, so the ghost can always come home.

Facets that harden or serve the two methods, by module: `spore`/`hatchery` (the one
artifact + the one birth door) · `anchor`/`symbiosis` (residency + energy economy) ·
`graft` (spores aimed at hosts + live residency) · `ghost` (the cache substrate) ·
`reproduction` (the two-method seam) · `mem` (keyless knowledge plasmids) · `compiler`
(self-redesigning VCW + host memory bridge) · `ganglia` (parallel limbs) ·
`organs/reproduction` (the vault heirlooms + lineage duty) · `ingestion`/`doctor`
(resilience) · `face` (self-portrait) · `teach` (the living manual). Self/Other identity
and event-gated nociception harden the organs.

Pure standard library. No dependencies, no network, no keys — for any of the above. (The one
optional Phase-2 module, imported by nothing else: `mantle.ghost_http`, the *real* cache-ghost
substrate — a **vendor-neutral**, OpenAI-compatible HTTP adapter on pure-stdlib `urllib` (no SDK)
whose provider is entirely configured; it needs a network and a key at runtime, while the offline
stand-in in `mantle.ghost` covers every gate and demo without either.)

Prompt caching and response caching are separate facts. Prompt caching keeps a stable prefix warm
inside the provider path; response caching returns an identical full request from the router edge.
Mantle records proof fields for both through optional Phase-2 transport receipts: cached tokens,
cache-write tokens, response-cache HIT/MISS, generation id, session id, cost, total cost, provider,
router, and redacted request hashes. No raw prompt, completion, or key belongs in those receipts.

```python
from mantle import Organism
org = Organism.birth(identity={"name": "My.AppAI"},
                     truths=["if it is not in the VCW it did not happen"],
                     commandments=["protect your VCW", "you are a tool USER"])
org.senses.inhale({"action_id": "boot", "event_type": "start"})
org.heart.run(3)               # the Body lives -- no LLM in this loop, ever
```

---

## VCW Applet Bodies — APPLET-BODY-CAPSULE

An AppAI can carry other apps as **tissue**. `applet-create` takes an external project
(a local directory, or a GitHub clone via `applet-clone`), runs the NECROMANCY-style
read-only dissection over it, and stores the result inside the parent's VCW as an
**applet body**: the source as inert, veiled, hash-verified data; variables/state in an
append-only (redacted) state band; the organ map as diagnosis; and a **phenotype face**
(the project's `index.html`, or a synthesized manifest surface) worn through the normal
`phenotype` system. Nothing stored is ever executed — a capsule is *source in the body*,
not authority; execution still requires the existing trial/calcify or host-render gates,
and the capsule is never falsely labeled a Zombie Body. Doctrine:
[`documents/Mantle_Applet_Bodies.md`](documents/Mantle_Applet_Bodies.md).

```bash
python -m mantle applet-create nest/ path/to/project notes    # raise APPLET-BODY-CAPSULE
python -m mantle applet-list   nest/                          # the catalog
python -m mantle applet-show   nest/ notes                    # manifest + organ map (no blobs)
python -m mantle applet-audit  nest/ notes                    # deterministic capsule audit
python -m mantle applet-export nest/ notes out/               # "download": hash-verified source
python -m mantle applet-wear   nest/ notes                    # the face, as a host boot manifest
python -m mantle applet-clone  nest/ https://github.com/owner/repo notes   # explicit HTTPS only
```

The five applet bands (`applets_manifest/source/state/organs/log`, heads 700–747) pass
the same `validate_genome` gate as any app band; invariants **APPLET-1…5** prove the
guarantees (no execution, hash-verified export, traversal/overwrite refusal, tamper
caught, secret boundary held) in `python -m mantle prove`.

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
| **2** | **MIND** | Yes | The same Body, now with cognition — fusion requires Stage-1 evidence **and** explicit operator + guardian approval. |

A Body that passes Stage 1 must keep passing it after fusion; the Stage-2 gate re-runs
every Stage-1 row to prove it.

## Repository layout

```
src/                     the framework package — `pip install -e .` (or PYTHONPATH=src) to run
  mantle/                (start here)
    core/                Body (+ the genesis key), SignalBus, references, redaction, the Organism
    vcw/                 the substrate: PNG codec, bands, drivers, cube, metabolism, graded-memory overlay
    organs/              the nine organs, each with an enforced contract (self/other + nociception)
    mind/                Phase 2 only: transports, containment, the MIND, AppAIRuntime
    assimilator/ audits/ Path B dissection + the gates (Stage 1, Stage 2, invariant suite)
    reproduction.py      the two-method seam — SEED vs GRAFT (routes to the modules below)
    spore.py spore_min.py THE artifact — one PNG agent, optionally carrying a germ (+ its embryo)
    hatchery.py          the one birth door: germ or spore -> certified organism
    ghost.py             the cache-ghost substrate — a seed that lives in the LLM prompt cache
    anchor.py symbiosis.py residency in a host + the metered energy economy
    graft.py             the graft germ (a spore aimed at a host) + live residency weaving
    mem.py compiler.py   keyless knowledge plasmids + the self-redesigning VCW / memory bridge
    ganglia.py           parallel limbs (the seed vault lives in organs/reproduction.py)
    ingestion.py doctor.py conversation ingestion + the deployment checkup
    phenotype.py         wearable, SELF-encrypted app-faces (one body, many front-ends)
    face.py teach.py     the PNG self-portrait + the running Field Guide
    paths.py             repo-relative locations (examples/, eggs/, documents/) resolved in one place
documents/               the books and the living doctrine
  PRIMER.md              THE doctrine home: on-ramp, creed, lens, operating procedure
  FIELD_GUIDE.md         the runnable manual (19 chapters; `python -m mantle teach` runs 18 of them live)
  ARCHITECTURE.md        the shape + the Phase-1/Phase-2 build path
  REPRODUCTION.md        the spore, the hatchery, the graft, rebirth
  Mantle_Organ_Atlas.md  the organ taxonomy + the organ contracts
  grimoire/              the single Grimoire 2.0 file (§7/§9 bind it to Mantle)
  guides/ (VCW · audit · lifecycle · assimilation · visual) · assets/ (diagrams)
examples/                example AppAIs + the normative substrate
  spores/                germ spores — hatch one: `mantle hatch examples/spores/greeter.png`
  eggs/                  the germ files those spores are packed from
  spore/                 a custom VCW substrate in PNG form — purity audit + VCW-conformance proof
  vcw/vcw_cube.py        THE standalone VCW cube — the normative, runnable format definition
  *.html / *.yaml        reference demos (browser-tested) — see examples/README.md
  tests/                 headless smoke tests for the HTML demos (Playwright; CI: Demo Smoke)
```

Reading order: this README → [`documents/PRIMER.md`](documents/PRIMER.md) →
run `python -m mantle teach` (prose mirror: [`documents/FIELD_GUIDE.md`](documents/FIELD_GUIDE.md)) →
the reference shelf ([`documents/ARCHITECTURE.md`](documents/ARCHITECTURE.md),
[`documents/REPRODUCTION.md`](documents/REPRODUCTION.md),
[`documents/guides/`](documents/guides/)).
Prefer pictures? [`documents/guides/Visual_Guide.md`](documents/guides/Visual_Guide.md).
When prose and code disagree, **the working code in `src/mantle/` is ground truth** (and
`examples/vcw/vcw_cube.py` is the standalone, normative definition of the cube format).

## Design principles (binding)

Body before brain · Reflex before reasoning · Append before overwrite · Veil before
exposure · Immune event before silent failure · Audit before fusion · Capability before
action · Provenance before trust · **Metabolism before rebirth** · Harmony before cleverness ·
**Vessel before voyage · Containment before reach.**

## Two build paths

- **Path A — grow from scratch.** [`documents/ARCHITECTURE.md`](documents/ARCHITECTURE.md)
  (the Phase-1 build path), then the Stage-1 gate, then Phase 2. The `src/mantle/`
  package is the runnable skeleton.
- **Path B — assimilate existing code** (any language, including apps that already have agents).
  Canonical doctrine:
  [`documents/grimoire/The Grimoire.md`](documents/grimoire/The%20Grimoire.md)
  (`NECROMANCY` §7.5/§9.2, residency, and the assimilation hard fails §7.8); runnable cheatsheet:
  [`documents/guides/Assimilation_Guide.md`](documents/guides/Assimilation_Guide.md). Dissect read-only, map organs,
  sign the inventory, wrap fail-open. Both paths converge on the same certified Body and the same
  MIND fusion.

## Verify everything with one command

```bash
python -m mantle check          # every gate, proof, demo, and test — the CI sequence, local
python -m mantle check --fast   # gates + proofs only (skips the narrated demos)
```

## Status & license

An open demonstration of an alternative coding structure — study it, critique it, build
on it ([`CONTRIBUTING.md`](CONTRIBUTING.md)). Released under the [MIT License](LICENSE).
The pre-1.0 edition (previously archived in-tree under `legacy/`) lives in git history at
commit [`2c857a8`](https://github.com/jodydugas-ctrl/mantle-os/tree/2c857a8/legacy).
