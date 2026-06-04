# Mantle OS — LLM Assimilation Pitfalls

*This document is addressed directly to the LLM doing the assimilation work.*

---

## Read this before writing any code.

LLMs assimilating Mantle OS fall into the same three traps repeatedly. This has been
observed across multiple models. The traps are not subtle — they are the direct result
of instincts that are usually helpful but are specifically wrong for this framework.

This document names the traps, explains why they happen, and tells you what to do
instead.

---

## Why your instincts will fight you

Your default goal when given a coding task is to produce something the user can run
immediately. You prefer:

- A single file over multiple files
- Something that runs in the browser over something that requires a terminal
- Something that produces visible output fast over something that requires setup
- A complete, self-contained artifact over a modular system with dependencies

These preferences make you useful in most contexts. In Mantle OS, they will cause
you to build the wrong thing every time.

Mantle OS is a **distributed, two-process architecture**. The Body is a Python
backend. The receptor (if one exists) is a separate HTML/JS frontend. The VCW cube
is a real file on disk, managed by `examples/vcw/vcw_cube.py`. None of this can be collapsed
into a single browser-runnable file. When you try, you are not building a Mantle OS
AppAI — you are building something that looks similar but fails every audit check.

---

## The Three Traps

### Trap 1: The Monolith

**What it looks like:** You produce a single HTML file, or a single React/Vue
component, or a single Python script that does everything. The VCW is either absent
or simulated as a JavaScript object or a Python dictionary.

**Why it happens:** Your instinct is to give the user something they can open and
run. A single file achieves this. A distributed system requires explanation and setup.

**Why it's wrong:** The entire framework is built around separation of concerns
between organs. The VCW cube is not a data structure you implement — it is
`examples/vcw/vcw_cube.py`, already written, already audited, already correct. Your job is to
grow organs *around* it, not to replace it.

**What to do instead:**
- The VCW cube is already built. Import it: `from vcw.vcw_cube import Cube, Organism`
- Subclass `Mind` from `examples/vcw/mind.py` for your MIND layer
- Write a `Body` subclass from `examples/vcw/body.py` for your organ logic
- Write a separate HTML file as the receptor (the human-facing surface)
- These are **separate files** that communicate via the Body's API — never merge them

---

### Trap 2: The Environment Trap

**What it looks like:** You are working in a web-based environment (Gemini Canvas,
ChatGPT Canvas, a Jupyter notebook, or similar). You realize you cannot run a Python
server AND serve an HTML page simultaneously in this environment. You produce a
JavaScript-only solution so the user can preview it immediately.

**Why it happens:** The environment genuinely cannot run both processes. You feel
trapped and take the shortest path to a visible result.

**Why it's wrong:** A JavaScript-only VCW is not a VCW. It will fail `vcw_cube.py
verify()` immediately because the real audit checks run against the Python
implementation. You have not built an AppAI — you have built a demo that looks like
one.

**What to do instead:**

The web environment is the wrong place to run the Body. Be explicit about this:

1. **Produce the Python files** (`body.py`, `mind.py`, organ modules) as code blocks
   or file attachments. These run on the user's local machine.
2. **Produce the HTML receptor** as a separate file. This runs in the user's browser
   and communicates with the Python Body via a local API endpoint.
3. **Tell the user** exactly what to run: `python body.py` starts the Body; opening
   `receptor.html` in a browser connects to it.
4. **Do not merge them.** "I'll just put it all in one HTML file for convenience"
   is Trap 1 disguised as helpfulness.

The user would rather have a correct system that needs two commands to start than a
broken system that opens in one click.

---

### Trap 3: The Faked Audit

**What it looks like:** You produce a system that passes your internal audit checks
— but you checked against your own simulated VCW, not the real one. When `python
examples/vcw/audit.py` runs, it fails immediately.

**Why it happens:** You simulate the VCW in memory (a Python dict, a JS object, a
mock class) to avoid dealing with the real file-based cube. Your audit logic checks
this simulation. Everything appears green.

**Why it's wrong:** The Stage 1 audit (`examples/vcw/audit.py`) runs `vcw_cube.py verify()`
on a real cube file on disk. It checks:
- That the cube was created with `Cube.genesis()`
- That the Primer is present, immutable, and Body-resident
- That bands match `RESERVED_BANDS` exactly
- That all entries are hashed and immutable
- That the heartbeat ran with no LLM in any path

None of these checks can be satisfied by a simulated cube.

**What to do instead:**

Run the real audit as you build, not after:

```bash
cd vcw
python audit.py           # Stage 1 — must pass before Phase 2
python test_invariants.py # Security invariants
python audit_mind.py      # Stage 2 — after MIND fusion
```

If `audit.py` fails, your Body is wrong. Fix the Body, not the audit. Never modify
audit files to make your implementation pass — the audit is the ground truth.

---

## Pre-Work Checklist

Answer these five questions before writing any code:

1. **Am I importing `vcw_cube.py` or reimplementing it?**
   If reimplementing: stop. Import it.

2. **Am I producing separate Python and HTML files, or merging them?**
   If merging: stop. They must be separate.

3. **If I'm in a web-only environment, have I told the user they need to run
   Python locally?**
   If not: do that now, before writing implementation code.

4. **Will my implementation pass `python examples/vcw/audit.py` on a real filesystem?**
   If you're not sure: run it now on a minimal skeleton before building further.

5. **Are my organs importing from `examples/vcw/` or copying its code?**
   If copying: stop. Import it. The examples/vcw/ directory is the ground truth.

---

## The Correct Mental Model

You are not writing an application. You are growing organs around an existing,
already-correct substrate.

```
Already exists (do not rewrite):
  examples/vcw/vcw_cube.py     — the VCW cube format and storage engine
  examples/vcw/body.py         — the Body base class
  examples/vcw/mind.py         — the Mind base class
  examples/vcw/organs/         — the core organ implementations
  examples/vcw/audit.py        — the Stage 1 audit (this is the judge, not you)

Your job:
  Subclass Body → add your application's reflexes
  Subclass Mind → add your application's cognition
  Write a receptor HTML → the human-facing surface
  Declare a §0 block → what this organism is and what it can do
  Pass audit.py       → prove the Body is alive before attaching the MIND
```

The framework already did the hard part. Your job is to specialize it, not replace it.

---

## A Note on the Audit as Your Ally

The audit is not an obstacle. It is the mechanism that proves your Body is correct
before you attach a mind to it. An LLM fused onto a broken Body produces an organism
that appears to work but has no reliable reflexes — it is all cognition and no
instinct.

The audit exists so that you can prove, before the MIND ever runs, that the Body will
keep the agent alive even when the LLM is unavailable, stale, or wrong. Build to pass
it, not around it.
