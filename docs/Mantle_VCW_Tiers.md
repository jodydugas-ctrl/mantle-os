# Mantle OS — VCW Compliance Tiers

**Mantle OS v3.0** · Non-normative concept note.
*Read this if your environment cannot create a file-backed VCW cube — or if you are
building tooling for constrained runtimes.*

---

## Why tiers exist

The VCW cube (`mantle/vcw/` engine; `examples/vcw/vcw_cube.py` standalone) requires two things:

1. A **Python runtime** — the codec is pure Python; there is no JavaScript equivalent.
2. A **writable filesystem** — the cube is a real `.vcw` file (ZIP of PNGs) on disk.

Some environments provide neither (web-only LLM canvases). Some provide Python but no
persistent filesystem (serverless functions, sandboxed containers). A framework that
only works in one environment fails the organisms built on it.

The solution is not to relax the invariants — it is to make the constraint **visible
and declared**. An organism that honestly declares it cannot run a full cube is valid.
An organism that silently fakes a cube is not.

> **Rule:** An organism that cannot fully instantiate its VCW must declare
> `VCW_BACKEND` in §0. An undeclared fake VCW is a hard fail on first heartbeat —
> the same class of violation as an undeclared credential pool (`HF-M01`). A
> declared constraint is an honest, auditable state.

---

## The Three Tiers

| Tier | Name | Runtime | Audit | §0 declaration |
|------|------|---------|-------|----------------|
| **1** | Full | Python + writable filesystem | `audit.py` passes | `VCW_BACKEND: file` *(default; may be omitted)* |
| **2** | Structural | Python, no persistent filesystem | `audit.py --mode structural` *(future)* | `VCW_BACKEND: <adapter_name>` |
| **3** | Schema-only | None — web-only environment | Human checklist at local boot | `VCW_BACKEND: schema-only` |

---

## Tier 1 — Full (the default)

The organism runs on a machine with Python and a writable disk. `Cube.genesis()` creates
the `.vcw` file. `audit.py` runs against the real file. This is the target state for
every deployed organism.

`VCW_BACKEND: file` may be omitted from §0 — it is the assumed default. If it is
omitted and no cube file exists at boot, the organism fails with a hard error on the
first heartbeat. That is the correct behavior: a missing cube is not recoverable.

---

## Tier 2 — Structural compliance (constrained backend)

The environment has Python but the filesystem is ephemeral or unavailable (a serverless
function, a managed container without a volume, a CI test harness that cannot write
files). A real cube cannot survive across invocations.

**What the organism does:**
- Substitutes a conforming backend adapter for the default `Cube` class.
- The adapter implements the same interface (see below) backed by memory, a database,
  object storage, or any other durable store.
- All structural invariants hold: band naming, entry format, provenance, append-only
  semantics, hash-linked entries, veil behavior.
- Declares `VCW_BACKEND: <adapter_name>` in §0.

**What audit checks:** A future `audit.py --mode structural` will verify the invariants
without requiring a file on disk. Until that tooling exists, Tier 2 organisms should
run the semantic checks manually and document the results in §0.

### VCWBackend contract

Any conforming adapter must implement this interface:

```python
class VCWBackend:
    def genesis(self, genome: dict) -> None:
        """Initialize the cube with the given band map. Called once."""

    def append(self, band: str, entry: dict) -> str:
        """Append an immutable entry to a band. Returns the entry hash."""

    def read_band(self, band: str, since: int = 0) -> list[dict]:
        """Return all entries in the band, optionally from a sequence number."""

    def verify(self) -> bool:
        """Run integrity checks. Returns True if the cube is intact."""

    def seal(self) -> None:
        """Finalize the cube generation — no further writes allowed."""

    def circulate(self) -> None:
        """Flush any in-flight writes to the backing store."""
```

The adapter must also:
- Enforce append-only semantics (no entry may be modified or deleted)
- Hash each entry at write time; verify hashes on read
- Respect the veil reflex (hide quarantined / retired entries on read)
- Refuse writes to sealed bands

---

## Tier 3 — Schema-only (web-only environment)

