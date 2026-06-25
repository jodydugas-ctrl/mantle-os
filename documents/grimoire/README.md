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
(currently **4.4**): advancing either advances both.

| Read | Document | Scope |
| --- | --- | --- |
| **1st** | [The Grimoire 4.4.md](The%20Grimoire%204.4.md) | **The Core Spellbook** -- universal engineering spells for any codebase, document, or system. Standalone; **load this first.** It is the introduction; the rest does not make sense without it. |
| **2nd** | [The Grimoire AppAI Chapter 4.4.md](The%20Grimoire%20AppAI%20Chapter%204.4.md) | **The AppAI Domain Extension** -- domain spells for AppAI work: birth (ANIMARE), assimilation (NECROMANCY), residency, memory, limbs, metabolism, reconstruction, and retirement. **Extends the Core; never use it alone.** |

The Core is self-contained: it covers general software engineering, documentation, analysis,
review, security, operations, product evaluation, and public web-presence research. The moment a
task touches AppAI, Mantle OS, `.mantle/` nests, VCW cubes, zombie bodies, organ maps,
SELF/OTHER, MIND fusion, or assimilation, the AppAI Chapter is loaded **in addition to** the Core.
If the Core is absent, the Chapter permits only read-only comprehension (cast `Intellige`) and
forbids any mutation.

## Current addition

Version 4.4 adds **Vestigare**, the Core macro for `WEB-PRESENCE-RECON`. Cast it when an artifact,
product, app, platform, or clone target has a public web presence and public web or image evidence
would improve understanding, fidelity, or feature parity. It gathers cited official and
corroborating sources, requires image evidence when visual fidelity matters, and leaves a sourced
evidence packet for the next spell.

## Relationship to the code

The AppAI Chapter's **NECROMANCY** spell defines the read-only, language-agnostic dissection
pipeline that `src/mantle/assimilator/` implements:

- `language_agnostic` doctrine -> [`src/mantle/assimilator/scanner_ts.py`](../../src/mantle/assimilator/scanner_ts.py) (tree-sitter parser) + [`scanner.py`](../../src/mantle/assimilator/scanner.py) (neutral classifier, reused across languages).
- The organ/role model -> `scanner.classify_symbol` and [`organ_map.py`](../../src/mantle/assimilator/organ_map.py).

The Python package in [`src/mantle/`](../../src/mantle/) is the **reference implementation**, not the
boundary of the doctrine: the Grimoire is language-, AI-, and container-agnostic by design (see
the project [`README.md`](../../README.md)). When the doctrine and the code disagree, treat the
code as authoritative for current behavior and the Grimoire as the design intent; reconcile by
updating whichever is stale.
