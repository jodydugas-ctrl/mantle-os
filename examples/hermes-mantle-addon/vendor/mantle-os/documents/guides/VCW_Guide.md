# Mantle OS — The VCW Substrate Guide

The VCW ("Visual Cortex Workspace") cube is the organism's durable nervous-memory: a
stack of 800 real PNG layers (800×800 RGBA) in a ZIP container, addressable byte-by-byte
(`offset = (y*SIDE + x) * 4`), readable in any image viewer. *If it's not in the VCW, it
didn't happen.* The on-disk format is unchanged from v2 (`vcw-cube-png-v2`).

For the canonical measurement anatomy shared by cube layers, app-band ranges, spores,
private tissue, and display surfaces, see
[`VCW_Anatomical_Atlas.md`](VCW_Anatomical_Atlas.md). The atlas consolidates coordinate
ownership and colour/visibility semantics; this guide explains substrate behaviour.

## The mental model

```
cube   = one GENERATION of experiential memory (identity lives in the Body, never here)
band   = a named, contiguous reserved RANGE of layers, self-described by a boot sector
layer  = one real PNG; materialized on demand inside the band's range
entry  = one immutable record; hashed over EVERY non-volatile field
veil   = private bands read as [] unless deliberately lifted; tombstoned/quarantined
         entries never surface
```

Standard genome ownership, app-band reservations, and tail space are defined in the
anatomical atlas and exported from `mantle.vcw.atlas`.

## Boot sectors and drivers (two-level encoding)

A band's boot sector (level 1, fixed format) names a **driver** (level 2, programmable):
`log-json` (immutable entry log), `keyvalue` (small mutable map), `calendar-spatial`
(data AS colors at coordinates — a real canvas), `exec` (a calcified reflex layer).
Drivers live in the Body (trusted code); boot sectors are data that select them.

## VCW is the law — the cube is one body plan, the PNG is another

The boot sector deciding behaviour (not hard-coded logic) has a larger consequence: **VCW is
not one file format. It is a memory GRAMMAR — a law about how state is stored, grown, proven,
and exposed.** The 800-layer cube (`vcw-cube-png-v2`) is one *body plan* that obeys the law. A
[**spore**](../../examples/spore/) — a single PNG that carries its whole memory in its top-half
colour field — is **another**. Same law, different medium. So the spore is not a toy Mantle; it
is proof the substrate can **molt into different media**.

A substrate *is* a VCW layer when it provides the nine properties of the memory grammar:

| The law (memory grammar) | The cube body plan | The SPORE-PNG body plan |
| --- | --- | --- |
| **addressable region** | bands over layers; `offset=(y·SIDE+x)·4` | the top-half VCW region; block index `i→(i%W, i//W)` |
| **canonical payload** | driver-native content per layer, hashed entries | one JSON payload with a `payload_checksum` |
| **append-only evolution** | `log-json` immutable entries, monotonic ids | append-only conversation, ids `0..n` |
| **integrity checks** | staged save→verify, content signatures, seals | magic + `payload_checksum` (a wiped header is refused) |
| **repair signaling** | coherence checks; a corrupt cube never replaces a healthy one | per-block Hamming SECDED in alpha: repair 1 bit, report 2 |
| **embedded boot instructions** | band + cube boot sectors (self-describing) | magic/version/header + `BOOTLOADER` + a runnable embedded reader/writer |
| **authority rules** | cube boot is the authoritative band map; the veil | `AUTHORITY` table: VCW payload canonical over metadata/strip |
| **read/write protocol** | `read` / `retrieve` / `append` | `read_spore` / retrieve-by-index / `append_turn` |
| **display separate from substrate** | private (veiled) bands vs. surfaced ones | bottom-half display strip vs. top-half VCW |

This is why a **Compiler-class** organism can refit its VCW to whatever it inhabits: the cube on
disk, a single PNG as a spore, or some host-native surface (a key-value band, a database table).
The medium changes; the law does not. That claim is not prose — it is checked:

```bash
python examples/spore/vcw_conformance.py                      # prove a fresh spore is a VCW layer
python examples/spore/vcw_conformance.py examples/spore/example_spore.png
```

## The three verbs

```python
cube.append(band, value)        # PRIME only; band-unique monotonic entry ids
cube.read(band)                 # the visible stream, veiled
cube.retrieve(band, address)    # one entry / key / coordinate — O(1) via the band index
```

## Substrate properties

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
- **Metabolism** (`src/mantle/vcw/metabolism.py`): `compact` drops dead entries and returns
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
