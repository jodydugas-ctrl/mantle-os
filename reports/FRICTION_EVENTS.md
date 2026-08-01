# Mantle 2 implementation friction ledger

This is an append-only engineering ledger. Each event records the observed friction,
the local mitigation, and the platform change that would prevent recurrence.

| ID | Friction point | Mitigation used | Prevention / MantleOS change |
| --- | --- | --- | --- |
| FRICTION-001 | The requested isolated branches were not created by an earlier combined shell invocation, so work initially remained on `main`. | Verified each repository independently and created the exact local branches from the pinned SHAs before editing. | Bootstrap should assert branch name and base SHA before allowing a write. |
| FRICTION-002 | The checked-in virtual environments pointed at removed Python installations; system Python lacked project imports/dependencies. | Used `PYTHONPATH=src` with the available interpreter for stdlib Mantle gates; recorded missing product dependencies rather than installing globally. | Add a deterministic `mantle doctor` preflight that reports broken venvs and required local extras. |
| FRICTION-003 | The first generated 98-row matrix patch was rejected because generated rows lacked patch prefixes. | Re-issued the same content through `apply_patch` with valid hunk lines. | Add a patch-builder helper for generated tracked matrices and validate it before applying. |
| FRICTION-004 | The new resident loop initially had no shared typed contracts, so host integrations could drift into custom command dictionaries. | Added `mantle.contracts`, `ResidentRuntime`, typed fusion authorization, and canonical Body commands. | Ship resident runtime and dispatcher as the only maintained integration seam; certify command-contract version. |
| FRICTION-005 | Safe spore inspection could have printed embedded conversation/system-like text through the existing `read` command. | Added manifest-only `spore inspect`; raw conversation requires `--include-conversation` and the artifact is explicitly inert. | Make safe inspection the default public operation and require an explicit raw-content opt-in. |
| FRICTION-006 | Product-side terminal tests use placeholder nests and may not have Mantle importable, while live integrations must use the shared dispatcher. | Added a narrow standalone fallback and live dispatcher path; no global install was used. | Provide a pinned Mantle runtime fixture for product tests and make drift visible in status. |
| FRICTION-007 | Existing full-gate output is long-running and tool output can truncate, hiding final results. | Used bounded compile/focused commands and retained the final 109/109 result. | Stream child gate results to structured artifacts and expose partial/timeout states explicitly. |

The product’s detailed Organize friction register remains at
`C:/Users/jodyd/mantle-workspaces/organize-appai/reports/FRICTION_LOG.md` and is
referenced by the consolidation matrix.

