# Hermes Mantle Addon

A standalone Hermes Agent plugin that wraps Hermes with a deterministic Mantle autonomic Body without modifying Hermes core.

## Current vertical slice

Version `0.4.0` provides:

- the read-only `mantle_status` tool;
- the bounded `mantle_record_discovery` mutation, which writes only an explicitly unverified idea to `discoveries` through a Limbs `ControlBridge`;
- one persistent Mantle Body per active Hermes profile and Hermes home, resolved at each invocation;
- explicit contracts for Heart, Genome, Nervous System, Senses, Immune, Limbs, Memory, Brain, and Reproduction;
- a sealed Primer and cryptographic SELF minted once at Body birth;
- observer-only integration through twelve documented Hermes hooks, including approval lifecycle, subagent lifecycle, and gateway ingress;
- redacted/derived Senses records rather than raw prompts, tool arguments, tool results, approval commands, subagent goals, or gateway messages;
- a Body heartbeat after each observed hook, with an atomic durable checkpoint by default (or deferred to session end/finalization when `checkpoint_each_turn=false`);
- Action Execution Proofs for observed `post_tool_call` outcomes;
- Immune events for observed tool failures;
- fail-open hook behavior so instrumentation faults do not change Hermes control flow.

The Brain is present but dormant and unfused. Isolated addon and framework Stage-1 receipts pass, but the real plugin resident remains uncertified. A fail-closed Phase-2 configuration transition exists, but the live `NOT_READY`/`DEFERRED` evidence cannot satisfy it and no runtime fusion lifecycle exists. MIND fusion and reproduction activation remain unauthorized. The sole model-facing mutation is confined to unverified discoveries; it cannot write facts, Primer, Genome, immune state, or host files.

## Bounded mutation

`mantle_record_discovery` accepts one non-empty idea of at most 2,000 characters. The runtime maps that control on both Senses and Limbs, validates it inside the `ControlBridge`, writes a BODY-authored `INGESTED` entry with `verified=false` and `confidence=inferred`, records a BODY-authored Action Execution Proof, and checkpoints atomically. Failed validation produces a failed proof and no discovery. The tool response never echoes the idea.

## Containment verification

`mantle_addon.containment.run_containment()` runs only against an isolated verification resident and emits an eleven-row JSON-serializable receipt:

- C-01/C-02 prove the single-field schema and Senses/Limbs bridge;
- C-03 through C-06 submit adversarial band, authority, path, JSON, and script-shaped input, proving only `discoveries` plus the BODY proof change and the response does not echo input;
- C-07 through C-09 prove the vendored MIND write surface is exactly `thoughts` plus `brain`, every other band is refused and immune-recorded, and only the allowed bands accept MIND writes;
- C-10 proves uncertified fusion is refused and MIND Special Instruction proposals stay inert;
- C-11 proves verified reload, BODY proof authorship, and no writes elsewhere in the isolated verification scope.

Run it with:

```bash
python tests/verify_containment.py
```

The verifier uses an OS-safe temporary directory and deletes the verification resident afterward.

## Registered hooks

- `on_session_start`
- `on_session_end`
- `on_session_finalize`
- `pre_llm_call`
- `post_llm_call`
- `pre_tool_call`
- `post_tool_call`
- `pre_approval_request`
- `post_approval_response`
- `subagent_start`
- `subagent_stop`
- `pre_gateway_dispatch`

All callbacks are observers and return `None`. In particular, Mantle cannot approve or deny commands, alter subagent dispatch, or skip/rewrite gateway messages. Disabling the plugin prevents their registration and restores ordinary Hermes behavior.

## Durable state

By default, profile-scoped Body and VCW state is stored under:

```text
$HERMES_HOME/mantle/organisms/<profile>/
```

The immutable defaults are recorded in `config/defaults.json`. Raw prompts, raw tool arguments, raw results, and raw host correlation identifiers are prohibited in this observer release. Resident snapshots are written into owner-only staging directories under an interprocess profile lock, verified, and atomically published; sealed reload rejects missing or invalid SELF seals. The vendored runtime uses an origin-checked private Python package namespace and does not trust preloaded global or private-alias modules.

## Layout

