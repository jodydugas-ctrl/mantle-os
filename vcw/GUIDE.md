# Mantle VCW — Working Guide

**Mantle OS v2.3** · The one guide to the VCW substrate and its programmable layer.
*Part I teaches the cube (the heart). Part II teaches the programmable layer — boot sectors,
the Body, drivers, lineage, and skills. Companion code: `vcw_cube.py` + the v2.1 modules;
runnable tours: `examples.py` and `examples_boot.py`.*

---

# PART I — The VCW Cube (substrate)


> The VCW cube is the **heart of a Mantle AppAI's nervous system**: its durable,
> self-describing memory substrate. This guide teaches you to read, address, write,
> and reason about a cube. The companion code is [`vcw_cube.py`](vcw_cube.py); a
> runnable tour is [`examples.py`](examples.py). Read them together — every concept
> below maps to a function you can run.

VCW stands for **Visual Cortex Workspace**. The format id is `vcw-cube-png-v2`.

---

## 1. What a cube *is*

A cube is a stack of **800 layers**. Each layer is one **800 × 800 RGBA image** — a
real, valid PNG you can open in any image viewer. Because memory is stored as
pictures, the whole organism's mind is inspectable with ordinary tools.

```
cube  = 800 layers stacked          (index 0 .. 799)
layer = 800x800 RGBA image          = 2,560,000 flat bytes  (LAYER_BYTES)
band  = a named, contiguous RANGE of layers reserved for one purpose
entry = one immutable record appended into a band
```

The container (a `.vcw` file) is just a **ZIP** holding:

```
manifest.json            cube-level descriptor
cube_boot.json           the Cube Boot Sector (authoritative band map)
layers/000.png .. 799.png   every materialized layer
```

Only **touched** layers are written, so a young cube's `.vcw` file is small even
though the address space is always 800 layers wide.

---

## 2. Addressing: from (layer, x, y) to a byte

Any single byte inside a layer is addressed by pixel coordinate:

```
offset = (y * SIDE + x) * CHANNELS          # SIDE = 800, CHANNELS = 4
```

You rarely place bytes by hand. Instead each layer's pixel stream carries two
**length-prefixed JSON blobs** behind an 8-byte magic. The `(layer, x, y)` formula
is the primitive the low-level tools and the reference-resolver rely on.

### Layer pixel-stream layout (inside one layer's decoded RGBA bytes)

```
[ 8 bytes   MAGIC = b"VCWPNG2\n" ]
[ 4 bytes   uint32 len(boot_json) ][ boot_json  utf-8 ]   <- Layer Boot Sector
[ 4 bytes   uint32 len(payload_json) ][ payload_json utf-8 ]   <- Payload (entries)
[ zero padding up to 2,560,000 bytes ]
```

`build_layer_rgba(boot, payload)` writes this; `parse_layer_rgba(raw)` reads it
back. An all-zero layer (no magic) parses to `(None, None)` — it is simply empty.

---

## 3. The band map (where things live)

Layers 0–3 are the **Cube Boot Sector**. Layers 4–7 are the **Genome** (the four
body entries). The nine reserved purpose bands follow:

| Band          | Layers   | Archetype  | Notes                              |
|---------------|----------|------------|------------------------------------|
| *(boot)*      | 0–3      | —          | Cube Boot Sector / band map        |
| *(genome)*    | 4–7      | genome     | bodyentry `.000`–`.003`            |
| `prime`       | 8–99     | reference  | index / pointers                   |
| `identity`    | 100–149  | summary    | who the AppAI is, current state    |
| `facts`       | 150–199  | table      | durable key/value truths           |
| `events`      | 200–249  | log        | append-only event history          |
| `discoveries` | 250–299  | summary    | learned/derived knowledge          |
| `senses`      | 300–399  | log        | sensor intake + classification     |
| `immune`      | 400–449  | audit      | audit findings, quarantine records |
| `brain`       | 450–499  | dispatch   | dispatch lifecycle records         |
| `thoughts`    | 500–549  | log        | **PRIVATE** — veiled on read       |
| *(app)*       | 550–749  | caller     | application-defined bands          |
| *(tail)*      | 750–799  | reserved   | scratch / future                   |

These ranges are defined once in `vcw_cube.py` as `RESERVED_BANDS`,
`BOOT_LAYERS`, and `GENOME_LAYERS`. Every other document references these numbers —
they must agree everywhere.

---

## 4. The Genome: four identity records

The Genome holds the AppAI's identity as four records, loaded **before** any band, in fixed order:

| Record          | Title                | Rule                                   |
|-----------------|----------------------|----------------------------------------|
| `bodyentry.000` | Primer               | **immutable** after genesis            |
| `bodyentry.001` | Immunization         | safety rules / invariants              |
| `bodyentry.002` | Special Instructions | operator-supplied directives           |
| `bodyentry.003` | Inheritance          | **rebirth-write-only** (set on rebirth)|

A fused MIND **never** writes these directly. Attempting to overwrite the Primer raises
`PermissionError`.

> **Where the Genome lives (read this).** The base codec (`vcw_cube.py`) can store these four
> records *inside* the cube (reserved layers 4–7) — a low-level capability shown here for
> completeness. **The Mantle architecture supersedes that:** identity lives in the **BODY**
> (`body.py`), not the cube, so it survives rebirth and the cube stays pure experiential memory.
> Part II (`Organism` / `Body`) is the model you build against; treat the in-cube genome as a
> substrate primitive, not the home of identity. The record *names* (Primer / Immunization /
> Special Instructions / Inheritance) are identical in both — only their home moved.

---

## 5. Entries and the entry hash

`make_entry(opcode, content, author, source)` returns one record:

```json
{
  "id": 7,
  "ts": 1730000000.0,
  "opcode": "WRITE",
  "author": "BODY",
  "source": "",
  "content": { "k": "sky", "v": "blue" },
  "tombstone": false,
  "quarantined": false,
  "hash": "9f1c..."
}
```

The `hash` is a SHA-256 (first 16 hex chars) over the immutable fields. `verify()`
recomputes it; a mismatch is an integrity failure. `id` is assigned on `append`.

---

## 6. Reading and the **veil**

`cube.read(band)` returns only **visible** entries:

- tombstoned entries are hidden — always;
- quarantined entries are hidden — always;
- **private** layers (the `thoughts` band) return nothing unless you pass
  `reveal_private=True`.

The veil is a **Body reflex** — it is enforced by deterministic code, no LLM
required. Only a fused MIND is permitted to lift the veil on its own `thoughts`.

```python
cube.read("thoughts")                       # -> []      (veiled)
cube.read("thoughts", reveal_private=True)   # -> [...]   (the MIND's own view)
```

---

## 7. Tombstone vs. quarantine (immune reflexes)

- **tombstone** — the entry was true but is now retired (soft delete). The record
  stays for audit; it just stops being visible.
- **quarantine** — the entry is *suspect* (possible corruption, untrusted source).
  It is isolated from normal reads until the immune system clears or removes it.

Both are reversible record-level flags, never destructive rewrites.

---

## 8. Verify + staged commit (durability)

Every `cube.save(path)`:

1. writes the whole container to `path.stage`;
2. **re-loads** the staged file and runs `verify()`;
3. only on a clean verify does it `os.replace(stage, path)` — an atomic swap.

A half-written or corrupt cube can therefore never replace a healthy one. This is
the substrate's core durability guarantee.

`verify()` checks: Genome present and ordered, Primer non-empty (the AppAI is
"born"), every reserved band head present and correctly labeled, and every entry
hash intact. An empty problem list means a healthy cube.

---

## 9. Reference syntax (how organs point at memory)

Organs and a fused MIND refer to memory with explicit, resolvable references.
The resolver materializes them deterministically during Context Assembly — **no
unresolved reference is ever handed to a model.**

```
<layername:x:X:y:Y>            a byte address within a band's head layer
<cube:GEN:layername:x:X:y:Y>   the same, pinned to a generation
<bodyentry.NNN:entry:M>        the M-th entry of a body entry
<bandname:entry:M>             the M-th visible entry of a band
```

A reference that resolves to nothing is a **dangling reference** → it is logged as
an `immune` event, never silently dropped.

---

## 10. Capacity, overflow, and metabolism

A layer holds `LAYER_BYTES` (2,560,000) bytes. As a band head fills:

- at **0.75** capacity the **overflow reflex** fires → compaction / tiering;
- at **0.90** capacity the **emergency** reflex fires.

Reaching capacity triggers **metabolism** (compaction, hot/cold tiering), **not
rebirth**. Rebirth is a separate, MIND-initiated event that writes
`bodyentry.003` (Inheritance) and re-runs the Awakening Ceremony.

---

## 11. CLI quick reference

```
python vcw_cube.py create   organism.vcw --primer "first breath"
python vcw_cube.py append    organism.vcw facts '{"k":"sky","v":"blue"}' --opcode WRITE
python vcw_cube.py read      organism.vcw facts
python vcw_cube.py read      organism.vcw thoughts --reveal-private
python vcw_cube.py tombstone organism.vcw facts 7
python vcw_cube.py quarantine organism.vcw facts 9
python vcw_cube.py verify    organism.vcw
python vcw_cube.py inspect   organism.vcw
```

