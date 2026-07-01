# examples/spore — the SPORE seed, proven pure

The **spore** is the smallest form of the **SEED** reproductive method (see
[`documents/Mantle_Reproduction.md`](../../documents/Mantle_Reproduction.md)): a single PNG that
*is* a whole minimal agent — identity, one task, one append-only conversation, and, embedded in its
own VCW pixels, the minimal Python reader/writer needed to read and grow itself without the SDK.

The engine lives in the package at [`src/mantle/spore.py`](../../src/mantle/spore.py) (with its
embryo `spore_min.py`). This directory carries its **purity gate** and an example seed.

```bash
# regenerate the example seed and verify it
python -m mantle spore demo examples/spore/example_spore.png
python -m mantle spore verify examples/spore/example_spore.png

# the purity audit: proves the seed stays MINIMAL and never grows into full Mantle OS
python examples/spore/audit_spore.py
python examples/spore/audit_spore.py examples/spore/example_spore.png   # also verify a given PNG
```

## Why a purity audit?

A spore's whole value is that it is transparent and small — *one PNG, one agent, one task, one
conversation, one append-only memory*. `audit_spore.py` inspects `spore.py`'s own source and
**refuses feature creep**: no organs, immune events, encryption, rebirth, lineage, child spores,
compaction, or summarization may appear in the seed. Strangeness — the cache-ghost substrate,
symbiosis, the eight organs — is Mantle tissue **layered on** the format
([`src/mantle/ghost.py`](../../src/mantle/ghost.py), the reproduction facade), never baked into the
seed itself. This gate is what keeps that promise honest.
