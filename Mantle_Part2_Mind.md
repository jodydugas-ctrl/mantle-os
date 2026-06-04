# Mantle OS — PART 2: THE MIND

**Mantle OS v2.3** · Phase 2 — fuse a brain into a certified Body
*Prerequisite: a Body that has PASSED `Mantle_Part1_Body_Audit.md` with zero open
hard-fails. If it has not, stop. Fusing a MIND onto an uncertified Body is forbidden.*

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

1. Confirm `Mantle_Part1_Body_Audit.md` is signed off with **0 open hard-fails**.
2. Confirm `vcw_cube.py verify` is healthy on the live cube.
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
2. If there are **SIGNIFICANT** senses (Stage 1 B-16) or pending INTENTIONs, the Body
   assembles a fresh context snapshot and issues a MODEL.REQUEST.
3. The MIND thinks (writes `thoughts`) and may author INTENTIONs.
4. The Body dispatches those INTENTIONs through the Limbs (§2.8).

Cognition is **event-gated**: no SIGNIFICANT input and no pending intention → no
model call. The Body keeps beating regardless.

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

## §2.9 Starvation & graceful sleep

- If the model is unavailable (no key, quota, network), the Immune System raises a
  **starvation** event and the MIND **sleeps gracefully** — the Body keeps running all
  Phase-1 reflexes. A starved organism is a Zombie Body again, not a dead one.
- On recovery, the Awakening reflex re-binds the model and resumes cognition.

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
letting the student prove it for themselves.

---

## §2.11 Optional online skills

Web lookup (e.g. OpenRouter `web_search`, append-only into `discoveries`) and the
"ask-MIND-opinion" skill are **optional** and specified in `Mantle_Extensions.md`.
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
