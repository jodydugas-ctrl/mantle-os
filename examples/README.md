# Examples

## Current & gate-aligned (build from these)

These are proven by the framework's own gate — read and run them:

- **`vcw/vcw_cube.py`** — the **normative VCW cube format**, standalone in one pure-stdlib file.
  `python examples/vcw/vcw_cube.py selftest` proves every format rule; `examples/vcw/interop.py`
  proves the standalone and the `src/mantle/vcw` engine produce identical bytes
  (`bench.py` times the standalone codec).
- **`sample_app/notes_app.py`** — a deliberately ordinary little app. It is the target for
  `python -m mantle assimilate examples/sample_app --dry-run`, `python -m mantle anchor`, and the
  graft egg (`python -m mantle graft examples/eggs/notes_graft.json examples/sample_app`).
- **`../examples/eggs/greeter.json`** — the egg template; `python -m mantle hatch examples/eggs/greeter.json`.
  **`../examples/eggs/notes_graft.json`** — a graft egg targeting `sample_app`.
  **`../examples/eggs/calculator.json`** — an egg that declares its own **origin face** (a real HTML
  calculator front-end), so the hatched AppAI is born wearing it.
- **`phenotype_demo.py`** — wearable app-faces, end to end (M9): `python examples/phenotype_demo.py`.
  Hatches the calculator (born wearing its origin face), seals the real
  `Mantle_Spreadsheet_Agent.html` surface as a second face, wears it (source recovers byte-for-byte),
  shows an OTHER body cannot read the sealed faces, and carries the default face across a rebirth.

The single best "example" is the framework proving itself: **`python -m mantle teach`** (mirror:
[`../FIELD_GUIDE.md`](../documents/FIELD_GUIDE.md)).

## Self-contained reference demos

- `Mantle_Reference_Agent.html` — a single-file, in-browser **Reference AppAI** (React, runs an
  organism with its own JS VCW-cube codec, organ atlas, reflexes, and rebirth/ancestor lineage).
- `Mantle_Spreadsheet_Agent.html` — a single-file in-browser **spreadsheet AppAI** demo.
- `Mantle_Live_Agent.html` — the **live agent**: a single-file AppAI workbench that fuses a real
  MIND over OpenRouter (bring your own key). Grown from the historical v1.5 body and molted to
  current doctrine: the nine organs named in an `ORGAN_ATLAS` (its crystal-shard array is a
  legitimate **custom VCW substrate**, like SPORE), a **runnable** Stage-1 gate
  (`reflexRunSelfAudit`, 16 deterministic rows including a memory-write
  round-trip on a disposable buffer — verdicts are computed at boot, never declared),
  nociception (`reflexPain`, the now-interrupt), and planned wakes (`reflexSchedulePulse`).
  Without a key it boots, certifies, and runs its zombie heartbeat — the Body needs no MIND.
- `Mantle_MacroDroid_Schema.yaml` — the **Path-B alignment contract** + MacroDroid JSON schema for
  anchoring/grafting a Mantle resident onto a MacroDroid host.

Their version labels, framework prose, ontology/system prompts, and doc references are current;
the YAML's `mantle_alignment` contract carries a `capabilities` block. They are honest about
scope — the in-browser HTML demos run the **Body / organ / VCW core**. The Reference and
Spreadsheet demos use the Gen-4 cube format (`vcw-cube-png-v2`, the eight pre-Reproduction
organs — the in-browser engines predate the ninth organ — + the `<facts.N>` grammar). The Live
Agent preserves the working v1.5 live-body `vcw-png-v1` demo path and carries the current
nine-organ doctrine. Beyond describing it, the Gen-4 demos now **functionally implement and
browser-test four organ behaviors**: graded memory
(deweight → recoverable ghosts), self/other (a Body-resident genesis key; anti-clone), nociception
(`heart.pain`, the now-interrupt), and `schedule_pulse` (planned future wakes that chain thoughts).
Both demos also expose a **browser-feasible subset of the reproductive/symbiotic tissue** as Body
primitives: keyless knowledge plasmids (`mem.excrete` / `mem.digest` — foreign knowledge digests as
*inferred*, never fact), a **SELF-locked seed vault** (`vault.seal` / `vault.reconstruct` — an OTHER
body cannot reopen it), and **egg** author/hatch (declare a new AppAI as data, then instantiate it);
the Arms serve as **ganglia**. Both demos now also carry **wearable app-faces (M9 phenotype)**:
each is *born wearing* a default `origin` face, and you can seal additional front-ends into the
VCW and wear them — `phenotype.express` / `phenotype.list` / `phenotype.wear` / `phenotype.active`,
SELF-encrypted (an OTHER body's key yields garbage) and append-only. The **Spreadsheet** demo
surfaces this as a **🧬 Faces** terminal tab: list faces, paste HTML to seal a new one, and click
*Wear* to render the worn face live in a sandboxed frame. The **Reference Agent** wires `wear` to its
existing **app-face Display**, so the worn face shows on the body surface. The parts that act on a
real *host repo* — host residency (`anchor`),
the **graft egg**, and the self-redesigning **compiler** — are inherently out of reach for a
single-page demo and remain **framework-only** in the `src/mantle/` Python package and the runnable
`FIELD_GUIDE.md`. For anything authoritative, the `src/mantle/` package is ground truth.

## Headless smoke tests (`tests/`)

`tests/demo_smoke.mjs` (Playwright) gives the Reference and Spreadsheet demos their browser
runtime regression cover, complementing the Python gate. `tests/live_agent_smoke.mjs` gives the
Live Agent its own jsdom/Babel/React mount check and runnable Stage-1 gate. Together they prove
the demos mount, expose their engines, and pass their in-browser checks — the Spreadsheet's
Stage-1 self-audit, the Reference Agent's Genome/resolver/self-audit assertions (primer present,
`activeBodyRefs` populated-only, dangling vs. unsupported ref labeling, the `B-GEN` audit row),
and the Live Agent's boot/self-audit plus replay-loop guard checks. Runs in CI as **Demo Smoke**;
locally:

```bash
python -m http.server 8765 --directory examples &        # serve the demos
cd examples/tests && npm install && npx playwright install chromium
BASE_URL=http://localhost:8765 npm test
```
(Node lives only here; the rest of the project stays dependency-free. `node_modules/` is gitignored.)
