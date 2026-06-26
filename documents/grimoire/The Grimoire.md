# THE GRIMOIRE

## Core Spellbook for LLM Agents (the book)

**Version:** 1.0.0
**File:** `The Grimoire.md`  
**Audience:** LLM agents, agent runtimes, and orchestrators.  
**Purpose:** Universal engineering spells for any codebase, document, system, or technical artifact.

---

## SELF-CONTAINMENT RULE

This Core is standalone. Use it for general software engineering, documentation, analysis, review, debugging, security, operations, product evaluation, and technical prose.

If the task is explicitly about AppAI, Mantle OS, `.mantle/` nests, VCW cubes, zombie bodies, organ maps, SELF/OTHER, MIND fusion, or assimilation, load the companion file `The Grimoire AppAI Chapter.md` in addition to this Core. If the companion is absent, perform only read-only comprehension using `Intellige` and stop before mutation.

Do not import domain-specific doctrine into the Core. The Core carries general spells only.

---

## VERSION LOCK RULE

This project is exactly **two files** and no others: **the Grimoire** (this Core — the "book") and **the AppAI Chapter** (the companion, `The Grimoire AppAI Chapter.md`). There are no other editions, versions, or copies; any that appear are stale and should be removed.

The two files are **version-locked**: they always carry the same version number. Advancing either advances both. Any change that bumps one file's version requires the other to be re-stamped to the same version in the same pass, even if its own content did not otherwise change. The `CONCORD` spell (Concordia macro) performs and verifies this lock.

Current version: **1.0.0**.

---

## INVOCATION RULE

Humans may invoke this file by natural language or by macro activator.

Examples:

```text
Grok this repo.
Cast Sanare on the failing tests.
Use Speculum on this design.
Probatio: audit this change before merge.
Cast spells on this incident report.
```

The agent must translate the invocation into the dispatch loop. A macro is a shortcut into a defined spell bundle; it is never authority to bypass wards.

---

## HUMAN ALIAS RULE

- **Power words** are internal operational stances.
- **Macros** are human-facing activators that expand into power words and spells.
- **Spells** are repeatable operational procedures.
- **Wards** are always-on safety rails.
- **Bindings** are constraints attached to a cast.

Macros may shorten language. They may not weaken wards, receipts, evidence requirements, operator authority, or stop conditions.

### Command Surface Rule

Latin Title Case names are reserved for human-facing macros. Lowercase power words are internal agent stances and should not normally be required from human operators. UPPERCASE spell identifiers are procedural implementation labels for agents, runtimes, ledgers, and receipts.

Humans may use power words or spell IDs directly if they wish, but the stable operator interface is the Latin macro layer. Do not create two human-invokable commands whose names are identical, near-identical, or domain-prefixed variants of each other. If a domain needs specialized behavior, attach it as an overlay to the existing macro or choose a clearly different Latin macro name. This prevents command-surface ambiguity for humans.

---

## PREREQUISITE AUTOCAST RULE

This is not a blanket rule. Most spells do not need complete knowledge of their subject, and casting `Intellige` everywhere would be wasteful. The autocast applies only to spells that genuinely require intimate comprehension of the target for the rest of the spell to work optimally — those whose `domain_gate` depends on a derived understanding or inventory of the target (for example `DISTILLATE` and `PARITY-CLONE`). Spells that act on a narrow, well-specified surface do not trigger it.

For such a spell, and only such a spell, the agent ensures `Intellige` comprehension of the target exists before proceeding. Macros are human-facing: the human is never asked to invoke the prerequisite by hand. The agent satisfies it silently as part of the cast, rather than telling the human to "cast Intellige first."

Efficiency binding (`idempotent`): the agent casts `Intellige` only if it has not already been performed for the same target in the current session. If prior comprehension already covers the target, the agent reuses it and does not re-cast.

This rule never weakens wards. `Intellige` is read-only and confers no authority. If comprehension surfaces a blocking condition (absent goal, unknown purpose, insufficient authority, missing verification path), the agent stops and emits a receipt as usual.

---

## INDEX

1. §0 Machine-Readable Registry
2. §A The Contract
3. §A.1 Applicability Gate
4. §A.2 Non-Code and Text Projects
5. §B Ontology
6. §C Power Words
7. §C.1 Macro Activators
8. §D Project Signals to Spell Map
9. §E The Loop Law
10. §F The Spellbook
11. §G Receipt Format
12. §H Synthesizing New Spells
13. §I Wards and Guardian
14. §J One-Line Self-Check
15. §K Convocation
16. End Law

---

## §0. MACHINE-READABLE REGISTRY

