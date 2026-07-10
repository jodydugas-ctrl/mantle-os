# Experimental Refinement Map

Cast: `Intellige;Speculum;Distillate;Probatio;Custodia`
Workspace: `C:\tmp\mantle-os-refinement-20260709-180527`
Source: `https://github.com/jodydugas-ctrl/mantle-os`, commit `f1a9695ca2d22c224d4d84477089de06200c4f68`

## Boundary Map

- **Mantle doctrine:** `documents/grimoire/` contains the single version-4 canonical Grimoire tomb. The `documents/Mantle_*.md` and `documents/guides/` files are implementation doctrine, guides, audits, and onboarding material; they explain and interpret the current reference body but are not additional Grimoire editions.
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

## Pass 17 Receipt

Function served: protocol section 6 requires one canonical vocabulary registry and a collision
audit before machine-only prompt or doctrine text can be safely compressed. The previous registry
only checked casefold collisions across a small alias list.

Changes:

- Added `REQUIRED_ALIAS_COLLISION_CHECKS` as the vocabulary collision-audit contract.
- Expanded `ALIAS_REGISTRY` to audit exact aliases, casefold, punctuation, prefix, class markers,
  mode markers, error codes, public CLI commands, environment variables, schema fields, Python
  symbols, and filesystem case collisions.
- Namespaced schema field and Python symbol checks so metadata/data fields and per-module symbols
  are audited without flattening unrelated schemas into false collisions.
- Extended strict optimization audit and generated receipts with vocabulary collision status.
- Added invariant `OPT-4 vocabulary-collision-audit`.
- Updated public invariant-count anchors from 94 to 95.

Deletion decision: no files were deleted. This pass makes later aliasing/compression safer; it
does not introduce a new dialect or rewrite doctrine.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 16 Receipt

Function served: protocol section 5 requires a project-wide model before local rewriting. The
inventory already had file rows and base references; this pass makes the named model maps explicit
so future chunk/subsystem optimization can prove it is acting from cross-file context.

Changes:

- Added `REQUIRED_PROJECT_MODEL_MAPS` as the checked project-model contract.
- Added `project_model` to `python -m mantle optimize-audit`, covering dependency, import/export,
  public API, CLI, configuration, schema, test, documentation, example, lifecycle, organ,
  SELF/OTHER, effect/proof, hard-fail, VCW, provider/cache, version, and duplicate-concept maps.
- Extended strict optimization audit and generated alignment/final receipts with project-model
  status.
- Added invariant `OPT-3 project-model-maps`.
- Updated public invariant-count anchors from 93 to 94.

Deletion decision: no files were deleted. This pass builds the cross-file model required before
safe deletions, merges, or semantic chunk rewrites.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 15 Receipt

Function served: the whole-repository optimization protocol requires each file inventory row to
carry more than path and metric data. Before safe file-by-file optimization, every row needs a
static model of relationships, interfaces, schemas/configuration, side effects, AppAI/lifecycle
roles, security relevance, invariants, proof path, complexity, duplication, and skip/block state.

Changes:

- Added `REQUIRED_FILE_FIELDS` as the checked protocol row contract for `FILE_INVENTORY`.
- Enriched inventory rows with conservative static metadata for schemas, configuration keys,
  external interfaces, AppAI roles, lifecycle roles, side effects, security/privacy relevance,
  invariant references, complexity indicators, and exact duplicate paths.
- Added cross-file relationship enrichment for importers, test references, and documentation
  references.
- Strengthened strict optimization audit and added invariant `OPT-2 inventory-protocol-fields`.
- Updated public invariant-count anchors from 92 to 93.

Deletion decision: no files were deleted. This pass expands the evidence model needed for later
deletions or rewrites; it does not alter runtime behavior.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 14 Receipt

Function served: the repository now has several mechanically important version/count surfaces:
Python package metadata, module metadata, the single Grimoire tomb stamp, the Grimoire doctrine
version, and public invariant-count anchors. The whole-repository optimization protocol needs those
surfaces checked together instead of updated by memory.

Changes:

- Added a `version_alignment` map to `python -m mantle optimize-audit`.
- Extended strict optimization audit failures to include stale package/module/Grimoire/count
  alignment.
- Added invariant `VERS-1 version-alignment-map`.
- Updated public invariant-count anchors from 91 to 92.

Deletion decision: no files were deleted. This pass adds a guard over existing surfaces; it does
not collapse package version, Grimoire version, or certification count into one meaning.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 13 Receipt