- `plugin.yaml` — Hermes plugin manifest
- `__init__.py` — tool and hook registration
- `mantle_addon/` — immutable configuration, Primer, storage boundary, vendored-runtime loader, Body factory, hook adapter, and reproducible C-01..C-11 containment audit
- `schemas.py` — model-facing tool schemas
- `tools.py` — read-only diagnostics plus the bounded discovery mutation handler
- `config/defaults.json` — deterministic resident defaults
- `tests/` — standard-library behavior and boundary tests
- `vendor/mantle-os/` — complete 146-file non-addon Mantle OS 1.3.0 snapshot, reproducibly checked by `scripts/sync_vendor.py --check`
- `docs/assimilation/` — reviewed Phase-0 inventory, nine-organ map, and host census
- `docs/FUSION_DECISIONS.{md,json}` — human and machine-readable operator/guardian decisions
- `docs/MIND_READINESS.{md,json}` — Step-9 evidence report; current verdict `NOT_READY`
- `VENDOR_PROVENANCE.md` — source commit, snapshot-integrity receipt, and certification result

## Test

```bash
cd examples/hermes-mantle-addon
python3 -m unittest discover -s tests -v
~/.hermes/hermes-agent/venv/bin/python tests/verify_real_plugin.py
~/.hermes/hermes-agent/venv/bin/python tests/verify_containment.py
PYTHONPATH=vendor/mantle-os/src python3 -m mantle check --fast
```

`tests/verify_real_plugin.py` creates disposable enabled and disabled Hermes homes and exercises the real `PluginManager` without installing into the active profile.

## Fusion decision gate

[`docs/FUSION_DECISIONS.json`](docs/FUSION_DECISIONS.json) is the machine-readable authority and [`docs/FUSION_DECISIONS.md`](docs/FUSION_DECISIONS.md) is its human-readable explanation. Both operator and guardian approve the current bounded Phase-1 runtime while explicitly **deferring MIND fusion**. The Step-9 [`MIND_READINESS.json`](docs/MIND_READINESS.json) verdict is **NOT READY**. Roadmap continuation, runtime approval, silence, enthusiasm, or a future readiness PASS cannot substitute for separate explicit operator and guardian fusion approvals.

## Roadmap

| # | Step | Status |
|---|------|--------|
| 1 | Addon-specific Stage-1 gate | ✅ Complete |
| 2 | Dual-flush / atexit proof | ✅ Complete |
| 3 | Reconstruction proof | ✅ Complete |
| 4 | Hermes-routed MIND transport adapter | ⛔ Blocked — current OpenAI-compatible prototype bypasses Hermes provider routing |
| 5 | Approval, subagent, and gateway observer hooks | ✅ Complete |
| 6 | Bounded mutating addon tool | ✅ Complete |
| 7 | Adversarial containment verification | ✅ Complete |
| 8 | Operator and guardian fusion-decision updates | ✅ Complete — both fusion decisions DEFERRED |
| 9 | Final MIND-readiness report | ✅ Complete — original verdict NOT READY |
| 10 | Complete Mantle OS repository alignment: verify every file against the plugin architecture and improve Mantle OS using lessons from building the plugin | ✅ Complete — 339-file receipt PASS; fusion and reproduction still unauthorized |

## Doctrine receipt

- **WHAT:** built the deterministic profile-resident Body, twelve observer hooks, one bounded discovery mutation, and an eleven-row adversarial containment audit.
- **WHY:** establish Body-before-MIND residency while permitting the smallest useful durable host-to-Body knowledge path without granting fact, instruction, Genome, immune, reproduction, or host-file writes.
- **EVIDENCE:** 96/96 addon tests, both tools through Hermes's real dispatcher, 14/14 addon Stage-1 probes, 20/20 target framework rows (21/21 in the reborn standalone demo), 111/111 invariants, 7/7 Stage-2 technical rows, 11/11 containment rows, 12/12 real observer hooks, 146-file vendor parity, and the 339-file alignment receipt pass.
- **CONFIDENCE:** high for the bounded Phase-1 addon and repaired core paths covered by the matrix. MIND readiness remains explicitly NOT READY.
- **NEXT:** separately scope B-03, the reversible addon fusion lifecycle; do not fuse MIND or activate reproduction.
- **RISKS:** the supported B-02 transition requires target-bound Stage-1, READY, and dual-authority evidence but no reversible addon fusion lifecycle exists; the addon lacks a ten-minute scheduler, Hermes-native provider route, and complete heartbeat budget/outage policy; discovery text is intentionally durable and callers must not submit secrets; host activity outside registered hooks remains external.
- **FILES:** source, docs, tests, examples, workflows, package metadata, and the non-recursive vendor snapshot were aligned in Step 10.
- **OPEN GAPS:** five blockers remain in the readiness set; a future READY report and new explicit target-bound fusion approvals remain incomplete.
- **OPERATOR DECISION:** current bounded Phase-1 runtime APPROVED; MIND fusion DEFERRED. Continuation does not authorize fusion or reproduction.
- **GUARDIAN DECISION:** current bounded Phase-1 runtime APPROVED; MIND fusion DEFERRED until readiness evidence is complete and both roles issue separate explicit approvals.
