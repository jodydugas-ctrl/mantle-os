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

## Pass 28 Receipt

Function served: protocol section 20 requires the whole-repository optimization work to proceed in
order and forbids skipping from local success to project completion. The audit had completion rows,
but not an explicit ordered execution ledger.

Changes:

- Added `EXECUTION_ORDER_STEPS` and `EXECUTION_ORDER_FIELDS`.
- Added `execution_order` to `python -m mantle optimize-audit`.
- Each section-20 step now records ordered status, evidence, and blockers.
- Strict audit now requires every execution-order step and row field.
- `ALIGNMENT_MATRIX`, `FINAL_RECEIPT`, CLI output, and JSON output now summarize execution-order
  totals.
- Added invariant `OPT-15 execution-order`.
- Updated public invariant-count anchors from 105 to 106.

Deletion decision: no files, functions, documents, or aliases were deleted. This pass prevents the
protocol from skipping unresolved middle steps while still allowing smaller receipted passes.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 29 Receipt

Function served: protocol section 7 requires characterization tests for poorly specified behavior
before merge, deletion, or semantic chunk rewrite. The execution-order matrix named this step, but
the queued test obligations were not yet first-class audit evidence.

Changes:

- Added `CHARACTERIZATION_TEST_FIELDS`.
- Added `characterization_tests` to `python -m mantle optimize-audit`.
- Each merge candidate now has a non-mutating characterization receipt with behavior surface,
  specification status, existing evidence, required focused tests, blockers, and
  `mutation_allowed: False`.
- Strict audit now requires characterization rows for every merge candidate.
- The section-20 execution-order row for characterization tests now reports ledger evidence instead
  of a hard-coded placeholder.
- `ALIGNMENT_MATRIX`, `FINAL_RECEIPT`, CLI output, and JSON output now summarize characterization
  totals.
- Added invariant `OPT-16 characterization-tests`.
- Updated public invariant-count anchors from 106 to 107.

Deletion decision: no files, functions, documents, or aliases were deleted. This pass preserves all
candidate surfaces until behavior can be specified by focused characterization tests and the full
proof path.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 30 Receipt

Function served: protocol section 8 requires file-by-file, chunk-by-chunk optimization progress to
be receipted. Previous audit passes could report changed files during a dirty-tree run, but a clean
checkout had no durable way to count which semantic chunks had already been inspected and verified.

Changes:

- Added `documents/refinement/CHUNK_OPTIMIZATION_LEDGER.json`.
- Added `CHUNK_OPTIMIZATION_RECEIPT_FIELDS` and `CHUNK_LEDGER_REL`.
- `python -m mantle optimize-audit` now loads the committed chunk ledger and counts only verified
  receipts as inspected chunks.
- File-completion rows now carry `chunk_receipts` and can distinguish `PARTIAL_CHUNK_REVIEW` from
  untouched `PENDING_CHUNK_REVIEW`.
- Strict audit now rejects malformed chunk receipts, missing paths, duplicate chunk IDs, and
  secret-like ledger content.
- Completion conditions, guardian evidence, execution-order step 8, `ALIGNMENT_MATRIX`,
  `FINAL_RECEIPT`, CLI output, and JSON output now summarize durable chunk progress.
- Added invariant `OPT-17 chunk-optimization-ledger`.
- Updated public invariant-count anchors from 107 to 108.

Deletion decision: no files, functions, documents, or aliases were deleted. This pass adds durable
section-8 evidence while preserving the rule that partial chunk review is not whole-file completion.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 31 Receipt

Function served: protocol section 7 requires focused characterization before merge, deletion, or
semantic rewrite. Four documentation-topic merge candidates were queued because they looked similar
by filename, but their behavior surfaces had not been characterized.

Changes:

- Added `documents/refinement/CHARACTERIZATION_TEST_LEDGER.json`.
- Added `CHARACTERIZATION_LEDGER_REL` and `CHARACTERIZATION_CASE_FIELDS`.
- `python -m mantle optimize-audit` now loads verified characterization cases and marks covered
  candidates as `CHARACTERIZED` instead of `QUEUED`.
- Strict audit now rejects malformed characterization cases, duplicate cases, unknown candidates,
  and unreadable characterization ledgers.
