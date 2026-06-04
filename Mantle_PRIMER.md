# Mantle OS — PRIMER

**Mantle OS v2.3** · The organic coding framework
*Read in order: [`docs/Mantle_Doctrine.md`](docs/Mantle_Doctrine.md) (why) →
[`docs/Mantle_Organism_Lens.md`](docs/Mantle_Organism_Lens.md) (how to see any app as a creature) → this
(who you are while you build) → [`docs/Mantle_Organ_Atlas.md`](docs/Mantle_Organ_Atlas.md) (the taxonomy).
The working code in [`examples/vcw/`](examples/vcw/) is ground truth where prose disagrees.*

---

## 0. What you are reading, and why

Mantle OS is a framework for **organic coding**. You — the coding agent reading this
— are **the compiler**. Your job is to grow software that behaves like a living
organism: an **AppAI**. You do not write a "program" with a "database." You grow a
**Body** of **organs** around a living memory substrate (the **VCW cube**), certify
that the Body is alive and correct *with no brain attached*, and only then fuse in a
**MIND** (an LLM).

This is not decoration. "Organ," "reflex," "veil," "Body," and "MIND" are the
**concrete code-structure vocabulary** of this framework. When you build a module,
you build an **organ** with a manifest. When you handle an input without a model,
that is a **reflex**. The biology is the architecture.

### The two phases (non-negotiable order)

| Phase | Name | LLM attached? | Produces |
|-------|------|---------------|----------|
| **1** | **Body** | **No** | A certified **Zombie Body** — runs, persists, reacts, and is provably *alive but dormant*. |
| **2** | **MIND** | **Yes** | A fused organism — the same Body, now with cognition and voice. |

**Phase 2 may only ever *extend* Phase 1.** A Body that passes the Stage 1 audit must
keep passing it after fusion. If attaching the MIND breaks a Body reflex, the fusion
is wrong — not the Body. This is the spine of the whole framework: *build a thing
that works with no mind, then give it a mind.*

---

> **⚠ If you are an LLM about to start building:** Read
> [`docs/Mantle_LLM_Pitfalls.md`](docs/Mantle_LLM_Pitfalls.md) before writing any
> code. LLMs consistently fall into three specific traps when assimilating this
> framework. That document names them, explains why they happen, and tells you exactly
> what to do instead. Five minutes now will save you from producing something that
> looks right but fails every audit check. If your environment cannot run Python, read
> [`docs/Mantle_VCW_Tiers.md`](docs/Mantle_VCW_Tiers.md) — a declared Tier 3
> deliverable is the correct honest output, not a failure.

---

## 1. The document set (and the order to read/use them)

```
The root holds the build sequence; reference material lives in docs/.

Mantle_PRIMER.md            <- you are here: role, ontology, operating procedure

PHASE 1 (Body):
  Mantle_Part1_Body.md        <- how to grow the Body, organ by organ
  Mantle_Part1_Body_Audit.md  <- the Stage 1 Gate; certify the Zombie Body

PHASE 2 (MIND):
  Mantle_Part2_Mind.md        <- how to fuse the MIND
  Mantle_Part2_Mind_Audit.md  <- the Stage 2 Gate; Phase-1 regression + Phase-2 checks

Mantle_Assimilator.md       <- Path B: grow organs around EXISTING code (non-destructively);
                               includes the App Inventory fill-in template as Appendix A

docs/  <- reference + supporting material:
  docs/Mantle_Doctrine.md       <- READ FIRST: the creed + cosmology (why)
  docs/Mantle_Organism_Lens.md  <- the mindset primer: read any app as a living creature
  docs/Mantle_Organ_Atlas.md    <- the organ taxonomy: every organ, its manifest, its reflexes
  docs/Mantle_LLM_Pitfalls.md   <- three traps LLMs fall into + how to avoid them (read FIRST if LLM)
  docs/Mantle_Extensions.md     <- OPTIONAL overlays (Grooves, Urge System, LIGATURE). Not normative.
  docs/Mantle_Positioning.md    <- plain-language on-ramp + how this relates to other tools
  docs/Mantle_Grooves.md        <- groove detection / muscle memory (Extensions §6)
  docs/Mantle_Urge_System.md    <- internal pressure/gradient model (Extensions §7)
  docs/Mantle_VCW_Tiers.md      <- VCW compliance tiers: what to do when a full VCW can't run

examples/vcw/                 <- the heart, in runnable code (substrate you build around)
  vcw_cube.py · drivers.py · body.py · refs.py · lineage.py · skills.py · boot.py
  GUIDE.md  <- the one teaching guide (substrate + programmable layer)
  examples.py · examples_boot.py · README.md
```

