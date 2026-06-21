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
`vcw-cube-png-v2`, same eight organs + the `<facts.N>` grammar). Beyond describing it, both demos
now **functionally implement and browser-test the four Gen-4 organ behaviors**: graded memory
(deweight → recoverable ghosts), self/other (a Body-resident genesis key; anti-clone), nociception
(`heart.pain`, the now-interrupt), and `schedule_pulse` (planned future wakes that chain thoughts).
Both demos also expose a **browser-feasible subset of the reproductive/symbiotic tissue** as Body
primitives: keyless knowledge plasmids (`mem.excrete` / `mem.digest` — foreign knowledge digests as
*inferred*, never fact), a **SELF-locked seed vault** (`vault.seal` / `vault.reconstruct` — an OTHER
body cannot reopen it), and **egg** author/hatch (declare a new AppAI as data, then instantiate it);
the Arms serve as **ganglia**. The parts that act on a real *host repo* — host residency (`anchor`),
the **graft egg**, and the self-redesigning **compiler** — are inherently out of reach for a
single-page demo and remain **framework-only** in the `mantle/` Python package and the runnable
`FIELD_GUIDE.md`. For anything authoritative, the `mantle/` package is ground truth.

## Headless smoke tests (`tests/`)

`tests/demo_smoke.mjs` (Playwright) gives the single-file demos their own runtime regression
cover, complementing the Python gate. Each demo must mount, expose its engine, and pass its
in-browser checks — the Spreadsheet's Stage-1 self-audit, and the Reference Agent's
Genome/resolver/self-audit assertions (primer present, `activeBodyRefs` populated-only, dangling
vs. unsupported ref labeling, the `B-GEN` audit row). Runs in CI as **Demo Smoke**; locally:

```bash
python -m http.server 8765 --directory examples &        # serve the demos
cd examples/tests && npm install && npx playwright install chromium
BASE_URL=http://localhost:8765 node demo_smoke.mjs
```
(Node lives only here; the rest of the project stays dependency-free. `node_modules/` is gitignored.)