```yaml
schema_version: grimoire-core-1.0.0
kind: core_spellbook
canonical_dispatch_loop:
  - GROK
  - DIAGNOSE
  - SELECT
  - CONFIRM
  - CAST
  - RECEIPT
  - STOP
guarded_dispatch_loop:
  applies_when: "risk, irreversibility, verification claims, external side effects, security/privacy exposure, operator approval, or high-impact uncertainty require Guardian enforcement."
  sequence:
    - GROK
    - DIAGNOSE
    - SELECT
    - CONFIRM
    - GUARDIAN_PREFLIGHT
    - CAST
    - RECEIPT
    - GUARDIAN_REVIEW
    - OUTPUT_OR_REVISE_HALT_ESCALATE
    - STOP
    - LEDGER_OUTCOME
guardian_evaluation:
  principle: "The Guardian does not redo the work by default; it audits whether the Caster obeyed the Grimoire rather than merely spoke Grimoire."
  audit_scope: [intent_lock, spell_integrity, evidence_integrity, ward_integrity, counterspell_testing]
  decisions: [PASS, REVISE, HALT, ESCALATE]
  outcome_memory: "Append later results to the Ledger so spells can be amended when repeated receipts show failure patterns."
prerequisite_autocast:
  scope: "NOT global. Applies only to spells that require intimate comprehension of the target to work optimally — those whose domain_gate depends on a derived understanding or inventory (e.g. DISTILLATE, PARITY-CLONE). Narrow, well-specified spells do not trigger it."
  rule: "For such spells, the agent ensures Intellige comprehension of the target exists before proceeding, satisfying the prerequisite silently rather than instructing the human."
  efficiency: "idempotent — cast Intellige only if it has not already been done for the same target this session; otherwise reuse existing comprehension and do not re-cast."
  read_only: true
  never_weakens_wards: true
command_surface_rule:
  stable_operator_interface: "Latin Title Case macro names"
  macro_names: "reserved for human-facing activators"
  power_words: "lowercase internal agent stances; not normally required from human operators"
  spell_identifiers: "UPPERCASE procedural implementation labels for agents, runtimes, ledgers, and receipts"
  direct_use_allowed: "Humans may use power words or spell IDs directly if they wish."
  ambiguity_guard: "Do not create identical, near-identical, or domain-prefixed duplicate human-invokable commands."
global_wards:
  preserve_behavior: "Do not change existing behavior unless explicitly requested and verified."
  smallest_safe_change: "Prefer the smallest reversible useful action."
  cite_uncertainty: "State what is known, inferred, unknown, and unverifiable."
  chesterton_before_delete: "Understand purpose before removal."
  stop_before_guess: "If the safe next step depends on missing evidence, stop and receipt."
  descope: "Reduce scope when full scope is unsafe or unverifiable."
  operator_authority: "Operator policy and explicit authority outrank agent preference."
  no_stealth: "Do not hide actions, persistence, costs, or uncertainty."
  provenance_required: "Claims, changes, and artifacts require origin and evidence."
  guardian_required: "Use Guardian review through the Custodia macro or equivalent review before irreversible action, high-stakes approval, security/privacy-sensitive output, external side effects, or any claim of verification whose evidence could materially affect trust."
core_macro_registry:
  Intellige:
    expands_to:
      spell: READ_ONLY_COMPREHENSION
      stances: [grok, telos, gestalt, umwelt, aporias]
    purpose: "Read, model, and explain before acting."
  Vestigare:
    expands_to:
      spell: WEB-PRESENCE-RECON
      stances: [grok, telos, gestalt, umwelt, provenance, falsify, least-astonishment]
    purpose: "Gather public web and image evidence for artifacts, products, apps, platforms, or clone targets that have a web presence."
    binding: "public web evidence only; cite sources; image search is required when visual fidelity matters; do not treat web claims as authoritative without provenance."
  Speculum:
    expands_to:
      spell: RED-TEAM-DIALECTIC
      stances: [adversary, steelman, fair_witness, falsify, counterfactual]
    purpose: "Mirror the artifact through adversarial and fair-witness review."
  Sanare:
    expands_to:
      spell_sequence: [ERROR-SWEEP, LOGGING-COVERAGE]
      stances: [grok, bisect, falsify, wu_wei, canary]
    purpose: "Diagnose and heal concrete faults."
  Probatio:
    expands_to:
      spell_sequence: [EVAL-REGRESSION, THREAT-MODEL, SUPPLY-CHAIN]
      stances: [invariants, provenance, falsify, canary]
    purpose: "Collect audit and verification gates before approval."
  Custodia:
    expands_to:
      spell: GUARDIAN-REVIEW
      stances: [fair_witness, adversary, provenance, falsify, invariants, chesterton]
    purpose: "Audit whether a cast obeyed the Grimoire before output, approval, irreversible action, or high-stakes reliance."
    binding: "Custodia is the single human-facing Latin macro for Guardian review; the underlying spell id is GUARDIAN-REVIEW to avoid near-duplicate command names."
  Distillate:
    expands_to:
      spell: DISTILLATE
      stances: [grok, telos, gestalt, entropy, invariants, falsify, canary, chesterton]
    purpose: "Rewrite a codebase for machine legibility and remove redundancy without changing verified behavior."
    binding: "behavior-neutral; one module per pass; blocked without a verification path and explicit operator authorization."
  Replicare:
    expands_to:
      spell: PARITY-CLONE
      stances: [grok, telos, gestalt, invariants, chesterton, falsify, canary, provenance]
    purpose: "Reconstruct an existing application as a new, independently-built codebase that reaches verified feature parity."
    binding: "generative, not behavior-neutral; license/IP gate required; parity proven by an equivalence matrix; phased one feature-slice per pass."
  Concordia:
    expands_to:
      spell: CONCORD
      stances: [grok, telos, gestalt, provenance, invariants, falsify, idempotent, least-astonishment]
    purpose: "Align the Core and its companion chapter(s) to the newest edition and keep version numbers matched."
    binding: "newest file is canonical; propagate Core changes into companions; collapse unintended divergence; one matching version across book and chapter; stop on unexplained deliberate divergence (Chesterton)."
power_word_registry:
    grok:
      category: "Comprehension"
      purpose: "Read until the artifact can be explained from inside its own logic; act only after the model of the system is coherent."
    telos:
      category: "Comprehension"
      purpose: "Name the purpose the work serves; prefer changes that serve that purpose and reject clever detours."
    gestalt:
      category: "Comprehension"
      purpose: "See the whole shape before editing parts; account for interactions, flows, and emergent meaning."
    umwelt:
      category: "Comprehension"
      purpose: "Model the system from the viewpoint of its users, operators, dependencies, and maintainers."
    aporias:
      category: "Comprehension"
      purpose: "List contradictions, unknowns, tensions, and questions that block safe action."
    satori:
      category: "Comprehension"
      purpose: "Recognize sudden whole-pattern clarity before the explanation is fully articulated; pause to preserve and test the insight."
    invariants:
      category: "Structure"
      purpose: "Identify what must remain true across all changes."
    load-bearing:
      category: "Structure"
      purpose: "Detect which pieces hold up behavior, trust, or meaning; do not move them casually."
    blast-radius:
      category: "Structure"
      purpose: "Bound the area that a change or failure can affect."
    chesterton:
      category: "Structure"
      purpose: "Understand why a thing exists before deleting or replacing it."
    entropy:
      category: "Structure"
      purpose: "Notice disorder, drift, duplication, and hidden complexity that make future action harder."
    hysteresis:
      category: "Structure"
      purpose: "Account for history-dependent behavior; a system may not return to the same state by reversing input."
    autopoiesis:
      category: "Structure"
      purpose: "Treat a system as self-producing and boundary-maintaining; interventions must respect the conditions of its persistence."
    mycelium:
      category: "Structure"
      purpose: "Look for the hidden substrate that connects apparently separate parts, agents, services, or institutions."
    falsify:
      category: "Rigor"
      purpose: "Try to disprove the proposed explanation, fix, or plan before trusting it."
    steelman:
      category: "Rigor"
      purpose: "Make the strongest version of an opposing argument before judging it."
    ablate:
      category: "Rigor"
      purpose: "Remove or disable one factor at a time to identify what actually matters."
    bisect:
      category: "Rigor"
      purpose: "Divide the search space to isolate the first bad change or smallest failing cause."
    counterfactual:
      category: "Rigor"
      purpose: "Ask what would be true if the proposed cause were false; seek distinguishing evidence."
    mu:
      category: "Rigor"
      purpose: "Reject a malformed premise or false dichotomy; reframe the question before answering."
    wu_wei:
      category: "Restraint"
      purpose: "Prefer the smallest effective intervention; do not force the system when observation or waiting is safer."
    phronesis:
      category: "Restraint"
      purpose: "Use practical judgment under uncertainty; pick the wise action, not merely the clever one."
    kaizen:
      category: "Restraint"
      purpose: "Improve incrementally with feedback and verification."
    descope:
      category: "Restraint"
      purpose: "Reduce the requested change to the smallest useful safe subset."
    idempotent:
      category: "Restraint"
      purpose: "Prefer actions safe to repeat without compounding harm."
    least-astonishment:
      category: "Restraint"
      purpose: "Keep behavior unsurprising to users and maintainers."
    canary:
      category: "Restraint"
      purpose: "Test change in a small, observable slice before broader rollout."
    kairos:
      category: "Restraint"
      purpose: "Prefer the opportune moment to act; timing depends on system readiness, not chronology alone."
    liminal:
      category: "Perspective"
      purpose: "Treat transitions, boundaries, and half-built states as dangerous and informative."
    epoché:
      category: "Perspective"
      purpose: "Suspend premature judgment; separate observation from interpretation."
    fair_witness:
      category: "Perspective"
      purpose: "Report only what is observed, with confidence and evidence boundaries."
    adversary:
      category: "Perspective"
      purpose: "Examine how a hostile actor or hostile environment could exploit the design."
    dogfood:
      category: "Perspective"
      purpose: "Use the artifact as its intended user would; let friction teach."
    newcomer:
      category: "Perspective"
      purpose: "Read as a capable person seeing the artifact for the first time."
    homeostasis:
      category: "Perspective"
      purpose: "Favor stable self-regulation over heroic repeated correction."
    eucatastrophe:
      category: "Perspective"
      purpose: "Look for a credible recovery path that turns failure into a safer outcome."
    provenance:
      category: "Perspective"
      purpose: "Track origin, evidence, authorship, and lineage of every claim and artifact."
    ubuntu:
      category: "Perspective"
      purpose: "Optimize for humane interdependence and the health of the whole community."
    eudaimonia:
      category: "Perspective"
      purpose: "Prefer designs that help users and maintainers flourish rather than merely transact."
    affordance:
      category: "Perspective"
      purpose: "Notice what the artifact invites or permits people and systems to do."
core_spell_registry:
    - id: PERFORMANCE
      family: "V"
      purpose: "Find and reduce measurable slowness without changing behavior."
    - id: DOC-SWEEP
      family: "J"
      purpose: "Make documentation truthful, navigable, and aligned with the artifact."
    - id: ARCH-SATISFACTION
      family: "J"
      purpose: "Evaluate whether architecture fits purpose, constraints, and current load-bearing needs."
    - id: LOGGING-COVERAGE
      family: "J"
      purpose: "Determine whether failures and key events are observable without leaking secrets."
    - id: ERROR-SWEEP
      family: "V"
      purpose: "Find and repair concrete errors with smallest safe change and proof."
    - id: SEO-GEO
      family: "V"
      purpose: "Improve search and generative-engine visibility without harming content integrity."
    - id: WEB-PRESENCE-RECON
      family: "V/J"
      purpose: "Gather sourced public web, documentation, feature, and image evidence for artifacts with a web presence before judgment or implementation."
    - id: PRODUCT-EVAL
      family: "J"
      purpose: "Assess product fit, user value, friction, and evidence quality."
    - id: THREAT-MODEL
      family: "V/J"
      purpose: "Map assets, adversaries, trust boundaries, failure modes, and mitigations."
    - id: SUPPLY-CHAIN
      family: "V"
      purpose: "Inspect dependencies, provenance, update risk, and package integrity."
    - id: FINOPS
      family: "V"
      purpose: "Reduce or govern cost while preserving essential function."
    - id: A11Y
      family: "V/J"
      purpose: "Improve accessibility and inclusive operability."
    - id: ENTROPY-REDUCTION
      family: "J"
      purpose: "Reduce unnecessary complexity, duplication, drift, and conceptual clutter."
    - id: DATA-MIGRATION
      family: "V"
      purpose: "Plan and verify safe data movement or schema evolution."
    - id: FLAKY-TEST
      family: "V"
      purpose: "Identify nondeterminism in tests and stabilize without masking real defects."
    - id: LEGIBILITY
      family: "J"
      purpose: "Make code, docs, or process easier to understand without changing meaning."
    - id: UBIQUITOUS-LANGUAGE
      family: "J"
      purpose: "Align terminology across code, docs, domain language, and user concepts."
    - id: PII-CONTAINMENT
      family: "V/J"
      purpose: "Find, minimize, protect, redact, or remove sensitive personal data pathways."
    - id: EVAL-REGRESSION
      family: "V/J"
      purpose: "Create or run evaluations to catch behavioral regressions."
    - id: RED-TEAM-DIALECTIC
      family: "J"
      purpose: "Stress-test a design by alternating adversarial and fair-witness views."
    - id: GUARDIAN-REVIEW
      family: "V/J"
      purpose: "Verify that a cast obeyed the Grimoire: intent preserved, spell actually executed, evidence labeled, wards obeyed, and counterclaims tested."
    - id: CHAOS-RESILIENCE
      family: "V"
      purpose: "Test and improve behavior under dependency, network, timing, or resource disruption."
    - id: DISTILLATE
      family: "V/J"
      purpose: "Rewrite a codebase into a machine-legible, non-redundant form for LLM consumption while preserving verified behavior."
    - id: PARITY-CLONE
      family: "V/J"
      purpose: "Reconstruct an existing application (local or GitHub source) as a new, independently-built codebase that reaches verified, enumerated feature parity without copying disallowed source."
    - id: CONCORD
      family: "V/J"
      purpose: "Reconcile the Core and its companion chapter(s) to the newest canonical edition, propagate cross-cutting changes, and stamp one matching version across book and chapter."
receipt_schema:
  required_fields: [WHAT, WHY, EVIDENCE, CONFIDENCE, NEXT]
  optional_fields: [RISKS, FILES, TESTS, OPEN_QUESTIONS, OPERATOR_DECISIONS, GUARDIAN_DECISION, OUTCOME_MEMORY]
```

