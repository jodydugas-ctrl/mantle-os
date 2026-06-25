# Mantle OS v3 — Migration Note (from `examples/vcw/` to `mantle/`)

**What moved, what changed, what is preserved.** The framework lives in `mantle/`;
`examples/vcw/` was rebuilt around the standalone, normative cube codec (see §4). The
complete v2.3 implementation remains available in git history.

---

## 1. Module map

| v2.3 (`examples/vcw/`) | v3 (`mantle/`) | Notes |
|---|---|---|
| `vcw_cube.py` (PNG codec half) | `vcw/png.py` | unchanged on-disk format (`vcw-cube-png-v2`) |
| `vcw_cube.py` (legacy Cube half) | *retired* | the legacy in-cube-genome Cube was already superseded; v3 keeps only the canonical Body-resident-identity model |
| `entry.py` | `vcw/entry.py` | + `content_hash` (dedup key), `make_entry` consolidated here |
| `boot.py` | `vcw/bands.py` | + capacity thresholds `OVERFLOW_THRESHOLD=0.75`, `EMERGENCY_THRESHOLD=0.90` |
| `drivers.py` | `vcw/drivers.py` | + `ProvenanceError` + `validate_calcify_payload` (hash/signature/capability/provenance now REQUIRED to calcify) |
| `lineage.py::Cube` | `vcw/cube.py` | + lazy materialization, band-unique entry ids, compact indexes, pressure→metabolism, seal fingerprints; staged atomic save and changed-layer-only persistence carried over (layer signatures now cover full content) |
| `lineage.py::Cube.compact` | `vcw/metabolism.py` | + `dedupe`, `reclaim`, `pressure`, `coherence` |
| — (new) | `vcw/indexes.py` | per-band id/position indexes; O(1) `retrieve` |
| `body.py` | `core/body.py` | + seal-fingerprint slots in the lineage index |
| `refs.py` | `core/refs.py` | unchanged grammar |
| `redact.py` | `core/redact.py` | unchanged rules |
| `lineage.py::Organism` | `core/organism.py` | now wires the full eight-organ mesh on a SignalBus; `stage1_certified` gates fusion; ancestors load lazy + seal-verified |
| — (new) | `core/events.py` | the deterministic, fail-open SignalBus |
| `audit_helpers.py` | `core/audit.py` | same helpers |
| `organs/heart.py` | `organs/heart.py` | pulse now runs the fixed order: tick → intake → assembly → reflexes → scan → checkpoint |
| `organs/senses.py` | `organs/senses.py` | + inbox/drain (heartbeat intake), Surface Map moved here (afferent half), redaction inside `inhale` |
| `organs/limbs.py` | `organs/limbs.py` | + `invoke_reflex` (calcified skills run through the Limb with a proof) |
| `organs/nervous.py` | `organs/nervous.py` | same protocol, organism-wired |
| — (implicit in `Organism`) | `organs/immune.py` | the Immune System is now a real organ: events, scan, marks, redaction |
| — (implicit in `Cube`) | `organs/memory.py` | remember/recall + metabolism + `promote_to_fact` (evidence-gated) |
| — (implicit in `Body`) | `organs/genome.py` | boot order, seal, inheritance records |
| — (new) | `organs/brain.py` | the dormant Phase-2 socket; fusion refused without Stage-1 certification |
| — (new) | `organs/contract.py` | `OrganContract` — manifests are now enforced, not prose |
| `mind.py` | `mind/{transport,containment,mind}.py` | same containment, now split; `fuse()` enforces audit-before-fusion |
| `skills.py` | `mind/inner_voice.py` | inferred-provenance rules unchanged; discoveries write goes through the Memory organ |
| — (new) | `mind/runtime.py` | `AppAIRuntime` — the agent-facing Body API |
| `Mantle_Assimilator.md` (prose only) | `assimilator/{scanner,organ_map,wrappers,report}.py` | Path B is now runnable: read-only dissection, organ map, APP_INVENTORY artifact, fail-open reversible wrappers |
| `audit.py` | `audits/stage1.py` | + mesh rows (B-06 pulse order, B-60 contracts, B-61 bus, B-62 overreach, B-63 pressure), `--break-seal` tamper proof |
| `audit_mind.py` | `audits/stage2.py` | + M-6 inferred provenance, M-7 audit-before-fusion |
| `test_invariants.py` (16) | `audits/invariants.py` (32) | every old invariant kept; 16 added (see below) |
| `__main__.py` (`python -m vcw`) | `cli.py` + `__main__.py` (`python -m mantle`) | + `assimilate` |

