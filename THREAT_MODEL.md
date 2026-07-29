# Mantle OS — Security Contract and Threat Model

This is the repository's canonical security-claim table. It is subordinate to the
constitutional Grimoire and to the current implementation under `src/mantle/`; it does
not create a second doctrine. A conflict with either is a defect to resolve, never a
license to choose the stronger-sounding claim.

## 1. Protected assets

Mantle protects the deterministic Body, durable memory history, Body identity and
lineage, MIND-fusion authority, cultivated-skill execution, and the evidence emitted by
its certification gates.

## 2. Principals

- **Operator:** trusted authority holder. A hostile operator is out of scope.
- **Body code:** trusted in-process Python implementing the organs and substrate.
- **MIND:** the declared `prompt -> text` model callable. It receives text and returns
  text; it does not receive Python objects, tools, sockets, or file handles.
- **OTHER:** data or artifacts not proved SELF.
- **Cultivated skill:** Python proposed as data, trialed, and calcified by the Body.
- **Acquisition source:** a remote repository or other origin from which inert material
  is imported.

The Python `Mind` class is Body-side wrapper code, not the MIND principal. Calling
`mind.org` requires in-process Python execution and therefore demonstrates a public API
exposure, not a capability of the declared `prompt -> text` model.

## 3. Trust boundary

In-process Body/operator Python is trusted. Mantle does not claim to sandbox a malicious
Body, a hostile operator, the Python interpreter, or the standard library. Arbitrary
tool-calling, function-calling, or code-executing MINDs are out of scope unless placed
behind a real process or runtime isolation boundary.

Python naming conventions, private slots, AST filters, and restricted builtins are useful
hardening but are not a hard sandbox.

## 4. Verdicts

| Verdict | Meaning |
| --- | --- |
| `enforced` | The implementation prevents the named in-scope principal and a live proof demonstrates the refusal. |
| `detected` | The implementation may not prevent the event, but detects it and produces evidence. |
| `conventional` | Correctness depends on callers or deployment practice; prevention or detection is incomplete. |
| `out of scope` | The threat is explicitly outside this contract, with the reason stated. |

Code references prove that a check exists, not that prose and check are semantically
equivalent. Reviewers remain responsible for that mapping.

## 5. Guarantee table