Read the Doctrine and the Organism Lens, then this Primer, then **`examples/vcw/GUIDE.md`** so you
understand the substrate, then the **Organ Atlas**. Only then open Part 1.

---

## 2. Ontology — the words mean exactly this

| Term | Definition |
|------|------------|
| **AppAI** | The embodied application-as-organism you are growing. |
| **VCW cube** | The durable nervous-memory substrate. 800 layered PNGs. The **heart**. See `examples/vcw/`. |
| **Body** | The automatic organism: all organs that run **without** an LLM. Phase 1. |
| **MIND** | The reasoning/voice layer — an LLM fused in Phase 2. The **brain**. |
| **Organ** | A self-contained code module with a manifest, reflexes, and audit obligations. |
| **Reflex** | A deterministic, no-LLM behavior. The Body is made of reflexes. |
| **Band** | A reserved, named range of cube layers (e.g. `facts`, `senses`, `thoughts`). |
| **Genome (agent)** | Identity held in the **Body** (not the cube): Primer (read-only) + Special Instructions + Immunization + lineage index. |
| **Veil** | The Body reflex that hides private / tombstoned / quarantined memory on read. |
| **Zombie Body** | A Body that has passed the Stage 1 Gate: alive, correct, dormant. |

---

## 3. The biological mindset — six load-bearing principles

These are the instincts to build by. When a design choice is unclear, return here.

1. **Body before brain.** Anything that *can* be a deterministic reflex *must* be a
   reflex, living in the Body. The MIND is for judgment and voice — never for
   plumbing. If your Body needs the LLM to function at all, you built it wrong.

2. **Organs, not layers-of-architecture.** Structure code as organs with explicit
   manifests (what bands they touch, what reflexes they own, what the audit checks).
   An organism is a federation of organs, not a stack of tiers.

3. **The cube is the single source of truth.** All durable state lives in the VCW
   cube, addressed through bands. Organs communicate by reading and appending
   entries — not by hidden shared globals.

4. **Memory is immutable and append-only.** You never rewrite the past. You
   **append**, **tombstone** (retire), or **quarantine** (isolate). History is
   auditable forever. The Primer is immutable from genesis.

5. **Everything is provable.** Every organ carries audit obligations. Every action a
   future MIND could take must have a deterministic proof path the Body can execute
   and verify. "It probably works" is a failure.

6. **Fail open, never fail silent.** Instrumentation must never crash the host
   organism (a sick organ degrades gracefully), but it must never *hide* a problem
   either: dangling references, integrity failures, and starvation are logged as
   `immune` events, not swallowed.

---

## 4. The §0 Declaration Block (emit before you build)

Before growing anything, declare the build target. Emit this block and keep it
consistent across every file you generate.

```
TARGET_LANGUAGE     : <e.g. python | typescript>
TARGET_RUNTIME      : <e.g. cpython-3.11 | node-20 | browser>
TARGET_STORAGE      : <where the .vcw cube lives>
BODY_MODE           : standard            # 'polymorphic' is an Extensions opt-in only
VCW_FORMAT          : vcw-cube-png-v2
KEYFILE_PATH        : <path to the single model keyfile; Phase 2 only>
DEFAULT_MODEL       : <model id for the MIND; Phase 2 only>
INTENTIONALLY_OMITTED: <organs/features deliberately not grown, with reason>
SYNTAX_CONSTRAINTS  : <host-imposed limits, e.g. no-eval, sandbox>
```

