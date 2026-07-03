# The Grimoire

**Read this first.** The Grimoire is the doctrine behind Mantle OS -- the spellbook the
framework's design follows, and the foundational literature anyone (human or agent) should read
*before* building, assimilating, or operating an AppAI. It is agent-facing reference material
(written for LLM agents, runtimes, and orchestrators) and it is the source of truth for the
concepts the code implements: organs, the VCW substrate, the AppAI growth paths, and the
NECROMANCY assimilation pipeline.

## The two files -- and the reading order

The Grimoire is **exactly two version-locked files** -- there are no other editions; any that
appear are stale and should be removed. The two files always carry the same version number
(currently **3.5.0**): advancing either advances both.

| Read | Document | Scope |
| --- | --- | --- |
| **1st** | [The Grimoire.md](The%20Grimoire.md) | **The Core Spellbook** -- universal engineering spells for any codebase, document, or system. Standalone; **load this first.** It is the introduction; the rest does not make sense without it. |
| **2nd** | [The Grimoire AppAI Chapter.md](The%20Grimoire%20AppAI%20Chapter.md) | **The AppAI Domain Extension** -- domain spells for AppAI work: birth (ANIMARE), assimilation (NECROMANCY), residency, memory, limbs, diagnostics, metabolism, cache-as-working-memory (CACHE-HAUNT), controlled reconstruction, and retirement. **Extends the Core; never use it alone.** |

The Core is self-contained: it covers general software engineering, documentation, analysis,
review, security, operations, product evaluation, and public web-presence research. The moment a
task touches AppAI, Mantle OS, `.mantle/` nests, VCW cubes, zombie bodies, organ maps,
SELF/OTHER, MIND fusion, or assimilation, the AppAI Chapter is loaded **in addition to** the Core.
If the Core is absent, the Chapter permits only read-only comprehension (cast `Intellige`) and
forbids any mutation.

## Bootstrapping the Grimoire (Intellige)

`Intellige` is read-only comprehension: read, model, and explain before acting. It grants no
authority to edit, mutate, or execute. It is **web-aware**: when the target has a material public
web presence, Intellige runs a bounded `WEB-PRESENCE-RECON` pass (under Vestigare constraints,
with citations) as part of comprehension before finalizing. To cast it on the Grimoire itself:

1. **If the Grimoire is already attached** to the current context, use that document and proceed.
2. **Otherwise**, read this README -- the canonical reading-order file -- and follow the order it
   names: the Core Spellbook first, then the AppAI Chapter **only** if the task is Mantle OS /
   AppAI-specific.
3. **If the files cannot be loaded** (no web or repository access), stop. Do not guess the
   doctrine -- return a brief blocked receipt naming the missing required files.

This README is the **source of truth for canonicality**: only the two files above are canonical.
Legacy files, old editions, summaries, and duplicate copies are not canonical unless this file
directs you to them.

An `Intellige` cast closes with an **Intellige receipt**: *Cast, Loaded Sources, Comprehension,
AppAI Scope Decision* (whether the Chapter was loaded and why, or skipped because the target is not
AppAI/Mantle work), *Aporias / Unknowns,* and a *Safe Next Cast.* See the Core Spellbook's §6.2
`INTELLIGE` for the full form.

## Command surface

The stable operator interface is the Latin Title Case macro layer: examples include `Intellige`,
`Vestigare`, `Animare`, and `Necromantia`. Lowercase power words are internal agent stances, and
UPPERCASE spell identifiers are procedural implementation labels for agents, runtimes, ledgers, and
receipts. Humans may use power words or spell IDs directly if they wish, but they should not be
required for ordinary operation.

## The Vestigare macro
The Grimoire includes **Vestigare**, the Core macro for `WEB-PRESENCE-RECON`. Cast it when an artifact,
product, app, platform, or clone target has a public web presence and public web or image evidence
would improve understanding, fidelity, or feature parity. It gathers cited official and
corroborating sources, requires image evidence when visual fidelity matters, and leaves a sourced
evidence packet for the next spell. `Intellige` also invokes it automatically as a bounded
comprehension subroutine when the target's public web presence is material to understanding;
Vestigare remains the macro to cast when the public-presence research is itself the task.

## Relationship to the code

The AppAI Chapter's **NECROMANCY** spell defines the read-only, language-agnostic dissection
pipeline that `src/mantle/assimilator/` implements:

- `language_agnostic` doctrine -> [`src/mantle/assimilator/scanner_ts.py`](../../src/mantle/assimilator/scanner_ts.py) (tree-sitter parser) + [`scanner.py`](../../src/mantle/assimilator/scanner.py) (neutral classifier, reused across languages).
- The organ/role model -> `scanner.classify_symbol` and [`organ_map.py`](../../src/mantle/assimilator/organ_map.py).

The AppAI Chapter's **CACHE-HAUNT** spell (macro **Larvare**) -- keep the MIND's working memory warm
in the provider's prompt cache while the seed stays dry -- is implemented by the cache-ghost:
[`src/mantle/ghost.py`](../../src/mantle/ghost.py) (`GhostSubstrate`, `LocalPromptCache`,
`warm`/`append`/`hydrate`/`status`) layered on [`spore.py`](../../src/mantle/spore.py); doctrine in
[`../Mantle_Reproduction.md`](../Mantle_Reproduction.md).

The Python package in [`src/mantle/`](../../src/mantle/) is the **reference implementation**, not the
boundary of the doctrine: the Grimoire is language-, AI-, and container-agnostic by design (see
the project [`README.md`](../../README.md)). When the doctrine and the code disagree, treat the
code as authoritative for current behavior and the Grimoire as the design intent; reconcile by
updating whichever is stale.