- The four documentation-topic candidates are characterized as distinct scoped documentation
  surfaces; no merge, deletion, or rewrite is authorized by this pass.
- The section-20 execution-order row for characterization tests can now reach `PASS` while later
  chunk optimization remains `REVISE`.
- Strengthened invariant `OPT-16 characterization-tests`.
- Added invariant `OPT-18 characterization-case-ledger`.
- Updated public invariant-count anchors from 108 to 109.

Deletion decision: no files, functions, documents, or aliases were deleted. The characterization
cases explain the current function of each candidate pair and why the function remains covered by
keeping the surfaces separate for now.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 27 Receipt

Function served: protocol section 19 lists the exact conditions required before PASS may be
declared. Scorecard and guardian rows existed, but the PASS conditions themselves were not yet a
first-class checked matrix.

Changes:

- Added `COMPLETION_CONDITIONS` and `COMPLETION_CONDITION_FIELDS`.
- Added `completion_conditions` to `python -m mantle optimize-audit`.
- Each section-19 PASS condition now records `PASS`, `REVISE`, or `UNVERIFIABLE` with evidence and
  blockers.
- Strict audit now requires the completion-condition matrix and row fields.
- `ALIGNMENT_MATRIX`, `FINAL_RECEIPT`, CLI output, and JSON output now summarize completion totals.
- Added invariant `OPT-14 completion-conditions`.
- Updated public invariant-count anchors from 104 to 105.

Deletion decision: no files, functions, documents, or aliases were deleted. This pass prevents
completion from being inferred from partial evidence; PASS remains blocked until every section-19
condition is proven.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 26 Receipt

Function served: protocol sections 14, 15, and 17 require performance evidence and final
verification receipts. The audit could record observed checks, but performance reporting remained
baseline-only and there was no bundled final-check mode.

Changes:

- Added `--run-checks=final` to `python -m mantle optimize-audit`.
- The final bundle runs the local stdlib proof surfaces: `check`, `audit`, `audit-mind`, `prove`,
  and standalone VCW selftest.
- `PERFORMANCE_REPORT` now records observed proof-command wall-clock durations as benchmark
  receipts when checks are run.
- Performance alignment, final verification, and scorecard rows now distinguish "no benchmark
  evidence" from observed proof-duration evidence.
- The audit remains honest that proof-command durations are not a dedicated baseline/final benchmark
  suite.
- Added invariant `OPT-13 final-mode-performance`.
- Updated public invariant-count anchors from 103 to 104.

Deletion decision: no files, functions, documents, or aliases were deleted. This pass improves
observed verification/performance receipts without adding dependencies or claiming final PASS.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 25 Receipt

Function served: protocol sections 17, 19, and 20 require an optimization scorecard, explicit
completion-condition evidence, and a guardian review before declaring PASS. The audit had a prose
guardian line, but not machine-readable scorecard or guardian rows.

Changes:

- Added `SCORECARD_METRICS`, `SCORECARD_FIELDS`, `GUARDIAN_CHECKS`, and `GUARDIAN_FIELDS`.
- Added `optimization_scorecard` to `python -m mantle optimize-audit`.
- Added `guardian_review` to decide current PASS/REVISE/UNVERIFIABLE completion status from
  evidence rather than intent.
- Scorecard rows point aggregate byte/line/token claims back to per-file evidence artifacts.
- Guardian rows record why inventory, merge parity, hard-fail, version, and ripple evidence passes,
  and why token measurement, final verification, blind semantic comparison, and full alignment remain
  open.
- Strict audit now requires scorecard and guardian rows.
- `ALIGNMENT_MATRIX`, `FINAL_RECEIPT`, CLI output, and JSON output now summarize scorecard and
  guardian totals.
- Added invariant `OPT-12 scorecard-guardian-review`.
- Updated public invariant-count anchors from 102 to 103.

Deletion decision: no files, functions, documents, or aliases were deleted. This pass adds
completion-accounting evidence and keeps the guardian result at `REVISE` until the protocol's PASS
conditions are actually proven.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 24 Receipt

Function served: protocol section 7 requires steelman, caller analysis, parity dimensions, mode
complexity review, compatibility-alias decisions, and proof requirements before any merge candidate
can be consolidated or deleted. The audit found candidates, but the merge map did not yet carry the
per-candidate parity evidence.

