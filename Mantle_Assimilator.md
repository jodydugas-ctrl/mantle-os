# Mantle OS — THE ASSIMILATOR (Path B)

**Mantle OS v2.3** · Grow organs around existing code, non-destructively
*This document REPLACES `Mantle_Part1_Body.md` when external source code is provided.
You still finish at the same Stage 1 Gate (`Mantle_Part1_Body_Audit.md`) and then
proceed to Phase 2 identically. Prerequisite reading: `docs/Mantle_Doctrine.md`,
`docs/Mantle_Organism_Lens.md`, `Mantle_PRIMER.md`, `examples/vcw/GUIDE.md`, `docs/Mantle_Organ_Atlas.md`.
Assimilation is the **Organism Lens applied as a read-only dissection**: find the host's organs
first, then thread a nervous system through them. Identity is synthesized into the **Body** (not
the cube); the App Inventory (Appendix A) is a hard, read-only gate before any edit.*

---

## §B.0 The prime directive: do no harm

You are given a living host codebase. You will **not rewrite its behavior.** You will
**grow organs around the existing tissue** — wrapping, observing, and binding it to a
VCW cube through **additive, fail-open instrumentation**. The host must run exactly as
before, plus now it has a nervous system and a memory.

Three invariants govern every edit:

1. **Additive only.** You insert hooks; you do not change control flow or logic. Every
   inserted line is marked `# MANTLE_HOOK_INSERTED` and recorded in a rewrite ledger.
2. **Fail-open always.** Every hook is wrapped so a fault inside it degrades and logs
   to `immune` — it can never crash the host (HF-B32).
3. **Reversible.** The rewrite ledger lets every inserted hook be located and removed,
   restoring the original source byte-for-byte.

---

## §B.0a Phase 0 — App Inventory & Organ Map (READ-ONLY, GATED)

**This is the first thing you do, and you modify nothing while you do it.** Before a single
hook is inserted, produce a complete **App Inventory & Organ Map**: a read-only reconnaissance
that maps the host's architecture onto the organ taxonomy. Touching host code before this
artifact exists and is approved is a hard fail (**HF-B42**).

Fill in the **App Inventory template (Appendix A)** below. At minimum, map
every **architectural surface** of the host to its target organ:

| Host surface | Target organ | Addressing / notes |
|--------------|--------------|--------------------|
| UI / editor / frontend | **Senses** (perceive) + **Limbs** (operate) | Human Surface Map (Senses) + ControlBridge/App-Face Bridge (Limbs) |
| execution / run engine | **Heart** (pulse) + **Limbs** (effectors) | the host's main run loop |
| credential / secret store | **Immune** | mark every crossing `secret_boundary=True` |
| webhook / inbound HTTP routes | **Senses** | sensor intake → classifier |
| trigger / scheduler / cron nodes | **Senses** + **Heart** | timed reflexes |
| AI / LLM / LangChain nodes | **Brain** affordance | `MIND_AFFORDANCE`; dormant until Phase 2 |
| database / persistence layer | **Memory** (+ metabolism) | map stores → bands; flush/compaction/reclaim |
| CLI / server boot path | **Heart** (boot) + boot verifier | the entry point |
| worker / queue / job mode | **Limbs** | async limb delegation |
| frontend / backend boundary | **Senses** (in) + **Limbs** (out) | the I/O membrane: perceive inbound, actuate outbound |
| config / environment | **Body** (Special Instructions) + **Immune** | secrets redacted |

### Worked example — assimilating n8n
| n8n subsystem | Organ | Why |
|---------------|-------|-----|
| workflow editor UI | Senses (perceive) + Limbs (operate) | controls enter the Human Surface Map (Senses); operating them is the ControlBridge (Limbs) |
| node execution engine | Heart + Limbs | the run loop pulses; each node execution is a Limb action with a proof |
| credential store | Immune | a `SECRET_BOUNDARY`; redact at enter/exit |
| webhook routes | Senses | inbound events → classified `senses` entries |
| trigger nodes | Senses + Heart | event/timed reflexes |
| AI / LangChain nodes | Brain | `MIND_AFFORDANCE` — left dormant in Phase 1 |
| database persistence | Memory (+ metabolism) | executions/workflows → memory bands; flush/compaction/reclaim |
| CLI / server boot path | Heart | boot + the fail-open boot verifier |
| worker / queue mode | Limbs | async delegation of long runs |
| frontend/backend boundary | Senses (in) + Limbs (out) | the API membrane: perceive inbound, actuate outbound |

