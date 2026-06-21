# Examples

## Current & gate-aligned (build from these)

These are proven by the framework's own gate — read and run them:

- **`vcw/vcw_cube.py`** — the **normative VCW cube format**, standalone in one pure-stdlib file.
  `python examples/vcw/vcw_cube.py selftest` proves every format rule; `examples/vcw/interop.py`
  proves the standalone and the `mantle/vcw` engine produce identical bytes. The rest of
  `vcw/` (`audit.py`, `test_invariants.py`, `examples_boot.py`, …) is the v2.3 back-compat
  reference suite the CI runs — it drives the live `mantle` package and stays green.
- **`sample_app/notes_app.py`** — a deliberately ordinary little app. It is the target for
  `python -m mantle assimilate examples/sample_app --dry-run`, `python -m mantle anchor`, and the
  graft egg (`python -m mantle graft eggs/notes_graft.json examples/sample_app`).
- **`../eggs/greeter.json`** — the egg template; `python -m mantle hatch eggs/greeter.json`.
  **`../eggs/notes_graft.json`** — a graft egg targeting `sample_app`.

The single best "example" is the framework proving itself: **`python -m mantle teach`** (mirror:
[`../FIELD_GUIDE.md`](../FIELD_GUIDE.md)).

## Self-contained reference demos (Gen-4-aligned)

- `Mantle_Reference_Agent.html` — a single-file, in-browser **Reference AppAI** (React, runs an
  organism with its own JS VCW-cube codec, organ atlas, reflexes, and rebirth/ancestor lineage).
- `Mantle_Spreadsheet_Agent.html` — a single-file in-browser **spreadsheet AppAI** demo.
- `Mantle_MacroDroid_Schema.yaml` — the **Path-B alignment contract** + MacroDroid JSON schema for
  anchoring/grafting a Mantle resident onto a MacroDroid host.

These were aligned to **Gen-4**: version labels, framework prose, ontology/system prompts, and
doc references are current; the YAML's `mantle_alignment` contract is fully Gen-4 (with a
`gen4_capabilities` block). They are honest about scope — the in-browser HTML demos run the
**inherited Body / organ / VCW core**, which Gen-4 carries *unchanged* (same cube format
`vcw-cube-png-v2`, same eight organs + the `<facts.N>` grammar), and their prompts now describe
the Gen-4 hardening (self/other, event-gated nociception, graded memory). The fuller Gen-4
reproductive/symbiotic tissue (egg/hatchery, anchor/symbiosis, graft, mem, compiler, ganglia,
vault) is **not reimplemented in JS** — it lives in the `mantle/` Python package and the runnable
`FIELD_GUIDE.md`. For anything authoritative, the `mantle/` package is ground truth.