Changes:

- Added `MERGE_PARITY_FIELDS` as a checked row contract.
- Added `merge_map.parity_review` to `python -m mantle optimize-audit`.
- Every merge candidate now records steelman rationale, caller matrix, authority/side-effect/
  security/lifecycle/proof dimensions, mode-complexity risk, required proof gates, and
  `safe_to_merge_now: false`.
- The duplicate-concept project model now points at the same parity review.
- Strict audit now requires one parity row for every merge candidate.
- `ALIGNMENT_MATRIX`, `FINAL_RECEIPT`, CLI output, and JSON output now summarize parity totals.
- Added invariant `OPT-11 merge-parity-review`.
- Updated public invariant-count anchors from 101 to 102.

Deletion decision: no files, functions, documents, or aliases were deleted. This pass converts
possible duplication into receipted review evidence and keeps all candidates unmerged until parity
and proof gates are satisfied.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 23 Receipt

Function served: protocol sections 15 and 16 require final verification coverage and blind
semantic comparison before any compressed or optimized machine doctrine can be accepted. The audit
already indexed configured proof commands, but did not expose these protocol obligations as
first-class matrices.

Changes:

- Added section-15 `final_verification` coverage to `python -m mantle optimize-audit`.
- Added section-16 `blind_semantic_comparison` coverage for machine-only doctrine elements:
  commands, modes, triggers, purposes, gates, invariants, blocks, procedures, receipt fields,
  hard fails, and implementation references.
- The audit records configured, observed, unobserved, and unverifiable proof surfaces without
  claiming that unrun checks passed.
- `ALIGNMENT_MATRIX`, `FINAL_RECEIPT`, and JSON output now summarize final verification and blind
  semantic comparison status.
- Strict audit now requires these matrices and row fields.
- Added invariant `OPT-10 final-verification+semantic`.
- Updated public invariant-count anchors from 100 to 101.

Deletion decision: no files were deleted. This pass adds final-proof accounting and deliberately
keeps the protocol result at `REVISE` until fresh final-suite and blind-evaluator evidence exists.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 22 Receipt

Function served: protocol section 14 requires a fresh whole-project A-O alignment audit after
file and subsystem passes. The existing alignment artifact had useful local references, but not the
full section-14 domain matrix.

Changes:

- Added `ALIGNMENT_AUDIT_DOMAINS` for section 14 A through O.
- Added `whole_project_alignment` to `python -m mantle optimize-audit`.
- The audit reports file, import/export, API, CLI, configuration, schema/storage, documentation,
  tests, AppAI, terminology, token dialect, duplication, version, security/privacy, and performance
  alignment.
- The matrix explicitly marks unresolved candidate review and unavailable token/benchmark data as
  `REVISE` or `UNVERIFIABLE` instead of claiming final pass.
- Strict audit now requires the A-O alignment rows.
- Added invariant `OPT-9 whole-project-alignment`.
- Updated public invariant-count anchors from 99 to 100.

Deletion decision: no files were deleted. This pass rebuilds alignment evidence from the current
tree; it does not claim the final protocol is complete.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 21 Receipt

Function served: protocol section 11 requires every name, path, command, field, mode, schema,
error-code, default, or public-behavior change to enqueue all possible ripples before a chunk or
file can be marked complete.

Changes:

- Added `REQUIRED_RIPPLE_SURFACES` and `RIPPLE_QUEUE_FIELDS` as checked ripple contracts.
- Added `ripple_queue` to `python -m mantle optimize-audit`.
- The queue records current working-tree changes and queued merge candidates, mapping them to
  imports, exports, CLI, config, schema, tests, examples, docs, implementation maps, hard-fail
  tables, error handlers, and other required ripple surfaces.
- Strict audit now requires ripple surfaces and row fields.
- Added invariant `OPT-8 ripple-queue`.
- Updated public invariant-count anchors from 98 to 99.

Deletion decision: no files were deleted. This pass records ripple obligations for future rewrites;
it does not resolve or claim completion for any semantic chunk.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 20 Receipt

Function served: protocol section 13 requires subsystem convergence passes after file completion.
Before any subsystem can be called converged, the audit needs a subsystem ledger covering imports,
exports, terminology, duplicates, config, schemas, docs/tests/examples, organ/lifecycle ownership,
SELF/OTHER boundaries, effect proofs, hard-fail coverage, performance, tokens, and file-completion
state.

