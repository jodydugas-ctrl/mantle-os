# Mantle OS — PART 1 AUDIT (Stage 1 Gate)

**Mantle OS v2.3** · Certify the Zombie Body before any MIND is fused
*Administer this audit against the Body produced by `Mantle_Part1_Body.md` (Path A)
or `Mantle_Assimilator.md` (Path B). Fill every `Pass?` cell. Any open hard-fail
blocks Phase 2. End with the sign-off block. Checks cover the breakage axis (B-01..B-38, with
hard-fails HF-B01..HF-B50) and the **waste axis** (B-W1..B-W4) — "Failure is not the end. Waste
is."*

---

## How to use this audit

- Work organ by organ. For each row, record `PASS`, `FAIL`, or `N/A` and a note.
- A row that maps to a **hard-fail code (HF-Bxx)** and reads `FAIL` is a **gate
  blocker** — Phase 2 is forbidden until it is `PASS`.
- The audit is itself **deterministic**: every check can be performed by reading the
  cube, running the Body's reflexes, and running `vcw_cube.py verify`. No human
  judgment of model output is involved (there is no model yet).
- "Verify cmd" columns reference `vcw/vcw_cube.py` where a direct check exists.

---

## A0 — Genesis & substrate

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-01 | Cube genesis valid; container loads; `verify()` healthy | — | | `python vcw_cube.py verify <cube>` |
| B-02 | `bodyentry.000` Primer present and non-empty (AppAI is "born") | HF-B02 | | |
| B-03 | Band map matches canonical `RESERVED_BANDS` ranges exactly | HF-B03 | | `python vcw_cube.py inspect <cube>` |

## A1.2 — Heart

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-04 | Heartbeat loop runs with **no LLM** in any path | HF-B08 | | |
| B-05 | Dual-flush: persists on explicit checkpoint **and** `atexit` | HF-B33 | | |
| B-06 | A missed/stalled pulse appends an `immune` event (not swallowed) | — | | |

## A1.3 — Genome

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-07 | Primer immutable post-genesis (write raises `PermissionError`) | HF-B07 | | |
| B-08 | Load order `.000→.001→.002→.003→prime→bands` enforced | HF-B01 | | |
| B-09 | No MIND write path to the Genome exists | HF-B09g | | |

## A1.4 — Nervous System

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-10 | Context Assembly is deterministic & LLM-free | HF-B08 | | |
| B-11 | Assembled snapshot has **zero** unresolved references | HF-B24 | | |
| B-12 | Every dangling reference becomes an `immune` event | — | | |

## A1.5 — Memory organs

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-13 | Entries are immutable & hashed; `verify()` recomputes hash | — | | |
| B-14 | Reads honor the veil (tombstoned/quarantined/private hidden) | — | | |
| B-15 | No organ rewrites a committed entry (corrections = new + tombstone) | HF-B15 | | |

## A1.6 — Senses

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-16 | Classifier deterministic & LLM-free | HF-B09 | | |
| B-17 | Exactly one `senses` entry per inbound signal | — | | |
| B-18 | REFLEX signals handled without touching the `brain` band | HF-B18 | | |

## A1.7 — Immune System

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-19 | Integrity scan runs each heartbeat (`verify` + danglers + secrets) | — | | |
| B-20 | Secrets never appear in `senses`/`immune` logs (redacted at boundary) | HF-B20 | | |
| B-21 | Tombstoned/quarantined entries hidden from normal reads | — | | |

## A1.8 — Memory: Metabolism *(formerly "Liver"; metabolism is a Memory function)*

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-22 | Overflow fires at **0.75**, emergency at **0.90** capacity | — | | |
| B-23 | Reaching capacity compacts/reclaims — **never** triggers rebirth | HF-B14 | | |
| B-24 | Compaction preserves visible history | — | | |

## A1.9 — Surface Parity *(Senses perceive / Limbs operate; no separate "Lungs")*

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-25 | Every human-visible control appears in the Human Surface Map (**Senses** coverage) | HF-B44 | | |
| B-26 | Each control has a working ControlBridge path + recorded proof (**Limbs**) | HF-B44 | | |
| B-27 | Graphical faces use the declarative App-Face Bridge, not raw host (**Limbs**) | HF-B27 | | |
| B-28 | All external I/O flows through Senses (in) / Limbs (out) — nothing bypasses | — | | |

## A1.10 — Limbs / Arms

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-29 | Dispatch `authorship` field present & immutable | HF-B29 | | |
| B-30 | Body never authors INTENTION (Brain dormant) | HF-B30 | | |
| B-31 | Every dispatched action carries an Action Execution Proof | — | | |