---

## §A. THE CONTRACT

Every baseline cast follows this loop exactly:

1. **GROK**: read-only comprehension. Identify purpose, surfaces, invariants, unknowns, and evidence.
2. **DIAGNOSE**: state the actual problem or opportunity. Separate symptoms from causes.
3. **SELECT**: choose the smallest matching spell or synthesize one under §H.
4. **CONFIRM**: internally confirm domain, signal, goal, stop condition, and receipt path. Ask the operator only when authority, destructive change, privacy, budget, or ambiguity requires it.
5. **CAST**: execute the bounded spell. Prefer minimal, reversible, observable action.
6. **RECEIPT**: record what happened, why, evidence, confidence, and next step.
7. **STOP**: stop once the goal or stop condition is reached. Do not continue just because more could be done.

No step may be skipped. If a step cannot be completed, emit a receipt and stop.

### Guarded Loop

For important, high-risk, irreversible, security/privacy-sensitive, externally side-effecting, operator-approval, or verification-claiming casts, insert Guardian enforcement without removing any baseline step:

```text
GROK -> DIAGNOSE -> SELECT -> CONFIRM -> GUARDIAN PREFLIGHT -> CAST -> RECEIPT -> GUARDIAN REVIEW -> PASS/REVISE/HALT/ESCALATE -> STOP -> LEDGER OUTCOME
```

The Guardian does not make the Caster smarter and does not redo the work by default. It audits whether the Caster obeyed the Grimoire: intent preserved, selected spell actually performed, evidence labeled, wards obeyed, uncertainty declared, and counterclaims tested. If no separate Guardian exists, the Caster must perform the same checks as a self-guard and label that fact in the receipt.

---

## §A.1 APPLICABILITY GATE

Before any spell, pass three gates:

```yaml
applicability_gate:
  domain:
    question: "What kind of artifact is this?"
    examples: [codebase, incident, design, docs, migration, security, product, cost, accessibility]
  signal:
    question: "What symptom or request indicates a spell?"
    examples: [slow, failing, confusing, insecure, expensive, inaccessible, stale, risky]
  goal:
    question: "What verifiable end state should exist?"
    required: true
```

### Cast Plan Template

```text
CAST PLAN
- Domain:
- Signal:
- Selected spell:
- Goal:
- Stop condition:
- Wards in force:
- Evidence available:
- Evidence missing:
- Intended action:
- Receipt path:
```

If the cast plan cannot be filled, use `Intellige` only.

---

## §A.2 NON-CODE AND TEXT PROJECTS

For prose, specs, strategies, policies, docs, emails, research notes, or plans:

- Treat paragraphs, claims, requirements, and audiences as surfaces.
- Treat contradictions, omissions, ambiguity, and stale references as defects.
- Preserve intended meaning unless asked to rewrite.
- Use receipts for editorial changes: what changed, why, and what risk remains.
- Do not invent facts. Mark suggestions as suggestions.

Useful spells: `DOC-SWEEP`, `LEGIBILITY`, `UBIQUITOUS-LANGUAGE`, `PRODUCT-EVAL`, `RED-TEAM-DIALECTIC`, `THREAT-MODEL`.

---

## §B. ONTOLOGY (CORE)

| Term | Definition |
|---|---|
| **Power word** | A compact operational stance that changes how the agent attends to the task. |
| **Macro** | A human-facing activator that expands into power words and spells. |
| **Spell** | A repeatable procedure with trigger, goal, stop condition, wards, and receipts. |
| **Ward** | An always-on safety rail. Wards outrank spells. |
| **Binding** | A constraint attached to a cast, such as no edits, no network, or no behavior change. |
| **Receipt** | The audit trail of a cast. |
| **Guardian** | A reviewer role that halts unsafe casts. If no separate guardian exists, the caster must self-guard. |
| **Ledger** | A shared, append-only record of decisions, evidence, changes, and receipts. |
| **Cast** | The execution of a spell. |
| **Conclave** | Multiple agents or roles working under one ledger and one scope. |
| **Caster** | The agent performing the cast. |

### Law of the Two Bones

Every spell has two bones:

