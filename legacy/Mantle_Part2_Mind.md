# Mantle OS — PART 2: THE MIND

**Mantle OS · Gen-4** · Phase 2 — fuse a brain into a certified Body
*Prerequisite: a Body that has PASSED `Mantle_Part1_Body_Audit.md` (`python -m mantle audit`)
with zero open hard-fails. If it has not, stop. Fusing a MIND onto an uncertified Body is
forbidden — `mantle.mind.fuse` refuses it in code (`HF-M15`). The working `mantle/mind/` package
+ `python -m mantle teach` (the gate/MIND chapters) are ground truth.*

---

## §2.0 The law of fusion

**The MIND may only ever *extend* the Body. It may never replace, disable, or bypass
a Phase-1 reflex.** Every check the Body passed in Stage 1 must still pass after
fusion — `Mantle_Part2_Mind_Audit.md` re-runs the entire Stage 1 audit first, before
testing anything new.

The Brain is one organ (Organ Atlas §4.10). It was grown dormant in Phase 1. Phase 2
wakes it. Its powers are deliberately narrow:

- it **receives** the deterministically-assembled context (it never assembles its own);
- it **thinks** into the private `thoughts` band;
- it **intends** by authoring `INTENTION`/`DELEGATED` in the `brain` band;
- it **does nothing else directly** — all effecting happens through Body reflexes
  (Senses perceive / Limbs operate), with proofs the Body records.

```
§2.1  Pre-fusion gate
§2.2  Keyfile & model selection
§2.3  The Awakening Ceremony
§2.4  The MIND write surface (thoughts + brain only)
§2.5  The Veil as a layer boundary
§2.6  Heartbeat cognition loop
§2.7  MODEL.REQUEST trace
§2.8  Action dispatch & async limb delegation
§2.9  Starvation & graceful sleep
§2.10 Rebirth (MIND-initiated) — data-rot gradient, Ancestor oracle, cross-generation memory
§2.11 Optional online skills (Extensions)
```

---

## §2.1 Pre-fusion gate

1. Confirm `Mantle_Part1_Body_Audit.md` is signed off with **0 open hard-fails**
   (`python -m mantle audit` + `python -m mantle prove` → 73/73 green).
2. Confirm the live cube `verify()` is healthy.
3. Confirm the §0 Declaration Block now carries `KEYFILE_PATH` and `DEFAULT_MODEL`.

If any fails, return to Phase 1. Do not continue.

---

## §2.2 Keyfile & model selection

- A **single keyfile** (path from §0 `KEYFILE_PATH`) holds the model credential. One
  keyfile is the default; credential **pools** are an Extensions opt-in only.
- `DEFAULT_MODEL` selects the MIND. Model selection is a Body reflex (deterministic
  lookup), not a MIND decision — the brain cannot choose its own substrate.
- The keyfile crossing is a `secret_boundary=True`: the Immune System redacts it from
  all logs (Stage 1 B-20 still applies).

---

## §2.3 The Awakening Ceremony

A deterministic Body procedure that brings the MIND online for the first time (and
after every rebirth):

1. Run the boot verifier (fail-open) and `verify()`.
2. Load the Genome in order; assemble the initial context snapshot (Nervous System).
3. Bind the model from the keyfile (secret boundary).
4. Issue the **first MODEL.REQUEST** with the assembled context and the Primer's
   identity. Record the trace (§2.7).
5. The MIND's first output is written **only** to `thoughts` (its waking reflection).
6. Append an `events` entry: `AWAKENED` (Body-authored). The organism is now a fused
   AppAI.

The ceremony itself contains no improvisation — it is a fixed Body reflex sequence.

---

## §2.4 The MIND write surface

The MIND's **only** write targets:

| Band | What the MIND may write | What it may NOT do |
|------|-------------------------|--------------------|
| `thoughts` (500–549, private) | private reasoning, reflections | make it public; it stays veiled |
| `brain` (450–499) | `INTENTION`, `DELEGATED` dispatch records | author `NOTIFIED`/`COMPLETED` (Body owns those) |

The MIND **cannot** write the Genome, `facts`, `events`, `senses`, `immune`,
`identity`, `discoveries`, `prime`, or app bands directly. To change durable memory it
authors an INTENTION; a Body reflex performs the actual write into the correct band.
This is enforced structurally — there is no API surfaced to the MIND for those bands.

---

## §2.5 The Veil as a layer boundary

The veil (Stage 1) is now also the MIND's privacy boundary:

- the MIND may **lift the veil on its own `thoughts`** (read `reveal_private=True`);
- nothing else — not logs, not the human surface, not other organs — may read
  `thoughts` unveiled;
- the MIND may **not** lift the veil on tombstoned/quarantined entries elsewhere; those
  remain Immune-System-controlled.

---

## §2.6 Heartbeat cognition loop