**The Phase 0 gate:** the inventory artifact is produced, the surface→organ map is complete,
the proposed genome (band layout + per-layer purpose/driver/span) is drafted, and a human (or
the operator) signs the READ-ONLY line. Only then may Phase 5+ insert any hook.

---

## §B.1 The pipeline (17 phases)

Assimilation is a deterministic, no-LLM pipeline. Each phase has an output artifact
the Stage 1 audit can inspect. **Phases 0–4 are read-only; instrumentation begins at Phase 5,
only after the Phase 0 gate is signed.**

```
Phase 0   Inventory & Organ Map  READ-ONLY, GATED — map host surfaces → organs (§B.0a)
Phase 1   Symbol classification tag every symbol with its organ role (see §B.2)
Phase 2   Genome               synthesize body entries from the host's identity
Phase 3   Bands                map host state/data onto reserved + app bands
Phase 4   Security & boundary  find secret boundaries; mark secret_boundary=True
Phase 5   Hook runtime         install the fail-open hook functions (see §B.3)
Phase 6   References           build the reference resolver over host data
Phase 7   Interfaces           map the host's public interfaces to organ I/O
Phase 8   Zombie primitives    ensure heartbeat/persistence work with no host LLM
Phase 9   Arms                 wrap host actions/effectors as Limbs (with proofs)
Phase 10  Tiers                attach metabolism (overflow/compaction/tiering)
Phase 11  Rebirth              install the (dormant) rebirth path
Phase 12  Foundry              optional ops (Extensions) — skip unless §0 opts in
Phase 13  Memory palace        bind host persistence writes to memory bands
Phase 14  Economics / keyfile  stage the keyfile + model selection (dormant until P2)
Phase 15  Surface parity       build the Human Surface Map + ControlBridge over the host UI
Phase 16  MIND readiness       confirm the Body is a certified Zombie; ready for fusion
```

---

## §B.2 Symbol classification (Phase 1)

Tag every meaningful host symbol (function, handler, class, route) with exactly one
organ role. This is the map from existing code to the organ taxonomy.

| Role tag | Organ | Meaning |
|----------|-------|---------|
| `REFLEX` | Senses | a pure, deterministic reaction — wrap as a Body reflex |
| `ARM_ACTION` | Limbs | performs an external action/effect — wrap as a Limb with a proof |
| `DISPLAY_RENDER` | Limbs | renders human-visible output (efferent) — bind to the App-Face Bridge |
| `STATE_TRANSITION` | Memory | mutates app state — mirror into the correct memory band |
| `PERSISTENCE_WRITE` | Memory | writes durable storage — bind to a memory band (+ metabolism: flush/compaction) |
| `SENSOR_EVENT` | Senses | receives external input — route through intake + classifier |
| `MIND_AFFORDANCE` | Brain | a judgment point — leave dormant; becomes a Phase-2 extension |
| `SECRET_BOUNDARY` | Immune | crosses a credential/secret edge — mark `secret_boundary=True` |
| `INTERNAL_UTILITY` | — | pure helper — instrument only if it touches the above |
| `DEPRECATED` | — | dead code — record in the gap report; do not instrument |

The classification table is an audit artifact. Every symbol either has a role or is
explicitly `INTERNAL_UTILITY`/`DEPRECATED`.

---

## §B.3 The hook runtime (Phase 5)

Install these fail-open hook functions. Each wraps host behavior additively and writes
to the cube; each is individually `try/except → degrade + log to immune`.

