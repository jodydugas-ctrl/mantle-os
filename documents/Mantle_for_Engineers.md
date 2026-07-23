# Mantle OS for Engineers

Non-normative translation layer for engineers and AI agents.

This document describes Mantle OS in systems language. It does not replace the README,
PRIMER, Grimoire, or organ-oriented doctrine. The organic vocabulary is the design language
of the project; this file maps that language to implementation boundaries so maintainers
can reason about the code quickly.

When this file and source code disagree, the source code wins.

## 1. System Summary

Mantle OS is a Python reference implementation for deterministic application runtimes that
can later be connected to an LLM under explicit containment rules.

The implementation has two phases:

- **Phase 1:** deterministic runtime only. No model call is required for certification.
  The runtime receives inputs, records state, executes predefined handlers, persists data,
  verifies integrity, and emits audit evidence.
- **Phase 2:** optional LLM integration. The LLM is connected through a bounded transport
  and containment layer. It can write only to designated cognition bands and propose
  actions; deterministic runtime code still applies, verifies, and records external effects.

The repository also supports read-only analysis of existing applications. That path scans a
host project, classifies symbols into runtime responsibilities, emits evidence, and can
produce a portable build artifact without modifying the host.

## 2. Term Mapping

| Mantle term | Engineering meaning | Primary implementation |
| --- | --- | --- |
| AppAI | Managed application instance | `src/mantle/core/organism.py` |
| Body | Deterministic runtime that runs without an LLM | `src/mantle/core/`, `src/mantle/organs/` |
| MIND | Optional model-backed reasoning layer | `src/mantle/mind/` |
| Brain | Runtime slot that holds a fused MIND | `src/mantle/organs/brain.py` |
| Organ | Runtime module with a declared contract | `src/mantle/organs/contract.py` |
| Reflex | Deterministic handler; no model call | organ modules and `SignalBus` subscribers |
| Senses | Inbound input boundary | `src/mantle/organs/senses.py` |
| Limbs | Outbound action boundary | `src/mantle/organs/limbs.py` |
| Immune | Error, integrity, and policy violation boundary | `src/mantle/organs/immune.py` |
| Genome / Primer | Identity and immutable bootstrap data held outside the cube | `src/mantle/core/body.py` |
| VCW cube | Append-only PNG-layer storage substrate | `src/mantle/vcw/` |
| Band | Named range of VCW storage layers | `src/mantle/vcw/bands.py` |
| Spore | Portable PNG artifact | `src/mantle/spore.py` |
| Germ | Declarative build document carried by a spore or JSON file | `src/mantle/hatchery.py` |
| Anchor | Additive resident runtime in an existing host project | `src/mantle/anchor.py` |
| Graft | Non-destructive patch artifact aimed at a named host | `src/mantle/graft.py` |

Use Mantle terms when naming existing symbols. Use the engineering meaning when explaining
behavior to maintainers who are not using the conceptual framing.

## 3. Runtime Modules

The canonical organ list is source-defined by `ORGAN_ORDER` in
`src/mantle/core/organism.py`. There are nine organs:

| Organ | Responsibility |
| --- | --- |
| Heart | Fixed runtime pulse, checkpointing, scheduled cognition wakeups, nociceptive wakeups |
| Genome | Identity and lineage facade over the Body store |
| Nervous | Reference resolution and deterministic context assembly |
| Senses | Input intake, classification, redaction, human surface map |
| Immune | Failure boundary, integrity scans, quarantine/tombstone, SELF/OTHER checks |
| Limbs | Outbound dispatch, action proofs, control bridge, skill cultivation gate |
| Memory | Remember/recall, memory bands, compaction and pressure handling |
| Brain | Dormant Phase-1 slot; Phase-2 MIND holder |
| Reproduction | Seed/graft verbs, seed vault, spore heirlooms, lineage duty |

High-level runtime flow:

```text
external input
  -> Senses.inhale(...)
  -> SignalBus event dispatch
  -> deterministic handlers
  -> VCW append or Body state update
  -> optional outbound request
  -> Limbs dispatch and action proof
  -> checkpoint
```

Failure flow:

```text
exception, invalid reference, policy violation, integrity failure
  -> Immune.event(...)
  -> redacted immune log entry
  -> optional quarantine/tombstone/distress signal
  -> fail-open behavior for host instrumentation
```

