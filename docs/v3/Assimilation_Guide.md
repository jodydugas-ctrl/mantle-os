# Mantle OS v3 — Assimilation Guide (Path B, runnable cheatsheet)

> **Canonical doctrine moved.** The full assimilation/scanning doctrine now lives in one place:
> **[`docs/grimoire/GRIMOIRE_APPAI_DOMAIN_v1_0.md`](../grimoire/GRIMOIRE_APPAI_DOMAIN_v1_0.md)**,
> section **NECROMANCY — operational detail (the assimilation manual)**. This file is now just the
> runnable command cheatsheet. **The prime directive: do no harm** — the host runs exactly as
> before, plus a nervous system and a memory.

## 1. Dry run (Phase 0 — read-only, gated)

```bash
python -m mantle assimilate <host-path> --dry-run
python -m mantle assimilate <host-path> --out=./assimilation   # + artifacts
```

Scans every module (Python via `ast`; `.js/.mjs/.go/.rs` via the optional tree-sitter scanner,
`pip install mantle-os[multilang]` — host code is never executed, never modified), classifies
every symbol into an organ role, and prints the **assimilation map** (Heart / Senses / Limbs /
Memory / Immune / Brain affordance / external host code). With `--out=DIR` it writes
`APP_INVENTORY.md` (with the **unsigned READ-ONLY sign-off**) and `assimilation_map.json` next to
the operator, never inside the host tree. **Hook insertion before the sign-off is HF-B42.**

## 2. Wrapping (Phase 5+ — only after the gate is signed)

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

Wrapper guarantees: behavior preserved (HF-B40) · fail-open (HF-B32) · reversible via `asm.ledger`
/ `asm.unwrap(fn)` (HF-B41) · redacted at the secret boundary. See the canonical doctrine for the
full hook table, hard-fails, and the APP_INVENTORY template.

## 3. Convergence

When surfaces are mapped, validation layers pass, and heartbeat/persistence run with no host LLM,
administer the same Stage-1 gate as Path A (`python -m mantle audit`). Zero open hard-fails → the
same MIND fusion and Stage-2 gate. Both paths converge on the same certified creature.