## 2. Behavioral changes (all tightenings; nothing loosened)

1. **Capacity thresholds are executable.** Allocation pressure ≥ 0.75 fires `capacity_overflow`
   (metabolism: compact); ≥ 0.90 fires `capacity_emergency` (aggressive: dedupe + compact).
   `CapacityError` only when the range is exhausted *after* metabolism. Rebirth is untouched
   by any of this and remains a separate, chosen act.
2. **Entry ids are band-unique** (monotonic per band), not per-layer positions — stable
   tombstone/quarantine addressing across layer rolls and reuse.
3. **Calcify is gated harder:** missing code-hash, capability set, signature, or
   provenance-with-author now raises `ProvenanceError` (v2 accepted any payload shape).
4. **Layer signatures cover full entry content** (v2 covered id/hash/flags only), so an
   in-place tamper can never hide behind the PNG cache; the staged verify catches it.
5. **Seal fingerprints:** sealing a generation fingerprints its entire content; the Body's
   lineage index records it; a rewritten ancestor is detectable (`--break-seal` proves it).
6. **Organ contracts are enforced:** an organ writing a band it never declared gets a
   `PermissionError` plus an `organ_overreach` immune event.
7. **Fusion requires certification:** `mind.fuse()` refuses unless the organism passed the
   Stage-1 gate this run (or was loaded with a recorded certification).
8. **Inference cannot become fact:** `Memory.promote_to_fact` demands cited, verified
   evidence; the Inner Voice writes only discoveries/thoughts.

## 3. New invariants (red/green, in `mantle/audits/invariants.py`)

HF-B08 no-phase1-llm-path (clean-subprocess proof) · HF-B08 static import scan ·
B-15 tombstone+quarantine hidden · HF-B46b seal-tamper detected · B-CAP capacity→metabolism
(never rebirth) · B-LZ lazy-load equivalence · HF-B52 calcify-requires-gates ·
HF-M15 fusion-requires-stage1 · HF-M16 self-inquiry-never-facts · B-OC organ overreach ·
HF-B32 reflex-fault fail-open · B-DD dedupe · B-SC staged-save-rejects-corrupt — plus all
sixteen v2.3 invariants, unweakened.

## 4. The examples directory (updated in the second v3 pass)

`examples/vcw/` is no longer a frozen v2.3 snapshot; every file was updated:

| Old file | Fate |
|---|---|
| `vcw_cube.py` (v2 codec + legacy in-cube genome) | **rewritten** as the standalone, normative v3 cube — pure stdlib, no `mantle` imports, byte-compatible with the engine, `selftest` + full CLI (create/append/read/retrieve/tombstone/quarantine/verify/seal/inspect/extract) |
| — (new) | `interop.py` — proves standalone <-> engine byte compatibility both directions, including identical seal fingerprints (run in CI) |
| `GUIDE.md`, `README.md` | rewritten for v3 around the standalone cube |
| `audit.py`, `audit_mind.py`, `test_invariants.py` | now thin shims into `mantle/audits/` — the v2.3 commands keep working from this directory |
| `examples_boot.py`, `examples_mind.py`, `__main__.py` | shims into `python -m mantle demo` / `mind` |
| `bench.py` | rewritten for the standalone codec |
| `lineage.py`, `body.py`, `boot.py`, `drivers.py`, `entry.py`, `refs.py`, `redact.py`, `skills.py`, `mind.py`, `organs/`, `examples.py`, `audit_helpers.py` | **retired** — they grew up into the `mantle/` package (see the module map above); the old code is one `git log` away |

## 5. Compatibility

- The **container format is unchanged** (`vcw-cube-png-v2`): a v3 cube is a ZIP of real
  PNGs with `cube.json`, loadable by eye and by the old tooling's decoder.
- v3 adds `next_entry_id` and `seal_fingerprint` to `cube.json`; v2 files load into v3
  (missing fields default safely), v3 files carry strictly more metadata.
- The old commands still work where they always did: `cd examples/vcw && python audit.py`.
  The new entry point is `python -m mantle ...` from the repository root.
