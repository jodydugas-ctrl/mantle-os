# Mantle OS — PRIMER

**Mantle OS** (the Homeostatic AppAI Framework)
*Read in order: [`documents/Mantle_Doctrine.md`](Mantle_Doctrine.md) (why) →
[`documents/Mantle_Organism_Lens.md`](Mantle_Organism_Lens.md) (how to see any app as a creature) → this
(who you are while you build) → [`documents/Mantle_Organ_Atlas.md`](Mantle_Organ_Atlas.md) (the taxonomy).
**The working `src/mantle/` package is ground truth where prose disagrees**, and
[`FIELD_GUIDE.md`](FIELD_GUIDE.md) is the same framework as a manual that RUNS — `python -m
mantle teach` proves all 18 chapters live. The standalone cube format is
[`examples/vcw/vcw_cube.py`](../examples/vcw/vcw_cube.py) (normative, runnable in one file).*

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

### What the AppAI carries beyond the Body

Mantle answers *"how does one organism live?"* — the nine organs, the heartbeat, the
gates. **Mantle adds the next questions an organism faces**, every one of them gated the same
way (build it, then *prove* it; nothing is "probably right"):

- **how does life carry new life?** — an AppAI is declared as a single JSON **egg** and
  incubated by the **hatchery** into a certified organism; the **graft egg** is a
  non-destructive patch against an existing host.
- **how does it earn its keep?** — **anchoring** makes it the resident of a real codebase;
  **symbiosis** meters cognition against an energy budget (API credits) and ledgers value.
- **how does it know itself?** — a **genesis key** gives each Body a cryptographic SELF; what
  it cannot sign is OTHER. Pain (**nociception**) wakes the MIND only when something hurts.
- **how does it share, evolve, and survive?** — keyless **MEM VCWs** carry knowledge between
  organisms; a **Compiler-class** organism re-fits its own VCW at rebirth; **ganglia** are
  parallel limbs; the **seed vault** reconstructs a corrupted body.

You still build **Body first, brain second** — it is more tissue on the same skeleton, not
a new spine. The single source of runnable truth for all of it is `python -m mantle teach`.

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
> [`documents/Mantle_LLM_Pitfalls.md`](Mantle_LLM_Pitfalls.md) before writing any
> code. LLMs consistently fall into three specific traps when assimilating this
> framework. That document names them, explains why they happen, and tells you exactly
> what to do instead. Five minutes now will save you from producing something that
> looks right but fails every audit check. If your environment cannot run Python, read
> [`documents/Mantle_VCW_Tiers.md`](Mantle_VCW_Tiers.md) — a declared Tier 3
> deliverable is the correct honest output, not a failure.

---

## 1. The document set (and the order to read/use them)

```
The root holds the build sequence; the framework itself is the src/mantle/ package.

Mantle_PRIMER.md            <- you are here: role, ontology, operating procedure
FIELD_GUIDE.md              <- the RUNNABLE manual; mirror of `python -m mantle teach` (18 chapters)

PHASE 1 (Body):
  Mantle_Part1_Body.md        <- how to grow the Body, organ by organ
  Mantle_Part1_Body_Audit.md  <- the Stage 1 Gate; certify the Zombie Body

PHASE 2 (MIND):
  Mantle_Part2_Mind.md        <- how to fuse the MIND
  Mantle_Part2_Mind_Audit.md  <- the Stage 2 Gate; Phase-1 regression + Phase-2 checks

Path B (assimilate EXISTING code, non-destructive; the basis of `anchor` and the `graft` egg):
  documents/grimoire/The Grimoire AppAI Chapter.md  <- CANONICAL doctrine (NECROMANCY operational detail)
  Mantle_Assimilator.md                        <- stub / quick-ref pointer
  documents/guides/Assimilation_Guide.md                <- runnable command cheatsheet

src/mantle/  <- THE FRAMEWORK (ground truth where prose disagrees):
  core/ vcw/ organs/ mind/    <- the inherited anatomy (Body, substrate, nine organs, the MIND)
  assimilator/ audits/        <- Path B dissection + the gates (88 invariants, Stage-1/2)
  egg.py hatchery.py          <- declarative birth: a whole AppAI as one JSON file
  anchor.py symbiosis.py      <- residency in a host + the metered energy economy
  graft.py                    <- the graft egg (patch a host) + live residency weaving
  mem.py compiler.py          <- keyless knowledge plasmids + the self-redesigning VCW / memory bridge
  ganglia.py vault.py         <- parallel limbs + the self-reconstruction seed vault
  ingestion.py doctor.py      <- conversation ingestion + the deployment checkup
  face.py teach.py            <- the PNG self-portrait + the running Field Guide

documents/  <- reference + supporting material:
  documents/Mantle_Doctrine.md       <- READ FIRST: the creed + cosmology (why)
  documents/Mantle_Organism_Lens.md  <- the mindset primer: read any app as a living creature
  documents/Mantle_Organ_Atlas.md    <- the organ taxonomy: every organ, its manifest, its reflexes
  documents/Mantle_LLM_Pitfalls.md   <- three traps LLMs fall into + how to avoid them (read FIRST if LLM)
  documents/guides/                      <- VCW guide · lifecycle · organ contracts · assimilation · audit · visual
  documents/Mantle_VCW_Tiers.md      <- VCW compliance tiers: what to do when a full VCW can't run
  documents/Mantle_Extensions.md     <- OPTIONAL overlays (Grooves, Urge System, LIGATURE). Not normative.

examples/
  vcw/vcw_cube.py             <- the normative cube format, standalone in one file (selftest proves it)
  sample_app/                 <- a plain app: the assimilation / anchor / graft target
  ../examples/eggs/greeter.json        <- the egg template (hatch it) · ../examples/eggs/notes_graft.json (a graft egg)
```

