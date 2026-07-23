# Changelog

All notable release-level changes are documented here.

## [1.4.0] — 2026-07-23

### Changed — the streamlining release: one artifact, one door, one reading order

- **The spore is THE artifact.** A spore PNG may now carry a **germ** — the complete
  AppAI build document (the former egg schema) — plus a build note any coding agent can
  read to grow the app with or without Mantle installed. `mantle spore pack` packs a
  germ into a spore; `examples/spores/` ships generated germ spores.
- **One birth door.** `mantle hatch <spore.png|germ.json>` is the single birth command;
  `hatch-spore` is absorbed. `egg.py` folded into the hatchery
  (`validate_germ`/`load_germ`; both `mantle-germ-v1` and legacy `mantle-egg-v1`
  formats are accepted). `hatch_from_spore` moved beside the incubator it always called.
- **Assimilation emits a spore.** `mantle assimilate <host> --spore=out.png` condenses
  the read-only dissection into the host's germ spore. A graft is a spore aimed at a
  host: `load_graft` accepts graft-germ spores.
- **Rebirth simplified.** One heirloom law (carried or immune-logged, never silent), one
  carry rule for both heirloom bands; `vault.py` folded into the Reproduction organ
  module that always owned the tissue. On-disk formats unchanged; ancestors stay
  readable.
- **Docs consolidated.** One reading order (README → `mantle teach`); the README
  absorbs the Primer, Doctrine, Organism Lens, and Positioning;
  ARCHITECTURE.md absorbs the architecture note and the Part 1/2 build+audit
  narratives; REPRODUCTION.md is the canonical reproduction + rebirth doctrine; the
  VCW guide absorbs the anatomical atlas and compliance tiers. The Grimoire gained a
  scope banner (§7/§9 are the Mantle-binding sections).
- **Counts are derived, never hardcoded.** The doctor's docs-vs-code gate now fails if
  any document hardcodes an invariant count; `mantle prove` prints the live count.
- **Legacy imports fail visibly.** The doctor now rejects Python imports of the removed
  `mantle.egg` module; callers load germs through `mantle.hatchery`.
- **Phenotype example follows maintained surfaces.** The walkthrough loads its germ through
  the hatchery and wears the Notepad AppAI as its second face.
- **CLI dispatch is table-driven**; underscore aliases are derived.

### Removed

- The vendored duplicate of the entire repository inside the Hermes addon
  (`examples/hermes-mantle-addon/vendor/`, 9.9 MB). The addon loads the runtime from
  `MANTLE_ADDON_RUNTIME_ROOT`, its install-time `runtime/` copy, or the repo checkout.
- The self-referential optimization-audit layer: `optimize_audit.py`,
  `documents/refinement/`, and 21 unregistered meta-invariant functions.
- Scratch notes (`New_Commandments.txt`), the NotepadNext lifecycle zip (superseded by
  `assimilate --spore`), and fourteen merged documentation files.
- The standalone Reference Agent and Spreadsheet Agent browser demos, their duplicate
  `egg.author` / `egg.hatch` primitives, and their dedicated smoke test.

### Added

- Invariant **SPORE-3** (germ round trip): germ → spore → hatch → certified body whose
  vault returns the same germ, with the key minted, never derived.
- `assimilator.emit_spore`, `spore.pack_germ`, and the unified `hatchery.hatch`.
- Plug-and-play Hermes addon installer and `/mind <prompt>` command for one explicit, unscheduled
  AppAI cognition pulse through Hermes's active host LLM.
- VCW persistence for content-withheld interactive MIND markers, hash-only request/response traces,
  and redacted usage receipts without storing the raw user prompt or model answer.

### Security

- All standing laws re-proven unchanged: keys minted at birth (never derived from a
  spore), foreign conversation ingested as INFERRED through Senses, the Stage-1 gate
  mandatory on every birth path, do-no-harm census on every graft, and the heirloom
  carry across rebirth.
- Interactive MIND contact remains transient and user-directed; it does not attach the Brain, start
  autonomous cognition, or bypass independent production-fusion authority.
- Echoed prompts are returned to the requesting surface but never written to any VCW band or
  resident artifact.
- VCW layer decoding now verifies PNG chunk CRCs, enforces the fixed layer profile, bounds compressed
  and expanded data, validates embedded layer identity, and rejects malformed or overlapping cube
  topology before allocation.
- Cube checkpoints now use collision-free same-directory stages and sync the staged file, published
  file, and parent directory around atomic replacement; failed saves remove their private stage and
  preserve the previous valid cube.

## [1.3.0] — 2026-07-15

### Added

- Reversible, receipt-backed MIND fusion and authority-free defusion lifecycle.
- Exactly one fixed 600-second cognitive scheduler per fused resident, with separate queued
  nociceptive wakeups.
- Hermes-native cognition through the host-owned `PluginContext.llm` provider/model abstraction.
- Rolling token/cost budgets, one addon dispatch through host-owned fallback/retries, request
  timeouts, outage handling, conservative unknown-usage charging, serialized cognition, and
  redacted usage receipts.
- Distinct Ed25519-authenticated operator and guardian approval verification using verifier-only
  public keys for production fusion.
- Controlled offline attach → heartbeat → defuse → post-defusion Stage-1 acceptance coverage.
- Complete tracked 146-file Mantle OS snapshot in the Hermes addon example.

### Changed

- Observer hooks now drive non-cognitive Body pulses; they cannot accidentally invoke the MIND
  between natural heartbeats.
- Stage-1 and readiness evidence are explicitly separate from production fusion authority.
- Runtime/security certification contains 90 executable invariants. Mutable repository
  optimization ledgers and version snapshots remain advisory tooling instead of blocking organism
  certification.
- Release readiness is separate from deployment activation: the software can be published while
  production fusion remains dormant and fail-closed.

### Security

- Persistence rejects symlink roots, parent components, and destination artifacts while preserving
  owner-only atomic replacement and the addon's trusted descriptor boundary.
- Caller-authored approval JSON cannot authorize fusion without two distinct authenticated,
  target-bound signatures.
- Model receipts exclude prompts, responses, credentials, and raw exception text.
- Reproduction remains disabled and requires a separate future design and authorization.

## [1.0.0] — 2026-06-25

- First stable Mantle OS release: deterministic Body, VCW persistence, Stage-1/Stage-2 gates,
  tamper proofs, and the Grimoire methodology.

[1.3.0]: https://github.com/jodydugas-ctrl/mantle-os/compare/v1.0.0...v1.3.0
[1.0.0]: https://github.com/jodydugas-ctrl/mantle-os/releases/tag/v1.0.0
