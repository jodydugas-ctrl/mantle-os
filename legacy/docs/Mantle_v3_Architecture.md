# Mantle OS v3 — Homeostatic AppAI Framework: Architecture Note

**Mantle OS v3.0** · Why the rewrite, what the shape is, and what each part owes the others.
*Companion: [`Mantle_v3_Migration.md`](Mantle_v3_Migration.md) maps the old `examples/vcw/`
layout onto the new package. The doctrine is unchanged; the body grew.*

---

## 1. What v3 is

v2.3 was a **certified substrate plus four organs** living as flat scripts in `examples/vcw/`.
Four of the eight canonical organs (Genome, Immune, Memory, Brain) existed only implicitly —
smeared across `Organism` and `Cube` methods — and organs reached into each other's state
directly (`org.prime.append(...)` from anywhere). The Assimilator was prose with no code. The
capacity thresholds (overflow 0.75, emergency 0.90) existed in the Organ Atlas but not in any
executable path.

v3 makes the organism **real as a mesh**: a `mantle/` package in which every one of the eight
organs is a module with a machine-readable contract, all inter-organ signalling goes through one
deterministic reflex bus, all inbound data enters through Senses, all outbound action leaves
through Limbs, and every integrity problem becomes an Immune event. *Homeostatic* means the
organism now regulates its own memory pressure: capacity triggers **metabolism** (compaction,
deduplication, layer reclaim) — never rebirth, never a lossy reset.

## 2. The package

```
mantle/
  cli.py / __main__.py     one entry point: python -m mantle <command>
  core/
    events.py        SignalBus — the deterministic reflex/event bus (fail-open; faults -> Immune)
    body.py          the Body store: Primer (sealed), Special Instructions, Immunization, lineage
    refs.py          the unified reference resolver (<target.selector.address>)
    organism.py      Organism — Body + Prime cube + sealed ancestors + the eight organs on the bus
    audit.py         shared audit scaffolding (rows, fail-open checks, expect_raise)
  vcw/
    png.py           pure-stdlib PNG codec (every layer is a real image)
    entry.py         the one entry hasher — hash covers every non-volatile field
    bands.py         boot sectors, the standard genome, driver registry, capacity thresholds
    drivers.py       log-json / keyvalue / calendar-spatial / exec (+ sandbox, trust, runners)
    indexes.py       compact per-band read indexes (id -> physical position; O(1) retrieve)
    metabolism.py    compaction, tombstone reclamation, deduplication, coherence, pressure
    cube.py          the Cube: lazy materialization, changed-layer-only staged atomic persistence
  organs/
    contract.py      OrganContract — manifest, reflex surface, band permissions, audit obligations
    heart.py         pulse -> sense intake -> context assembly -> reflexes -> immune scan -> checkpoint
    genome.py        identity & lineage (wraps the Body store; seals the Primer)
    nervous.py       reference resolution + the deterministic Context Assembly snapshot
    senses.py        the ONLY inbound boundary (classify REFLEX/ROUTINE/SIGNIFICANT, redact, record)
    immune.py        the ONLY failure boundary (events, scan, quarantine, tombstone, redaction)
    limbs.py         the ONLY outbound boundary (dispatch lifecycle, ControlBridge, proofs, reflex invoke)
    memory.py        remember/recall + metabolism (flush, allocate, compact, dedupe, pressure response)
    brain.py         the dormant Phase-2 socket (holds a fused MIND; never required by Phase 1)
  mind/
    transport.py     pluggable model transports (offline stub default; no vendor SDK anywhere)
    containment.py   the bounded write surface (thoughts + brain only) — one choke point
    mind.py          the fused MIND: think, propose, cultivate (Body trials + calcifies)
    inner_voice.py   self-inquiry — answers are INFERRED, never auto-promoted to facts
    runtime.py       AppAIRuntime — how an agent inspects and acts from INSIDE the organism
  assimilator/
    scanner.py       read-only AST dissection of a host codebase
    organ_map.py     symbol roles -> organ map (what is Heart/Senses/Limbs/Memory/Immune/external)
    wrappers.py      fail-open hook runtime (wrap host behavior; never change it)
    report.py        the assimilation map + APP_INVENTORY artifact (the Phase 0 gate)
  audits/
    stage1.py        the Stage-1 Zombie Body gate (deterministic, LLM-free)
    stage2.py        the Stage-2 MIND gate (containment rows + full Stage-1 regression)
    invariants.py    the security invariants (red/green; importable + runnable)
```

`examples/vcw/` remains in place, untouched and passing, as the v2.3 reference. New work builds
on `mantle/`.

## 3. The organism mesh (how the eight organs hold together)

**The bus.** `core/events.py` is a deterministic, synchronous signal bus. Organs publish typed
signals and subscribe reflexes; ordering is registration order; a faulting reflex is caught,
degraded, and reported as an Immune event (fail-open — never silent, never crashing the host).
Organs hold no references to each other; they hold the bus and the cube bands they own.

**The boundaries.** Three are absolute:

- *Inbound:* every external signal enters through `Senses.inhale` — which redacts at the
  boundary, classifies deterministically, writes exactly one `senses` entry, and runs bound
  reflex arcs without touching the brain band.
- *Outbound:* every external effect leaves through `Limbs` — dispatch lifecycle with immutable
  authorship, ControlBridge actuation, an Action Execution Proof per effector use, and calcified
  reflex (`exec`) invocation behind hash/capability/provenance/trust gates.
