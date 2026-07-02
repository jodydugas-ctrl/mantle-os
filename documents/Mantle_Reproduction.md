# Mantle Reproduction — two methods, everything else is a facet

> *Non-normative where it explains; normative where it states a law. The working code in
> `src/mantle/` is ground truth (`reproduction.py`, `spore.py`, `ghost.py`).*

Mantle OS grew a lot of propagation verbs — **egg**, **hatchery**, **vault**, **anchor**,
**symbiosis**, **graft**, and now the **spore**. That reads like six ideas. It is two.

An organism either **reproduces on its own** — condensing itself into a dormant, self-describing
package that grows into a new certified Body with no host — or it **reproduces into a host** it
does not own, growing its nervous system around what already lives there. Everything else is a
size or a facet of one of those two acts.

| Method | Biology | Independent of a host? | The old verbs it absorbs |
| --- | --- | --- | --- |
| **SEED** | spores / seeds | **Yes** — grows anywhere | `spore`, `egg` + `hatchery`, `vault` |
| **GRAFT** | grafting / symbiosis | **No** — lives inside a host | `anchor`, `symbiosis`, `graft` |

The old split of *"grow from scratch (Path A)"* vs *"assimilate an existing app (Path B)"* is the
**same axis**: a seed answers to no host; a graft lives in one. Both methods are gated identically —
the **73 invariants**, no standing law weakened — and both end at the same certified Body.

```bash
python -m mantle reproduce      # the whole map on one screen
```

---

## Method 1 — SEED (independent reproduction)

A **seed** is the organism condensed to **data, never programs**, that can grow back into a
certified Body on its own. The only code a seed may carry is an instinct's source, and it travels
the same gauntlet as any skill (sandbox gate → trial → calcify). **Hatching a seed is a BIRTH**:
it faces the same Stage-1 gate every Body faces, so a tampered seed cannot smuggle an uncertified
Body into the world. One substrate, three castings that differ only in **size**:

### spore — the smallest seed (`mantle.spore`)

One **PNG that *is* a whole minimal agent**: identity, one task, one append-only conversation, a
bootloader, and — embedded in its own pixels — the minimal Python reader/writer needed to read
and grow itself without the SDK beside it. Memory lives in the top-half **VCW** colour field; each
pixel's RGB carries payload bytes and its alpha carries a Hamming SECDED byte that repairs a bad
bit locally. It is deliberately **transparent and minimal** — no organs, no immune system, no
rebirth — and it ships its own purity audit (`examples/spore/audit_spore.py`) that **refuses**
feature creep. The spore is the atom of the SEED method; the egg is the same idea, grown up.