## 4. Storage Semantics

The VCW cube is append-only storage implemented as PNG layers. Records are assigned to named
bands. Entries are hashed, and persistence uses staged writes followed by verification and
atomic replacement.

Rules that matter for implementation:

- Append new records instead of mutating historical records.
- Tombstone or quarantine old records instead of deleting them silently.
- Use band declarations from `src/mantle/vcw/bands.py`; do not invent ad hoc storage.
- Keep identity and primer data in `Body`, not in the VCW cube.
- Keep secrets out of input and error logs by using the existing redaction boundary.
- Preserve sealed ancestors as read-only storage.
- Do not hardcode invariant counts in documentation; `python -m mantle prove` derives them.

The standalone normative cube implementation is `examples/vcw/vcw_cube.py`.

## 5. Primer and Body Store

`src/mantle/core/body.py` is the authoritative source for primer behavior.

At birth, `Body.birth(...)` writes identity, truths, and commandments into `_primer` and then
sets `_primer_sealed = True`. A later call to `birth(...)` raises `PermissionError`. The
primer is therefore immutable after birth for that generation and is held outside the VCW
cube in the Body store. Commandments also seed the mutable immunization working copy.

The Body also holds the genesis key, key fingerprint, lineage index, special instructions,
and immunization records. The genesis key is persisted in `body.json`, never in the cube,
and is excluded from the model boot order and self record.

## 6. MIND Integration Contract

The MIND write surface is source-defined in `src/mantle/mind/containment.py`:

```python
WRITE_SURFACE = ("thoughts", "brain")
```

`guarded_write(...)` refuses every other band, records an immune event, and raises
`PermissionError`. The Stage-2 audit verifies this by attempting a write to `facts` and
expecting refusal plus immune logging.

The model transport contract is `model(prompt: str) -> str`. The OpenAI-compatible adapter in
`src/mantle/mind/transport.py` returns that callable shape. Usage, cache, generation, and
request-hash data are sidecar attributes on the callable, not a tool-calling interface.

Phase-2 flow:

```text
Nervous.assemble()
  -> already-resolved, already-veiled snapshot
  -> Mind.think(...)
  -> model(prompt) -> text
  -> trace request/response hashes in brain
  -> write inferred reflection to thoughts
  -> optional proposed intent
  -> Body/Limbs validation and application
```

The MIND may propose special instructions and candidate skills. The Body applies special
instructions through `Limbs`, and candidate skills must pass the sandbox, trial, hash,
signature, capability, and provenance gates before calcification.

## 7. Nociception and Scheduling

Nociception is not a repeated-fault heuristic. It is implemented by explicit event wiring:

- `Senses` emits `significant`; `Heart.on_significant(...)` stores a pending wake reason.
- `Immune.event(...)` emits `distress` for fixed severe event kinds in
  `AUTONOMIC_KINDS`; `Heart.on_distress(...)` stores the stressor coordinates.
- `Heart.pain(...)` issues an immediate unscheduled pulse.
- `Heart.schedule_pulse(...)` queues a future one-shot cognition wake.

Severe immune kinds currently include `integrity`, `organ_overreach`,
`mind_write_refused`, `foreign_rejected`, `autoimmune_risk`, `unresolved_ref`,
`ancestor_tamper`, and `flush_failed`.

These wakeups add stressor-anchored cognition when a Brain is fused. They do not replace
the natural Phase-2 baseline pulse.

## 8. Extended Module Map

The following descriptions are summarized from module docstrings and source:

| Module | Engineering summary |
| --- | --- |
| `spore.py` | Implements the spore PNG format: visible artifact, embedded state, optional germ payload, append/read/render/verify operations. |
| `hatchery.py` | Single birth path for germ-bearing spores, bare spores, and germ JSON files. Validates data, wires runtime declarations, runs proving cases, and requires Stage-1 certification. |
| `reproduction.py` | Routes the two reproduction methods: independent seed spores and dependent graft/anchor residency paths. |
| `organs/reproduction.py` | Runtime organ for seed/graft verbs, seed vault reconstruction, spore heirlooms, and lineage carry across rebirth. |
| `anchor.py` | Read-only host dissection followed by additive `.mantle/` resident creation; verifies host files are unchanged. |
| `graft.py` | Validates graft germs and applies them to a workspace copy of a named host; live weaving uses fail-open reversible wrappers. |
| `symbiosis.py` | Append-only credits ledger for model-call metering; records grants, spends, value, and starvation refusal. |
| `mem.py` | Keyless knowledge cube for sharing inferred knowledge and microcode-as-data; foreign microcode must be sandbox-tested and re-derived. |
| `compiler.py` | Validates MIND-proposed app-band genomes and adopts them only at chosen rebirth; also provides a host memory bridge backed by a keyvalue VCW band. This is not arbitrary self-modifying storage. |
| `ganglia.py` | Bounded parallel limbs that write progress telemetry into a VCW band and fail open on task errors. |
| `ghost.py` | Cache-ghost substrate for spore state over a provider prompt-cache abstraction, while retaining the PNG as the durable source. |
| `ghost_http.py` | Optional pure-stdlib HTTP adapter for real prompt-cache substrates; imported by nothing else. |
| `ingestion.py` | Deterministic ingestion of conversation lines through Senses into facts, discoveries, or Body-applied special instructions. |
| `doctor.py` | Deployment checkup for cube integrity, ancestor seals, genesis key consistency, nonnegative ledger, and docs-vs-code coherence. |
| `phenotype.py` | Stores SELF-encrypted front-end faces in private VCW bands and returns boot manifests for a host to render. |
| `applet_body.py` | Stores external projects as inert applet capsules inside the VCW; source is not executed or certified as a Body. |
| `face.py` | Deterministic PNG state portrait rendered with the repository PNG codec. |

## 9. Command Reference

Command dispatch is table-driven in `src/mantle/cli.py`. Hyphenated commands also accept
underscore aliases.

Common verification and inspection commands:

```bash
python -m mantle audit
python -m mantle prove
python -m mantle audit-mind
python -m mantle check --fast
python -m mantle check
python -m mantle teach
python -m mantle demo
python -m mantle mind
python -m mantle reproduce
python -m mantle assimilate examples/sample_app --dry-run
python -m mantle hatch examples/spores/greeter.png --out=nest/
python -m mantle ghost selftest
```

Commands that require an existing organism directory:

```bash
python -m mantle doctor nest/
python -m mantle face nest/ face.png
python -m mantle face-list nest/
python -m mantle face-wear nest/ origin
```

Host-residency commands:

```bash
python -m mantle anchor path/to/host
python -m mantle ask path/to/host "question"
python -m mantle ask path/to/host --mind "question"
python -m mantle feed path/to/host --credits=20 --key=provider-name
python -m mantle vitals path/to/host
python -m mantle graft examples/spores/notes_graft.png examples/sample_app
```

Applet capsule commands:

```bash
python -m mantle applet-create nest/ path/to/project name
python -m mantle applet-list nest/
python -m mantle applet-show nest/ name
python -m mantle applet-export nest/ name out/
python -m mantle applet-wear nest/ name
python -m mantle applet-audit nest/ name
python -m mantle applet-clone nest/ https://github.com/owner/repo name
```

Run only commands whose required paths exist in your current workspace.

## 10. Verification Expectations

For narrow source changes:

```bash
python -m mantle audit
python -m mantle prove
```

For containment or fusion changes:

```bash
python -m mantle audit-mind
```

For storage, artifact, lifecycle, audit, or cross-module changes:

```bash
python -m mantle check --fast
```

For broader changes, run the full local certification:

```bash
python -m mantle check
```

For browser demo changes, serve `examples/` and run the Node tests from `examples/tests/`.

## 11. Change Rules for Agents

- Inspect the relevant module and its audit rows before editing.
- Preserve Phase-1 determinism. Do not add network, key, SDK, or model dependencies to
  certified Phase-1 paths.
- Route inbound data through Senses, outbound effects through Limbs, and faults through Immune.
- Keep host assimilation read-only unless the operator explicitly asks for anchoring or grafting.
- Maintain fail-open behavior for instrumentation around existing host code.
- Add focused tests when changing shared behavior, storage semantics, audit contracts, host
  wrapping, or demo-visible workflows.
- Update docs only when they describe behavior that exists in source.
- Do not rewrite the conceptual language in the main documentation unless the task explicitly
  asks for that. This file is the technical translation layer.

Before opening a PR, check `git diff --check` and run the smallest verification command that
matches the risk of the change.