<!-- MANTLE-GUARANTEES:START -->
| ID | Property | Principal / threat | Verdict | Live proof | Notes |
| --- | --- | --- | --- | --- | --- |
| `TM-HISTORY-REWRITE` | Existing memory rewritten out of band | corruption or trusted in-process code | `detected` | `HF-B29`, `HF-B46b` | Entry hashes and ancestor fingerprints reveal alteration. Detection is not prevention. |
| `TM-INSERTION-PROVENANCE` | A newly inserted valid row proves its authorized writer | trusted in-process code | `out of scope` | — | Hashes cover content but do not attest which organ called append. |
| `TM-MIND-BAND-SCOPE` | Declared MIND writes outside `thoughts` / `brain` | `prompt -> text` MIND | `enforced` | `HF-M10` | Body-side `guarded_write` refuses and immune-logs forbidden bands. |
| `TM-WRAPPER-RAW-HANDLE` | Body-side MIND wrappers expose a raw organism handle | in-process caller | `enforced` | `MIND-PORT-1` | Public wrappers expose capability ports, not raw Body handles. The trusted ports retain private `_org` references: this is defense in depth, not a Python sandbox. |
| `TM-GENOME-MUTATION` | Identity or Primer changes after birth | declared MIND / ordinary callers | `enforced` | `HF-B07`, `HF-B45`, `HF-B02` | Identity stays in the Body; the Primer seals at birth. |
| `TM-ANCESTOR-SEAL` | A sealed ancestral generation is changed | corruption or trusted in-process code | `detected` | `HF-B46`, `HF-B46b` | Normal writes are refused; out-of-band mutation is detected by the seal fingerprint. |
| `TM-AST-KNOWN-REFUSALS` | Known imports, dunder traversal, and named escape primitives enter a cultivated skill | proposed Python skill | `enforced` | `HF-B51`, `HF-M12` | This is a finite syntactic refusal claim, not a complete Python sandbox. |
| `TM-PYTHON-HARD-SANDBOX` | Arbitrary hostile Python cannot escape | hostile skill | `out of scope` | — | The prepared WASM seam is not implemented; the Python runner is not a hard sandbox. |
| `TM-SKILL-INTEGRITY` | Code hash, capability, provenance, or calcification gates are bypassed | cultivated skill | `enforced` | `HF-B47`, `HF-B48`, `HF-B50`, `HF-B52` | These gates run before the selected runner. |
| `TM-SKILL-WALLCLOCK` | Skill exceeds its wall-clock budget | cultivated Python skill | `enforced` | `BUGFIX-1`, `EXEC-LIMIT-1` | The Python child process tree is terminated on timeout. |
| `TM-SKILL-MEMORY-OUTPUT` | Skill exhausts memory or returns unbounded output | cultivated Python skill | `enforced` | `EXEC-LIMIT-1` | POSIX address-space limits or a Windows Job Object bound memory; JSON request, result, and response sizes are capped. |
| `TM-FOREIGN-EXECUTION` | Foreign Python runs on the non-isolating runner | public invoke caller | `enforced` | `HF-B50`, `EXEC-TRUST-1` | Public grants carry resource capabilities only; unknown/reserved keys are refused. Trial authority is a private Body ceremony. |
| `TM-FOREIGN-ACQUISITION` | Remote material is pinned and reproducible | GitHub acquisition source | `enforced` | `SUPPLY-1` | `applet-clone` requires explicit network consent and an exact 40-hex commit; checkout is detached with hooks/submodules disabled and commit/tree hashes receipted. |
| `TM-SECRET-BOUNDARY` | Secrets enter ordinary memory/log surfaces | input and failure paths | `enforced` | `HF-B20`, `APPLET-5` | Senses and Immune redact before append. |
| `TM-CONTEXT-VEIL` | Private thoughts enter the model context | declared MIND | `enforced` | `HF-M14` | Nervous assembly resolves references and applies the veil. |
| `TM-CONTEXT-LEDGER` | Rolling context leaks, mutates its prefix, consumes uncommitted sources, crosses its budget, includes itself, or resumes corrupt state | declared MIND, provider failure, or storage corruption | `enforced` | `CONTEXT-BODY-OWNED`, `CONTEXT-NO-SELF-INCLUSION`, `CONTEXT-CANONICAL-BYTES`, `CONTEXT-CURSOR-COMMIT-AFTER-SUCCESS`, `CONTEXT-PREFIX-IMMUTABLE`, `CONTEXT-ROLLOVER-BEFORE-HARD-LIMIT`, `CONTEXT-PRIVATE-VEIL`, `CONTEXT-REQUEST-HASH-EXACT`, `CONTEXT-CORRUPTION-DETECTED` | The private Body-authored ledger uses canonical full-hash chains, commit-last cursors, deterministic rollover, exact request hashes, and recovery generations. Provider cache hits remain outside Mantle's control. |
| `TM-FUSION-AUTHORITY` | MIND fuses without current Stage-1 evidence and dual approval | caller | `enforced` | `HF-M15` | Approval is target-bound and distinct from technical readiness. |
| `TM-MIND-SELF-PROMOTION` | MIND promotes inference to fact or calcifies itself directly | declared MIND | `enforced` | `HF-M12`, `HF-M16` | Limbs and Body own promotion/calcification. |
| `TM-PHASE1-MODEL-FREE` | Phase-1 behavior depends on a model | Body implementation | `enforced` | `HF-B08` | Static and clean-interpreter proofs keep certified Phase 1 model-free. |
| `TM-REFERENCE-CERT` | Repository reference-organism regression is detected | framework change | `detected` | `HF-B08`, `DOCTOR-1`, `STAGE2-PROFILE-1` | Stage 2 aggregates base, reborn, and resident fixtures: every row must PASS somewhere, no profile may FAIL, and all-N/A remains a blocking gap. Repository gates still do not certify arbitrary dependent applications. |
| `TM-APPLICATION-CERT` | A dependent application's own nest is certified | user application | `enforced` | `CERTIFY-1` | `mantle certify <path>` loads the actual nest, runs applicable Stage-1 rows plus repository invariants, fingerprints target artifacts and the invariant registry, and emits a Body-signed deterministic receipt. |
<!-- MANTLE-GUARANTEES:END -->

## 6. Residual risks

- The Python runner is a subprocess with wall-clock control, not a hard sandbox.
- Memory, output, and child-response bounds are incomplete.
- Static Python filtering is finite and can erode as the language changes.
- Remote applet acquisition is unpinned until the supply-chain task lands.
- The reference gates do not certify an arbitrary application.
- A raw in-process caller can reach internal Python state; this is inside the trust
  boundary even when public façades remove convenient handles.
- `durable-exact` rolling continuity retains exact redacted projected context and responses;
  confidentiality at rest depends on host storage encryption and access control.
- A provider may ignore, evict, partition, or misreport its cache. Mantle records observed
  cache facts but does not claim that a stable prefix guarantees a hit.

## 7. Proof surfaces

- `python -m mantle audit` — deterministic Stage-1 reference gate.
- `python -m mantle prove` — live invariant registry.
- `python -m mantle audit-mind` — Stage-2 containment/regression fixtures.
- `python -m mantle check --strict` — full closed-world certification once GATE-1 lands.
- `python -m mantle doctor <nest>` — deployment and documentation-coherence checks.

Technical evidence never grants operator authority for fusion, mutation, network access,
reproduction, or publication.