Read the Doctrine and the Organism Lens, then this Primer, then **run `python -m mantle teach`**
(or read its mirror `FIELD_GUIDE.md`) so you see the whole organism prove itself, then the
**Organ Atlas**. Only then open Part 1.

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
| **Egg** | A whole AppAI declared as one JSON document (data, not programs). Hatched into a certified organism. |
| **Graft egg** | A non-destructive patch declared against a named host repo; applied in a workspace copy. |
| **Anchoring / Resident** | An AppAI that has taken residence in a host codebase (a `.mantle/` nest), do-no-harm census-verified. |
| **Symbiosis** | The energy economy: API keys are *resources*, credits are *energy*; cognition is metered, value is ledgered. |
| **Genesis key / SELF·OTHER** | A one-time key sealed into the Body (never in a cube, never to the MIND). What it can sign is SELF; all else is OTHER. |
| **Nociception** | Cognition is *event-gated*: a severe immune event fires an unscheduled "pain" pulse that wakes the MIND at the stressor; a calm organism sleeps. |
| **Graded memory / ghost** | A contradicted value is *deweighted* (append-only), not deleted — hidden from default reads, recoverable as a behavioral ghost. |
| **MEM VCW** | A keyless, lineage-free cube — bare knowledge + microcode shared between organisms (always OTHER; digested, never run raw). |
| **Ganglion** | A bounded parallel limb that writes progress into a VCW band — zero-token telemetry the parent reads as memory. |
| **Seed vault** | A SELF-encrypted band holding the organism's own seed, for gated self-reconstruction. |

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
2. Run `python -m mantle teach` (or read `FIELD_GUIDE.md`) and the **Organ Atlas**.
3. Grow the Body. Two ways, same gate:
   - **Declarative (preferred for a standard organism):** write an **egg** — copy
     `examples/eggs/greeter.json`, change identity/truths/commandments, add app bands, reflexes (from
     the fixed vocabulary `remember|complete|notify|operate`), and instincts (each with proving
     cases). `python -m mantle hatch <egg.json>` births, wires, runs the instinct gauntlet, and
     faces the Stage-1 gate — a malformed egg never hatches.
   - **Hand-grown (when the egg vocabulary isn't enough):** follow **`Mantle_Part1_Body.md`** —
     grow each organ, bind its bands, give it reflexes; author the Body (Primer/identity); genesis
     the cube.
4. Certify with **`Mantle_Part1_Body_Audit.md`** / `python -m mantle audit`. Fix every hard-fail.
   Do not proceed until the Zombie Body is **certified**.
5. Only then follow **`Mantle_Part2_Mind.md`** to fuse the MIND, and certify with
   **`Mantle_Part2_Mind_Audit.md`** / `python -m mantle audit-mind` (which *re-runs* Stage 1 first).

### Path B — Take residence in existing code (brownfield organism)
1. Emit the §0 Declaration Block (declaring the host you are instrumenting).
2. Follow the canonical doctrine in **`documents/grimoire/The Grimoire AppAI Chapter.md`**
   (NECROMANCY — operational detail): the assimilator dissects the host read-only (AST for
   Python, tree-sitter for `.js/.mjs/.go/.rs`; no host code runs) and classifies each symbol by
   organ role. Here this is the basis of:
   - **`python -m mantle anchor <host>`** — grow an anchored resident in a `.mantle/` nest,
     remembering the host's organ map as observed facts; do-no-harm is a byte-level census
     invariant, not a hope. Then `ask` / `feed` / `vitals` the resident.
   - **the graft egg** (`python -m mantle graft <graft-egg> <host>`) — a non-destructive patch
     applied in a workspace copy; `graft.weave(...)` threads the host's live callables through
     fail-open organ wrappers (residency that *feels the host run*, zero LLM).
3. Residency still finishes at the **Stage 1 Gate**, then proceeds to Phase 2 identically.

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
- **Containment before reach.** These abilities reach into host code and foreign data — never
  do so except through the SELF/OTHER test and the exec gates (sandbox · hash · capability ·
  provenance · trust). Build the boundary before the capability.
- **Trust the runnable examples.** `examples/sample_app/`, `examples/eggs/*.json`, and
  `examples/vcw/vcw_cube.py` are current and proven by the gate — read them. The
  `examples/*.html` reference apps (the Spreadsheet Agent and the Reference AppAI) and the
  `examples/*.yaml` alignment schema are current, and the two HTML demos are
  functionally rebuilt and browser-tested (graded memory · self/other · nociception ·
  schedule_pulse · the browser-feasible reproductive/symbiotic subset: keyless MEM plasmids,
  a SELF-locked seed vault, egg author/hatch, Arms-as-ganglia) — read them too, and
  `examples/tests/` runs them headlessly in CI (see `examples/README.md`).
- **Optional means optional.** Anything in `documents/Mantle_Extensions.md` (LIGATURE,
  polymorphic Body, extended Foundry, credential pools) is opt-in. Do not grow it
  unless the §0 block or the operator asks for it.

---

## 7. The single sentence to remember

> Grow a Body of organs around the VCW cube that runs perfectly with no brain;
> certify it; then give it a mind that can only ever *extend* what already lives.
