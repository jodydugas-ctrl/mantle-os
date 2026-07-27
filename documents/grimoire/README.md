# The Grimoire

**Read this first.** The Grimoire is Mantle OS's canonical VCW software profile: the
machine specification for encoding and decoding semantic pixel runs on a VCW-compatible
substrate.

## Canonical File

The Grimoire is exactly one canonical file:

| Read | Document | Scope |
| --- | --- | --- |
| **1st** | [The Grimoire.md](The%20Grimoire.md) | `GRIMOIRE v0.9 -- VCW SOFTWARE EDITION`: RGBA channels, atom groups, roles, evidence, force, parity, encoded BOOK rows, conformance, Mantle companion duties, and known bends. |

Do not add old procedural manuals, split editions, companion copies, or compatibility mirrors.
If a task touches Grimoire semantics, load this file. If a task touches Mantle runtime
behavior, use the runnable code and the Mantle docs that own that behavior.

## Loading

Load by section and declare what is absent. The file is machine-oriented by design:

| Section | Use |
| --- | --- |
| `0 AXIOMS` | Edition, framing, grouping, lane-integrity, and authority boundaries. |
| `1 CHANNELS` | RGBA lane meaning and statement framing. |
| `2 ROLE`, `3 EVIDENCE`, `4 FORCE` | The `G`, `B`, and `A` channel registries. |
| `5 ATOM ADDRESS SPACE`, `6 ATOM TABLE` | Atom addressing and the canonical concept rows. |
| `7 ENCODED BOOK`, `8 BOOK ROWS` | The encoded law corpus. |
| `9 DECODER RULES`, `10 CONFORMANCE`, `11 MANTLE COMPANION RULES` | Decoder obligations, profile conformance, and how Mantle treats the profile. |
| `12 KNOWN BENDS` | Explicit measured and structural limitations. |

The profile's own rule `S6 PARTIAL LOAD` is binding for readers: a partial load declares
absent sections, and a model may not fill missing law from memory.

## Relationship To Code

VCW is the booted substrate hardware: RGBA-capable lanes, frames, append discipline,
integrity, layers, bands, and storage. The Grimoire is the software profile that gives
semantic meaning to four logical lanes: atoms, roles, evidence, and force.

Current Mantle code surfaces that interact with this boundary:

| Area | Mantle OS surface |
| --- | --- |
| VCW booted substrate | [`src/mantle/vcw/`](../../src/mantle/vcw/), [`examples/vcw/vcw_cube.py`](../../examples/vcw/vcw_cube.py) |
| Carrier profiles / drivers | [`src/mantle/vcw/drivers.py`](../../src/mantle/vcw/drivers.py), [`src/mantle/vcw/bands.py`](../../src/mantle/vcw/bands.py) |
| Grimoire v0.9 executable profile | [`src/mantle/vcw/grimoire.py`](../../src/mantle/vcw/grimoire.py) and the registered `grimoire-v0.9` driver |
| Spore PNG carriers | [`src/mantle/spore.py`](../../src/mantle/spore.py), [`src/mantle/spore_min.py`](../../src/mantle/spore_min.py), [`examples/spore/`](../../examples/spore/) |
| Assimilation / residency | [`src/mantle/assimilator/`](../../src/mantle/assimilator/), [`anchor.py`](../../src/mantle/anchor.py), [`graft.py`](../../src/mantle/graft.py) |
| Reproduction | [`src/mantle/reproduction.py`](../../src/mantle/reproduction.py), [`src/mantle/organs/reproduction.py`](../../src/mantle/organs/reproduction.py), [`hatchery.py`](../../src/mantle/hatchery.py) |

Presence of an encoded Grimoire profile is data, not adoption or authority. The registered
`grimoire-v0.9` driver decodes raw runs, verifies statement parity, measures a full-lane
fingerprint when a carrier claims tamper evidence, reports atom-address provenance, and
records adoption state from boot policy (`data`, `quote`, `quarantine`, or `adopted`).
Mantle runtime authority still comes from operator decisions, Body policy, and the audited
code path.
