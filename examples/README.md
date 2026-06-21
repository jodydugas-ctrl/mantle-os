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

## Legacy reference artifacts (do NOT build from these)

- `Mantle_Reference_Agent.html`
- `Mantle_Spreadsheet_Agent.html`
- `Mantle_MacroDroid_Schema.yaml`

These large, generated artifacts were produced for the **v2-era** framework and predate the v3
package and all of Gen-4 (the egg/hatchery/anchor/graft/mem/compiler/ganglia/vault tissue, the
66-invariant gate, the self/other key, nociception, graded memory). They are kept for historical
reference only and have **not** been regenerated against the current system. **Do not treat them
as current examples** — use the runnable items above and the `mantle/` package (ground truth).
Regenerating them against Gen-4 is a worthwhile but separate task.
