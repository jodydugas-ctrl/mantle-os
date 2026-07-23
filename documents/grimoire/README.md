# The Grimoire

**Read this first.** The Grimoire is the doctrine behind Mantle OS: the constitutional
operating specification for bounded agent action and the source of truth for AppAI,
Mantle OS, VCW, organs, SELF/OTHER, MIND containment, reproduction, and assimilation.

## Canonical File

The Grimoire is exactly one canonical file:

| Read | Document | Scope |
| --- | --- | --- |
| **1st** | [The Grimoire.md](The%20Grimoire.md) | Grimoire 2.0: Core law, runtime, spells, AppAI extension, and Mantle OS environment binding. |

Do not treat old split editions, summaries, companion chapters, or copied excerpts as
canonical. If a task touches Mantle OS, load the AppAI and environment-binding sections
from the same file instead of looking for a separate chapter.

## Loading

Load by task class using the file's §0 manifest. §1 and §6 are always in force whether
their text is loaded or not. For Mantle OS work, consult §7 and §9 in addition to the
minimum cast loadout.

`Intellige` remains read-only comprehension. It grants no authority to edit, mutate,
spend, disclose, execute, or widen scope; authority still comes from the operator.

## Relationship To Code

The Mantle OS binding lives in [The Grimoire.md](The%20Grimoire.md) §9. The reference
implementation is under [`src/mantle/`](../../src/mantle/), with command bindings through
`python -m mantle <command>`.

Key doctrine-to-code anchors:

| Grimoire area | Mantle OS surface |
| --- | --- |
| NECROMANCY / assimilation | [`src/mantle/assimilator/`](../../src/mantle/assimilator/), [`anchor.py`](../../src/mantle/anchor.py), [`graft.py`](../../src/mantle/graft.py) |
| VITALS-CHECKUP / audit | [`src/mantle/doctor.py`](../../src/mantle/doctor.py), [`src/mantle/audits/`](../../src/mantle/audits/) |
| Reproduction | [`src/mantle/reproduction.py`](../../src/mantle/reproduction.py), [`src/mantle/organs/reproduction.py`](../../src/mantle/organs/reproduction.py), [`spore.py`](../../src/mantle/spore.py), [`hatchery.py`](../../src/mantle/hatchery.py) |
| CACHE-HAUNT | [`src/mantle/ghost.py`](../../src/mantle/ghost.py), [`src/mantle/ghost_http.py`](../../src/mantle/ghost_http.py) |
| VCW band plan | [`src/mantle/vcw/bands.py`](../../src/mantle/vcw/bands.py) |

When doctrine and runnable behavior disagree, treat the disagreement as an alignment
task: verify the current code surface, then update whichever side is stale under the
operator's authority.
