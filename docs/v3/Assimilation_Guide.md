# Mantle OS v3 — Assimilation Guide (Path B, runnable)

Path B grows organs around EXISTING code, non-destructively. v3 makes the
`Mantle_Assimilator.md` doctrine runnable: `mantle/assimilator/` dissects a host,
maps its tissue to organs, emits the Phase-0 artifacts, and threads host behavior
through the organism with fail-open, reversible wrappers. **The prime directive: do no
harm.** The host runs exactly as before — plus now it has a nervous system and a memory.

## 1. Dry run (Phase 0 — read-only, gated)

```bash
python -m mantle assimilate <host-path> --dry-run
python -m mantle assimilate <host-path> --out=./assimilation   # + artifacts
```

This scans every Python module (AST only — host code is never executed, never modified),
classifies every symbol into an organ role, and prints the **assimilation map**:

- what is **Heart** (main loops, schedulers, clocks)
- what is **Senses** (handlers, routes, listeners, triggers)
- what is **Limbs** (outbound calls, renders, effectors)
- what is **Memory** (state transitions, persistence writes)
- what is **Immune** (validation, retries, secret boundaries)
- what is a **Brain affordance** (LLM/judgment points — left dormant)
- what **remains external host code** (pure utilities; untouched)

A missing organ is information too: an app with no immune tissue is fragile — the
assimilation should compensate.

With `--out=DIR` it writes `APP_INVENTORY.md` (Appendix-A format, pre-filled, with the
**unsigned READ-ONLY sign-off**) and `assimilation_map.json`. Artifacts land next to the
operator, never inside the host tree. **Hook insertion before the sign-off is HF-B42.**

## 2. The proposed genome

The dry run proposes a cube genome sized to the host's observed shape (high-churn
surfaces get more span and faster reclaim; durable knowledge gets room), including two
app bands: `host_state` (mirrored transitions) and `host_actions` (wrapped effector
calls). Author the final genome from this draft in Phase 3.

## 3. Wrapping (Phase 5+ — only after the gate is signed)

```python
from mantle import Organism
from mantle.assimilator import Assimilation, propose_genome

org = Organism.birth(identity={"name": "Host.AppAI", "host": "notes_app"},
                     truths=[...], commandments=[...],
                     genome=propose_genome(role_counts))
asm = Assimilation(org)

handle_create_note = asm.wrap("SENSOR_EVENT", handle_create_note)
send_notification  = asm.wrap("ARM_ACTION",   send_notification)
save_notes         = asm.wrap("PERSISTENCE_WRITE", save_notes)
```

Wrapper guarantees (each is an invariant, not a hope):

1. **Behavior preserved (HF-B40).** Same args, same return, same exceptions — the wrap
   adds observation only.
2. **Fail-open (HF-B32).** A fault inside any hook degrades to an immune event; it can
   never crash the host.
3. **Reversible (HF-B41).** Every wrap is ledgered (`asm.ledger`) and undoable
   (`asm.unwrap(fn)` returns the original).
4. **Redacted.** Everything crossing into the cube passes the secret boundary first.

What each role gets: SENSOR_EVENT/REFLEX → a classified `senses` entry per call;
ARM_ACTION/DISPLAY_RENDER → an Action Execution Proof (ok or failed) through Limbs;
STATE_TRANSITION/PERSISTENCE_WRITE → a mirrored `host_state` entry; any raised host
exception → a `host_error` immune event (and the exception still propagates to the host,
unchanged).

## 4. Convergence

When the host's surfaces are mapped (Human Surface Map + ControlBridges for every
human-visible control), validation layers pass, and the heartbeat/persistence run with no
host LLM, administer the same Stage-1 gate as Path A (`python -m mantle audit`, or
`stage1.run(org)` against the live assimilated organism). Zero open hard-fails → the same
MIND fusion, the same Stage-2 gate. Both paths converge on the same certified creature.