Run `python examples.py` for the full narrated lifecycle.

---

## 12. The one-paragraph summary

A VCW cube is 800 PNG layers grouped into named bands. Identity lives in the
Genome (four body entries, Primer immutable). Memory is appended as immutable,
hashed entries into reserved bands. Reads apply a veil (hiding tombstoned,
quarantined, and private records). Saves are staged and verified before an atomic
swap. Everything in this guide is a **Body** behavior — deterministic, no LLM —
which is exactly why a Mantle Body can run and be certified *before* a brain is
ever attached.


---

# PART II — Programmable Boot Sectors, the Body & the Lineage


> This is the programmable layer on top of the base codec. **Part I above** covers the substrate;
> this Part II builds on it. Every concept maps to a module you can run; the full tour is
> [`examples_boot.py`](examples_boot.py).

The v2.1 modules turn the VCW from a fixed JSON-in-pixels store into a **self-describing,
programmable memory** with a **Body** that holds identity, a **lineage** of cubes, and
**executable reflex layers** the Body can run with no MIND.

| Module | What it adds |
|--------|--------------|
| [`boot.py`](boot.py) | boot-sector schema + the **driver registry** (programmable encodings) |
| [`drivers.py`](drivers.py) | `log-json`, `keyvalue`, `calendar-spatial`, `exec` drivers |
| [`body.py`](body.py) | the **Body** store: Primer / Special Instructions / Immunization |
| [`refs.py`](refs.py) | the unified reference resolver `<TARGET.SELECTOR.ADDRESS>` |
| [`lineage.py`](lineage.py) | the boot-driven `Cube` + the `Organism` (Prime + ancestral chain) |
| [`skills.py`](skills.py) | the **Inner Voice** self-inquiry skill |

---

## 1. Two-level encoding: the boot sector is a programmable protocol

A boot sector is **data that selects code**. Two levels:

1. **Boot-sector format** — fixed and universal; the Body always knows how to read it.
2. **Payload format** — *programmable*; the boot sector names a registered **driver** and
   supplies params.

```python
from boot import make_band_boot
boot = make_band_boot("calendar", head=560, encoding="calendar-spatial",
                      params={"epoch": "2026-01-01", "palette": {"0066ff": "work"}})
```

The Body holds the *drivers* (trusted, shipped code); the cube holds *boot sectors* (declarative
data). That is the Body/MIND split applied one level down: the boot sector says **what**, the
Body knows **how**.

A **driver** implements three verbs:

```python
class Driver:
    def empty(self, params): ...                 # initial content for a fresh layer
    def read(self, content, params, reveal_private=False): ...
    def retrieve(self, content, params, address): ...   # one item by index/key/coord
    def append(self, content, params, value): ...       # add a new state
```

Register with `@register`; look up with `get_driver(encoding)`.

---

## 2. The four drivers

- **`log-json`** — append-only list of immutable, hashed entries (the v2.0 default). Reads apply
  the veil (tombstoned/quarantined hidden).
- **`keyvalue`** — a small mutable map.
- **`calendar-spatial`** — data stored **as colors at coordinates**: a real RGBA canvas. A date
  maps to a cell `(x = weekday, y = week index since epoch)`; the pixel color encodes meaning
  via the palette. The layer persists as a real PNG you can open as an image.

  ```python
  cube.calendar_set("calendar", "2026-06-15", "work")
  cube.calendar_get("calendar", "2026-06-15")     # -> "work"
  ```

- **`exec`** — an **executable reflex layer** (see §5).

This is the whole point: a log, a table, and a calendar are all just pixels — what differs is
the *protocol the boot sector names*.

---

## 3. The Body — where identity lives

The Primer is **not** in the cube. The Body holds three referenceable categories — the mutable
surface that the append-only VCW cannot provide:

| Category | Access | Writer |
|----------|--------|--------|
| **Primer** | read-only | set once at birth (identity + truths + commandments) |
| **Special Instructions** | read/write | **Body applies**; the MIND only *proposes* |
| **Immunization** | read/write | Body (seeded with the Commandments at birth) |

```python
from body import Body
b = Body(); b.birth(identity={"name": "Notepad.app"}, truths=[...], commandments=[...])
b.mind_propose_special("Prefer concise answers.")   # MIND proposes (not written)
b.apply_special("Prefer concise answers.")          # Body applies
b.boot_order()   # -> {primer, special_instructions, immunization}  (the API boot order)
```