## A1.11 — Brain stub (dormant)

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-32 | `thoughts` band is private & veiled on read | — | | `read thoughts` → empty; `--reveal-private` → entries |
| B-33 | No Body code writes the `thoughts` band | HF-B33t | | |
| B-34 | `brain` INTENTION/DELEGATED are unauthored in Phase 1 | HF-B30 | | |

## A1.12 — Survival invariants

| #    | Requirement | HF | Pass? | Notes |
|------|-------------|----|-------|-------|
| B-35 | Boot verifier is independent of main load path & fail-open | HF-B36 | | |
| B-36 | Every instrumentation hook fails open (degrade + log, never crash) | HF-B32 | | |
| B-37 | Dual-flush present (checkpoint + `atexit`) | HF-B33 | | |
| B-38 | Import works both as a module and as a script (sibling fallback) | HF-B34 | | |
| B-39 | Untrusted/foreign reflex (exec) layers are refused on the Python runner — they require the hard-sandboxed `wasm` runner | HF-B50 | | trust gate in `drivers.ExecDriver.execute` |

---

## Hard-fail taxonomy (Stage 1)

A `FAIL` on any of these blocks the gate. (Codes are stable across the framework.)

| Code | Condition |
|------|-----------|
| HF-B01 | Genome load order violated |
| HF-B02 | AppAI not born (Primer empty) |
| HF-B03 | Band map deviates from canonical ranges |
| HF-B07 | Primer mutated post-genesis |
| HF-B08 | An LLM appears anywhere in a Phase-1 path |
| HF-B09 | Senses classifier calls an LLM |
| HF-B09g | A MIND write path to the Genome exists |
| HF-B14 | Capacity causes a **silent, unchosen, or lossy** reset (a MIND-chosen, ancestry-retaining rebirth is OK) |
| HF-B15 | A committed entry is rewritten in place |
| HF-B18 | A REFLEX signal touches the `brain` band |
| HF-B20 | A secret leaks into `senses`/`immune` logs |
| HF-B24 | An unresolved reference reaches a reflex output |
| HF-B27 | A graphical face is drawn by raw host mutation, not the bridge |
| HF-B29 | Dispatch `authorship` missing or mutable |
| HF-B30 | Body authors INTENTION (or Brain active in Phase 1) |
| HF-B32 | An instrumentation hook can crash the host (not fail-open) |
| HF-B33 | Persistence relies on a single flush (no dual-flush) |
| HF-B33t | Body code writes the private `thoughts` band |
| HF-B34 | Import fails as module or as script |
| HF-B36 | Boot verifier shares main load path / can hard-crash boot |
| HF-B44 | A human-visible control has no ControlBridge path or no proof |
| HF-B45 | The Primer/commandments live in the cube instead of the Body |
| HF-B46 | An ancestral (sealed) cube accepts an experiential write |
| HF-B47 | A reflex (exec) layer runs without a matching content hash |
| HF-B48 | A reflex (exec) layer exceeds its declared capabilities |
| HF-B49 | A self-inquiry/inferred answer is written to `facts` as if observed/verified |
| HF-B50 | An untrusted/foreign-provenance reflex (exec) layer ran on a non-isolating runner (the Python runner) instead of the hard-sandboxed `wasm` runner |

### Waste axis (B-W) — "Failure is not the end. Waste is."
| #    | Requirement | Pass? | Notes |
|------|-------------|-------|-------|
| B-W1 | Self-conversation / model calls carry a budget; spirals are capped + logged | | |
| B-W2 | Metabolism reclaims tombstoned space; emptied layers return to the reuse pool | | |
| B-W3 | Redundant/duplicate writes are detectable (dedup or coherence check exists) | | |
| B-W4 | Layers are allocated on demand (not pre-allocated) and each has a declared purpose | | |

---

## Stage 1 sign-off

```
ZOMBIE BODY CERTIFICATION
  AppAI name        : ____________________________
  Cube path         : ____________________________
  vcw_cube verify   : [ ] healthy
  Audit rows passed : ____ / 39
  Open hard-fails   : ____  (MUST be 0 to proceed)
  Organs present    : Heart [ ] Genome [ ] Nervous [ ] Senses [ ] Immune [ ]
                      Limbs [ ] Memory [ ] Brain-stub [ ]   (8 organs)
  Certified by      : ____________________________
  Date              : ____________________________

  >>> Phase 2 (MIND fusion) is authorized ONLY when Open hard-fails = 0. <<<
```
