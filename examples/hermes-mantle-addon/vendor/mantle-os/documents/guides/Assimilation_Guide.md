# Mantle OS - Assimilation Guide

Runnable cheatsheet for Path B. The full doctrine lives in
[`documents/grimoire/The Grimoire.md`](../grimoire/The%20Grimoire.md), in the
NECROMANCY and Mantle OS binding sections. Prime directive: do no harm. The host runs
exactly as before, plus a nervous system and memory.

## 1. Dry Run

```bash
python -m mantle assimilate <host-path> --dry-run
python -m mantle assimilate <host-path> --out=./assimilation
```

Phase 0 is read-only. It first records the substrate census: languages, build files,
native/resource candidates, and parser coverage. It then scans what the current tooling
can parse:

- Python via `ast`
- `.js`, `.mjs`, `.go`, and `.rs` via optional tree-sitter
- native C-family, Qt UI/resource files, CMake, or other unparsed surfaces as explicit
  adaptive-tooling gaps

Host code is never executed and never modified. With `--out=DIR`, Mantle writes
`APP_INVENTORY.md` and `assimilation_map.json` beside the operator. The standalone
command refuses an output directory that is the host tree or inside the host tree.
`anchor` is the explicit additive-resident exception: it may create `.mantle/` and then
proves every non-nest host file unchanged. Hook insertion before the sign-off remains
`HF-B42`.

## 2. Wrapping

Only after the Phase-0 gate is signed:

```python
from mantle import Organism
from mantle.assimilator import Assimilation, propose_genome

org = Organism.birth(
    identity={"name": "Host.AppAI", "host": "notes_app"},
    truths=[...],
    commandments=[...],
    genome=propose_genome(role_counts),
)
asm = Assimilation(org)

handle_create_note = asm.wrap("SENSOR_EVENT", handle_create_note)
send_notification = asm.wrap("ARM_ACTION", send_notification)
save_notes = asm.wrap("PERSISTENCE_WRITE", save_notes)
```

Wrapper guarantees: behavior preserved (`HF-B40`), fail-open (`HF-B32`), reversible via
`asm.ledger` / `asm.unwrap(fn)` (`HF-B41`), redacted at the secret boundary.

## 3. Convergence

When surfaces are mapped, validation layers pass, and heartbeat/persistence run with no
host LLM, administer the same Stage-1 gate as Path A (`python -m mantle audit`). Zero
open hard-fails leads to the same MIND fusion and Stage-2 gate.

## 4. Production Rules From NotepadNext

- Do not infer language from the user's description or repository name. Census first.
- Distinguish source language, framework, build system, resource files, generated files,
  and vendored dependency tissue before proposing insertion.
- If parser coverage is incomplete, report the gap and generate or request the next
  substrate-specific tool. Do not imply Phase-0 completeness.
- Use `mantle.core.status.organism_status()` for lifecycle, terminal, and VCW receipts.
- Use app-band atlas/allocator helpers for generated eggs and app faces.
- Use Windows long-path-safe Git clone policy for GitHub ingestion.
