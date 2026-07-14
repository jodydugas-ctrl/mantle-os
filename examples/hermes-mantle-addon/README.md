# Hermes Mantle Addon

A standalone Hermes Agent plugin that hosts a deterministic Mantle Body beside Hermes without modifying Hermes core.

## Current vertical slice

Version `0.2.0` provides:

- the read-only `mantle_status` tool;
- one persistent Mantle Body per active Hermes profile;
- explicit contracts for Heart, Genome, Nervous System, Senses, Immune, Limbs, Memory, Brain, and Reproduction;
- a sealed Primer and cryptographic SELF minted once at Body birth;
- observer-only integration through seven documented Hermes hooks;
- redacted/derived Senses records rather than raw prompts, tool arguments, or tool results;
- a Body heartbeat after each observed hook, with an atomic durable checkpoint by default (or deferred to session end/finalization when `checkpoint_each_turn=false`);
- Action Execution Proofs for observed `post_tool_call` outcomes;
- Immune events for observed tool failures;
- fail-open hook behavior so instrumentation faults do not change Hermes control flow.

The Brain is present but dormant and unfused. The resident has **not** passed its addon-specific Stage-1 gate. MIND fusion, mutating addon tools, and reproduction activation remain unauthorized.

## Registered hooks

- `on_session_start`
- `on_session_end`
- `on_session_finalize`
- `pre_llm_call`
- `post_llm_call`
- `pre_tool_call`
- `post_tool_call`

All callbacks are observers and return `None`. Disabling the plugin prevents their registration and restores ordinary Hermes behavior.

## Durable state

By default, profile-scoped Body and VCW state is stored under:

```text
$HERMES_HOME/mantle/organisms/<profile>/
```

The immutable defaults are recorded in `config/defaults.json`. Raw prompts, raw tool arguments, raw results, and raw host correlation identifiers are prohibited in this observer release. Resident snapshots are written into owner-only staging directories under an interprocess profile lock, verified, and atomically published; sealed reload rejects missing or invalid SELF seals. The vendored runtime uses an origin-checked private Python package namespace and does not trust preloaded global or private-alias modules.

## Layout

- `plugin.yaml` — Hermes plugin manifest
- `__init__.py` — tool and hook registration
- `mantle_addon/` — immutable configuration, Primer, storage boundary, vendored-runtime loader, Body factory, and hook adapter
- `schemas.py` — model-facing tool schemas
- `tools.py` — read-only tool handlers
- `config/defaults.json` — deterministic resident defaults
- `tests/` — standard-library behavior and boundary tests
- `vendor/mantle-os/` — complete tracked Mantle OS snapshot at commit `235a0369503f1de0072739bade3e2b27a88a33d7`
- `docs/assimilation/` — reviewed Phase-0 inventory, nine-organ map, and host census
- `VENDOR_PROVENANCE.md` — source commit, snapshot-integrity receipt, and certification result

## Test

```bash
cd "/home/aibox/Hermes Mantle Addon"
python3 -m unittest discover -s tests -v
~/.hermes/hermes-agent/venv/bin/python tests/verify_real_plugin.py
PYTHONPATH=vendor/mantle-os/src python3 -m mantle check --fast
```

`tests/verify_real_plugin.py` creates disposable enabled and disabled Hermes homes and exercises the real `PluginManager` without installing into the active profile.

## Doctrine receipt

- **WHAT:** built the deterministic, profile-resident Body foundation and registered seven observer hooks after explicit Phase-0 authorization.
- **WHY:** establish Body-before-MIND residency with evidence-bearing boundaries before any cognition or mutating capability.
- **EVIDENCE:** behavior tests, complete vendored Mantle certification, reviewed Phase-0 census, and isolated real-PluginManager execution.
- **CONFIDENCE:** high for Body birth/reload, storage confinement, observer registration, redacted Senses intake, tool AEPs, and fail-open behavior; Stage-1 remains unclaimed.
- **NEXT:** add addon-specific Stage-1 probes and diagnostic receipts, expand host-version/platform compatibility coverage, and only then produce a MIND-readiness report.
- **RISKS:** vendored Mantle can drift from upstream; host activity outside registered hooks remains external; `post_tool_call` proves observed host outcomes but does not independently re-execute or verify the effect.
- **FILES:** project changes remain confined to this directory; the Hermes and source Mantle repositories are reference-only.
- **OPEN GAPS:** approval hooks, subagent hooks, gateway ingress, dual-flush/atexit proof, addon-specific Stage-1, and reconstruction proof are not yet implemented.
- **OPERATOR DECISION:** observer Body and documented hook registration approved on 2026-07-13; MIND fusion, mutating tools, and reproduction activation excluded.
- **GUARDIAN DECISION:** Phase-1 foundation may run as an observer; no claim of MIND readiness or fusion is permitted.