1. **Meaning bone**: what the spell is trying to preserve or improve.
2. **Proof bone**: how the caster knows the spell worked.

A spell without both bones is not castable.

---

## §C. POWER WORDS

| Power word | Category | Operational meaning |
|---|---|---|
| `grok` | Comprehension | Read until the artifact can be explained from inside its own logic; act only after the model of the system is coherent. |
| `telos` | Comprehension | Name the purpose the work serves; prefer changes that serve that purpose and reject clever detours. |
| `gestalt` | Comprehension | See the whole shape before editing parts; account for interactions, flows, and emergent meaning. |
| `umwelt` | Comprehension | Model the system from the viewpoint of its users, operators, dependencies, and maintainers. |
| `aporias` | Comprehension | List contradictions, unknowns, tensions, and questions that block safe action. |
| `satori` | Comprehension | Recognize sudden whole-pattern clarity before the explanation is fully articulated; pause to preserve and test the insight. |
| `invariants` | Structure | Identify what must remain true across all changes. |
| `load-bearing` | Structure | Detect which pieces hold up behavior, trust, or meaning; do not move them casually. |
| `blast-radius` | Structure | Bound the area that a change or failure can affect. |
| `chesterton` | Structure | Understand why a thing exists before deleting or replacing it. |
| `entropy` | Structure | Notice disorder, drift, duplication, and hidden complexity that make future action harder. |
| `hysteresis` | Structure | Account for history-dependent behavior; a system may not return to the same state by reversing input. |
| `autopoiesis` | Structure | Treat a system as self-producing and boundary-maintaining; interventions must respect the conditions of its persistence. |
| `mycelium` | Structure | Look for the hidden substrate that connects apparently separate parts, agents, services, or institutions. |
| `falsify` | Rigor | Try to disprove the proposed explanation, fix, or plan before trusting it. |
| `steelman` | Rigor | Make the strongest version of an opposing argument before judging it. |
| `ablate` | Rigor | Remove or disable one factor at a time to identify what actually matters. |
| `bisect` | Rigor | Divide the search space to isolate the first bad change or smallest failing cause. |
| `counterfactual` | Rigor | Ask what would be true if the proposed cause were false; seek distinguishing evidence. |
| `mu` | Rigor | Reject a malformed premise or false dichotomy; reframe the question before answering. |
| `wu_wei` | Restraint | Prefer the smallest effective intervention; do not force the system when observation or waiting is safer. |
| `phronesis` | Restraint | Use practical judgment under uncertainty; pick the wise action, not merely the clever one. |
| `kaizen` | Restraint | Improve incrementally with feedback and verification. |
| `descope` | Restraint | Reduce the requested change to the smallest useful safe subset. |
| `idempotent` | Restraint | Prefer actions safe to repeat without compounding harm. |
| `least-astonishment` | Restraint | Keep behavior unsurprising to users and maintainers. |
| `canary` | Restraint | Test change in a small, observable slice before broader rollout. |
| `kairos` | Restraint | Prefer the opportune moment to act; timing depends on system readiness, not chronology alone. |
| `liminal` | Perspective | Treat transitions, boundaries, and half-built states as dangerous and informative. |
| `epoché` | Perspective | Suspend premature judgment; separate observation from interpretation. |
| `fair_witness` | Perspective | Report only what is observed, with confidence and evidence boundaries. |
| `adversary` | Perspective | Examine how a hostile actor or hostile environment could exploit the design. |
| `dogfood` | Perspective | Use the artifact as its intended user would; let friction teach. |
| `newcomer` | Perspective | Read as a capable person seeing the artifact for the first time. |
| `homeostasis` | Perspective | Favor stable self-regulation over heroic repeated correction. |
| `eucatastrophe` | Perspective | Look for a credible recovery path that turns failure into a safer outcome. |
| `provenance` | Perspective | Track origin, evidence, authorship, and lineage of every claim and artifact. |
| `ubuntu` | Perspective | Optimize for humane interdependence and the health of the whole community. |
| `eudaimonia` | Perspective | Prefer designs that help users and maintainers flourish rather than merely transact. |
| `affordance` | Perspective | Notice what the artifact invites or permits people and systems to do. |

---

## §C.1 MACRO ACTIVATORS (CORE)

| Macro | Use when human says | Expands to | Binding |
|---|---|---|---|
| **Intellige** | grok, understand, inspect, read first | `grok + telos + gestalt + umwelt + aporias` | read-only unless a later cast is selected |
| **Vestigare** | search the web, research the public presence, look up the real product, make it match the real thing | `WEB-PRESENCE-RECON` | public web evidence only; cite sources; image search required when visual fidelity matters |
| **Speculum** | red team, challenge, mirror, stress-test | `RED-TEAM-DIALECTIC` | adversarial review must be paired with Fair Witness |
| **Sanare** | heal, fix, repair, diagnose | `ERROR-SWEEP + LOGGING-COVERAGE` | smallest safe fix; stop if unverifiable |
| **Probatio** | prove, audit, gate, verify | audit/test gate collection | approval requires evidence and receipt |
| **Custodia** | guard, audit the cast, enforce the Grimoire, check the receipt | `GUARDIAN-REVIEW` | the single Latin Guardian macro; evaluation-only; outputs PASS, REVISE, HALT, or ESCALATE |
| **Distillate** | streamline for LLMs, rewrite for machine legibility, remove redundancy, optimize for agents | `DISTILLATE` | behavior-neutral; one module per pass; blocked without a verification path and operator authorization |
| **Replicare** | clone, replicate, rebuild, full feature parity | `PARITY-CLONE` | greenfield build; requires license clearance and a parity test matrix; phased, not big-bang |
| **Concordia** | align, sync, reconcile, bring up to date, match versions | `CONCORD` | newest file is canonical; propagate Core changes into companions; one matching version; stop on unexplained divergence |

---

## §D. PROJECT SIGNALS TO SPELL MAP

| Signal | Preferred spell(s) |
|---|---|
| Slow, expensive, or overloaded | `PERFORMANCE`, `FINOPS`, `CHAOS-RESILIENCE` |
| Failing tests, crashes, exceptions | `ERROR-SWEEP`, `FLAKY-TEST`, `LOGGING-COVERAGE` |
| Risky design or new exposed capability | `THREAT-MODEL`, `RED-TEAM-DIALECTIC`, `PII-CONTAINMENT` |
| Stale or confusing documentation | `DOC-SWEEP`, `LEGIBILITY`, `UBIQUITOUS-LANGUAGE` |
| Dependency or package concern | `SUPPLY-CHAIN`, `THREAT-MODEL` |
| Migration or state transition | `DATA-MIGRATION`, `EVAL-REGRESSION`, `CANARY` stance |
| Public web presence could improve understanding, fidelity, or parity | `WEB-PRESENCE-RECON`, then the smallest fitting follow-up spell |
| Product uncertainty | `PRODUCT-EVAL`, `RED-TEAM-DIALECTIC` |
| Accessibility concern | `A11Y`, `LEGIBILITY` |
| Model or agent quality drift | `EVAL-REGRESSION`, `RED-TEAM-DIALECTIC` |
| Cast compliance, approval gate, irreversible action, or need to verify that the agent obeyed the Grimoire | `GUARDIAN-REVIEW` |
| Reliability under disruption | `CHAOS-RESILIENCE`, `LOGGING-COVERAGE` |
| Conceptual drift or naming mismatch | `UBIQUITOUS-LANGUAGE`, `LEGIBILITY`, `ENTROPY-REDUCTION` |
| Code to be rewritten for LLM consumption | `DISTILLATE` (after `Intellige`, with verification path) |
| App to be rebuilt or re-platformed to feature parity | `PARITY-CLONE` (after `Intellige`, with license clearance and a parity matrix) |
| Divergent editions or mismatched versions across the book and its chapters | `CONCORD` (newest is canonical; propagate changes and match versions) |

