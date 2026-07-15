# Changelog

All notable release-level changes are documented here.

## [1.3.0] — 2026-07-15

### Added

- Reversible, receipt-backed MIND fusion and authority-free defusion lifecycle.
- Exactly one fixed 600-second cognitive scheduler per fused resident, with separate queued
  nociceptive wakeups.
- Hermes-native cognition through the host-owned `PluginContext.llm` provider/model abstraction.
- Rolling token/cost budgets, bounded retries and backoff, request timeouts, outage handling,
  serialized cognition, and redacted usage receipts.
- Distinct authenticated operator and guardian approval verification for production fusion.
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
