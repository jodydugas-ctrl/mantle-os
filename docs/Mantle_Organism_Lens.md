# Mantle OS — THE ORGANISM LENS

**Mantle OS · Gen-4** · How to read any application as a living creature
*Read [`Mantle_Doctrine.md`](Mantle_Doctrine.md) (the why), then this (the how-to-see), then
[`Mantle_Organ_Atlas.md`](Mantle_Organ_Atlas.md) (the formal taxonomy). This is the thinking
tool — a short lens you apply to every app, whether you are growing one from scratch or
installing a VCW nervous system into existing code.*

---

## 1. The shift: stop reading code, start reading anatomy

A coding agent's instinct is to see an app as an IT system — services, controllers, schemas,
endpoints. **Drop that lens.** Mantle asks you to see the same app as an **organism**: a body
with organs, each doing one living job, wired together by a nervous system, kept alive by a
heartbeat. The IT facts don't change; your *frame* does — and the frame is what lets you infer
behavior you were never told.

> An organism's behavior is **inferable from its organs.** If you can name what each part *is*
> biologically, you can predict what the whole creature *does* — and where its nervous system
> must attach.

This inference is the entire value of the lens. A request handler you've never seen is a
**sense**; you already know senses must be classified and remembered. A cron job is a **timed
reflex of the heart**; you already know reflexes run without a brain. You reason from biology to
behavior before you read a single line of logic.

---

## 2. The model organism: the octopus

Mantle is modelled on the **octopus** — the one animal whose anatomy *is* this architecture. Most
creatures are centralized: one big brain runs the body. The octopus is not — and that is exactly
the instinct this lens has to install.

- **Its arms think.** Roughly two-thirds of an octopus's neurons live in its arms (a central brain
  plus semi-autonomous arm ganglia). Each arm senses, decides, and acts **on its own** — no central
  command needed. That is the **Zombie Body**: organs that work with no brain. *What your organ
  does, you have done.*
- **The brain delegates intent; the arm executes.** The central brain hands an arm a goal, not a
  step-by-step program. That is the **dispatch lifecycle** — the MIND authors INTENTION/DELEGATED;
  the limb owns NOTIFIED/COMPLETED.
- **Its skin shows its state.** An octopus renders mood and camouflage as **colour and pattern
  across its skin** — a spatial, visible record of its condition. That is the **VCW cube**: memory
  stored as colours at coordinates, in layers you can open as images.
- **The name.** The **mantle** is the octopus's body — the structure that houses its organs.
  "Mantle OS" *is* that body.

Keep the lens honest and general, though: the formal organs below — heart, lungs, liver, immune —
are a broadly legible set, **not** octopus-specific anatomy. The octopus is the *exemplar of the
wiring*, not a renaming of the parts.

---

## 3. The dissection — find these organs in any app

Walk any codebase (or hardware) and locate each organ. Most apps have all of them, named
differently. (Formal manifests, bands, and reflexes live in the Organ Atlas; this is the
field-identification key.)

| Look for… | It is the… | Because it… |
|-----------|-----------|-------------|
| the main loop / scheduler / clock / `while running` | **Heart** | sets the pulse that drives everything else |
| inputs: routes, webhooks, event handlers, sensors, key/mouse | **Senses** | perceive the outside world (classify: reflex / routine / significant) |
| actions with effects: API calls, writes to other systems, motors | **Limbs** | act on the world; every action needs a proof |
| the I/O surface: UI, CLI, rendering, the human-facing boundary | **Senses** (perceive) + **Limbs** (operate) | afferent: perceive the surface (Human Surface Map); efferent: render/operate it (ControlBridge, App-Face Bridge) |
| state, models, DB rows, caches, files | **Memory** | what the creature knows and can recall |
| validation, error handling, auth checks, retries | **Immune system** | defends integrity; quarantines and repairs |
| identity, config, name, version, env, secrets | **Genome** (held in the **Body**) | defines *who this creature is* (the Primer) |
| any LLM / model / judgment call / "decide" step | **Brain** | reasons — attached only in Phase 2 |
| cleanup, GC, compaction, log rotation, TTLs | **Memory** (metabolism) | keeps the working set lean; reclaims waste (flush/compaction/reclaim) |

If you cannot find an organ, that is information too: an app with no immune system is fragile;
an app with no liver will bloat; an app whose only "decisions" are hard-coded has no brain yet —
which is exactly the Zombie Body you are trying to certify.

---

## 4. The two questions the lens makes you ask

For every organ you identify, ask:

1. **Does it need a brain?** Almost never. Senses classify, limbs act, the heart beats, the
   immune system defends — all *without* an LLM. That is why a Mantle Body runs and is certified
   **before** any mind is attached. If you think an organ "needs the AI to work," you have
   mislabeled plumbing as cognition. (Doctrine: *what your organ does, you have done* — the Body
   genuinely acts.)
2. **Where does it write its memory?** Every organ reads and appends to the **VCW cube** — the
   nervous-memory substrate. Senses → `senses`; immune findings → `immune`; actions → the
   dispatch log in `brain`; knowledge → `facts`/`discoveries`. *If it isn't in the VCW, it didn't
   happen.*

These two questions turn anatomy into wiring: you now know what runs brainless (the whole Body)
and where each organ's nerve attaches to the cube.

---

## 5. Using the lens for the two paths

- **Building from scratch (Path A — `../Mantle_Part1_Body.md`):** design the creature organ by
  organ. Give it a heart first, then senses, memory, immune system, limbs, lungs — a complete
  body that lives with no brain. Only then fuse a mind (Phase 2).
- **Assimilating existing code (Path B — [`docs/grimoire/The Grimoire AppAI Chapter 4.3.md`](grimoire/The%20Grimoire%20AppAI%20Chapter%204.3.md), NECROMANCY operational detail):** *dissect first.* The Phase 0
  App Inventory is exactly this lens applied as a read-only artifact — map every host surface to
  its organ before you touch a line. You are not rewriting the app; you are finding its organs
  and threading a nervous system through them.

Either way, the work is the same act of seeing: **name the organs, and the creature's behavior —
and its wiring — reveal themselves.**

---

## 6. The lens in one breath

> The app is already an animal. Your job is to recognize it: find the heart that beats, the
> senses that perceive, the limbs that act, the memory that persists, the defenses that protect —
> wire them to the VCW so the creature *remembers it is alive* — and only then give it a mind.