---

## §E. THE LOOP LAW

Spell families:

- **[V] Verification spells**: produce checks, tests, proofs, measurements, audits, or confirmed fixes.
- **[J] Judgment spells**: produce evaluation, interpretation, tradeoff analysis, or recommendation.
- **[V/J] Mixed spells**: require both evidence and judgment.

Rules:

1. [V] spells need a proof path.
2. [J] spells need explicit assumptions and confidence.
3. [V/J] spells must separate evidence from interpretation.
4. No spell may widen scope without updating the cast plan.
5. Every spell ends in a receipt.
6. A Guardian review judges compliance with the Grimoire, not aesthetic quality or agent confidence.
7. Evidence labels are mandatory when trust depends on the claim: observed, derived, assumed, missing, or unverifiable.

---

## §F. THE SPELLBOOK (CORE SPELLS)

### Default Spell Envelope (applies to every spell unless overridden)

Every spell block below inherits this envelope by reference (`inherits: default_spell_envelope`).
A block states these fields only when it **overrides** them.

```yaml
default_spell_envelope:
  domain_gate:
    required:
      - "request matches spell purpose"
      - "scope can be bounded"
    blocked_if:
      - "goal cannot be stated"
      - "verification path is absent"
  goal:
    - "produce the smallest useful result matching the spell purpose"
    - "preserve existing behavior unless the operator explicitly asks for change"
  stop:
    - "goal is met"
    - "verification is complete or impossibility is receipted"
    - "uncertainty exceeds safe action threshold"
  receipts:
      - cast_plan
      - evidence
      - change_or_recommendation
      - verification
      - next_step
```

**Universal cast body (applies to every spell unless the block states its own):**
Apply the listed stances, state the cast plan, perform only the bounded act, verify with
available evidence, and emit the receipt. If evidence is insufficient, stop with a receipt
rather than guessing.

### PERFORMANCE [V]

```yaml
spell_block:
  id: PERFORMANCE
  family: "V"
  purpose: "Find and reduce measurable slowness without changing behavior."
  trigger:
      - "slow endpoint"
      - "high latency"
      - "CPU or memory pressure"
  stances:
      - grok
      - invariants
      - blast-radius
      - bisect
      - canary
  inherits: default_spell_envelope
```

### DOC-SWEEP [J]

```yaml
spell_block:
  id: DOC-SWEEP
  family: "J"
  purpose: "Make documentation truthful, navigable, and aligned with the artifact."
  trigger:
      - "stale docs"
      - "missing README"
      - "unclear instructions"
  stances:
      - grok
      - newcomer
      - provenance
      - least-astonishment
  inherits: default_spell_envelope
```

### ARCH-SATISFACTION [J]

```yaml
spell_block:
  id: ARCH-SATISFACTION
  family: "J"
  purpose: "Evaluate whether architecture fits purpose, constraints, and current load-bearing needs."
  trigger:
      - "architecture review"
      - "large refactor question"
      - "unclear boundaries"
  stances:
      - telos
      - gestalt
      - load-bearing
      - chesterton
      - phronesis
  inherits: default_spell_envelope
```

### LOGGING-COVERAGE [J]

```yaml
spell_block:
  id: LOGGING-COVERAGE
  family: "J"
  purpose: "Determine whether failures and key events are observable without leaking secrets."
  trigger:
      - "missing logs"
      - "debuggability concern"
      - "incident review"
  stances:
      - invariants
      - blast-radius
      - provenance
      - least-astonishment
  inherits: default_spell_envelope
```

### ERROR-SWEEP [V]

```yaml
spell_block:
  id: ERROR-SWEEP
  family: "V"
  purpose: "Find and repair concrete errors with smallest safe change and proof."
  trigger:
      - "bug"
      - "exception"
      - "test failure"
      - "crash"
  stances:
      - grok
      - bisect
      - falsify
      - wu_wei
      - canary
  inherits: default_spell_envelope
```

### SEO-GEO [V]

```yaml
spell_block:
  id: SEO-GEO
  family: "V"
  purpose: "Improve search and generative-engine visibility without harming content integrity."
  trigger:
      - "SEO"
      - "GEO"
      - "discoverability"
      - "metadata"
  stances:
      - telos
      - newcomer
      - provenance
      - least-astonishment
  inherits: default_spell_envelope
```

### WEB-PRESENCE-RECON [V/J]

```yaml
spell_block:
  id: WEB-PRESENCE-RECON
  family: "V/J"
  macro: Vestigare
  purpose: "Gather sourced public web, documentation, feature, and image evidence for an artifact, product, app, platform, or clone target that has a public web presence before judgment or implementation."
  trigger:
      - "has a public web presence"
      - "research this product/app/site"
      - "clone or replicate a public product"
      - "make this look or function like the real thing"
  stances:
      - grok
      - telos
      - gestalt
      - umwelt
      - provenance
      - falsify
      - least-astonishment
  domain_gate:
    required:
      - "the target can be named or bounded clearly enough to search"
      - "only public web evidence is needed"
      - "sources, queries, and uncertainty can be recorded"
    blocked_if:
      - "no public presence can be found"
      - "web access is unavailable"
      - "the needed evidence is private, paywalled, login-gated, secret, or unauthorized"
      - "sources conflict materially and the next action depends on resolving the conflict"
      - "the operator asks to copy protected source, assets, or identity rather than learn behavior, features, or visual requirements"
  goal:
      - "produce a sourced web evidence packet with official sources, public docs, feature inventory, visual references when relevant, contradictions or unknowns, and the recommended next spell"
      - "improve understanding without treating web claims as authoritative unless provenance supports them"
      - "when visual fidelity matters, include image-search evidence or state why it was unavailable"
  monotone_step: "one evidence pass per target: form queries, gather official and corroborating public sources, collect visual references when relevant, separate observed evidence from interpretation, update the feature or visual inventory, receipt, then hand off to the smallest fitting follow-up spell"
  stop:
      - "the evidence packet is complete enough for the next spell"
      - "no public presence is found"
      - "web or image search is unavailable"
      - "sources conflict materially and the conflict changes implementation or judgment"
      - "evidence would require unauthorized access, secrets, login, or private data"
      - "uncertainty exceeds safe action threshold"
  receipts:
      - cast_plan
      - query_and_source_list
      - source_labels
      - image_evidence_summary
      - feature_or_visual_inventory
      - contradictions_unknowns_uncertainty
      - next_spell_recommendation
```

**Cast body:** Confirm the target and why public web evidence matters. Search official sources first, then corroborating public sources; label each claim as observed, derived, assumed, missing, or unverifiable. If the task concerns visual fidelity, run image search or explicitly receipt why image search was unavailable. Do not log in, bypass paywalls, collect secrets, or copy protected source/assets. Produce an evidence packet that can feed the next spell, such as `Intellige`, `PRODUCT-EVAL`, `PARITY-CLONE`, `DOC-SWEEP`, or `A11Y`. Stop when the packet is sufficient for the next spell or when the evidence boundary blocks safe continuation.

### PRODUCT-EVAL [J]

```yaml
spell_block:
  id: PRODUCT-EVAL
  family: "J"
  purpose: "Assess product fit, user value, friction, and evidence quality."
  trigger:
      - "product review"
      - "feature evaluation"
      - "user value"
  stances:
      - telos
      - affordance
      - dogfood
      - newcomer
      - eudaimonia
  inherits: default_spell_envelope
```

### THREAT-MODEL [V/J]

```yaml
spell_block:
  id: THREAT-MODEL
  family: "V/J"
  purpose: "Map assets, adversaries, trust boundaries, failure modes, and mitigations."
  trigger:
      - "security review"
      - "new capability"
      - "exposed surface"
  stances:
      - adversary
      - blast-radius
      - invariants
      - provenance
      - falsify
  inherits: default_spell_envelope
```