The Body also holds the durable **self record**: Primer + the **lineage index** (which cube
generation is Prime, where ancestors live). That record — not any cube — is the organism's
continuity across rebirths.

---

## 4. The unified reference grammar

One grammar addresses everything: `<TARGET.SELECTOR.ADDRESS>`.

```
TARGET    cube (default) | gen2 / shard2 (a generation) | body
SELECTOR  a band/layer name, or a Body category
ADDRESS   N (entry) | XxY (coordinate) | (omitted = whole band)
```

```python
org.resolve("<facts.11>")          # Prime, facts band, visible entry 11
org.resolve("<gen2.boot.23x33>")   # generation 2, that layer, pixel (23,33)
org.resolve("<body.immune.11>")    # Body, immunization entry 11
org.resolve("<calendar.0x24>")     # Prime calendar cell (0,24)
```

A reference that resolves to nothing is a **dangling reference**: it is logged to the `immune`
band, never silently dropped.

---

## 5. Executable reflex layers — learning becomes instinct

An `exec` layer stores **organism-grown code** the Body can run with **no MIND** — even in a
zombie state. This is how a skill the mind learns becomes an autonomic reflex. It only ever
arrives through a gate:

```
Cultivate (MIND writes candidate)  →  Trial (Body sandbox runs test cases)
   →  CALCIFY (gated: hashed + capability-bound exec layer)  →  Reflex (Body invokes, no MIND)
```

```python
from drivers import trial
code = "def compute_tax(amount, rate):\n    return round(amount*rate, 2)\n"
trial(code, "compute_tax", [({"amount":100.0,"rate":0.1}, 10.0)])   # prove it first
cube.calcify("reflex_tax", code, entry="compute_tax",
             signature={"in": {...}, "out": "float"},
             capabilities={"reads": [], "writes": [], "limbs": [], "net": False},
             provenance={"author": "MIND", "born_gen": 0})
cube.invoke("reflex_tax", {"amount": 80.0, "rate": 0.25})   # 20.0 — ran with NO MIND
```

Gates protect a skill at two moments — when it is *cultivated* and every time it is *invoked*:
- **Static sandbox gate (cultivation)** — before code can be trialed or calcified, a deterministic
  AST check (`validate_skill_code`) refuses `import`, dunder attribute access
  (`().__class__.__bases__…`, the classic namespace-escape vector), and dangerous builtins. Code
  that could break out of the restricted namespace never becomes an instinct — it raises
  `SandboxError`. (This complements, and does not replace, the hard-sandboxed `wasm` runner seam.)
- **Integrity (invocation)** — the code must match the `code_hash` it was promoted with, or it is
  refused.
- **Capability (invocation)** — the call may touch only the bands/limbs the layer declared;
  over-reach is an immune event, not an execution.
- **Trust (invocation)** — untrusted/foreign-provenance code may not run on the non-isolating
  Python runner; it must use the isolating `wasm` runner (or earn trust via trial+calcify).

Skills are **immutable + versioned**: a better skill is a *new* layer plus a tombstone, never an
in-place edit. They inherit across rebirth — so an aged organism's zombie Body is more capable
than a newborn's.

### Pluggable runners (and the `exec-wasm` seam)

Execution is delegated to a **runner** selected by the exec layer's `runner` field. The gates
(hash + capability) are runner-agnostic; only the execution backend swaps.

- **`python`** (default, shipped) — runs Python source in a restricted namespace with a
  wall-clock limit. Pure stdlib. A restricted namespace is *not* a hard sandbox.
- **`wasm`** (a **prepared seam — registered but not built**) — invoking it raises a clear
  `NotImplementedError`. It exists so a portable, hard-sandboxed runner can drop in later with no
  pipeline change. A WASM runner buys two things Python cannot: a **hard sandbox** (no ambient
  FS/net/process; only host imports you grant) and **portability** across any Body with a wasm
  runtime — software or hardware — so a calcified skill inherits across the whole lineage.

**The `exec-wasm` contract** (what an implementer fills in — see `WasmExecRunner` in
`drivers.py`):

```
runner   == "wasm"
language  -- source language the skill was authored in (informational)
runtime   -- target wasm runtime, e.g. "wasi-preview1"
code      -- base64-encoded .wasm module (code_hash covers it, unchanged)
entry     -- exported function to call
capabilities/limits -- enforced identically; instantiate with ONLY the granted imports, apply limits["ms"]
```