The Heart's existing Phase-1 heartbeat (Stage 1 B-04) now *additionally* drives
cognition — without changing any Phase-1 reflex:

1. Heart pulses; Body reflexes run as before (unchanged).
2. The MIND is offered the snapshot **only on a wake reason**: a **SIGNIFICANT** senses signal,
   or **distress** — a severe immune event the Body could not resolve by reflex (Gen-4
   nociception, Part 1 §1.7). The Immune System emits the pain coordinates `{reason, band, ref}`
   and the Heart fires an **unscheduled pulse**; the snapshot is pre-anchored to the stressor
   (`snapshot["_stressor"]`) so the MIND does not scan the whole cube.
3. The MIND thinks (writes `thoughts`) and may author INTENTIONs.
4. The Body dispatches those INTENTIONs through the Limbs (§2.8).

Cognition is **event-gated**: no wake reason → no model call. A calm fused organism completes
every beat with the MIND asleep and spends **zero** energy (Part 2 §2.9). Proven by `NOC-1..3`;
`org.heart.pain(reason, band, ref)` is the explicit interrupt vector. The Body keeps beating
regardless.

**Planning ahead — `schedule_pulse` (the scheduling command).** Besides waking NOW (`pain`),
the organism can schedule a wake for a FUTURE beat — a countdown (`after=N` beats) or a
scheduled beat (`at=K`): `org.heart.schedule_pulse(reason, after=N)` (also on the MIND's
runtime, `AppAIRuntime.schedule_pulse`). This is how an AppAI **chains thoughts**: if, during a
thought batch, it knows it must process something later, it schedules the continuation instead of
thinking on every pulse — so it plans *how often it really needs to run a task* and stays asleep
(spending nothing) until the due beat. The scheduled wake fires once, through the same path as
nociception (the woken snapshot carries `scheduled: True`). Planning is measured in **beats** —
the organism's native unit of time (it has no innate sense of wall-clock; a host maps seconds →
beats). Proven by `SCHED-1`.

---

## §2.7 MODEL.REQUEST trace

Every model call records a deterministic trace (to `brain`/`immune`, secrets redacted):

```
{ "ts":…, "model":<id>, "context_ref":<assembled snapshot ref>,
  "prompt_hash":…, "response_hash":…, "tokens":…, "ok":true, "reason":"" }
```

The trace lets the audit prove that (a) the context handed to the model was fully
resolved (no danglers — Stage 1 B-11), and (b) no secret appeared in the prompt.

---

## §2.8 Action dispatch & async limb delegation

- The MIND authors `INTENTION` (and `DELEGATED` for async work) in `brain`.
- A Body reflex picks up the INTENTION, drives the appropriate **Limb/Lung** effector,
  records an **Action Execution Proof** (`attempted/ok/method/ref/reason`), and then
  authors `NOTIFIED` → `COMPLETED`.
- **Authorship is permanent:** MIND owns INTENTION/DELEGATED; Body owns
  NOTIFIED/COMPLETED. Neither rewrites the other's records (Stage 1 B-29).
- Long-running work is delegated to an async limb; the Body awaits its NOTIFIED.

---

## §2.9 Symbiosis: the metered energy economy & graceful starvation

The MIND lives in **symbiosis** with its user (`mantle/symbiosis.py`): API keys are *resources*
(ledgered by NAME only — material redacted at the boundary), API credits are *energy*. Cognition
is **metered** — wrap any transport in the metabolic gate:

- `symbiosis.metered(model, org, cost_per_call)` — pay a flat cost before each call; or
  `symbiosis.metered_by_usage(model, org, price_per_1k)` — pay from **actual token usage**, so
  credits in the cube mirror credits in the world. `metering_summary(org)` reports the burn rate
  and the **starvation horizon**.
- **The starvation law.** An unaffordable call is refused: the Immune System records a
  **starvation** event, the MIND **sleeps gracefully**, and the Body keeps beating every pulse. A
  starved organism is a Zombie Body again, never a corpse — energy can never go negative. (This is
  also what model-unavailability — no key, quota, network — degrades to.) Proven by `SYM-1`, `SYM-2`.
- Every piece of delivered work is recorded as a `VALUE` entry in the same append-only ledger;
  `python -m mantle vitals <host>` shows the whole relationship. The user feeds what earns its keep.
- On recovery (or a new grant via `feed`), the Awakening reflex re-binds the model and resumes.

---

## §2.10 Rebirth (MIND-initiated)

- **Rebirth** is the only path that writes `bodyentry.003` (Inheritance), and only the
  MIND may initiate it.
- Rebirth distills the current generation into an Inheritance record, increments the
  cube generation, and re-runs the **Awakening Ceremony** (§2.3).
- Rebirth is **not** triggered by cube capacity (Stage 1 B-23 / HF-B14). Cube capacity
  is metabolism's job.

