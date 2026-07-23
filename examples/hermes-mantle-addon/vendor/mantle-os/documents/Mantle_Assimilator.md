# Mantle OS - The Assimilator (Path B)

**Mantle OS** - take residence in existing code, non-destructively.

> **Moved.** The full assimilation and scanning doctrine - the prime directive, the
> Phase-0 App Inventory gate, the 17-phase pipeline, the symbol-role table, the hook
> runtime, the hard-fail list, and the APP_INVENTORY template - now lives in one
> canonical home: [`documents/grimoire/The Grimoire.md`](grimoire/The%20Grimoire.md).
>
> The consolidation rule is: NECROMANCY (assimilate/anchor/graft) and RESURGERE
> (reconstruct from an egg/seed) share one substrate model. Discover the host first,
> then use or grow the scanner, adapter, verifier, and fail-open hook runtime that
> fits that host.

## Assimilation, In One Breath

You are given a living host codebase. You do not rewrite its behavior. You grow organs
around the existing tissue with additive, fail-open, reversible instrumentation. Nothing
touches host code until the read-only Phase-0 App Inventory and Organ Map is produced
and signed (`HF-B42`). See the canonical doctrine above for the full procedure.

## Automation

`src/mantle/assimilator/` plus `anchor.py` and `graft.py` automate the path:

- `python -m mantle assimilate <host> --dry-run` performs the read-only substrate
  census, AST dissection, and Organ Map. Python is parsed with `ast`; `.js`, `.mjs`,
  `.go`, and `.rs` use the optional tree-sitter scanner
  (`pip install mantle-os[multilang]`). Native C-family, Qt, CMake, and other
  discovered-but-unparsed surfaces are reported as adaptive tooling gaps instead of
  being silently counted as complete. Zero host writes.
- `python -m mantle anchor <host>` grows an anchored resident in a `.mantle/` nest,
  remembers the host organ map as observed facts, passes the Stage-1 gate, and proves
  do-no-harm with a byte-level census. Then `ask`, `feed`, and `vitals` operate it.
- `python -m mantle graft <graft-egg> <host>` applies a non-destructive patch in a
  workspace copy. `graft.weave(...)` threads the host live callables through fail-open
  organ wrappers, and `unweave` detaches cleanly.

## Production Refinements From NotepadNext

The NotepadNext C++/Qt/CMake assimilation added platform rules that now apply generally:

- Phase 0 identifies languages, frameworks, build files, and unparsed native/resource
  surfaces before it proposes organs.
- Standalone Phase-0 artifacts are refused if `--out` is the host tree or a child of
  the host tree. Anchored residents remain the explicit exception: `anchor` may create
  the additive `.mantle/` nest and proves all non-nest host files unchanged.
- GitHub clone surfaces use Windows long-path-safe Git checkout policy.
- Runtime and lifecycle receipts report VCW status through
  `mantle.core.status.organism_status()`, not ad hoc Cube/Body convenience calls.
- App-band generators use the reserved atlas and allocator helpers instead of
  hand-picking spans near vault, phenotype, spore, or applet tissue.

The manual procedure for hosts the current automation does not cover remains in the
canonical NECROMANCY section of the Grimoire.