Changes:

- Added `SUBSYSTEM_CONVERGENCE_FIELDS` as the checked subsystem row contract.
- Added `subsystem_convergence` to `python -m mantle optimize-audit`.
- The report groups files by subsystem and records convergence status, proof paths, pending chunk
  counts, token status, and section-13 alignment dimensions.
- Strict audit now requires the subsystem convergence ledger and required row fields.
- Added invariant `OPT-7 subsystem-convergence`.
- Updated public invariant-count anchors from 97 to 98.

Deletion decision: no files were deleted. This pass creates the subsystem convergence evidence
needed before future subsystem rewrites or completion claims.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 19 Receipt

Function served: protocol sections 9 and 12 require every file/chunk optimization pass to record
identified chunks, inspection state, proof paths, skipped chunks, token status, references,
imports/exports, duplicate state, tests, public behavior, and ripples before a file can be called
complete.

Changes:

- Added `FILE_COMPLETION_FIELDS` as the checked file-completion row contract.
- Added `file_completion_gate` to `python -m mantle optimize-audit`.
- The gate identifies conservative chunk units for Python, Markdown, structured data, text, and
  binary/media files.
- The gate explicitly reports pending chunk review instead of claiming whole-repository completion.
- Strict audit now requires the completion ledger and required row fields.
- Added invariant `OPT-6 file-completion-gate`.
- Updated public invariant-count anchors from 96 to 97.

Deletion decision: no files were deleted. This pass records the completion state needed before
future chunk rewrites or file-level completion claims.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 18 Receipt

Function served: protocol section 7 requires searching the whole repository for duplicate and
near-duplicate commands, functions, classes, procedures, and documents before any merge. The
previous merge map only listed exact duplicate hashes and a known CLI compatibility alias.

Changes:

- Added `MERGE_CANDIDATE_FIELDS` as the checked row contract for merge candidates.
- Added non-mutating merge-candidate analysis to `MERGE_MAP`, grouping similar public Python
  symbols and documentation topics by normalized keys.
- Each candidate records side-effect, security, lifecycle, proof, caller/test, decision, and
  reason fields.
- Candidates are marked `blocked`, `queued-review`, or `low-confidence`; this pass performs no
  merges.
- Fed candidate decisions into the project model's duplicate-concept map.
- Added invariant `OPT-5 merge-candidate-analysis`.
- Updated public invariant-count anchors from 95 to 96.

Deletion decision: no files were deleted. This pass is prerequisite evidence for future safe
merges; it explicitly blocks or queues candidates instead of collapsing them by name similarity.

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

## Pass 33 Receipt

Function served: the whole-repository protocol says cache/build output must be inventoried and
reviewed by ignore/build-output rules, not optimized as production source. Editable Python installs
can create `*.egg-info` files under `src/`, which previously inherited the `src/` production-source
category.

Changes:

- Added Python packaging `*.egg-info` path recognition to the optimization inventory.
- Classified those files as `O cache/build output`.
- Marked build output as generated, inventory-only, and ineligible for semantic chunk rewriting.
- Strengthened `OPT-1` to prove `src/*.egg-info` metadata maps to cache/build output and
  inventory-only disposition.

Deletion decision: no files or features were deleted. The prior `src/` fallback served broad source
classification; this pass narrows only generated packaging residue while preserving tracked source
coverage and all certification gates.

Proof path: `PYTHONPATH=src python -m mantle check`.

## Pass 32 Receipt

Function served: GitHub Action emails showed the online `Zombie Body Audit` failing in `OPT-14`
even though the update commits had reached `main`. The completion-condition audit needed to prove
tracked source inventory without treating harmless generated or untracked CI residue as missing
source.

Changes:

- Updated the `every repository file was inventoried` completion row to pass when every tracked
  file is present and inventoried.
- Added `extra_untracked` evidence so generated or untracked residue remains visible.
- Strengthened `OPT-14` to prove tracked coverage, explicit extra-file accounting, and no missing
  tracked files.

Deletion decision: no files or features were deleted. The stricter equality check served as a
clean-worktree guard, but that function is better covered by explicit evidence plus existing git
status, receipt, and certification checks.

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
