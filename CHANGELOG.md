# Changelog

All notable release-level changes are documented here.

## [Unreleased]

### Added

- Plug-and-play Hermes addon installer and `/mind <prompt>` command for one explicit, unscheduled
  AppAI cognition pulse through Hermes's active host LLM.
- VCW persistence for content-withheld interactive MIND markers, hash-only request/response traces,
  and redacted usage receipts without storing the raw user prompt or model answer.

### Security

- Interactive MIND contact remains transient and user-directed; it does not attach the Brain, start
  autonomous cognition, or bypass independent production-fusion authority.
- Echoed prompts are returned to the requesting surface but never written to any VCW band or
  resident artifact.

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
