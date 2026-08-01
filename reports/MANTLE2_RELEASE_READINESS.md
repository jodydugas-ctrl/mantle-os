# MantleOS 2.0.0rc1 local release readiness

## Repositories

- MantleOS branch: `codex/mantle-2-platform-consolidation`
- MantleOS base: `c9d6274c6c2e562fd8c1630dd9395197fe60ad6e`
- MantleOS scanner/lifecycle implementation commit: `dcfef68`
- Organize.AppAI branch: `codex/organize-appai-mantle2`
- Organize.AppAI base: `8ef42a4dbe1991d197c65862825634b0c252af16`
- Organize.AppAI final implementation commit: `861efe8`

No branch was pushed and no online repository was changed.

## Verification

| Check | Result |
| --- | --- |
| Mantle compileall | PASS |
| Mantle contract regression script | PASS (6 checks) |
| `python -m mantle prove` | PASS (109/109) |
| `python -m mantle audit` | PASS |
| `python -m mantle audit-mind` | PASS |
| Mantle full pytest suite | PASS (18 passed, 1 skipped) |
| `python -m mantle check` | PARTIAL (13 passed, 1 skipped, 0 failed; not a certification) |
| Organize source compilation | PASS |
| Organize full dependency suite | PASS (299 passed, 4 skipped) |

## Delivered

- Shared evidence/claim contracts and GroundedAnswer boundary.
- Canonical Mantle resident protocol v2 command surface, including `/mind`,
  `/provider-test`, and `/evidence`.
- Typed fusion authorization builder.
- Safe inert spore inspection with explicit raw-conversation opt-in.
- Target-bound lifecycle authorization/journal primitives.
- Body action execution proof type requiring post-state verification.
- Explicit substrate coverage states and a pure-stdlib Rust fallback scanner.
- Shared native/Qt fallback scanner covering C/C++ bodies, constructor initializer
  lists, balanced Qt connections, helper-wired actions, UI XML, QRC resources, and
  CMake topology.
- Target-bound, one-shot lifecycle authorization enforced at external hatch and
  graft boundaries, with staged journals and atomic promotion.
- Organize terminal migration to the shared dispatcher with deterministic fallback.
- Organize assist GroundedAnswer projection and Mantle 2 status fields.
- Tracked consolidation matrix and friction ledger.

## Known limitations / blockers

This is a release-preparation candidate, not a certification claim. The final full Mantle
check is `PARTIAL` because its B-47 resident-host scenario is not applicable to the
repository fixture used by the gate. Native C/C++ prefers installed tree-sitter evidence
and retains a pure-stdlib fallback; unsupported or truncated constructs remain explicit
coverage gaps. Real resource-offer credential adapters, face attestation, lifecycle
resume, and complete NotepadNext migration remain matrix work. Exact final local commit
IDs are written after the tracked report commit to the untracked local gate manifest
under `work/`.