The LLM is running in a web-based canvas (Gemini Canvas, ChatGPT Canvas, a hosted
notebook) with no Python runtime and no filesystem. A running organism cannot be
produced in this environment.

**This is not a failure. It is the correct honest state for this environment.**

### What a correct Tier 3 deliverable looks like

The LLM produces a **blueprint** — a complete, correct set of files that the user
instantiates locally. The deliverable includes:

1. **§0 Declaration Block** — with `VCW_BACKEND: schema-only` and a note explaining
   that this organism requires local Python execution to run.
2. **`body.py`** — the organism's Body subclass, importing from `mantle/core/body.py`.
3. **`mind.py`** — the MIND subclass (if Phase 2 is in scope).
4. **Organ modules** — one file per organ, each a Body reflex, no LLM in Phase 1.
5. **`receptor.html`** — the human-facing surface (separate from the Body).
6. **`boot.py`** — the entry point the user runs locally.
7. **A human checklist** replacing `audit.py` — the steps the user runs after booting
   to verify the Zombie Body is alive:

```
Tier 3 Local Boot Checklist:
[ ] python boot.py  ← starts the Body; look for "Zombie Body alive" in output
[ ] cd examples/vcw && python audit.py  ← Stage 1 Gate; must pass before Phase 2
[ ] Open receptor.html in a browser; confirm it connects to the Body
[ ] cd examples/vcw && python audit_mind.py  ← Stage 2 Gate (after MIND is fused)
```

### What the LLM must say explicitly

When producing a Tier 3 deliverable, state this in the conversation:

> "This organism requires local Python execution. I have produced the correct files
> but cannot run them here. To deploy: copy these files, install Python 3.x, run
> `python boot.py`, then follow the checklist above to certify the Zombie Body."

### What is NOT a valid Tier 3 deliverable

- A JavaScript-only VCW (Trap 3 in `docs/Mantle_LLM_Pitfalls.md`)
- A single merged HTML file that simulates the Body in the browser (Trap 1)
- Any output that does not pass `audit.py` when run on a real filesystem
- `VCW_BACKEND` missing from §0 when no real cube exists

---

## Declaring VCW_BACKEND in §0

Add `VCW_BACKEND` to the §0 Declaration Block alongside `BODY_MODE`:

```
§0 IMPLEMENTATION_DECLARATION
  ORGANISM:        <name>
  VERSION:         <semver>
  BODY_MODE:       standard
  VCW_BACKEND:     file           ← Tier 1 (default; omit or state explicitly)
  VCW_BACKEND:     schema-only    ← Tier 3; web-only env; local boot required
  VCW_BACKEND:     memory         ← Tier 2 example; in-memory adapter
  VCW_BACKEND:     postgres       ← Tier 2 example; database-backed adapter
```

Only one `VCW_BACKEND` value applies per organism. Choose the tier that matches the
actual deployment environment — not the one that makes the audit easiest to pass.

---

## Relationship to the Immune System

The immune system enforces tier honesty at runtime:

- **Boot:** if `VCW_BACKEND` is missing and no `.vcw` file exists → `immune` event
  `HF-VCW-01: undeclared backend; cube not found`. Hard fail.
- **Heartbeat:** if `VCW_BACKEND: file` but `circulate()` cannot write to disk →
  `immune` event `HF-VCW-02: backend write failure`. Hard fail.
- **Audit:** if `VCW_BACKEND: schema-only` but a running cube is detected →
  `immune` event `HF-VCW-03: backend declaration mismatch`. Flag for review.

These immune events follow the same pattern as all other hard fails: the organism
halts rather than continuing in an undeclared state.

---

## Tier progression

Organisms can move up tiers as their deployment environment matures:

- A Tier 3 schema-only blueprint becomes Tier 1 the moment the user boots it locally.
- A Tier 2 structural organism becomes Tier 1 if a filesystem is attached and the
  backend is swapped to `file`.
- Tier progression is tracked in the cube's generation record (the new generation
  declares the new `VCW_BACKEND`).

Moving *down* tiers — from `file` to `schema-only` mid-life — is not valid. An
organism that has a real cube does not lose it by declaration.
