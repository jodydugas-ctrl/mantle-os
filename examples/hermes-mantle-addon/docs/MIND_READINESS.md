# Hermes Mantle Addon — MIND Readiness Report

**Target:** `mantle-os` v0.4.0 (`Hermes.Mantle.AppAI`) on Mantle OS 1.3.0

**Recorded:** 2026-07-15T00:02:34-03:00

**Machine-readable report:** [`MIND_READINESS.json`](MIND_READINESS.json)

**Verdict:** **NOT READY**

**MIND fusion authorized:** **NO**

**Reproduction activation authorized:** **NO**

## Executive finding

Step 10 resolved the framework and governance defects identified by Step 9. APPLET-5 now
passes in the addon's private vendor namespace, core and vendor are synchronized, Stage-1
language no longer grants authority, natural fused cognition is a baseline rather than an
event gate, fusion requires target-bound operator and guardian approval, addon resident
snapshots are atomic and owner-only, and core artifacts use owner-only atomic replacement.

The MIND is nevertheless **not ready to fuse**. Five blockers remain: no addon
fusion/defusion lifecycle, no addon ten-minute scheduler, no Hermes-native provider route,
no complete heartbeat budget/outage policy, and no APPROVED operator or guardian fusion
decision.

## Evidence matrix

| Evidence | Result |
|---|---:|
| Addon Stage-1 probes | **14/14 PASS** |
| Framework gate rows | **20/20 PASS** |
| Framework security invariants | **111/111 PASS** |
| Addon unit tests | **96/96 PASS** |
| Containment receipt | **11/11 PASS** |
| Real Hermes observer hooks | **12** |
| Complete non-addon vendor snapshot | **146/146 aligned** |
| Repository alignment receipt | **339 practical files, PASS** |
| Strict optimization audit | **PASS under bounded closure** |
| Owner-only storage | **PASS** |
| Raw payload exclusion | **PASS** |
| Real-plugin `stage1_certified` | `false` |
| Operator fusion decision | **DEFERRED** |
| Guardian fusion decision | **DEFERRED** |

## Resolved Step-9 blockers

### B-01 — Complete framework Stage-1 gate — RESOLVED

The absolute `mantle.compiler` import was removed. APPLET-5 now uses the vendored-relative
compiler symbol and passes under `_hermes_mantle_vendor`. The full framework receipt is
20/20 gate rows and 111/111 invariants.

### B-02 — Authorized Phase-2 configuration — RESOLVED

`ResidentConfig.authorize_phase2()` is the sole supported transition. It consumes a
complete fresh Stage-1 receipt and `READY` engineering verdict bound to the resident
identity and Body fingerprint, then requires post-receipt target-bound `APPROVED` operator
and guardian decisions, explicit effective MIND authorization, and explicit reproduction
denial. Direct construction and Hermes configuration remain fail-closed. The live
`NOT_READY`/`DEFERRED` records cannot enable it.

### B-08 — Gate language and authority — RESOLVED

Core, vendor, addon, tests, and doctrine now distinguish:

- Stage-1 certification: technical evidence;
- readiness: an engineering verdict;
- operator approval: one independent authority;
- guardian approval: a second independent authority;
- fusion: permitted only when all four gates are satisfied.

Core `fuse()` and the Brain socket enforce target-bound `APPROVED` decisions from both roles.

## Remaining blockers

### B-03 — Runtime fusion lifecycle — HARD

`ResidentRuntime` has no supported fusion ceremony, defusion path, lifecycle receipt,
restoration contract, or fused-state recovery behavior.

### B-04 — Natural ten-minute cognitive heartbeat — HARD / PARTIAL

Core Heart now declares a 600-second natural interval and calls a fused MIND on every pulse.
NOC-1..3 and SCHED-1 prove the unconditional baseline and additional nociceptive/scheduled
stressors. The addon still lacks a legal fused runtime and ten-minute scheduler.

### B-05 — Hermes-native provider routing — HARD

The existing transport remains a **bounded OpenAI-compatible HTTP prototype**. It reads
`HERMES_MANTLE_API_KEY`, `HERMES_MANTLE_MODEL`, and `HERMES_MANTLE_URL`; it is not
Hermes-native routing and must not be described as such.

### B-06 — Heartbeat budget and outage policy — HARD

No complete aggregate cost/token budget, retry/backoff policy, outage behavior, cadence
receipt, or bounded durable usage policy exists for the ten-minute baseline.

### B-07 — Explicit fusion decisions — HARD

Both decisions remain **DEFERRED**. Step-10 continuation authorized engineering and
verification only. It did not authorize fusion or reproduction.

## Step-10 engineering improvements

- Mantle OS version advanced to 1.3.0.
- Framework count advanced to 111 invariants with `PERSIST-1`.
- `APPLET-5` is namespace-safe without weakening secret detection.
- Brain/MIND fusion requires Stage-1 evidence plus dual target-bound authority.
- Fused Heart cognition runs on every natural baseline pulse; pain is additional.
- `Organism.save()` uses same-directory atomic replacement and owner-only modes per artifact;
  complete standalone multi-file generation publication remains a documented limitation.
- Bare unclosed `open()` calls were removed from executable non-vendor Python.
- Synthetic transport tests that bypassed immutable configuration were removed; valid Phase-1
  configuration proves the bespoke HTTP prototype unreachable.
- Active Hermes home, profile, and plugin configuration resolve per invocation.
- The 288 KB MacroDroid schema is valid YAML.
- The full 146-file non-addon vendor snapshot is reproducibly synchronized and tested.
- The 339-file repository digest/parse/claim receipt passes.
- Stage-1 output says technical evidence, never “Phase 2 authorized.”

## Verdict

> **NOT READY. Do not enable `mind_enabled`, call `fuse()` in the addon, schedule addon
> cognitive heartbeats, or activate reproduction.**

The ten-step repository-alignment roadmap is complete. Any Phase-2 implementation requires
a separately scoped engineering plan. Even a future `READY` report cannot authorize fusion;
new explicit target-bound `APPROVED` decisions from both operator and guardian are still
required.
