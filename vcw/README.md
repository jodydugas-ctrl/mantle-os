# `vcw/` — The VCW Cube (working code)

**Mantle OS v2.3** · The heart of the nervous system, in runnable code.

This directory is the **heart of the Mantle nervous system** in runnable form: the durable
nervous-memory substrate (`vcw-cube-png-v2`) that every Mantle AppAI Body is built around. Pure
Python standard library — no third-party packages, no PIL. It is meant to be *read* as much as
*run*: an LLM that studies it comes away able to use a VCW cube.

## Files

| File | What it is |
|------|------------|
| [`GUIDE.md`](GUIDE.md) | **The one teaching guide** — substrate (Part I) + programmable layer (Part II). |
| [`vcw_cube.py`](vcw_cube.py) | The base codec + `Cube` API + CLI. The substrate spec, in code. |
| [`entry.py`](entry.py) | The **one** entry hasher (covers every non-volatile field, incl. `authorship`). |
| [`boot.py`](boot.py) | Programmable boot-sector schema + the **driver registry**. |
| [`drivers.py`](drivers.py) | `log-json`, `keyvalue`, `calendar-spatial`, `exec` drivers. |
| [`body.py`](body.py) | The **Body** store: Primer / Special Instructions / Immunization + lineage index. |
| [`refs.py`](refs.py) | The unified reference resolver `<TARGET.SELECTOR.ADDRESS>`. |
| [`lineage.py`](lineage.py) | Boot-driven `Cube` + the `Organism` (Prime + ancestral chain) + rebirth. |
| [`skills.py`](skills.py) | The **Inner Voice** self-inquiry skill. |
| [`examples.py`](examples.py) | Narrated tour of a single cube's lifecycle. |
| [`examples_boot.py`](examples_boot.py) | Narrated tour: boot sectors, Body, reflex layers, on-demand layers, lineage. |
| [`organs/`](organs/) | The **runnable reference Body**: Heart, Senses, Limbs, Nervous System (pure stdlib, no LLM). |
| [`audit.py`](audit.py) · [`test_invariants.py`](test_invariants.py) | The Stage-1 gate + the red/green security invariants. |

## Run it

```bash
# one command from the repo root (no network, no LLM)
python -m vcw demo            # the full narrated tour
python -m vcw audit           # the Stage-1 Zombie Body gate (substrate + runnable Body)
python -m vcw prove           # the security invariants

# or directly, from inside vcw/
python examples.py            # the base cube tour
python examples_boot.py       # the full tour: programmable layers, Body, reflexes, rebirth
python audit.py               # the Stage-1 audit; --break-hash / --break-primer must FAIL
python vcw_cube.py create organism.vcw --primer "first breath"
python vcw_cube.py inspect organism.vcw
python vcw_cube.py verify  organism.vcw
```

## The contract in five lines

1. A cube is **800 layers**; each layer is one **800×800 RGBA PNG**.
2. Layers are grouped into **bands** (reserved ranges); each band declares a driver, a `span`,
   and a `purpose`. Layers are allocated **on demand** and reclaimed for reuse.
3. **Identity lives in the BODY, not the cube** (`body.py`): Primer (read-only) + Special
   Instructions + Immunization + lineage index. The cube is pure *experiential* memory.
4. Memory = **immutable, hashed entries** appended to bands; reads apply the **veil** (hide
   tombstoned / quarantined / private).
5. `save()` is a **staged commit**: write `.stage` → re-load → `verify()` → atomic `os.replace`.
   A corrupt cube can never replace a healthy one.

## Why this lives apart from the prompts

The framework documents (`../Mantle_*.md`) describe the organism; this directory is the **organ
they all depend on** — a small, complete, inspectable reference an LLM can import, run, and reason
against. Where prose and this code ever disagree, **the code is ground truth.**

Read [`GUIDE.md`](GUIDE.md) to learn the substrate, then [`../Mantle_Organ_Atlas.md`](../Mantle_Organ_Atlas.md)
to see how every organ binds to it.
