# Mantle OS — PART 1: THE BODY

**Mantle OS** · Phase 1 — grow a certified Zombie Body (no brain attached)
*Prerequisites: read `documents/Mantle_Doctrine.md`, `documents/Mantle_Organism_Lens.md`, `Mantle_PRIMER.md`,
run `python -m mantle teach` (or read `FIELD_GUIDE.md`), and read `documents/Mantle_Organ_Atlas.md`. This
document tells you HOW to grow the Body, organ by organ; the working `src/mantle/` package is ground
truth. When you finish, certify with `Mantle_Part1_Body_Audit.md` (`python -m mantle audit` runs it).
The fastest Phase-1 build is a declarative **egg** (`examples/eggs/greeter.json` → `python -m mantle hatch`);
this document is the organ-by-organ path when the egg vocabulary is not enough.*

---

## §1.0 The goal of Phase 1

Grow an organism that **runs, persists, perceives, defends itself, and acts — with no
LLM anywhere in the loop.** The product is a **Zombie Body**: provably alive (it has a
heartbeat, memory, senses, reflexes, and a mapped surface) but dormant (no cognition,
no voice). If any behavior in Phase 1 depends on a model, the design is wrong — push
that logic into a reflex or defer it to a Phase-2 extension.

The armory band (groove storage — see `documents/Mantle_Extensions.md` §6) is **not grown in
Phase 1**. If declared in §0, reserve the band address at genesis but leave it empty.
Grooves are a Phase-2 / Extensions capability; the Zombie Body does not calcify or
execute grooves.

You will build in this order. Each section ends with the **audit hooks** that
`Mantle_Part1_Body_Audit.md` checks. Build to the hooks.

```
§1.1  Declaration & genesis
§1.2  Heart            (clock, heartbeat, circulation)
§1.3  Genome           (body entries, identity)
§1.4  Nervous System   (references, Context Assembly)
§1.5  Memory organs    (identity/facts/events/discoveries + metabolism)
§1.6  Senses           (intake + classifier + Human Surface Map — afferent I/O)
§1.7  Immune System    (audit, tombstone, quarantine)
§1.8  Memory metabolism (flush, allocation, compaction, reclaim)
§1.9  Surface Parity   (Senses perceive / Limbs operate the I/O surface)
§1.10 Limbs/Arms       (effectors, dispatch lifecycle, surface actuation — Body-owned states)
§1.11 Brain stub       (dormant bands, no writer)
§1.12 Boot, dual-flush, fail-open
§1.13 Zombie certification
```

---

## §1.1 Declaration & genesis

1. Emit the **§0 Declaration Block** (PRIMER §4). Fix `BODY_MODE: standard` unless the
   operator opted into `polymorphic` (Extensions). Set `VCW_BACKEND: file` (or omit —
   `file` is the default). If your environment cannot create a file-backed cube, declare
   `VCW_BACKEND: schema-only` now, before writing any implementation code, and produce
   a Tier 3 blueprint deliverable instead of a running system. See
   `documents/Mantle_VCW_Tiers.md` for the full tier model.
2. **Birth the Body & design the cube genome.** Identity lives in the Body, the band layout in
   the cube boot sector:
   - `Body.birth(identity, truths, commandments)` sets the read-only Primer, seeds
     Immunization, and **mints the one-time genesis key** (the cryptographic SELF — see §1.3)
     (`src/mantle/core/body.py`). This is the **agent genome** — never written to the cube.
   - Author the **cube genome**: the band layout, each band declaring an `encoding` (driver), a
     **`span`** of reserved layers, and a **`purpose`** to fit the app. Layers are allocated **on
     demand** within the span and **reclaimed** after compaction — give high-churn bands more
     span. Longevity is a property of this design.
   - `Cube.genesis(genome)` + `Organism.save(dir)` performs the staged commit. The AppAI is
     **born** once the Body holds a Primer.
3. Confirm the band map matches the canonical layout (`src/mantle/vcw/bands.py::standard_genome`). Never
   invent a parallel store outside the cube.

**Audit hooks:** B-01 cube genesis valid; B-02 Primer present, immutable & Body-resident; B-03
band map matches the canonical ranges.

---

## §1.2 Heart — clock, heartbeat, circulation

Grow the Heart first; every other organ's reflexes are driven by its pulse.

- **Clock / `tick`:** a monotonic time source the whole Body shares. No wall-clock
  assumptions baked into reflexes.
- **Heartbeat loop:** a deterministic loop that, each pulse, lets due organs run their
  reflexes (immune scan, metabolism check, sense draining, circulation flush).