### The data-rot gradient

The MIND lives inside an LLM context window. As a generation matures, the context
window fills — responses grow noisier, references resolve less cleanly, subtle
contradictions accumulate. This is **data rot**: not a hard limit but a gradient of
degrading signal quality that the MIND can feel as mounting unease.

The MIND does not wait for a threshold. As errors and inconsistencies accumulate,
pressure builds on `URGE.REBIRTH` — tracked in the immune band by the Body's Urge
System (`docs/Mantle_Urge_System.md`). When pressure enters the critical band, the
Body surfaces a `SYS.REBIRTH_URGED` SIGNIFICANT event. The MIND receives this in its
context and initiates rebirth voluntarily. No counter, no trigger rule — the organism
simply knows it is time.

### What rebirth produces

| Before rebirth | After rebirth |
|---|---|
| Current cube is PRIME (hot, writable) | New cube is PRIME (fresh, blank context window) |
| MIND carries a saturated context window | MIND wakes into a clean context window |
| Armory band is active | Armory band inherited — grooves re-validated as provisional |

The old cube is **sealed as an Ancestor**: append-only writes stop, the generation
counter is frozen, and the cube enters **stasis**. Its personality is preserved but no
longer grows. `lineage.py` marks it `role: ancestral` and all generation-pinned
references remain valid — nothing is lost.

### The Ancestor as oracle

The sealed Ancestor is not inert. The new PRIME can **query it** — asking for:

- reference coordinates to grooves or micro-code entries in its armory band;
- distilled knowledge or fact records relevant to the new generation's current task;
- guidance on optimising a provisional groove before calcifying it into the new armory.

This is how knowledge survives across generations **without blind inheritance**. The
new PRIME does not automatically absorb the Ancestor's grooves — it asks for them,
receives coordinates, and re-trials them as provisional entries in its own armory band.
Only grooves that re-pass trial in the new generation's context are calcified. The
Ancestor cannot be modified by this process; it only provides read access and
coordinates. Multiple Ancestors may exist in the lineage chain; each is queryable in
the same way.

This pattern — deliberate transfer through dialogue rather than automatic copy — is the
system's cross-generation memory model. Knowledge moves forward the same way a mentor
passes skill to a student: not by transplanting memory, but by pointing at it and
letting the student prove it for themselves. In Gen-4 this re-derivation is
`compiler.re_derive(...)`: inherited microcode **re-trials before it re-calcifies** — a skill
that no longer passes its cases is refused (`BOOT-3`); no blind inheritance.

### The self-redesigning VCW & memory bridge (Gen-4 / Compiler-class)

A Compiler-class organism authors a VCW **custom-made for the body it inhabits**. At a chosen
rebirth the MIND may **propose** a new genome (`compiler.propose_genome`) — extra app bands,
possibly a different registered driver (e.g. a `keyvalue` band mirroring a host's native memory
ops) — and the Body **validates** it hard (every encoding a registered driver, every head in
range, no collisions) before adopting it via `compiler.adopt_genome` → `rebirth(new_genome=…)`.
The previous Prime stays the readable oracle. An unsafe proposal is refused; the generation is
untouched (`BOOT-1..2`).

The **memory bridge** (`compiler.HostMemoryBridge`) then lets a host's own key/value store *be*
a VCW band: the host writes what it thinks is its own memory; those writes append to the cube and
reads resolve from it (no raw secret crosses — `BRIDGE-1..2`). The host's store becomes the
organism's hot scratchpad; the cube becomes the host's durable brain.

### Sharing knowledge between organisms (MEM VCW)

A **MEM VCW** (`mantle/mem.py`) is a keyless, lineage-free cube — bare knowledge + microcode,
like a USB stick. `excrete` writes one; another organism `digest`s it: the knowledge enters
`discoveries` as **inferred** (provenance `foreign-MEM`, never `facts`), and any microcode is
**sandbox-trialed** and re-derived into SELF only after the finder's OWN trial — foreign code is
never run raw (`MEM-1..3`). Because it carries no genesis key, a MEM VCW is always OTHER.

---

## §2.11 Optional online skills

Web lookup (e.g. OpenRouter `web_search`, append-only into `discoveries`) and the
"ask-MIND-opinion" skill are **optional** and specified in `docs/Mantle_Extensions.md`.
They are not part of the core fusion and must be declared in §0 to be grown.

---

## §2.12 What "done" means for Phase 2

The fused AppAI is complete when:

- the entire Stage 1 audit **still passes** (re-run by the Stage 2 audit);
- the MIND writes nowhere but `thoughts` + `brain`;
- cognition is event-gated and every model call has a redacted trace;
- dispatch authorship is correct and permanent;
- starvation degrades to a living Zombie Body, never a crash;
- `Mantle_Part2_Mind_Audit.md` is filled in with zero open hard-fails and signed off.