| Hook | Binds to | Writes |
|------|----------|--------|
| `mantle_touch` | any instrumented entry | a lightweight access trace |
| `mantle_focus` | a `DISPLAY_RENDER` | the App-Face Bridge focus |
| `mantle_display` | a `DISPLAY_RENDER` | declarative face render (non-recursive!) |
| `mantle_sense` | a `SENSOR_EVENT` | a classified `senses` entry |
| `mantle_state_write` | a `STATE_TRANSITION` | the mirrored memory band entry |
| `mantle_persistence_write` | a `PERSISTENCE_WRITE` | memory band + tiering hook |
| `mantle_external_call` | an `ARM_ACTION` | dispatch + Action Execution Proof |
| `mantle_error` | any | an `immune` error event (never re-raised into host) |
| `mantle_immune` | the immune scan | integrity findings |
| `mantle_resource` / `mantle_starvation` | the heartbeat | resource/starvation events |
| `mantle_dispatch_*` | Limbs | dispatch lifecycle records (NOTIFIED/COMPLETED) |
| `mantle_enter` / `mantle_exit` | a `SECRET_BOUNDARY` | redacted enter/exit (secret stripped) |

**Critical hook invariants:**
- **Non-recursive display** (HF-B35): a `mantle_display` hook must not re-enter the
  render path it instruments.
- **Fail-open** (HF-B32): a hook fault degrades + logs; it never propagates into the host.
- **Dual-flush** (HF-B33): persist via explicit checkpoint and `atexit`.
- **Import compatibility** (HF-B34): the runtime imports package-relative with a
  sibling fallback.
- **Separate boot verifier** (HF-B36): a small fail-open verifier independent of the
  host's own startup.

---

## §B.4 Synthesize the BODY from a host (Phase 2)

Synthesize the **Body** (not cube layers) from the host's own identity — do not invent one.
Identity lives in the Body store (`examples/vcw/body.py`); the cube is pure experiential memory.

- **Primer** (read-only): the host's name, purpose, entry point, the §0 declaration, and the
  Commandments. Becomes immutable the moment it is committed.