Function served: the Grimoire 4 one-tomb migration needed an executable guard so future
edits cannot accidentally restore the obsolete two-file authority model.

Changes:

- Added invariant `GRIM-1 single-grimoire-tomb`.
- The invariant proves `The Grimoire.md` is stamped `G4.0-U`, the grimoire README presents the
  single tomb, the former AppAI chapter file is absent, and stale exact chapter path references are
  gone.
- Updated the public invariant-count anchors from 90 to 91.

Deletion decision: no files were deleted in this pass. The former chapter deletion was completed
in Pass 11; this pass adds a guard over that already-migrated shape.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 12 Receipt

Function served: the whole-repository optimization protocol requires every changed, skipped,
generated, binary, vendored, blocked, and pending file to be recorded. The previous ledger only
reported working-tree changes or a clean-tree placeholder.

Changes:

- Added per-file `git_status`, `disposition`, and `skip_block_reason` fields to the inventory.
- Changed `CHANGE_LEDGER` to emit one receipt per inventoried file.
- Added disposition totals to token/final reports and expanded `SKIP_BLOCK_REPORT` into
  non-pending and pending sections.
- Strengthened `--strict` and `OPT-1` so ledger coverage must exactly match the file inventory.

Deletion decision: no files were deleted. This pass improves accounting only; semantic
file-by-file rewrites still remain pending where the ledger says `pending-pass-review`.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 11 Receipt

Function served: the operator supplied the latest optimized Grimoire tomb and stated that the
AppAI chapter has been consolidated into one Grimoire, now version 4.

Changes:

- Replaced `documents/grimoire/The Grimoire.md` with the supplied consolidated tomb and stamped it
  as repository Grimoire `G4.0-U`.
- Removed the obsolete separate AppAI chapter file so no second canonical
  chapter competes with the tomb.
- Rewrote `documents/grimoire/README.md` around the one-file version-4 canonical model.
- Updated README, implementation docstrings, and doctrine/guides that pointed at the separate
  AppAI chapter.

Deletion decision: the former separate AppAI chapter previously served as the AppAI domain extension.
That function is now covered by the consolidated `The Grimoire.md` tomb's MantleOS `@` doctrine,
including Body/MIND, SELF/OTHER, VCW, residency, reproduction, cache, diagnostics, and lifecycle
law.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 10 Receipt

Function served: the protocol's `TEST_REPORT` requires observed command receipts when proof
commands are actually run. The inventory path should remain cheap by default, but the operator
needs an explicit way to attach exit-code evidence.

Changes:

- Added optional `python -m mantle optimize-audit --run-checks=prove|fast|full`.
- Observed command receipts include command, exit code, timeout status, duration, and redacted
  stdout/stderr tails.
- Default `optimize-audit` behavior still records only the verification index and does not run
  heavy gates.
- Strengthened `OPT-1` to prove observed receipts can be attached without leaking secret-like
  strings.

Deletion decision: no files were deleted. The prior unobserved proof index still serves cheap
baseline inventory; observed receipts are now an explicit mode rather than a competing artifact.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 9 Receipt

Function served: the whole-repository optimization protocol requires baseline runtime metadata and
configured verification-command discovery before later file-by-file rewrite claims can be trusted.

Changes:

- Added runtime/tool/project baseline metadata to `FILE_INVENTORY` and `TOKEN_REPORT`.
- Changed `TEST_REPORT` from a generic proof-path note into a verification index that names
  discovered local and CI proof commands, with network requirements marked where applicable.
- Kept observed exit-code receipts out of `optimize-audit` by default so the inventory command
  stays non-mutating and cheap.
- Strengthened `OPT-1` to prove the baseline metadata and verification index are present.
- Removed the stale invariant-count claim from `CONTRIBUTING.md`.

Deletion decision: no files were deleted. The stale exact count in `CONTRIBUTING.md` served
operator orientation, and that function remains covered by the README anchor plus the live
`python -m mantle prove` output.

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

Function served: the operator supplied an earlier LLM-optimized Grimoire archive when the
repository still used two canonical version-locked files. The repository needed those canonical
files updated together while preserving the then-current README authority rule.

Changes:

- Replaced `documents/grimoire/The Grimoire.md` from `grimoire_3.8_llm_optimized.zip`.
- Replaced the former separate AppAI chapter file from the same archive.
- Updated `documents/grimoire/README.md` so the canonical version lock matched that edition.

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