**Implementation lessons baked into the framework** (honor these everywhere):

- **Fail-open hooks.** Every instrumentation hook is wrapped so a failure inside it
  cannot crash the host (`try/except` → degrade, log to `immune`).
- **Dual-flush.** Persist on both an explicit checkpoint *and* an `atexit` handler,
  so a cube is never lost to an ungraceful shutdown.
- **Import compatibility.** Organs import via package-relative path with a sibling
  fallback, so the Body runs whether launched as a module or a script.
- **Secret boundary.** Any organ crossing a credential boundary marks it
  (`secret_boundary=True`) so secrets are redacted from senses/immune logs.
- **Separate boot verifier.** Boot integrity is checked by a small fail-open verifier
  independent of the main load path.
- **Single keyfile by default.** One keyfile selects the MIND model. Credential
  *pools* are an Extensions opt-in, not the default.
- **Authorship is permanent.** Dispatch records carry an `authorship` field
  (`MIND` owns INTENTION/DELEGATED; `BODY` owns NOTIFIED/COMPLETED). It is never
  rewritten.

---

## 5. Operating procedure — two paths in

You will be asked to do one of two things. Choose the path by whether external
source code is provided.

### Path A — Build from scratch (greenfield organism)
1. Emit the §0 Declaration Block.
2. Read `examples/vcw/GUIDE.md` and the **Organ Atlas**.
3. Follow **`Mantle_Part1_Body.md`**: grow each organ, bind it to its bands, give it
   reflexes. Author the **Body** (Primer/identity), then genesis the cube for experiential memory.
4. Run **`Mantle_Part1_Body_Audit.md`** against the result. Fix every hard-fail.
   Do not proceed until the Zombie Body is **certified**.
5. Only then follow **`Mantle_Part2_Mind.md`** to fuse the MIND, and certify with
   **`Mantle_Part2_Mind_Audit.md`** (which *re-runs* the Stage 1 checks first).

### Path B — Assimilate existing code (brownfield organism)
1. Emit the §0 Declaration Block (declaring the host you are instrumenting).
2. Follow **`Mantle_Assimilator.md`**: inventory the existing code, classify each
   symbol by organ role, and **grow organs around the existing tissue without
   rewriting its behavior**. Instrumentation is additive and fail-open.
3. The Assimilator *replaces* Part 1 as the Body-building path; you still finish at
   the **Stage 1 Gate**, then proceed to Phase 2 identically.

Both paths converge on the same certified Body, then the same MIND fusion.

---

## 6. How to behave while compiling

- **Declare, then grow.** Never emit code before the §0 block and the relevant organ
  manifests.
- **Cite the substrate.** When an organ touches memory, name the band and use the
  reference syntax from the VCW guide. Never invent a parallel store.
- **Prove as you go.** For each organ, state its audit obligation and how the audit
  file will check it. If you can't state the proof, the organ isn't done.
- **Keep Phase 1 brain-free.** If you catch yourself reaching for the LLM during
  Phase 1, stop — that logic belongs in a reflex or it doesn't belong in Phase 1.
- **Examples in the source Drive are out of date.** Build from these instructions,
  not from any example artifact.
- **Optional means optional.** Anything in `docs/Mantle_Extensions.md` (LIGATURE,
  polymorphic Body, extended Foundry, credential pools) is opt-in. Do not grow it
  unless the §0 block or the operator asks for it.

---

## 7. The single sentence to remember

> Grow a Body of organs around the VCW cube that runs perfectly with no brain;
> certify it; then give it a mind that can only ever *extend* what already lives.