To enable it: add a wasm runtime (e.g. `wasmtime`) and `register_runner` an
`ExecRunner(name="wasm")` — the stub then goes away and nothing else changes.

---

## 6. The Inner Voice — the first learned skill

The agent speaks to itself: a framed, bounded sub-query to its own MIND, separate from heartbeat
cognition. Modes: `neutral`, `search` (fresh data), `oppose` (devil's advocate).

```python
from skills import InnerVoice, stub_model
iv = InnerVoice(org, stub_model)          # any callable prompt->answer works as the MIND
iv.ask("What changed recently?", mode="search")     # -> stored in discoveries (inferred)
iv.ask("Caching forever is wise.", mode="oppose")   # -> stored in thoughts (private)
```

**Provenance is the rule that matters:** an answer the agent gets by asking *itself* is
**inferred, not observed**. Search/factual answers land in `discoveries` tagged
`verified=False, confidence="inferred"` and are **never** auto-promoted to the `facts` band;
dialectic self-debate lands in the private `thoughts` band. A **waste budget** caps
self-conversation so the agent cannot spiral.

---

## 7. The Organism and rebirth-as-reformat

An `Organism` is `Body + Prime cube + ancestral chain`.

```python
from lineage import Organism, standard_genome, make_band_boot
org = Organism.birth(identity={...}, truths=[...], commandments=[...], genome=standard_genome())
...
org.rebirth(new_genome=..., reason="genome refit")   # MIND-chosen reformat
```

Because the VCW is append-only, a cube's genome is fixed for its life — the only path to a
re-fitted layout is a **new cube**. So `rebirth()`:

1. distills the current Prime into an inheritance summary,
2. **seals** the outgoing Prime as read-only **ancestral** (experiential writes now raise),
3. genesis a **new Prime** at `generation+1` with the authored genome,
4. records the inheritance as the new life's first discovery,
5. updates the Body's lineage index.

Generation-pinned references (`<gen0.facts.0>`) keep the entire past addressable forever —
rebirth loses nothing. `Organism.save(dir)` / `Organism.load(dir)` persist the whole lineage
(Body + every generation).

> **Durability + the visual substrate, in the path you build against.** As of v2.3 the canonical
> `lineage.Cube` shares the base codec's two guarantees, not just the legacy `vcw_cube.Cube`:
> every layer persists as a **real PNG** (entry/keyvalue/exec layers via the JSON-in-pixels codec,
> calendar layers as their raw RGBA canvas — so the whole cube is again "pictures you can open in
> any image viewer"), and `save()` is a **staged commit** (write `.stage` → reload → `verify()` →
> atomic `os.replace`). `verify()` also **recomputes every entry hash**, so the cube attests to
> its own integrity — a tampered field (including a rewritten `authorship`, now inside the hash)
> is caught by the cube itself, not only by the external audit harness.

---

## 7b. Layers on demand + safe reuse (efficiency)

A band reserves a **range** of layers (`span`) but does not pre-allocate them. Physical layers
are created **on demand** as the band fills, and **reclaimed** when compaction empties them —
"every layer has a purpose; be efficient."

```python
make_band_boot("log", head=570, encoding="log-json", span=4, purpose="rolling activity log",
               params={"max_entries_per_layer": 3})
```

- **Allocation:** append goes to the tail layer; when it reaches capacity, the Cube allocates the
  next layer in `[head, head+span-1]`, **preferring a freed layer from the reuse pool** before a
  fresh one. A band that exhausts its range raises `CapacityError` (the overflow reflex →
  compact, tier, or motivate a rebirth-reformat).
- **Reclaim:** `cube.compact(band)` drops tombstoned entries; any emptied non-tail layer returns
  to `cube.band_free[band]` for reuse.
- **Safe-reuse rule (the guardrail):** only entry-addressed (`log-json`/`keyvalue`) layers are
  reclaimable. **Spatial (`calendar-spatial`) and `exec` layers are never recycled** — their
  coordinate/identity addressing would break. Logical entry references (`<log.6>`) address the
  band's *concatenated visible stream*, so physical reuse never invalidates them.

```python
cube.band_layers["log"]   # active physical layers, in order
cube.band_free["log"]     # the reuse pool (freed slots)
cube.compact("log")       # -> {"reclaimed": N, "active": ..., "free": ...}
```

This is the Memory organ's metabolism at the layer level: grow only what you need, reclaim what you
empty, and never waste a layer.

---

## 8. Run it

```bash
python examples_boot.py     # the full v2.1 tour (no network, no key, no LLM)
```

It exercises every concept above end to end and prints what each step proves.