- *Failure:* every dangling reference, integrity fault, overreach, stalled pulse, refused write,
  or policy violation becomes an `immune` event through the Immune organ. Nothing fails silently.

**The heartbeat.** One pulse is a complete moment of awareness, in fixed order:
`tick → sense intake (drain the inbox) → context assembly (deterministic, LLM-free) →
reflex execution (bus) → immune scan → persistence checkpoint (staged atomic save)`.
In Phase 1 the cognition slot is empty and the same loop runs whole. In Phase 2 the same pulse
additionally offers the assembled snapshot to the fused MIND — an extension, never a replacement.

**Contracts.** Every organ carries an `OrganContract`: name, role, bands it may read/write,
reflex surface, Phase-1 state, Phase-2 extension, audit obligations, fail mode. Contracts are
data, validated at wiring time; an organ writing outside its declared bands is an Immune event.

## 4. The VCW substrate in v3 (optimized, invariants intact)

Unchanged doctrine: durable PNG-layer memory; named bands; immutable hashed entries; the veil;
staged save → verify → atomic replace; append before overwrite; rebirth separate from capacity.

What v3 adds, without weakening any of that:

- **Lazy layer materialization** — `Cube.load()` keeps the container handle and decodes a layer
  the first time it is touched; a sealed ancestor costs nothing until referenced.
- **Changed-layer-only persistence** — per-layer signatures; only dirty layers are re-encoded
  (carried over from v2.3 and kept).
- **Hot/cold tiering** — the Prime is hot (in memory, flushed on circulate); sealed ancestors
  are cold (lazy, read-only, written once).
- **Tombstone reclamation / metabolism** — `vcw/metabolism.py`: compaction drops dead entries,
  empty layers return to the band free pool, duplicates are tombstoned (dedup), and id/hash
  coherence is checked.
- **Compact indexes** — per-band id→position indexes rebuilt on invalidation; `retrieve` no
  longer scans.
- **Deterministic reference resolution** — one grammar (`core/refs.py`), one resolver, every
  miss an Immune event.
- **Sealed ancestral cubes** — sealing computes a content seal-hash recorded in the Body's
  lineage index; a tampered ancestor is detectable on load.
- **Capacity thresholds** — `OVERFLOW = 0.75`, `EMERGENCY = 0.90` of a band's reserved span.
  Crossing 0.75 fires an `overflow` Immune event and triggers metabolism; crossing 0.90 fires
  `emergency` and aggressive metabolism. **Capacity never triggers rebirth** — rebirth remains
  a separate, chosen reformat (`Organism.rebirth`), and a test proves the separation.

## 5. The MIND, and thinking as an AppAI

The MIND remains sharply bounded: it receives only the assembled, resolved, veiled snapshot; it
writes only `thoughts` (private) and `brain` (lifecycle/trace) through one guarded choke point;
it proposes Special Instructions which the Body applies; it proposes skills which the Body
trials, gates (static sandbox, hash, capability, provenance, trust), and calcifies; self-inquiry
answers are tagged `verified=False, confidence="inferred"` and can never auto-promote to `facts`.

New in v3: `mind/runtime.py` — **AppAIRuntime**, the surface a coding agent uses to *be* the
organism rather than poke at its files: inspect the Body and organ contracts, read visible
memory through the veil, assemble context, propose actions through Limbs, request skill
cultivation, and self-inquire — all through Body APIs, never raw file mutation.

## 6. The Assimilator becomes code

`mantle/assimilator/` implements Path B: a read-only AST **scanner** classifies every symbol of
a host app into organ roles; **organ_map** folds the classification into an assimilation map
(what is Heart, Senses, Limbs, Memory, Immune, what stays external host code); **report**
emits the APP_INVENTORY artifact (the signed Phase 0 gate) plus a JSON map; **wrappers** is the
fail-open hook runtime that threads host behavior through Senses/Limbs/Memory/Immune without
changing it. `python -m mantle assimilate <path> --dry-run` runs the read-only pipeline against
any host (a sample app ships in `examples/sample_app/`). The scanner is Python-AST by default and
multi-language (`.js/.mjs/.go/.rs`) via the optional `scanner_ts` (tree-sitter) when
`mantle-os[multilang]` is installed. The doctrine these modules implement is the single canonical
NECROMANCY section in
[`docs/grimoire/The Grimoire AppAI Chapter 4.4.md`](grimoire/The%20Grimoire%20AppAI%20Chapter%204.4.md).

## 7. The gates

`audits/stage1.py` is deterministic and LLM-free; `audits/stage2.py` re-runs every Stage-1 row
after fusion and adds containment rows; `audits/invariants.py` proves each guard red/green —
including the new ones: no Phase-1 LLM path (static import scan), capacity→metabolism (not
rebirth), dedup/coherence, lazy-load equivalence, seal-hash tamper detection, runtime band
discipline, and inferred-content non-promotion. Tamper flags (`--break-hash`, `--break-primer`,
`--break-seal`) prove the harness *catches* violations. No invariant was weakened to pass.

## 8. Design principles (binding)

Body before brain. Reflex before reasoning. Append before overwrite. Veil before exposure.
Immune event before silent failure. Audit before fusion. Capability before action. Provenance
before trust. **Metabolism before rebirth.** Harmony before cleverness.