- **`circulate`:** flush dirty bands to disk via the cube's **staged commit**. Honor
  **dual-flush**: persist on an explicit checkpoint *and* via an `atexit` handler.
- **`pulse-check`:** if a heartbeat is missed/stalled, append an `immune` event. Never
  swallow a stall.

**Audit hooks:** B-04 heartbeat runs with no LLM; B-05 dual-flush persists on both
checkpoint and `atexit`; B-06 a missed pulse is logged to `immune`.

---

## §1.3 Genome — identity in the BODY

The Genome (who the AppAI is) lives in the **Body store** (`src/mantle/core/body.py`), **not** in the cube.
The cube is pure experiential memory. Design the *cube* genome (band layout) separately in §1.1
— each band declaring a **`span`** of reserved layers and a **`purpose`**.

- Write the **Primer** (identity + Commandments) at birth only; thereafter `seal-primer` rejects
  any write (`Body.birth` once; re-write raises `PermissionError`). The Primer is read-only.
- Populate **Immunization** (the safety invariants, seeded with the Commandments) and, if the
  operator supplies them, **Special Instructions** (the MIND guides, the Body applies).
- The **lineage index** records this as generation 0; Inheritance is written only on a later
  rebirth.
- The model **boot order** is fixed: **Primer + Special Instructions + Immunization**. A
  violation of this assembly order is a hard fail (HF-B01).
- **The genesis key (cryptographic SELF).** `Body.birth` mints a one-time key
  (`secrets.token_hex`) — generated once, known only to this Body. It is **never in any cube and
  never in `boot_order`/the MIND's snapshot** (the MIND cannot leak what it does not know).
  `body.sign`/`verify` (HMAC) and `seal_bytes`/`open_bytes` (the seed vault) ride on it: what the
  Body can sign is **SELF**, everything else is **OTHER**. This is the containment that earns
  Mantle's reach into host code. Proven by `SELF-1..4`.

**Audit hooks:** B-07 Primer immutable post-birth & Body-resident (not in the cube); B-08 boot
order correct; B-09 no MIND write path to the Genome exists; **SELF-1 the genesis key is minted
once and is absent from boot_order, the snapshot, and every cube band.**

---

## §1.4 Nervous System — references & Context Assembly