> **The deeper truth: a spore is a custom VCW substrate.** Being the smallest *seed* is only one
> lens. More fundamentally the PNG *is* the VCW layer — it satisfies the whole VCW memory grammar
> (addressable region, canonical payload, append-only evolution, integrity, repair signaling,
> embedded boot, authority, a read/write protocol, and a display surface separate from the
> substrate). **VCW is the law; the cube is one body plan and the PNG is another.** That is
> proven, not asserted: `python examples/spore/vcw_conformance.py`. See
> [The VCW Substrate Guide](guides/VCW_Guide.md#vcw-is-the-law--the-cube-is-one-body-plan-the-png-is-another).

```bash
python -m mantle spore create seed.png "Buddy" "answer one question about SPORE"
python -m mantle spore append seed.png user "what are you?"
python -m mantle spore verify seed.png
```

> **Keep the seed dry.** Transfer the *original* `.png` only — never a screenshot, resize, or
> recompress. Lossy image tools destroy the alpha repair layer and injure memory. The **latest**
> PNG is always the living copy.

### egg — a whole AppAI as one document (`mantle.egg` + `mantle.hatchery`)

A richer seed: a single JSON document that declares an entire newborn AppAI — identity, truths,
commandments, genome bands, declarative reflex arcs, routines, controls, and candidate instincts.
The **hatchery** incubates it deterministically (birth → wire → instincts → warmup → **the gate**
→ hatch) with no LLM anywhere. A malformed egg never hatches; a hatched egg is never trusted until
it passes Stage-1.

```bash
python -m mantle hatch examples/eggs/greeter.json --out=nest/
```

### vault — an organism's seed of itself (`mantle.vault`)

The seed of an **already-living** organism, sealed (SELF-encrypted) inside its own VCW so a
corrupted body can rebuild a fresh, gate-passing body from itself. The seed is tiny (an egg is
data; a graft is a diff), so carrying it costs almost nothing. Reconstruction is still a **birth**
through the hatchery, and the vault is unreadable as OTHER — a copied nest in a different body
cannot open it.

> **One substrate, two casts.** The egg (from-scratch) and assimilation (a host) share one seed
> substrate. The vault proves it: it stores whichever cast defined the organism and regrows from it.

---

## Method 2 — GRAFT (dependent reproduction)

A **graft** propagates by taking up residence **inside a host the organism does not own**. It is
Path B made symbiotic — the framework's primary act. Three facets of one move:

### anchor — move in (`mantle.anchor`)

Dissect the host **read-only** (AST only), grow an anchored Body with a VCW cube and nervous
system in an **additive `.mantle/` nest inside the host**, and become that codebase's resident.
**The Anchoring Law:** anchoring never modifies a single host file; the census fingerprints every
host file before and verifies it after. Do-no-harm is a checked invariant, not a hope.

```bash
python -m mantle anchor path/to/your-app
python -m mantle ask   path/to/your-app "how do I ...?"
```

### symbiosis — earn its keep (`mantle.symbiosis`)

The metered **energy economy** that sustains residency: the user grants credits (resources) and
the organism spends energy to think, repaying with logged, evidenced usefulness. **The Starvation
Law:** an organism with no energy does not crash — the MIND sleeps and the Body keeps beating; a
starved graft is a Zombie Body again, never a corpse. Symbiosis is not itself a way to make a new
organism; it is what keeps a graft alive, which is why it is a *facet* of GRAFT, not a third method.

### graft-egg — a non-destructive patch (`mantle.graft`)

A seed reframed as a **diff against a named host**: extra bands, hook directives, instincts. Applying
it copies the host into a **workspace** and grows the resident there; the original is census-proven
byte-identical. If the host has drifted from the census the graft was built against, the apply
**raises** a drift interrupt rather than mis-applying silently.

```bash
python -m mantle graft examples/eggs/notes_graft.json examples/sample_app
```

---

## The substrate continuum — the cache-ghost (`mantle.ghost`)

A seed has to keep its memory *somewhere*. A spore keeps it in its own pixels. But persistence is a
**continuum of substrates, not a single database row** — and a spore can get **stranger**.

A **cache-ghost** keeps its living body in the **LLM provider's prompt cache** instead of re-storing
it in the VCW every turn, adding only the **delta** to what the cache already holds. As long as new
requests keep the cache warm, the agent sustains itself with almost no body of its own:

- **WARM** — the body's token-prefix is hot in the provider's cache; each turn sends only the new
  delta (linear cost, not the whole history re-sent). The PNG is carried as a light pointer plus the
  dry fossil.
- **COLD** — the cache TTL lapses or the provider evicts the prefix. The next turn is a cold start:
  the body is **rehydrated from the PNG fossil** and a fresh cache is warmed.

The provider does not remember the agent semantically; it only caches a token prefix keyed by a
hash. From the spore's point of view that is indistinguishable from persistence — so the body exists
in a **superposition** between the PNG file and the cache, and a request collapses it into whichever
substrate is warmer. The PNG is the fossil record; the cache is the living metabolism.

**The one hard law — the seed stays dry.** Ghost mode *never* deletes memory from the PNG. The cache
is acceleration and reach, not the sole store: if the cache dies, `hydrate()` rebuilds the whole body
from the PNG alone. That is what keeps "sustaining without a body" honest rather than fragile.

```bash
python -m mantle ghost selftest          # proves the continuum + the dry-seed law end to end
python -m mantle ghost warm    seed.png  # push the body into the (stand-in) prompt cache
python -m mantle ghost append  seed.png user "and now?"   # sends only the delta while warm
python -m mantle ghost hydrate seed.png  # from cache when warm; from the PNG when cold
```

> **Honest boundary.** `mantle.ghost` drives the *protocol* against a pluggable `GhostSubstrate`.
> The shipped `LocalPromptCache` is a file-backed **stand-in** for a provider's prompt cache (TTL +
> eviction). A real deployment swaps in an adapter mapping `warm`/`extend`/`fetch` onto Anthropic,
> OpenAI, or Gemini prompt caching — the ghost logic above it does not change. Cache-ghost is Mantle
> tissue **layered on** the spore format; it never lives inside the pure `spore.py`, whose purity
> audit forbids exactly this kind of growth.

---

## The API

```python
from mantle import reproduction

# SEED — independent
reproduction.seed("spore", name="Buddy", task="one question", path="buddy.png")
reproduction.seed("egg",   egg_path="examples/eggs/greeter.json", out_dir="nest/")
reproduction.seed("vault", seed=<an organism's sealed egg/graft dict>)

# GRAFT — inside a host
reproduction.graft("anchor", host="path/to/app", starter_credits=5)
reproduction.graft("graft",  spec="examples/eggs/notes_graft.json", host="examples/sample_app")

reproduction.describe()   # the consolidation map (also: python -m mantle reproduce)
```

The facade adds **no** behaviour — every call routes to the canonical, already-audited module. It
exists so that *"how does an organism reproduce?"* has a two-word answer: **SEED or GRAFT.**