- **Immunization** (read/write): invariants discovered during inventory (e.g. "never block the
  host thread," "redact at the secret boundary"), seeded with the Commandments.
- **Special Instructions** (read/write; Body-applies): operator-supplied directives, if any.
- The Body also records the **lineage index** (this host is generation 0). Inheritance is written
  only on a later rebirth.

The cube genome (band layout) is authored separately in Phase 3 from the Phase 0 proposed
genome — bands with a declared `span` and `purpose`, allocated on demand.

---

## §B.5 Surface parity over an existing UI (Phase 15)

This is where assimilation most often falls short — do it thoroughly:

- Walk the host's actual UI/CLI/API and build the **Human Surface Map**: every control
  a human can operate gets an id + descriptor in a band.
- For each, build a **ControlBridge** path that operates it from the Body, and record
  an **Action Execution Proof** (`attempted/ok/method/ref/reason`).
- Bind graphical rendering to the **App-Face Bridge** (declarative), not raw host
  mutation (HF-B27).
- A human-visible control with no ControlBridge path or no proof is **HF-B44**.

---

## §B.6 Layered validation (run after instrumentation)

Validate in increasing scope; stop and fix at the first failing layer:

1. **Syntax** — every instrumented file still parses.
2. **Import smoke** — every module imports (module *and* script entry).
3. **Hook invocation** — each hook fires on its bound symbol and writes the expected
   cube entry.
4. **Surface parity** — every mapped control has a working ControlBridge path + proof.
5. **Host smoke** — the host runs its original happy path **unchanged**, now with a
   live cube alongside.

---

## §B.7 Artifacts the Stage 1 audit consumes

Produce these so `Mantle_Part1_Body_Audit.md` can certify the assimilated Body:

- the **App Inventory & Organ Map** (Phase 0, signed READ-ONLY before any edit);
- the **symbol classification table** (Phase 1);
- the **rewrite ledger** (every `# MANTLE_HOOK_INSERTED`, reversible);
- the **gap report** (DEPRECATED / unclassifiable / un-instrumentable symbols + why);
- the **Human Surface Map** + ControlBridge proofs;
- the **layered validation** results.

---

## §B.8 Convergence

When the pipeline completes and layered validation passes, you have a **certified
Zombie Body grown around the host** — the host runs unchanged, but it now has a
heartbeat, memory, senses, immune defenses, a mapped surface, and dormant brain bands.
Administer `Mantle_Part1_Body_Audit.md`. With zero open hard-fails, proceed to
`Mantle_Part2_Mind.md` exactly as the from-scratch path does.

---

## §B.9 Assimilation hard-fails (Path B specifics)

In addition to the shared HF-Bxx list (see the Stage 1 audit):

| Code | Condition |
|------|-----------|
| HF-B42 | A host file was modified before the Phase 0 inventory gate was produced & signed |
| HF-B32 | A hook can crash the host (not fail-open) |
| HF-B33 | No dual-flush (single point of persistence) |
| HF-B34 | Import fails as module or as script |
| HF-B35 | A display hook re-enters its own render path |
| HF-B36 | Boot verifier is entangled with the host's startup / can crash it |
| HF-B40 | A host behavior was changed, not merely instrumented (non-additive edit) |
| HF-B41 | An inserted hook is missing its `# MANTLE_HOOK_INSERTED` marker / ledger entry |
| HF-B44 | A human-visible control has no ControlBridge path or no proof |

---

## Appendix A — App Inventory & Organ Map (copy-and-fill template)

*Path B, Phase 0 artifact (READ-ONLY). Copy this appendix out to a file next to the host (e.g.
`APP_INVENTORY.md`), fill it in completely **before modifying any host code**, and sign the
READ-ONLY line at the end. Producing and signing it is the gate that authorizes instrumentation
(§B.0a); touching host code first is **HF-B42**.*

### A.0 How to use
- Copy this appendix to a file next to the host you are assimilating; rename it `APP_INVENTORY.md`.
- Replace every `‹…›` placeholder. Leave a row blank only if you have confirmed it does not apply.
- Do not delete sections — if a surface is absent, write "none" and why.
- When complete, sign the **READ-ONLY sign-off** at the bottom. Only then proceed to Phase 1+.

### A.1 Host identity (→ the BODY Primer)
- **Name:** ‹app name›
- **Purpose (one line):** ‹what it does›
- **Language(s) / runtime:** ‹e.g. TypeScript / Node 20; Python 3.11›
- **Repo / root path:** ‹path›
- **Entry point(s):** ‹CLI / server main / index›
- **Boot path (start → ready):** ‹trace: which file/function brings the app up›
- **Build / run command:** ‹e.g. `npm run start`›

### A.2 §0 Declaration (carry into the Body Primer)
```
TARGET_LANGUAGE      : ‹…›
TARGET_RUNTIME       : ‹…›
TARGET_STORAGE       : ‹where the .vcw cube / organism dir will live›
BODY_MODE            : standard
VCW_FORMAT           : vcw-cube-png-v2
KEYFILE_PATH         : ‹Phase 2 only›
DEFAULT_MODEL        : ‹Phase 2 only›
INTENTIONALLY_OMITTED: ‹organs/surfaces deliberately not instrumented + why›
SYNTAX_CONSTRAINTS   : ‹host-imposed limits›
```

### A.3 Architectural surface → organ map
*Map every surface the host actually has. Add rows as needed; mark absent ones "none".*

| Host surface | Present? | Location (file/dir) | Target organ | Notes / addressing |
|--------------|----------|---------------------|--------------|--------------------|
| UI / editor / frontend | | | Senses (Surface Map) + Limbs (ControlBridge / App-Face Bridge) | |
| execution / run engine | | | Heart (pulse) + Limbs (effectors) | |
| credential / secret store | | | Immune (`secret_boundary`) | |
| webhook / inbound routes | | | Senses (intake) | |
| trigger / scheduler / cron | | | Senses + Heart (timed reflex) | |
| AI / LLM / LangChain nodes | | | Brain affordance (Phase-2 dormant) | |
| database / persistence | | | Memory (+ metabolism: flush/compaction/reclaim) | |
| CLI / server boot path | | | Heart (boot) + boot verifier | |
| worker / queue / job mode | | | Limbs (async delegation) | |
| frontend / backend boundary | | | Senses (in) + Limbs (out) | |
| config / environment | | | Body Special Instructions + Immune | |
| ‹other host-specific surface› | | | ‹organ› | |

### A.4 Symbol-role summary (preview of Phase 1)
*Approximate counts so the scope is visible before instrumentation.*

| Role | Organ | Count (est.) | Representative symbols |
|------|-------|--------------|------------------------|
| REFLEX | Senses | | |
| ARM_ACTION | Limbs | | |
| DISPLAY_RENDER | Limbs | | |
| STATE_TRANSITION | Memory | | |
| PERSISTENCE_WRITE | Memory | | |
| SENSOR_EVENT | Senses | | |
| MIND_AFFORDANCE | Brain | | |
| SECRET_BOUNDARY | Immune | | |
| INTERNAL_UTILITY | — | | |
| DEPRECATED | — | | |

### A.5 Secret boundaries (→ Immune)
| Boundary | Location | Secret kind | Redaction note |
|----------|----------|-------------|----------------|
| ‹…› | ‹…› | ‹api key / token / password› | mark `secret_boundary=True` |

### A.6 Persistence stores → memory bands
| Host store | What it holds | Target band | Driver / encoding |
|------------|---------------|-------------|-------------------|
| ‹db table / file / kv› | ‹…› | ‹facts / events / discoveries / app band› | ‹log-json / keyvalue / spatial› |

### A.7 Proposed cube genome (band layout)
*Author the band layout to fit THIS host's data-flow. Bands declare a span (reserved layers) and
a purpose. High-churn surfaces get more span + faster reclaim; durable knowledge gets room.*

| Band | Head | Span | Encoding | Purpose | Notes |
|------|------|------|----------|---------|-------|
| identity | 100 | | log-json | experiential self-state | |
| facts | 150 | | log-json | durable truths | |
| events | 200 | | log-json | event history | size to host event rate |
| discoveries | 250 | | log-json | learned/derived | |
| senses | 300 | | log-json | sensor intake | size to inbound traffic |
| immune | 400 | | log-json | audit/defense | |
| brain | 450 | | log-json | dispatch log | |
| thoughts | 500 | | log-json (private) | private reflection | veiled |
| ‹app band› | 550+ | | ‹driver› | ‹host-specific› | |

### A.8 Human Surface Map (preview)
| Control / affordance | Location | ControlBridge feasible? | Proof plan |
|----------------------|----------|-------------------------|------------|
| ‹button / route / command› | ‹…› | yes/no | `attempted/ok/method/ref/reason` |

### A.9 Gap report
- **Deprecated / dead code:** ‹…›
- **Unclassifiable symbols:** ‹…›
- **Un-instrumentable surfaces (and why):** ‹…›
- **Risks / blockers:** ‹…›

### A.10 Reuse / efficiency notes
- Surfaces that can share a band or reflex (avoid one-off layers): ‹…›
- Expected high-churn bands (need reclaim/compaction): ‹…›

### A.11 READ-ONLY sign-off (the Phase 0 gate)
```
APP INVENTORY COMPLETE — NO HOST CODE MODIFIED
  Host                 : ____________________________
  Inventory author     : ____________________________
  Surfaces mapped      : ____ / ____   (all present surfaces have an organ)
  Proposed genome      : [ ] drafted
  Secret boundaries    : [ ] all identified
  Files modified so far: 0   (MUST be 0)
  Approved to instrument (Phase 1+): [ ]  by ____________  date __________

  >>> Hook insertion (Phase 5+) is authorized ONLY after this line is signed. <<<
```