- **Reference resolver:** one grammar addresses everything the organism can remember
  (`src/mantle/core/refs.py`): **`<TARGET.SELECTOR.ADDRESS>`** — e.g. `<facts.11>` (Prime, facts
  band, visible entry 11), `<gen2.boot.23x33>` (generation 2, that layer, pixel 23,33),
  `<body.immune.11>` (the Body's immunization store, entry 11). TARGET defaults to the current
  Prime cube when omitted. A reference that resolves to nothing is a **dangling reference** →
  append an `immune` event. Never silently drop it.
- **9-step Context Assembly Protocol** — deterministic, no LLM. Each pulse (or on
  demand) assemble a fully-materialized snapshot:
  1. Load Genome (fixed order).
  2. Resolve `prime` index/pointers.
  3. Gather `identity`.
  4. Gather `facts` (visible, through the veil).
  5. Gather recent `events`.
  6. Gather `discoveries`.
  7. Drain & include classified `senses`.
  8. Resolve every reference encountered (no danglers reach output).
  9. Emit a single resolved snapshot object — **no unresolved reference remains.**
- This snapshot is exactly what a future MIND will receive. In Phase 1 it feeds Body
  reflexes and the audit.

**Audit hooks:** B-10 Context Assembly is deterministic & LLM-free; B-11 output
contains zero unresolved references; B-12 every dangling reference is an `immune` event.

---

## §1.5 Memory organs — identity / facts / events / discoveries

- All durable knowledge is **append-only, immutable, hashed** entries (`make_entry`).
- `remember`: append to the correct band. `recall`: read through the veil.
- `summarize`: deterministic roll-ups into `identity` / `discoveries` — **no LLM**
  (e.g. counts, latest-value tables, dedup). If a summary needs judgment, defer it as a
  Phase-2 extension; do not fake it with a model in Phase 1.
- Never rewrite history. Corrections are new entries plus a `tombstone` on the old one.
- **Graded memory.** Between "remembered" and "retired" there is a middle ground:
  `memory.deweight(band, id, weight=0.0)` lowers an entry's weight via an **append-only DEWEIGHT
  event** — never mutating the original. A contradicted value becomes a **behavioral ghost**:
  hidden from default `recall` (which is weight-ordered), still physically present, recoverable
  via `memory.recall_ghosts(band)`. Belief history is preserved; nothing is overwritten. Proven
  by `MEMW-1..3`.

**Audit hooks:** B-13 entries immutable & hashed; B-14 reads honor the veil; B-15 no
organ rewrites a committed entry; **MEMW-1 a deweighted entry is hidden yet recoverable and the
original is never mutated.**

---

## §1.6 Senses — intake & classifier

- Ingest every external signal through the Senses boundary (`inhale`) into the `senses` band.
- **Classifier** (scripted, no LLM): tag each signal `REFLEX | ROUTINE | SIGNIFICANT`
  using the **compound key** `(action_id, event_type)`. Exactly one `senses` entry per
  signal.
- **REFLEX** signals trigger their bound Body response immediately and must **not**
  touch the `brain` band.
- **SIGNIFICANT** signals are marked for the (future) MIND; in Phase 1 they are simply
  recorded.

**Audit hooks:** B-16 classifier deterministic & LLM-free; B-17 one entry per signal;
B-18 REFLEX handled without touching `brain`.

---

## §1.7 Immune System — audit, tombstone, quarantine

- `scan`: each heartbeat, run `cube.verify()` plus dangling-reference and
  secret-boundary checks; append findings to `immune`.
- `tombstone`: retire an obsolete entry (hidden on read, kept for audit).
- `quarantine`: isolate a suspect entry (corruption / untrusted source) until cleared.
- `redact`: at any `secret_boundary=True` crossing, strip secrets from senses/immune
  logs before they are written.
- **SELF / OTHER.** `immune.is_self(data, mac)` verifies an artifact against the Body's
  genesis key; `immune.reject_foreign(...)` records OTHER as a `foreign_rejected` event. This is
  the recognition boundary that bounds an organism's reach to its own anatomy.
- **Nociception.** A *severe* immune event (an `AUTONOMIC_KINDS` member: integrity,
  organ_overreach, foreign_rejected, …) emits a `distress` signal carrying the pain coordinates
  `{reason, band, ref}`. In Phase 1 there is no MIND to wake, but the Heart turns distress into an
  unscheduled pulse; in Phase 2 that pulse is what *event-gates* cognition (Part 2). Proven by
  `SELF-2`, `NOC-2`.

**Audit hooks:** B-19 integrity scan each heartbeat; B-20 secrets never appear in
logs; B-21 tombstoned/quarantined entries hidden from normal reads; **SELF-2 OTHER artifacts are
rejected; NOC-2 a severe fault fires exactly one unscheduled pulse anchored to the stressor.**

---

## §1.8 Memory: Metabolism — flush, allocation, reclaim

*Metabolism is a function of the **Memory** organ (the former "Liver" is not a separate organ —
memory housekeeping belongs to the organ that owns the bands).*

- `flush`: keep the hot working set in RAM and **flush** it to the physical Prime cube
  periodically (write-back cache + **dual-flush** on checkpoint + `atexit` + delta compression).
  This is the only "hot/cold" — NOT inter-cube tiering.
- `allocate`: grow a band onto the next layer in its reserved span only when the tail fills —
  preferring a freed layer from the band's **reuse pool** before a fresh one.
- `compact`: drop tombstoned entries; an emptied layer returns to the reuse pool. Safe-reuse:
  only entry-addressed layers are reclaimed; spatial/exec layers are never recycled.
- `overflow`: near a band's layer/range capacity (**0.75**) compact; **emergency** at **0.90**.
- **Capacity ≠ rebirth** (HF-B14). Filling up triggers metabolism; rebirth is MIND-chosen and
  never silent or lossy.

**Audit hooks:** B-22 overflow at 0.75 / emergency at 0.90; B-23 capacity never
triggers rebirth; B-24 compaction preserves visible history.

---

## §1.9 Surface Parity — Senses (perceive) & Limbs (operate)

The I/O surface is *not* a separate organ. It is split by direction of flow: **Senses** perceive
the surface (afferent), **Limbs** operate it (efferent). **Surface Parity** means: every affordance
a human can use, a future MIND can also drive — with proof — *and you prove it now, in Phase 1,
with no MIND.* This is the most often shortchanged work; do it thoroughly.

- **Human Surface Map (Senses):** enumerate every human-visible control/affordance (buttons,
  fields, commands, screens). Each gets an id and a band-recorded descriptor. *Perceiving what
  controls exist is afferent — it is the Senses organ.*
- **ControlBridge (Limbs):** for each mapped control, a Body-callable path that **operates** it.
- **App-Face Bridge (Limbs):** render the app's visible face **declaratively** (a drawing
  bridge), never by ad-hoc raw DOM/host mutation.