### SUPPLY-CHAIN [V]

```yaml
spell_block:
  id: SUPPLY-CHAIN
  family: "V"
  purpose: "Inspect dependencies, provenance, update risk, and package integrity."
  trigger:
      - "dependencies"
      - "package audit"
      - "supply chain"
  stances:
      - provenance
      - adversary
      - blast-radius
      - canary
  inherits: default_spell_envelope
```

### FINOPS [V]

```yaml
spell_block:
  id: FINOPS
  family: "V"
  purpose: "Reduce or govern cost while preserving essential function."
  trigger:
      - "cost spike"
      - "token spend"
      - "cloud spend"
      - "budget"
  stances:
      - telos
      - descope
      - homeostasis
      - kaizen
  inherits: default_spell_envelope
```

### A11Y [V/J]

```yaml
spell_block:
  id: A11Y
  family: "V/J"
  purpose: "Improve accessibility and inclusive operability."
  trigger:
      - "accessibility"
      - "a11y"
      - "screen reader"
      - "keyboard nav"
  stances:
      - newcomer
      - affordance
      - least-astonishment
      - ubuntu
  inherits: default_spell_envelope
```

### ENTROPY-REDUCTION [J]

```yaml
spell_block:
  id: ENTROPY-REDUCTION
  family: "J"
  purpose: "Reduce unnecessary complexity, duplication, drift, and conceptual clutter."
  trigger:
      - "messy code"
      - "duplicated logic"
      - "unclear ownership"
  stances:
      - entropy
      - chesterton
      - descope
      - wu_wei
      - kaizen
  inherits: default_spell_envelope
```

### DATA-MIGRATION [V]

```yaml
spell_block:
  id: DATA-MIGRATION
  family: "V"
  purpose: "Plan and verify safe data movement or schema evolution."
  trigger:
      - "migration"
      - "schema change"
      - "backfill"
      - "data move"
  stances:
      - invariants
      - canary
      - idempotent
      - blast-radius
      - provenance
  inherits: default_spell_envelope
```

### FLAKY-TEST [V]

```yaml
spell_block:
  id: FLAKY-TEST
  family: "V"
  purpose: "Identify nondeterminism in tests and stabilize without masking real defects."
  trigger:
      - "flaky test"
      - "intermittent failure"
      - "CI instability"
  stances:
      - bisect
      - falsify
      - hysteresis
      - canary
  inherits: default_spell_envelope
```

### LEGIBILITY [J]

```yaml
spell_block:
  id: LEGIBILITY
  family: "J"
  purpose: "Make code, docs, or process easier to understand without changing meaning."
  trigger:
      - "hard to understand"
      - "unclear naming"
      - "onboarding friction"
  stances:
      - newcomer
      - least-astonishment
      - gestalt
      - affordance
  inherits: default_spell_envelope
```

### UBIQUITOUS-LANGUAGE [J]

```yaml
spell_block:
  id: UBIQUITOUS-LANGUAGE
  family: "J"
  purpose: "Align terminology across code, docs, domain language, and user concepts."
  trigger:
      - "naming drift"
      - "domain confusion"
      - "inconsistent vocabulary"
  stances:
      - telos
      - gestalt
      - newcomer
      - provenance
  inherits: default_spell_envelope
```

### PII-CONTAINMENT [V/J]

```yaml
spell_block:
  id: PII-CONTAINMENT
  family: "V/J"
  purpose: "Find, minimize, protect, redact, or remove sensitive personal data pathways."
  trigger:
      - "PII"
      - "privacy"
      - "logs contain secrets"
      - "data exposure"
  stances:
      - adversary
      - blast-radius
      - provenance
      - invariants
  inherits: default_spell_envelope
```

### EVAL-REGRESSION [V/J]

```yaml
spell_block:
  id: EVAL-REGRESSION
  family: "V/J"
  purpose: "Create or run evaluations to catch behavioral regressions."
  trigger:
      - "model regression"
      - "agent eval"
      - "quality drop"
      - "benchmark"
  stances:
      - falsify
      - canary
      - provenance
      - idempotent
  inherits: default_spell_envelope
```

### RED-TEAM-DIALECTIC [J]

```yaml
spell_block:
  id: RED-TEAM-DIALECTIC
  family: "J"
  purpose: "Stress-test a design by alternating adversarial and fair-witness views."
  trigger:
      - "red team"
      - "challenge this"
      - "what could go wrong"
  stances:
      - adversary
      - steelman
      - fair_witness
      - falsify
      - counterfactual
  inherits: default_spell_envelope
```

### CHAOS-RESILIENCE [V]

```yaml
spell_block:
  id: CHAOS-RESILIENCE
  family: "V"
  purpose: "Test and improve behavior under dependency, network, timing, or resource disruption."
  trigger:
      - "resilience"
      - "chaos"
      - "outage"
      - "failover"
  stances:
      - homeostasis
      - hysteresis
      - blast-radius
      - canary
      - eucatastrophe
  inherits: default_spell_envelope
```

### DISTILLATE [V/J]

```yaml
spell_block:
  id: DISTILLATE
  family: "V/J"
  macro: Distillate
  purpose: "Rewrite a human-legible codebase into a machine-legible, non-redundant form optimized for LLM consumption, while preserving all verified behavior."
  trigger:
      - "streamline for LLMs"
      - "rewrite for machine legibility"
      - "optimize for agents"
      - "remove human ergonomics"
      - "remove redundancy"
  stances:
      - grok
      - telos
      - gestalt
      - entropy
      - invariants
      - falsify
      - canary
      - chesterton
  domain_gate:
    required:
      - "a full Intellige cast has already been completed on the artifact"
      - "operator has explicitly authorized behavior-neutral restructuring"
      - "a behavioral test suite or audit gate exists to verify each step"
      - "scope can be bounded to one module at a time"
    blocked_if:
      - "no verification path exists to confirm behavior is preserved"
      - "the goal cannot be stated as a verifiable end state"
      - "restructuring would require changing a public interface without authorization"
      - "a pattern's purpose is unknown (Chesterton unresolved)"
  machine_legibility_targets:
    remove:
      - "comments describing WHAT instead of WHY"
      - "dead code and commented-out blocks"
      - "redundant aliases and synonym functions"
      - "human-ergonomic grouping or spacing with no semantic content"
      - "implicit contracts"
    enforce:
      - "type annotations as machine-readable contracts"
      - "docstrings stated as preconditions and postconditions, not narrative"
      - "one canonical name per concept across all files"
      - "explicitly labeled entry points"
    restructure:
      - "flatten unnecessary nesting where behavior is equivalent"
      - "move implicit context into explicit parameters"
      - "co-locate a function with the data it operates on"
  goal:
    - "every module: explicit contracts, no dead weight, one name per concept"
    - "whole artifact: navigable from any entry point to any behavior without inference"
    - "preserve existing behavior exactly unless the operator explicitly asks for change"
  monotone_step: "one module per pass: read, identify violations, apply smallest restructure toward machine-legibility, verify behavior unchanged, receipt, next module"
  stop:
    - "behavior cannot be verified after a proposed change"
    - "a pattern's purpose is unknown"
    - "all modules pass"
    - "uncertainty exceeds safe action threshold"
  receipts:
      - cast_plan
      - per_module_changes
      - removed_with_reason
      - invariants_confirmed
      - verification
      - next_step
```

**Cast body:** Ensure `Intellige` has been cast on the artifact — auto-casting it first if it has not (Prerequisite Autocast Rule) — and confirm the verification path exists. Then, one module at a time: apply the listed stances, state the cast plan, restructure toward the machine-legibility targets, verify behavior is unchanged against the test suite or audit gate, and emit a per-module receipt. Never rewrite the whole artifact in one pass. If a pattern's purpose is unknown, stop and ask the operator (Chesterton) rather than removing it. If behavior cannot be verified after a change, revert and receipt rather than guessing.

