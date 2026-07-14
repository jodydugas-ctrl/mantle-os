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
the full invariant suite, no standing law weakened — and both end at the same certified Body. Since molt 3.7.0 the ceremonies live under the **Reproduction organ** (`src/mantle/organs/reproduction.py`): the seed vault is a birthright, the sealed seed survives every rebirth, and SPORE-DISTILLATION lets a spore become the primer — never the key — of the body it births.

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

#### SPOREAGENT lifecycle receipt

A **SPOREAGENT** is not a larger `spore.py`. It is the agent-readable launch artifact around a
spore: the operator gives it source retrieval instructions, the agent retrieves or declares the
source, assimilates it through the Grimoire, and aims first at a certified **Zombie Body**. The
pure SPORE remains a public, minimal seed; lifecycle evidence lives in
`hatch_from_spore(..., source_receipt=...)` and the Reproduction organ's receipt.

The transition is auditable: the receipt records declared source, fetched/assimilated/certified
status, the SPORE-to-PRIMER boundary, and whether that boundary was sealed. Host or application
code remains **OTHER** until the Body proves it through PRIMER, seal, provenance, and the
certification path. The PRIMER may root the Body's identity and personal encryption identity, but
the key itself is minted by the Body. The MIND never receives, reads, infers, logs, transmits, or
handles that key material; it may only request Body-owned cryptographic acts.

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

> **Follow-up hardening:** the current vault is SELF-encrypted and gate-verified on
> reconstruction. A future compatible vault envelope should add an authentication tag while
> continuing to open existing vaulted seeds.

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

**The first hard law — the seed stays dry.** Ghost mode *never* deletes memory from the PNG. The
cache is acceleration and reach, not the sole store: if the cache dies, `hydrate()` rebuilds the
whole body from the PNG alone. That is what keeps "sustaining without a body" honest rather than
fragile.

**The second hard law — the cache is write-only.** A real provider's prompt cache can only ever be
spoken *into*, never read back *out of*: there is no fetch API, the full prefix still travels on
every request, and the only warmth signal is provider usage telemetry (`cached_tokens` or an
equivalent cache-read field) on the *next*
response. Warmth buys skipped **prefill compute** — roughly a tenth of the input price on the cached
span, and a large latency drop — never storage or bandwidth. So on a real substrate the dry-seed law
is not prudence but physics: the PNG is always the only recoverable copy. Substrates declare this
(`write_only=True`), `hydrate()` then always rebuilds from the fossil, and `status` reports
**PREDICTED-WARM / PREDICTED-COLD** rather than a warmth it cannot actually see.

**The third hard law — the prefix is append-only.** Providers match byte-exact prefixes; mutating
one early byte evicts everything after it. The cache-facing body is therefore *not* the spore's full
JSON state (whose sorted keys and `updated_at` would shift early bytes every turn) but a
**prefix-stable stream**: one immutable genesis line (identity at birth, tools protocol, embedded
tool hash), then one appended line per conversation turn. Growing the body only ever appends bytes —
the selftest proves the byte-prefix property. The PNG payload format is untouched.

**The fourth hard law — the window must fit the heartbeat, or DO-NOT-HAUNT.** Provider cache
windows differ by a lot — most are 15–60 minutes, but some are as short as ~5 minutes — while a
haunting organism has a *fixed* heartbeat (a METABOLIC-GOVERNANCE property, classically ~10 min).
The heartbeat must fit inside the window or the prefix is cold on *every* wake, paying the write
premium for a cache that never gets read. So haunting is a per-deployment feasibility check with a
hard **DO-NOT-HAUNT** verdict, remedied by lengthening the window (or an extended-TTL tier), or by
**supplementing the heartbeat** — keep the scheduled beat and push a one-shot *forced* beat partway
through the window (a 10-min beat plus a forced beat at +4 min covers a 5-min window without
disturbing the base timer). `hauntable(window_s, heartbeat_s)` decides; `warm()`/`status()` refuse
when it fails.

**The neutrality law — the provider is configuration, never code.** Mantle OS is a nervous-system
transplant: it must join *any* MIND to *any* container, so no module may name or code for a
specific LLM or company. A provider's window, minimum prefix, endpoint, auth headers, and any cache
directive are **data the operator supplies** — exactly as the MIND transport is a pluggable
`model(prompt) → text` with no vendor SDK. Tools may be *configured* to run optimally against a
given provider; they may never be *coded* for one.

Facets of governed haunting that follow from the laws:

- **TOO-SMALL-TO-HAUNT** — providers *silently* refuse prefixes below a floor (often ~1k–4k
  tokens; the exact number is provider config). The ghost measures and refuses to pretend: small
  spores live cold-and-cheap in their PNGs and *grow into* hauntability.
- **Warmth telemetry → nociception** — warm hits, cold starts, and the hit ratio are recorded in
  the ghost pointer every wake; **three consecutive cold wakes** raise a nociception flag (the
  heartbeat is slower than the true window, the prefix is unstable, or the provider is evicting).
- **Neutral economics** — reads refresh the window, so an actively-conversing ghost sustains
  itself at read prices; a cache write carries a premium, so warm-keeping pays only when the
  expected warm reads before the next cold event exceed a break-even count. That count is a
  function of the *provider's own* write premium (`break_even_reads(write_premium)`), never a
  hardcoded rate. SLEEP mode never keep-alives.
- **Usage proof, not hope** — real provider calls record cache and cost receipts: cached tokens,
  cache-write tokens, response-cache HIT/MISS, generation id, session id, provider/router metadata,
  cost, total cost, and redacted request hashes. The receipt never stores raw prompts, completions,
  or keys.

Prompt caching and response caching are different substrates. Prompt caching is provider-side
prefix reuse: Mantle keeps stable instructions and consolidated context at the front, then appends
dynamic scratch late so cache reads can be observed through token telemetry. Response caching is
router-side replay of an identical full request: it is useful for deterministic retries, evaluator
calls, unit tests, and failed workflow resumes, and a HIT is recorded as a zero-cost call rather
than disappearing from the ledger.

```bash
python -m mantle ghost selftest          # proves the continuum, the hard laws, the gates,
                                         #   telemetry/nociception, and the write-only seam
python -m mantle ghost warm    seed.png  # push the body into the (stand-in) prompt cache
python -m mantle ghost append  seed.png user "and now?"   # sends only the delta while warm
python -m mantle ghost hydrate seed.png  # from cache when warm; from the PNG when cold
# ONE real warm against a provider you configure (env-only; no vendor hardcoded, no SDK):
GHOST_CACHE_URL=... GHOST_MODEL=... GHOST_KEY=... python -m mantle.ghost_http seed.png
```

> **Honest boundary.** `mantle.ghost` drives the *protocol* against a pluggable `GhostSubstrate`.
> The shipped `LocalPromptCache` is a file-backed **stand-in** for a provider's prompt cache (TTL +
> eviction) that — unlike reality — *can* be read back, so offline tests stay deterministic. The
> **real substrate** is [`src/mantle/ghost_http.py`](../src/mantle/ghost_http.py)
> (`HttpPromptCache`): write-only, **vendor-neutral**, speaking the OpenAI-compatible
> chat-completions shape over pure-stdlib `urllib` (lazy import, no SDK). The provider is entirely
> configured — endpoint URL, model string, auth headers, cache window, minimum prefix, and an
> optional `request_shaper` hook for providers that want an explicit cache directive — so swapping
> providers is swapping config, never code. It is optional Phase-2 tissue: it needs a network and a
> key, and nothing else imports it, so the gates stay keyless and offline. Cache-ghost is Mantle
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
