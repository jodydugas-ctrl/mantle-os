# Mantle OS v3 — The VCW Substrate Guide

The VCW ("Visual Cortex Workspace") cube is the organism's durable nervous-memory: a
stack of 800 real PNG layers (800×800 RGBA) in a ZIP container, addressable byte-by-byte
(`offset = (y*SIDE + x) * 4`), readable in any image viewer. *If it's not in the VCW, it
didn't happen.* The on-disk format is unchanged from v2 (`vcw-cube-png-v2`).

## The mental model

```
cube   = one GENERATION of experiential memory (identity lives in the Body, never here)
band   = a named, contiguous reserved RANGE of layers, self-described by a boot sector
layer  = one real PNG; materialized on demand inside the band's range
entry  = one immutable record; hashed over EVERY non-volatile field
veil   = private bands read as [] unless deliberately lifted; tombstoned/quarantined
         entries never surface
```

Standard genome (reserved bands): identity 100–149 · facts 150–199 · events 200–249 ·
discoveries 250–299 · senses 300–399 · immune 400–449 · brain 450–499 · thoughts 500–549
(private) · app bands 550–749 · tail 750–799.

## Boot sectors and drivers (two-level encoding)

A band's boot sector (level 1, fixed format) names a **driver** (level 2, programmable):
`log-json` (immutable entry log), `keyvalue` (small mutable map), `calendar-spatial`
(data AS colors at coordinates — a real canvas), `exec` (a calcified reflex layer).
Drivers live in the Body (trusted code); boot sectors are data that select them.

## The three verbs

```python
cube.append(band, value)        # PRIME only; band-unique monotonic entry ids
cube.read(band)                 # the visible stream, veiled
cube.retrieve(band, address)    # one entry / key / coordinate — O(1) via the band index
```

## v3 substrate properties

- **Lazy materialization.** `Cube.load(path, lazy=True)` decodes a layer on first touch.
  `Organism.load` uses it for every sealed ancestor: the cold tier costs nothing until
  referenced. (`materialized_count()` shows the effect.)
- **Hot/cold tiering.** The Prime is hot (in memory, flushed each checkpoint); ancestors
  are cold (lazy, read-only, written to disk exactly once).
- **Changed-layer-only persistence.** Each layer carries a content signature; clean
  layers reuse cached PNG bytes on save. The signature covers *every byte of every
  entry*, so an in-place tamper invalidates the cache and is caught by the staged verify.
- **Staged atomic commit.** `save()` writes `<path>.stage`, verifies the freshly-encoded
  layers (hash recompute + coherence), and only then `os.replace`s. A corrupt cube can
  never replace a healthy one.
- **Compact indexes.** Per-band id/position indexes (pure memo, invalidated on mutation)
  make `retrieve` and tombstone/quarantine-by-id O(1) after one lazy build.
- **Metabolism** (`mantle/vcw/metabolism.py`): `compact` drops dead entries and returns
  emptied non-tail layers to the band's free pool (safe-reuse: entry-addressed layers
  only); `dedupe` tombstones repeated (opcode, content) entries; `coherence` checks
  duplicate ids and active/free overlap.
- **Capacity thresholds.** Allocation pressure = allocated layers / reserved span.
  ≥ **0.75** → `capacity_overflow` immune event + compaction. ≥ **0.90** →
  `capacity_emergency` + dedupe + compaction. `CapacityError` only if the range is full
  *after* metabolism — and even that only *motivates* a chosen rebirth-reformat.
  **Capacity never triggers rebirth.**
- **Sealed generations.** `seal()` freezes the cube and fingerprints its entire content
  (`sha256` over band metadata + every entry field + spatial/exec payloads). The
  fingerprint is recorded in the Body's lineage index; `verify_seal()` (run on load with
  `verify_seals=True`, and by the Stage-1 gate) detects any rewritten history.

## Exec layers (calcified skills)

To become an instinct, code must pass, in order: the **static sandbox gate** (no imports,
no dunder access, no forbidden builtins), the **trial** (proving cases), and the
**calcify payload gate** (code-hash + signature + capability set + provenance naming an
author — `ProvenanceError` otherwise). At every invocation: the **integrity gate** (hash
match), the **capability gate** (no undeclared reads/writes/limbs/net), and the **trust
gate** (foreign/untrusted provenance is refused on the non-isolating Python runner; the
`wasm` runner is the prepared hard-sandbox seam). Invoke through the Limb
(`org.limbs.invoke_reflex`) to get an Action Execution Proof per run.

## Reference grammar

`<TARGET.SELECTOR.ADDRESS>` — target `cube`/`prime` (default), `genN`, or `body`;
selector a band or Body category; address an entry index, `XxY` coordinate, or omitted
for the whole band. Every dangling reference becomes an immune event, never a silent
drop. Resolution is deterministic.
