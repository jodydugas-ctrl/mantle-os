# Germ spores — one file births one AppAI

Each PNG here is a **germ spore**: a single self-contained file carrying

- the **germ** — the complete build data for an AppAI (identity, truths,
  commandments, genome bands, declarative reflexes, controls, instincts with
  proving cases), and
- the **build note** — instructions any coding agent can read to grow the app,
  with or without Mantle installed.

Hatch one:

```bash
python -m mantle hatch examples/spores/greeter.png --out=nest/
```

Without Mantle, decode the pixels (the Quickstart is printed on the image
itself and mirrored in its PNG metadata) and read the payload key `germ`.

`notes_graft.png` carries a **graft germ** — a spore aimed at a host — applied
with `python -m mantle graft examples/spores/notes_graft.png examples/sample_app`.

The PNGs are generated from the germ files in `../eggs/` by
`python examples/spores/make_spores.py`; regenerate them after editing a germ.