- **Action Execution Proof (Limbs):** every effector use records
  `{attempted, ok, method, ref, reason}` to the `brain`/`immune` bands.
- `inhale` (Senses) / `exhale` (Limbs): all external input enters through Senses (→ `senses`) and
  all output leaves through the Limbs' bridges, so nothing bypasses the nervous system.

**Audit hooks:** B-25 every human control is in the Surface Map (Senses coverage); B-26 each has a
working ControlBridge path with a recorded proof (Limbs); B-27 graphical faces use the declarative
App-Face Bridge, not raw host mutation (Limbs); B-28 all I/O flows through Senses (in) / Limbs (out).

---

## §1.10 Limbs / Arms — effectors & dispatch lifecycle

- Build effectors/tools and the **async limb delegation** mechanism.
- Implement the dispatch lifecycle records in `brain`:
  `INTENTION → DELEGATED → NOTIFIED → COMPLETED`, each with an `authorship` field.
- In Phase 1 the Body owns **NOTIFIED** and **COMPLETED** only. **INTENTION** and
  **DELEGATED** have no author yet (the Brain is dormant). Verify the Body *cannot*
  author INTENTION.
- Every dispatched action carries an Action Execution Proof (Limbs surface actuation, §1.9).

**Audit hooks:** B-29 authorship field present & immutable; B-30 Body never authors
INTENTION; B-31 every dispatch has an Action Execution Proof.

---

## §1.11 Brain stub — dormant, no writer

- The cube already has the `brain` (450–499) and `thoughts` (500–549) bands. In Phase 1
  there is **no writer** for `thoughts` and no INTENTION author for `brain`.
- Confirm the bands exist, are correctly typed (`thoughts` is **private**, veiled), and
  that nothing in the Body writes them as the MIND would.

**Audit hooks:** B-32 `thoughts` band private & veiled; B-33 no Body code writes
`thoughts`; B-34 `brain` INTENTION/DELEGATED unauthored in Phase 1.

---

## §1.12 Boot, dual-flush, fail-open (the survival invariants)

- **Separate boot verifier:** a small, **fail-open** verifier checks cube integrity at
  boot, independent of the main load path. If it finds damage, it logs to `immune` and
  brings up a degraded-but-alive Body — it never hard-crashes the boot.
- **Fail-open hooks:** every instrumentation hook is wrapped so a fault inside it
  degrades + logs, never crashes the host.
- **Dual-flush:** persist on explicit checkpoint *and* `atexit`.
- **Import compatibility:** organs import package-relative with a sibling fallback, so
  the Body runs as a module or a script.

**Audit hooks:** B-35 boot verifier is independent & fail-open; B-36 hooks fail open;
B-37 dual-flush present; B-38 import works as module and as script.

---

## §1.13 Zombie certification

The Body is a **certified Zombie Body** when:

- it boots, beats, persists, perceives, defends, and acts with **no LLM** in any path;
- every organ's manifest is present and its reflexes are deterministic;
- the cube `verify()` is healthy and every audit hook passes;
- **the executable gate is green**: `python -m mantle audit` (the Stage-1 Zombie Body gate) plus
  `python -m mantle prove` (the **88 security invariants**, red/green) — and the three tamper
  proofs (`audit --break-hash/primer/seal`) must each exit non-zero, proving the gate *catches*
  violations. `Mantle_Part1_Body_Audit.md` is the human checklist for the same gate.

**Do not proceed to Phase 2 until certification is complete.** A MIND fused onto an
uncertified Body inherits every latent defect and hides it behind plausible text.

---

## Appendix 1A — Phase-1 hard-fail quick list

These are the conditions that *fail* a Body outright (full list in the Audit):

- **HF-B01** Genome load order violated.
- **HF-B08** an LLM appears anywhere in a Phase-1 path.
- **HF-B09** the Senses classifier calls an LLM.
- **HF-B14** capacity/overflow triggers rebirth.
- **HF-B24** an unresolved reference reaches a reflex output.
- **HF-B32** an instrumentation hook can crash the host (not fail-open).
- **HF-B33** persistence relies on a single flush (no dual-flush).
- **HF-B36** boot verifier shares the main load path / can hard-crash boot.
- **HF-B44** a human-visible control has no ControlBridge path or no proof.
