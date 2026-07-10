# Experimental Refinement Map

Cast: `Intellige;Speculum;Distillate;Probatio;Custodia`
Workspace: `C:\tmp\mantle-os-refinement-20260709-180527`
Source: `https://github.com/jodydugas-ctrl/mantle-os`, commit `f1a9695ca2d22c224d4d84477089de06200c4f68`

## Boundary Map

- **Mantle doctrine:** `documents/grimoire/` contains the two version-locked canonical Grimoire files. The `documents/Mantle_*.md` and `documents/guides/` files are implementation doctrine, guides, audits, and onboarding material; they explain and interpret the current reference body but are not additional Grimoire editions.
- **Mantle implementation:** `src/mantle/core`, `vcw`, `organs`, `audits`, `mind`, and top-level capability modules implement the organism runtime, VCW substrate, certification gates, Phase-2 MIND containment, reproduction, cache-ghost, symbiosis, residency, and applet/face surfaces.
- **Standard host/app code:** `examples/sample_app`, browser demos, JS smoke tests, standalone VCW examples, eggs, and notepad AppAI examples are examples or host/application artifacts. They remain ordinary code unless explicitly assimilated through Mantle seams.
- **Essential surfaces:** `python -m mantle check`, Stage-1 and Stage-2 gates, the current invariant suite, no-LLM Phase-1 import boundary, SELF/OTHER proof, Body-owned key material, spore/vault lineage, CLI compatibility, and append-only VCW behavior.
- **Duplicated surfaces:** the README is the mechanically checked certification-count anchor; secondary docs now prefer "current invariant suite" where an exact number is not needed. Reproduction doctrine still appears in README, Reproduction, Primer, and Grimoire chapter; cache-ghost laws appear in Grimoire chapter, Reproduction docs, and implementation docstrings; organ atlas concepts appear in several guides.
- **Stale surfaces found in pass 1:** an old smoke-test comment still said 84 invariants, positioning docs referenced `python -m vcw audit`, Reproduction docs used an older provider cache-read field name, and Part 2 MIND docs had a `Limb/Lung` wording slip.
- **Distillable but not safe for pass 1:** broad doc consolidation, Grimoire version changes, example app modernization, and deletion of duplicate doctrine blocks. These need their own receipted passes and full proof paths.

## Lifecycle Invariant

Pass 2 defines and proves the transition:

1. A SPOREAGENT carries source retrieval instructions.
2. The agent fetches or declares the source and uses the Grimoire to assimilate it into a Body.
3. The first target is a certified Zombie Body.
4. The SPORE becomes the PRIMER for identity, role, commandments, boundaries, and Body-owned key material.
5. MIND never receives key material and may only request Body-owned cryptographic actions.
6. The transition records source fetched, body certified, and boundary sealed.
7. Host/application code remains OTHER until proven through PRIMER, seal, provenance, and certification.

## Smallest Safe Pass

Pass 1 is documentation-only:

- Update stale command/count references.
- Update stale cache telemetry wording to current `cached_tokens`/receipt language.
- Correct one terminology slip from `Limb/Lung` to `Limb`.
- Verify with `python -m mantle check`; use `--fast` only for exploratory preflight.

## Pass 2 Receipt

Function served: the requested lifecycle invariant needs a proof that a SPOREAGENT can carry
source provenance into SPORE-DISTILLATION without bloating the pure SPORE-PNG substrate or handing
key material to MIND.

Changes:

- Added a Reproduction-layer source receipt to `hatch_from_spore(..., source_receipt=...)`.
- Recorded declared/fetched/assimilated/certified/sealed source status under
  `spore_distillation.source`.
- Stated the PRIMER boundary, Body key ownership, and MIND exclusion in the receipt.
- Added an executable invariant proving backward-compatible hatching, explicit missing-source
  status, redacted provenance, OTHER-until-proven host code, and no SPORE substrate creep.

Deletion decision: no files or features were deleted in this pass. The function served by the
duplicated lifecycle prose is still onboarding and operator guidance; consolidation should wait for
a separate deletion-safe documentation pass.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 8 Receipt

