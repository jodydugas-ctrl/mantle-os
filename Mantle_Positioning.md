# Mantle OS — Positioning & On-ramp

**Non-normative.** This file is *not* part of the doctrine and you do not need it to build. It
exists for one reason: Mantle's vocabulary (organisms, bodies, minds, cubes) is deliberately
opinionated, and that can be a wall on first contact. This page is the plain-language door. If you
want the real thing, read [`Mantle_Doctrine.md`](Mantle_Doctrine.md) → [`Mantle_PRIMER.md`](Mantle_PRIMER.md)
→ [`examples/vcw/GUIDE.md`](examples/vcw/GUIDE.md).

---

## In plain terms

Strip the biology and Mantle is one idea:

> **Build an app that fully works with *no* AI in it. Prove it works with an automated audit.
> *Then* bolt on an LLM that can only add notes and propose actions — it can never change or break
> what already works.**

That's the whole stance. The rest is rigor about how you make "can never break it" *true*, not
hopeful:

| Plain word | Mantle term | What it actually is |
|---|---|---|
| The app's deterministic core | **Body** (its **organs**) | Ordinary, testable code that runs with no model attached |
| A hard-coded, no-AI behavior | **reflex** | A plain function the Body runs itself |
| The database / memory | **VCW cube** | An append-only log where each record is hashed; you add or retire records, never rewrite them. It's a normal ZIP of PNG files, so you can literally open the memory in an image viewer |
| The "who am I" config | **Genome / Primer** | Read-only identity, set once, held outside the cube |
| The LLM | **MIND** | A plain `prompt → text` function, added last, allowed to write to only two scratch areas |
| The "is it correct?" test suite | **the audit / Stage-1 & Stage-2 gates** | Real scripts that exit non-zero on failure (`python -m vcw audit`) |

If you've ever said "the AI is doing too much; I wish the important parts were just deterministic
code I could test" — that instinct *is* Mantle.

---

## How Mantle relates to other approaches

Mantle is not competing to be a better LangChain. It's solving an adjacent, narrower problem:
**the boundary between deterministic code and an autonomous model.** It's a *stance*, not a feature
set — so the honest comparison is about where each puts the LLM, not which has more integrations.

| Space | Familiar examples | Different stance in Mantle (not "better," different) |
|---|---|---|
| **Agent frameworks** | LangChain, LlamaIndex, AutoGen, CrewAI | Those typically put the LLM at the center from day one and wire tools to it. Mantle requires Phase 1 to be *certifiably correct with the LLM absent*, and only then attaches it. |
| **Memory systems** | Mem0, Zep, MemGPT | Those are retrieval layers added to an existing LLM loop. In Mantle, the memory substrate *is* the organism's source of truth, append-only and auditable; the LLM is the late addition. |
| **Output constraints** | Constitutional AI, Guardrails | Those constrain what the model *says*. Mantle constrains what the model can *do* — its write access is bounded by construction (and, more deeply, the model has no capability to act at all; it only returns text). |
| **Agent runtimes / orchestration** | OpenAgents, Agency Swarm | Those focus on tool-calling and coordination. Mantle focuses on one organism's durable identity, memory, and provable containment. |

The one-line thesis behind all of that:

> **Design the containment boundary *before* you invite the autonomous component in.**

That idea — common in safety-critical and distributed-systems design, rarer in today's AI tooling —
is what makes Mantle distinct rather than another agent wrapper.

---

## Honest limitations (so expectations are calibrated)

Mantle's discipline includes admitting what it is *not*:

- **It is a reference implementation, not a production runtime.** The `examples/vcw/` package is meant to be
  read and run as a clear, complete example — not deployed as-is at scale.
- **The hard-sandbox (`wasm`) runner is a prepared seam, not built.** This is a deliberate trade to
  keep the project pure-standard-library (zero dependencies). The Python runner is hardened with a
  static AST gate that refuses escape vectors at skill-cultivation time, but a true hard sandbox
  is left as a documented extension point.
- **Scope is a *single* organism.** There is no built-in task queue or multi-agent coordination.
  Multi-cube operations (merge, clone, distill) live in the optional Foundry/lineage extensions,
  not core.
- **The worldview is opinionated on purpose.** You accept "body before brain" and the organism
  vocabulary, or the framework isn't for you. That focus is the point; it also means Mantle suits a
  dedicated niche more than broad, drop-in adoption.

None of these are accidents. They are the cost of the thing Mantle optimizes for: a small,
provable, dependency-free boundary between deterministic code and an LLM.
