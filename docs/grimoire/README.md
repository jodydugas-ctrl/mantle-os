# The Grimoire

The doctrine behind Mantle OS — the spellbook the framework's design follows. These are
agent-facing reference documents (written for LLM agents, runtimes, and orchestrators), and
they are the source of truth for the concepts the code implements (organs, the VCW substrate,
the AppAI growth paths, and the NECROMANCY assimilation pipeline).

| Document | Scope |
| --- | --- |
| [THE_GRIMOIRE_CORE_v3_0.md](THE_GRIMOIRE_CORE_v3_0.md) | The Core Spellbook — universal engineering spells for any codebase, document, or system. Standalone; load this first. |
| [GRIMOIRE_APPAI_DOMAIN_v1_0.md](GRIMOIRE_APPAI_DOMAIN_v1_0.md) | The AppAI Domain Extension — domain spells for AppAI work: birth (ANIMARE), assimilation (NECROMANCY), residency, memory, limbs, metabolism, reconstruction, and retirement. Extends the Core. |

## Relationship to the code

The AppAI extension's **NECROMANCY** spell defines the read-only, language-agnostic dissection
pipeline that `mantle/assimilator/` implements:

- `language_agnostic` doctrine ↔ [`mantle/assimilator/scanner_ts.py`](../../mantle/assimilator/scanner_ts.py) (tree-sitter parser) + [`scanner.py`](../../mantle/assimilator/scanner.py) (neutral classifier, reused across languages).
- The organ/role model ↔ `scanner.classify_symbol` and [`organ_map.py`](../../mantle/assimilator/organ_map.py).

When the doctrine and the code disagree, treat the code as authoritative for current behavior
and the Grimoire as the design intent; reconcile by updating whichever is stale.