Function served: the optimization audit needed a gate mode, not only a report mode, so the
whole-project alignment audit can fail loudly on unresolved references or incomplete artifact
coverage.

Changes:

- Added `python -m mantle optimize-audit --strict`.
- `--strict` fails on unknown file categories, missing tracked files, unresolved normalized path
  references, unresolved Mantle CLI references, alias collisions, missing proof surfaces, or missing
  required artifacts.
- Added strict-mode status to JSON output.
- Strengthened `OPT-1` to prove strict-mode failure detection currently returns no failures.

Deletion decision: no files were deleted. This pass adds an explicit gate over the existing
generated artifacts and alignment maps.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 7 Receipt

Function served: the optimization audit must not maintain a competing CLI command registry. The
actual CLI router is the canonical command surface; alignment checks should read from that source.

Changes:

- Added `known_commands()` to `src/mantle/cli.py` as the canonical machine-readable command list.
- Normalized underscore compatibility aliases through one alias map before routing.
- Changed `src/mantle/optimize_audit.py` to consume `known_commands()` instead of a local duplicate
  command set.
- Strengthened `OPT-1` to prove `optimize-audit` is present in the canonical CLI registry.

Deletion decision: no files were deleted. A duplicate in-code registry was removed from the audit
module and replaced by the canonical CLI helper.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 6 Receipt

Function served: the optimization audit's alignment matrix needed to separate real stale
references from prose fragments, wildcard examples, and command placeholders before it could guide
safe whole-repo optimization.

Changes:

- Normalized documented file and directory references before checking them.
- Added Mantle CLI command reference extraction and validation against the known command surface.
- Filtered weak non-path fragments from stale-path reporting.
- Strengthened `OPT-1` so the invariant proves zero unresolved normalized path references and zero
  unresolved Mantle CLI command references in the generated alignment map.

Deletion decision: no files were deleted. The pass reduces false-positive alignment noise without
removing any documented behavior.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 5 Receipt

Function served: the whole-repository optimization protocol requires a complete file inventory,
token-measurement honesty, skip/block accounting, and generated artifacts before safe semantic
optimization. MantleOS now has an executable baseline audit instead of a manual-only checklist.

Changes:

- Added `src/mantle/optimize_audit.py`, a stdlib-only non-mutating repository inventory and
  artifact generator.
- Added `python -m mantle optimize-audit [--out=DIR] [--json]` to the CLI.
- Added invariant `OPT-1 repository-inventory-audit` to prove tracked files are inventoried,
  key surfaces are classified, artifacts are written outside the source tree, and token counts are
  labeled measured or unverifiable.
- Updated checked invariant-count anchors from 89 to 90.

Deletion decision: no files were deleted. The protocol's required final artifacts are generated
outside the production source tree unless the operator separately authorizes committing them.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 4 Receipt

Function served: the operator supplied a 3.8.0 LLM-optimized Grimoire archive containing the two
canonical version-locked files. The repository needed those canonical files updated together while
preserving the README's two-file authority rule.

Changes:

- Replaced `documents/grimoire/The Grimoire.md` from `grimoire_3.8_llm_optimized.zip`.
- Replaced `documents/grimoire/The Grimoire AppAI Chapter.md` from the same archive.
- Updated `documents/grimoire/README.md` so the canonical version lock says 3.8.0.

Deletion decision: no Grimoire files were deleted. The existing README still serves the canonical
reading-order and version-lock function; the supplied archive replaces only the two canonical bodies.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 3 Receipt

Function served: certification counts were duplicated across onboarding, audit, and reproduction
manuals. The README is already checked by `doctor`, so it should remain the numeric anchor; other
manuals should point to the live invariant suite unless an exact count is operationally useful.

Changes:

- Kept the README's current certification count for `doctor` coherence.
- Replaced secondary numeric count claims with "current invariant suite", "full invariant suite",
  or "all green" phrasing.
- Updated this map so the SPOREAGENT lifecycle is no longer described as future work.

Deletion decision: no files were deleted. The function served by the duplicate count references was
operator orientation; that function remains covered by the README anchor, `Audit_Guide`, and the
executable `python -m mantle prove` output.

Proof path: `PYTHONPATH=src python -m mantle check`.