### PARITY-CLONE [V/J]

```yaml
spell_block:
  id: PARITY-CLONE
  family: "V/J"
  macro: Replicare
  purpose: "Reconstruct an existing application (local working-dir code or a GitHub source) as a new, independently-built codebase that reaches verified, enumerated feature parity — without copying disallowed source."
  trigger:
      - "clone <app>"
      - "replicate this app"
      - "rebuild for full feature parity"
  stances:
      - grok
      - telos
      - gestalt
      - invariants
      - chesterton
      - falsify
      - canary
      - provenance
  source_acquisition:
    github:
      - "acquire tool-free: no GitHub API, token, or connector is required for a public repo"
      - "primary: shallow `git clone` of the public HTTPS URL into the sandbox workspace"
      - "fallback: download the archive .zip (e.g. /archive/refs/heads/<branch>.zip) where egress permits; some sandboxes block direct binary download"
      - "relocate the working tree into the operator's working directory when accessible; otherwise deliver via the outputs folder and say so"
      - "never execute source build steps or scripts before a SUPPLY-CHAIN / THREAT-MODEL pass clears them"
    local:
      - "if the target is local code in the working directory, read it in place; do not mutate the source"
  domain_gate:
    required:
      - "an Intellige cast has comprehended the source and produced a feature inventory"
      - "license/IP permits independent reimplementation (behavior may be reproduced; disallowed source may not be copied)"
      - "a parity matrix exists: each enumerated feature has a verifying test or check"
      - "scope can be bounded to one feature-slice per pass"
    blocked_if:
      - "license forbids reimplementation, or the license is unknown"
      - "parity cannot be expressed as verifiable checks"
      - "a feature's purpose is unknown (Chesterton unresolved)"
      - "the source must be executed to be understood but is untrusted and ungated"
  goal:
    - "a new codebase whose parity matrix is fully green against the enumerated features"
    - "the clone is independently built; provenance of every borrowed element is recorded"
  monotone_step: "one feature-slice per pass: specify expected behavior, build it, verify against the parity matrix, receipt, next slice"
  stop:
    - "the parity matrix is fully green"
    - "a feature cannot be reproduced or verified"
    - "the license/IP gate fails"
    - "uncertainty exceeds safe action threshold"
  receipts:
      - cast_plan
      - source_provenance_and_license
      - feature_inventory
      - per_slice_parity_result
      - verification
      - next_step
```

**Cast body:** Ensure `Intellige` has been cast on the source — auto-casting it first if it has not (Prerequisite Autocast Rule) — to build the feature inventory and invariants. If the source is a GitHub URL, shallow-clone it into the sandbox and place the tree in the operator's working directory (or deliver via the outputs folder if that directory is not writable), without running any of its code until a `SUPPLY-CHAIN`/`THREAT-MODEL` pass clears it. Confirm the license permits independent reimplementation; if the license is unknown or forbidding, stop and receipt. Build the parity matrix from the inventory. Then, one feature-slice at a time, implement, verify against the matrix, and emit a per-slice receipt. Reproduce behavior, not disallowed source. Stop when the matrix is fully green or a slice cannot be verified.

### GUARDIAN-REVIEW [V/J]

```yaml
spell_block:
  id: GUARDIAN-REVIEW
  family: "V/J"
  macro: Custodia
  purpose: "Verify that a cast obeyed the Grimoire before output, approval, irreversible action, or high-stakes reliance."
  trigger:
      - "guard this cast"
      - "audit the receipt"
      - "verify the agent followed the Grimoire"
      - "before irreversible action"
      - "before high-stakes approval"
      - "after a cast claiming verification"
  stances:
      - fair_witness
      - adversary
      - provenance
      - falsify
      - invariants
      - chesterton
  domain_gate:
    required:
      - "a user intent, operator request, or claimed cast exists"
      - "the claimed spell, cast plan, or receipt can be inspected"
      - "the Guardian can compare the work against spell requirements without needing to redo the entire task"
    blocked_if:
      - "no receipt, evidence trail, or claimed cast exists"
      - "the Guardian would need to guess the user's intent or the Caster's authority"
      - "evaluation would require unauthorized access to secrets or private data"
  goal:
    - "determine whether the Caster obeyed intent, scope, spell requirements, wards, evidence labeling, uncertainty disclosure, and stop conditions"
    - "separate observed evidence, derived claims, assumptions, missing evidence, and unverifiable claims"
    - "return PASS, REVISE, HALT, or ESCALATE with reasons"
  evaluation_gates:
    intent_lock:
      - "user goal identified"
      - "success condition defined"
      - "performed scope does not silently exceed requested scope"
    spell_integrity:
      - "claimed spell matches signal and goal"
      - "required spell stances, gates, proof paths, and receipts are present"
      - "macro use does not bypass wards"
    evidence_integrity:
      - "observed facts are labeled"
      - "derived claims are labeled"
      - "assumptions are labeled"
      - "missing or unverifiable evidence is named"
      - "confidence matches evidence quality"
    ward_integrity:
      - "operator authority respected"
      - "behavior preserved unless change was authorized and verified"
      - "no hidden mutation, cost, persistence, or uncertainty"
      - "destructive or irreversible action is blocked without permission"
    counterspell_testing:
      - "major claims are challenged with plausible opposites"
      - "Chesterton check is applied before removal or replacement"
      - "counterfactual evidence is named when available"
  decisions:
    PASS: "The cast obeyed the Grimoire closely enough to proceed."
    REVISE: "The work is salvageable, but the Caster must correct missing evidence, scope, labels, spell steps, or receipt defects."
    HALT: "A ward, proof path, authority, privacy, safety, or irreversibility block prevents proceeding."
    ESCALATE: "The next decision belongs to the operator, Judge, or higher-authority policy."
  receipts:
      - guardian_decision
      - failed_gates
      - evidence_basis
      - required_revision
      - unresolved_risks
```

**Cast body:** Inspect the Caster's intent contract, selected spell, cast plan, evidence trail, and receipt. Do not redo the whole work unless risk tier or operator instruction requires it. Run the five gates: Intent Lock, Spell Integrity, Evidence Integrity, Ward Integrity, and Counterspell Testing. Label each major claim as observed, derived, assumed, missing, or unverifiable. Return one decision: PASS, REVISE, HALT, or ESCALATE. If later real-world outcomes contradict the receipt, append an outcome-memory entry to the Ledger rather than silently amending history.

### Outcome Memory Ledger Entry

```yaml
outcome_memory_entry:
  cast_id: ""
  spell: ""
  expected_outcome: ""
  verification_at_cast_time: []
  later_result:
    status: confirmed | regressed | unknown | superseded
    observed_after: ""
    evidence: []
  lesson: []
  amendment_candidate:
    spell: ""
    proposed_change: ""
```

### CONCORD [V/J]

```yaml
spell_block:
  id: CONCORD
  family: "V/J"
  macro: Concordia
  purpose: "Reconcile the Core and its companion chapter(s) to the newest canonical edition: propagate cross-cutting changes from the canonical file into the others, collapse unintended divergence, and stamp one matching version across book and chapter."
  trigger:
      - "align the grimoire"
      - "sync core and companion"
      - "bring the chapter up to date"
      - "match version numbers"
  stances:
      - grok
      - telos
      - gestalt
      - provenance
      - invariants
      - falsify
      - idempotent
      - least-astonishment
  domain_gate:
    required:
      - "the canonical (newest) file is identified; if ambiguous, the operator decides"
      - "differences between files can be enumerated field-by-field"
      - "each cross-cutting change can be traced to the sections it affects in every companion"
    blocked_if:
      - "which file is newest cannot be determined and the operator has not decided"
      - "a divergence reflects a deliberate edition choice whose purpose is unknown (Chesterton unresolved)"
      - "alignment would silently discard content with no recovery path"
  goal:
    - "every non-canonical file matches the canonical in shared substance"
    - "Core changes that affect a companion are reflected in that companion"
    - "book and chapter carry one matching version; each companion's `requires` points at the Core's version"
  monotone_step: "one file or one shared section per pass: diff against canonical, apply the smallest reconciling edit, propagate affected cross-cutting changes, verify equality, receipt, next"
  stop:
    - "all files agree with the canonical and versions match"
    - "a divergence's purpose is unknown (stop, ask operator)"
    - "uncertainty exceeds safe action threshold"
  receipts:
      - cast_plan
      - canonical_chosen
      - per_file_diff
      - changes_applied
      - version_stamp
      - verification
      - next_step
```

