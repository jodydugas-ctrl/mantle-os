# Mantle OS — THE ASSIMILATOR (Path B)

**Mantle OS** · Take residence in existing code, non-destructively.

> **Moved.** The full assimilation / scanning doctrine — the prime directive, the Phase-0
> App-Inventory gate, the 17-phase pipeline, the symbol-role table, the hook runtime, the
> hard-fail list, and the APP_INVENTORY template — now lives in **one canonical home**:
>
> 👉 **[`documents/grimoire/The Grimoire.md`](grimoire/The%20Grimoire.md)**,
> especially the AppAI extension (§7: `NECROMANCY`, `RESURGERE`, residency, the §7.8 hard
> fails) and the Mantle OS environment binding (§9.2, the operator's assimilation ritual).
>
> This consolidation reflects that **the egg and assimilation are the same thing**: NECROMANCY
> (assimilate/anchor/graft) and RESURGERE (reconstruct from an egg/seed) run on one shared
> substrate — one scanner, one `ROLES` table, one fail-open hook runtime.

## Assimilation, in one breath

You are given a living host codebase. You do **not** rewrite its behavior — you grow organs
around the existing tissue with additive, fail-open, reversible instrumentation. Nothing touches
host code until the read-only **Phase-0 App Inventory & Organ Map** is produced and signed
(`HF-B42`). See the canonical doctrine above for the full procedure.

## Automation (quick reference)

`src/mantle/assimilator/` + `anchor.py` + `graft.py` automate the whole path:

- `python -m mantle assimilate <host> --dry-run` — the read-only AST dissection + Organ Map
  (Phase 0). `.py` via `ast`; `.js/.mjs/.go/.rs` via the optional tree-sitter scanner
  (`pip install mantle-os[multilang]`). Zero host writes.
- `python -m mantle anchor <host>` — grow an anchored **resident** in a `.mantle/` nest, remember
  the host's organ map as observed facts, pass the Stage-1 gate, and **prove do-no-harm with a
  byte-level census**. Then `ask` / `feed` / `vitals` it.
- `python -m mantle graft <graft-egg> <host>` — apply a non-destructive **patch** in a workspace
  copy; `graft.weave(...)` threads the host's live callables through fail-open organ wrappers and
  `unweave` detaches cleanly.

The doctrine behind these commands — and the manual procedure for hosts the automation does not
cover — is in the canonical NECROMANCY section linked above.
