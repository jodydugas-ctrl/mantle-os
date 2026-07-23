# Examples

## Current And Gate-Aligned

These are proven by the framework's own gate. Read and run these first:

- **`vcw/vcw_cube.py`** - the normative VCW cube format, standalone in one
  pure-stdlib file. `python examples/vcw/vcw_cube.py selftest` proves every
  format rule; `examples/vcw/interop.py` proves the standalone and
  `src/mantle/vcw` engine produce identical bytes.
- **`sample_app/`** - the canonical Path-B teaching host: an ordinary notes app
  with a README role map for Heart, Senses, Memory, Immune, Limbs, and Brain
  affordance. Use it with `python -m mantle assimilate examples/sample_app
  --dry-run` (add `--spore=out.png` to emit its germ spore), `python -m mantle
  anchor`, and the graft spore.
- **`spores/`** - germ spores, the one artifact that births an AppAI:
  `python -m mantle hatch examples/spores/greeter.png --out=nest/`.
- **`eggs/`** - the germ files those spores are packed from: `greeter.json`
  (the template), `notes_graft.json` (a graft germ targeting `sample_app`),
  and `calculator.json` (declares its own origin face, including the AppAI
  terminal surface and submit/blur text commit policy).
- **`phenotype_demo.py`** - wearable app-faces end to end.

The single best example is the framework proving itself: `python -m mantle teach`
(mirror: [`../FIELD_GUIDE.md`](../documents/FIELD_GUIDE.md)).

## Self-Contained Reference Demos

- `Mantle_Reference_Agent.html` - a single-file, in-browser Reference AppAI.
- `Mantle_Spreadsheet_Agent.html` - a single-file in-browser spreadsheet AppAI
  demo.
- `Mantle_Live_Agent.html` - the live agent workbench that fuses a real MIND over
  OpenRouter when the operator supplies a key.
- `Mantle_MacroDroid_Schema.yaml` - the Path-B alignment contract and MacroDroid
  JSON schema for anchoring/grafting a Mantle resident onto a MacroDroid host.

The browser demos are useful demonstrations, but the authoritative implementation
lives in the `src/mantle/` Python package and its runnable gates.

## Headless Smoke Tests

`examples/tests/` contains browser/runtime smoke tests for the demos and the
Calculator AppAI terminal behavior. Locally:

```bash
python -m http.server 8765 --directory examples
cd examples/tests
npm install
npm test
npm run test:calculator
```

Node lives only in `examples/tests`; the rest of the project stays dependency-light.