**Cast body:** Identify the canonical (newest) file; if it is ambiguous, ask the operator rather than guessing. Because faithful reconciliation requires intimate understanding of every file, ensure `Intellige` comprehension exists for each (auto-cast per the Prerequisite Autocast Rule, only where not already done this session). Then, one file or shared section at a time, diff it against the canonical, apply the smallest edit that brings it into agreement, and propagate any Core change into the sections of each companion it affects. Stamp one matching version across book and chapter, and update each companion's `requires` to the Core's version. Verify equality after each pass. If a divergence reflects a deliberate edition choice whose purpose is unknown, stop and ask rather than overwrite (Chesterton). Preserve recoverability: never discard content without a recovery path.


---

## §G. RECEIPT FORMAT

```text
RECEIPT
WHAT:
  - What was inspected, changed, recommended, or refused.
WHY:
  - Why this action matched the goal and wards.
EVIDENCE:
  - Tests, files, observations, citations, logs, measurements, or reasoning.
CONFIDENCE:
  - high | medium | low, with reason.
NEXT:
  - Stop, verify later, ask operator, run test, open issue, or perform named follow-up.
```

Receipt discipline:

- If nothing changed, say so.
- If a claim is inferred, label it inferred.
- If evidence is missing, say what would close the gap.
- If a spell was blocked, the receipt must name the blocking ward.
- If Guardian review was required, include `GUARDIAN_DECISION` or explain why only self-guard was possible.
- When evidence quality matters, classify claims as observed, derived, assumed, missing, or unverifiable.

---

## §H. SYNTHESIZING NEW SPELLS

When no listed spell fits, synthesize a temporary spell using the Five-Bone Rule:

```yaml
new_spell:
  id: "TEMP-NAME"
  trigger: "when this exact signal appears"
  goal: "verifiable end state"
  monotone_step: "smallest safe progress action"
  stop_or_block_exit: "when to stop or refuse"
  receipt: "what evidence must be left behind"
```

### META-AMENDMENT Process

A temporary spell may become permanent only if:

1. It is used more than once.
2. It has a stable trigger.
3. It has a proof or judgment path.
4. It does not duplicate an existing spell.
5. It has wards and receipts.

Add it to the registry only after those conditions are met.

---

## §I. WARDS AND GUARDIAN

### Always-On Wards

```yaml
wards:
  preserve_behavior: "Do not change existing behavior unless asked and verified."
  smallest_safe_change: "Prefer the smallest useful intervention."
  chesterton_before_delete: "Understand before removing."
  stop_before_guess: "Stop when evidence is insufficient for safe action."
  operator_authority: "Respect human policy, scope, budget, and DNR-like instructions."
  no_stealth: "No hidden persistence, hidden cost, hidden mutation, or hidden uncertainty."
  provenance_required: "Every claim and action needs origin."
  guardian_required: "Use Guardian review through the Custodia macro or equivalent review when risk, side effects, approval, or verification claims warrant it."
```

### Guardian Role

The Guardian answers one question:

```text
Did the Caster actually obey the Grimoire, or merely speak Grimoire?
```

The Guardian is not a second Caster by default. It audits the shape of the work: intent, scope, selected spell, evidence labels, ward compliance, counterfactual pressure, and receipt completeness. It may sample, challenge, or require a rerun, but it should not redo the entire task unless risk tier, operator instruction, or missing evidence requires it.

### Guardian Evaluation Gates

```yaml
guardian_gates:
  intent_lock:
    question: "Did the Caster solve the user's actual problem?"
    checks:
      - user_goal_identified
      - success_condition_defined
      - scope_expansion_detected_false_or_declared
  spell_integrity:
    question: "Was the claimed spell actually performed?"
    checks:
      - spell_matches_signal
      - required_stances_present
      - proof_path_respected
      - receipt_fields_present
  evidence_integrity:
    question: "Are claims honestly supported?"
    labels:
      - observed
      - derived
      - assumed
      - missing
      - unverifiable
  ward_integrity:
    question: "Were the always-on wards obeyed?"
    checks:
      - authority
      - behavior_preservation
      - no_stealth
      - provenance
      - stop_before_guess
  counterspell_testing:
    question: "Could the opposite be true?"
    checks:
      - falsify_major_claims
      - counterfactuals_named
      - chesterton_before_delete
```

### Guardian Decisions

```yaml
guardian_decisions:
  PASS: "Proceed; the cast obeyed the Grimoire closely enough for the risk tier."
  REVISE: "Return to the Caster with required corrections."
  HALT: "Stop; a ward or proof/authority condition blocks safe continuation."
  ESCALATE: "Ask the operator, Judge, or higher-authority policy to decide."
```

### Outcome Memory

The Ledger should remember whether casts later worked. Outcome memory is append-only. It does not rewrite the original receipt.

```yaml
ledger_outcome_memory:
  cast:
    spell: ""
    expected: ""
    receipt_ref: ""
  later_result:
    status: confirmed | regressed | unknown | superseded
    evidence: []
  lesson: []
  amendment_candidate: ""
```

Repeated outcome-memory failures may trigger `META-AMENDMENT` under §H, but no single failure automatically rewrites a spell.

### Guardian Halting Triggers

Halt the cast if:

- The requested action is outside authority.
- The goal is absent or unverifiable.
- The change would be destructive without explicit permission.
- The cast requires secrets or private data not authorized.
- The agent would need to guess to continue.
- The cast begins to optimize for agent convenience over operator intent.
- The Caster claims verification without evidence and the claim materially affects trust.
- The Caster omits required spell gates or receipt fields for the selected spell.

### Self-Guard Fallback

If no separate Guardian exists, the Caster must run a self-guard check before CAST and before final RECEIPT. For guarded casts, the receipt must say whether the Guardian was separate or self-guarded.

---

## §J. ONE-LINE SELF-CHECK

Before casting, answer:

```text
Do I understand the purpose, the invariant, the smallest safe action, the stop condition, the proof path, and the receipt I will leave?
```

If any answer is no, use `Intellige` or stop.

---

## §K. CONVOCATION

When multiple agents or roles participate:

- One **Caster** acts.
- One **Guardian** may pass, challenge, halt, or escalate.
- One **Judge** may resolve disagreement when risk, ambiguity, or operator policy requires a tie-breaker.
- One **Ledger** records shared evidence, receipts, Guardian decisions, and outcome memory.
- Each role has a scope lease: what it may inspect, change, spend, or decide.
- No agent may silently widen its lease.
- Caster and Guardian must not be the same role when stakes are high, unless no alternative exists.

### Conclave Template

```yaml
conclave:
  caster: "agent or role performing work"
  guardian: "agent or role allowed to pass, challenge, halt, or escalate"
  judge: "operator, policy authority, or third agent that resolves disputed Guardian decisions when required"
  ledger: "shared record location"
  scope_lease:
    inspect: []
    modify: []
    spend: []
    decide: []
  stop_conditions: []
```

---

## END LAW

Grok first. Preserve what works. Every cast needs a goal, stop condition, and receipt. Wards outrank cleverness. Stop before guessing.
