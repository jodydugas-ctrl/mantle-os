# GRIMOIRE: APPAI DOMAIN EXTENSION

## Companion to the Core Grimoire

**Version:** 1.7 (self-audited; language-agnostic substrate across all growth paths)  
**File:** `GRIMOIRE_APPAI_DOMAIN_v1_0.md`  
**Schema:** `grimoire-appai-domain-1.0` (compatibility contract unchanged; v1.1 adds provenance and fills gaps — see §F)  
**Audience:** LLM agents, AppAI builders, Mantle-style runtimes, and agent orchestrators.  
**Purpose:** Domain-specific spells for AppAI work: birth, assimilation, residency, memory, limbs, diagnostics, metabolism, controlled reconstruction, and retirement.

---

## PREREQUISITE & EXTENSION RULE

This file extends `THE_GRIMOIRE_CORE_v3_0.md`. Load the Core first.

If the Core is missing, refuse AppAI mutation and operate only in `Intellige` mode: read, model, explain, and stop. Do not assimilate, hook, graft, anchor, fuse, reconstruct, cremate, or modify.

This extension is domain-specific. Use it only when the task concerns AppAI, Mantle OS, `.mantle/` nests, VCW cubes, zombie bodies, organ maps, Body/MIND, SELF/OTHER, residency, assimilation, or related organism-style application architecture.

This extension deliberately defines diagnostics without assuming every AppAI has a specialized diagnostic limb or sub-agent. Diagnostic spells describe what must be checked, not a required implementation name.

---

## INDEX

1. §0 Machine-Readable Domain Registry
2. §A AppAI Ontology
3. §B AppAI-Specific Power Words
4. §C AppAI Macro Activators
5. §D AppAI Spellbook
6. §E AppAI Appendices
7. §F Revision Ledger
8. End Law

---

## §0. MACHINE-READABLE DOMAIN REGISTRY

```yaml
schema_version: grimoire-appai-domain-1.0
kind: domain_extension
requires: grimoire-core-3.0
missing_core_behavior: "Intellige only; no mutation."
golden_rule:
  phase1: "Body/Zombie must be certified with no LLM."
  phase2: "MIND fusion may only extend a certified Body."
  containment: "MIND proposes; Body applies."
  other: "OTHER may teach; OTHER may not rule or execute raw."
appai_macro_registry:
  Animare:
    purpose: "birth a greenfield AppAI Body"
    expands_to: {spell: ANIMARE, stances: [grok, invariants, homeostasis, provenance]}
  Necromantia:
    purpose: "assimilate an existing application as an AppAI Body"
    expands_to: {spell: NECROMANCY, stances: [grok, chesterton, invariants, provenance, wu_wei]}
  Custodia:
    purpose: "guard AppAI boundaries and authority"
    expands_to: {spell: THREAT-MODEL, stances: [adversary, blast-radius, provenance]}
  Memoria:
    purpose: "inspect or reason about memory and provenance"
    expands_to: {spell: MEM-DIGESTION, stances: [provenance, fair_witness, digest]}
  Exorcizare:
    purpose: "quarantine or expel unsafe OTHER influence"
    expands_to: {spell: MEM-DIGESTION, stances: [adversary, SELF_OTHER, falsify]}
  Ossificare:
    purpose: "harden a proven behavior into a reflex"
    expands_to: {spell: SKILL-CALCIFICATION, stances: [calcify, invariants, provenance]}
  Resurgere:
    purpose: "controlled reconstruction under policy"
    expands_to: {spell: RESURGERE, stances: [eucatastrophe, provenance, operator_authority]}
  Cremare:
    purpose: "authorized retirement or DNR"
    expands_to: {spell: CREMATION, stances: [operator_authority, provenance, fair_witness]}
  Aegis:
    purpose: "shield and audit AppAI boundaries"
    expands_to: {spell_sequence: [VITALS-CHECKUP, THREAT-MODEL], stances: [invariants, adversary, provenance]}
  Vocare:
    purpose: "prepare MIND readiness after Stage 1"
    expands_to: {spell: VOCARE, stances: [liminal, invariants, provenance]}
  Silere:
    purpose: "put cognition to sleep and preserve Body reflexes"
    expands_to: {spell: METABOLIC-GOVERNANCE, stances: [homeostasis, descope]}
  Sanare:
    purpose: "diagnose AppAI Body health before healing"
    expands_to: {spell_sequence: [VITALS-CHECKUP, ERROR-SWEEP], stances: [fair_witness, nociception, wu_wei]}
  Codex:
    purpose: "read and write a VCW cube — the durable memory outside the prompt"
    expands_to: {spell: VCW-LITERACY, stances: [grok, invariants, provenance, idempotent, least-astonishment]}
appai_power_registry:
  nociception: "Treat severe unresolved Body distress as a localized wake signal."
  calcify: "Promote only proven behavior into deterministic reflex."
  digest: "Quarantine OTHER, inspect it, and re-derive safe value into SELF."
  SELF_OTHER: "Distinguish Body-proved SELF from all foreign OTHER artifacts."
  residency: "Operate as a bounded resident of a host without breaking the host."
  zombie_body: "A certified Phase-1 Body alive without a MIND."
  veil: "Hide private, quarantined, or tombstoned memory from ordinary reads."
  seed: "Minimal authorized identity or reconstruction material, policy-gated."
appai_spell_registry:
    - id: ANIMARE
      family: "V/J"
      purpose: "Grow a greenfield AppAI Body from declaration, certify Phase 1, and stop before MIND fusion."
    - id: NECROMANCY
      family: "V/J"
      purpose: "Raise an existing application as an audited AppAI Body without breaking host behavior."
    - id: VITALS-CHECKUP
      family: "V"
      purpose: "Run non-destructive AppAI diagnostics and report health, drift, and audit readiness."
    - id: MEM-DIGESTION
      family: "V/J"
      purpose: "Inspect foreign knowledge or memory artifacts, quarantine OTHER, and re-derive only safe useful parts."
    - id: SKILL-CALCIFICATION
      family: "V"
      purpose: "Convert proven learned behavior into a bounded deterministic reflex only after sandbox and trial gates."
    - id: METABOLIC-GOVERNANCE
      family: "V"
      purpose: "Control cognition, cost, wake frequency, and energy modes without hiding spend or starving critical reflexes."
    - id: CREMATION
      family: "V/J"
      purpose: "Retire, uninstall, or mark DNR for an AppAI body with authority, receipts, and no unauthorized resurrection."
    - id: VOCARE
      family: "V/J"
      purpose: "Prepare or request MIND readiness only after Phase 1 certification; fusion itself requires separate operator authority."
    - id: RESURGERE
      family: "V/J"
      purpose: "Controlled reconstruction from authorized seed or source lineage, with DNR and budget gates before action."
    - id: VCW-LITERACY
      family: "V/J"
      purpose: "Teach the agent to read, write, address, and metabolize a VCW cube — the durable, append-only, hash-verified memory an AppAI Body lives on. Field manual in §E.9."
```

---

## §A. APPAI ONTOLOGY

### A.1 Core Definitions

| Term | Definition |
|---|---|
| **AppAI** | A deterministic Body plus optional bounded MIND. |
| **Body** | The automatic organism: organs, reflexes, memory, identity, audit, and action surfaces that must run without an LLM. |
| **Zombie Body** | A certified Phase-1 Body: alive, persistent, auditable, and MIND-free. |
| **MIND** | Optional Phase-2 reasoning/voice layer. It may extend the Body, never replace it. |
| **Organ** | A bounded code responsibility with manifest, reflexes, phase state, and audit obligations. |
| **VCW cube** | Durable append-only picture-memory substrate, organized by bands. |
| **SELF** | Artifacts the Body can prove belong to its identity boundary. |
| **OTHER** | Anything not proven SELF. It may be studied, never trusted or executed raw. |
| **Residency** | A bounded AppAI living in or beside a host application without changing host behavior outside authorized hooks. |
| **Limb** | An effector or action surface. Limbs operate controls, tools, bridges, and outputs under proof. |
| **Brain** | The dormant Phase-1 cognition surface; active only after authorized Phase-2 fusion. |

### A.2 Golden Rule

```text
Phase 1: Grow or assimilate a Body that runs without an LLM.
Stage 1: Certify the Zombie Body.
Phase 2: Only after Stage-1 success may MIND readiness be considered.
MIND: Proposes and authors bounded intentions.
Body: Applies, verifies, records, and enforces.
```

**Concrete certification gates (provenance: Mantle OS Gen-4 reference implementation).**
"Certify" above is not abstract. In a Mantle-style runtime it resolves to named gates that
the Caster should look for and cite as evidence:

- **Stage-1 (Zombie Body) gate** — deterministic and LLM-free; proves the Body runs,
  senses, reflexes, remembers, protects, acts, and persists with no model on the path.
- **Security invariants** — a fixed, enumerated red/green set. Verified against the
  reference source: `python -m mantle prove` reports **68/68 invariants green** (the line
  grew 36 → 68 across generations; see `mantle/audits/invariants.py`, the `TESTS` table).
  Require the set enumerated and fully green; treat the count as version-bound (68 at
  Gen-4), not eternal.
- **Stage-2 gate** — runs only after fusion and **re-runs every Stage-1 row**, proving the
  MIND did not weaken a single Phase-1 reflex. Fusion is *refused* without a passed Stage-1.
- **Tamper proofs** — the audit must demonstrably CATCH violations (e.g. broken hash,
  broken primer, broken seal each force a non-zero exit). A gate that cannot fail on
  tampering is not evidence. See `VITALS-CHECKUP` → `tamper_proof_verification`.

### A.3 Organ Chart

| Organ | Role | Direction |
|---|---|---|
| **Heart** | pulse, scheduling, circulation, checkpoint | internal clock |
| **Genome** | identity, primer, commandments, lineage | Body-resident identity |
| **Nervous System** | routing, references, context assembly | internal signals |
| **Senses** | inbound perception, surface map | in |
| **Immune** | defense, quarantine, tombstone, redaction, integrity | protection |
| **Limbs** | effectors, tools, ControlBridge, App-Face Bridge, proofs | out |
| **Memory** | append-only recall, metabolism, compaction | durable experience |
| **Brain** | optional MIND, thoughts, intentions | bounded cognition |

**SignalBus (the connective tissue, provenance: Mantle OS architecture).** The eight organs
do not call each other directly; they mesh on a single **SignalBus** that carries reflexes —
deterministic and **fail-open**. It is the substrate, not a ninth organ: when the symbol
table (§E.3) classifies a `REFLEX`, that reflex *fires on the SignalBus*, and the Immune
organ turns every fault on the bus into an immune event rather than a silent failure.

### A.4 SELF/OTHER Rule

- Body owns identity proof and key material.
- MIND does not receive secret identity material.
- OTHER may be inspected only through quarantine and provenance.
- OTHER knowledge enters as inferred, not fact.
- OTHER code or microcode must never execute raw.
- Safe value from OTHER must be re-derived into SELF through the receiving Body's own gates.

### A.5 MIND Containment

- The MIND proposes; the Body applies.
- The MIND writes only to declared cognition surfaces such as `brain` or `thoughts`.
- The Body owns effects, memory writes, verification, immune actions, and final authority.
- Phase-2 fusion must never weaken Phase-1 reflexes.

---

## §B. APPAI-SPECIFIC POWER WORDS

These extend Core power words. Some Core words gain domain overlays here.

| Power word | Meaning in AppAI domain |
|---|---|
| `homeostasis` | Maintain stable Body operation before seeking clever improvement. |
| `eucatastrophe` | Seek a recovery path that preserves identity, evidence, and operator authority. |
| `hysteresis` | Account for memory and lineage: rebirth, drift, and past injury change current behavior. |
| `liminal` | Treat transitions such as fusion, reconstruction, anchoring, and cremation as high-risk gates. |
| `nociception` | Severe unresolved distress is a localized signal, not permission for unbounded action. |
| `calcify` | Harden only proven behavior into deterministic reflex. |
| `digest` | Convert foreign knowledge into SELF only through quarantine, trial, and provenance. |
| `SELF_OTHER` | Enforce identity boundary before trust. |
| `residency` | Preserve host independence while adding bounded AppAI presence. |
| `zombie_body` | Keep Phase 1 alive without MIND. |
| `veil` | Keep private, quarantined, or retired memory hidden from ordinary reads. |
| `seed` | Treat reconstruction material as high-risk, policy-gated identity substrate. |

---

## §C. APPAI MACRO ACTIVATORS

| Macro | Human meaning | Expands to | Binding |
|---|---|---|---|
| **Animare** | birth this AppAI | `ANIMARE` | certify Body before MIND |
| **Necromantia** | raise this existing app as a body | `NECROMANCY` | no host mutation before inventory gate |
| **Custodia** | guard the organism | Core `THREAT-MODEL` with AppAI overlays | no secret leakage, SELF/OTHER first |
| **Memoria** | inspect memory | `MEM-DIGESTION` or read-only memory review | provenance required |
| **Exorcizare** | quarantine unsafe OTHER | `MEM-DIGESTION` with adversarial stance | OTHER never executes raw |
| **Ossificare** | harden this learned skill | `SKILL-CALCIFICATION` | trial before reflex |
| **Resurgere** | rise again | `RESURGERE` | DNR, authority, budget gates first |
| **Cremare** | retire permanently | `CREMATION` | final unless policy permits resurrection |
| **Aegis** | shield and audit | `VITALS-CHECKUP + THREAT-MODEL` | non-destructive first |
| **Vocare** | call the MIND | `VOCARE` | readiness only until authorized fusion |
| **Silere** | sleep cognition | `METABOLIC-GOVERNANCE` | Body reflexes remain awake |
| **Sanare** | heal the Body | `VITALS-CHECKUP + ERROR-SWEEP` | diagnose before repair |
| **Codex** | read the cube, write to memory, learn the VCW | `VCW-LITERACY` | append-only; never overwrite, never put identity in the cube |

Extension macros refine Core macros only inside AppAI domain. They never weaken Core wards.

---

## §D. APPAI SPELLBOOK

### ANIMARE [V/J]

```yaml
spell_block:
  id: ANIMARE
  family: "V/J"
  purpose: "Grow a greenfield AppAI Body from declaration, certify Phase 1, and stop before MIND fusion."
  trigger:
      - "new AppAI"
      - "greenfield organism"
      - "birth from egg"
  stances:
      - grok
      - invariants
      - homeostasis
      - provenance
      - wu_wei
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  greenfield_sequence:
    - declaration
    - egg_or_body_plan
    - organ_manifests
    - band_plan
    - reflexes
    - stage1_gate
    - mind_readiness_report_only
  egg_schema:                         # verified: eggs/greeter.json, format "mantle-egg-v1"
    required: [identity.name, truths, commandments]
    optional: [identity.purpose, genome, reflexes, routines, controls, instincts]
    band_rule: "app bands declared in the egg live in heads 550-749"
    command: "python -m mantle hatch <egg.json> --out nest/  -> a malformed egg never hatches; the hatchery refuses with a reason"
  language_target:                    # greenfield is language-PARAMETRIC by declaration
    field: "the egg / §E.1 declaration carries TARGET_LANGUAGE + TARGET_RUNTIME"
    note: "ANIMARE grows a body from a declaration, so it does NOT dissect host source — there is no parser to make language-agnostic here. The target language is simply declared, and Phase-2 limbs/adapters are generated to it (same MIND-proposes / Body-applies pattern as NECROMANCY §language_agnostic)."
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### NECROMANCY [V/J]

```yaml
spell_block:
  id: NECROMANCY
  family: "V/J"
  purpose: "Raise an existing application as an audited AppAI Body without breaking host behavior."
  trigger:
      - "assimilate existing app"
      - "anchor host"
      - "zombie body"
      - "residency"
  stances:
      - grok
      - chesterton
      - invariants
      - blast-radius
      - provenance
      - wu_wei
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  pipeline:
    - N0_AUTHORITY: "Confirm operator authority, scope, budget, DNR policy, and companion Core loaded."
    - N1_GROK_HOST: "Read host code and docs without modification."
    - N2_DECLARATION: "Emit AppAI declaration block."
    - N3_INVENTORY_ORGAN_MAP: "Produce inventory and organ map; hard gate requires zero files modified."
    - N4_SYMBOL_CLASS: "Classify host symbols by organ role."
    - N5_BAND_PLAN: "Plan VCW bands and ownership."
    - N6_HOOKS: "Design fail-open additive hooks only after read-only sign-off."
    - N7_LIMBS: "Map controls/effectors, ControlBridge paths, and Action Execution Proofs."
    - N8_RESIDENCY: "Use dry-run, anchor, graft, or weave only under authority and do-no-harm."
    - N9_STAGE1_CERT: "Run Stage-1 certification and hard-fail table."
    - N10_MIND_READINESS_ONLY: "Report readiness; do not fuse MIND inside this spell."
    - N11_CAST_REPORT: "Emit full receipt and open issues."
  code_anchors:                       # verified against Mantle OS Gen-4 source
    command: "python -m mantle assimilate <host> --dry-run  -> scan -> map -> report, ZERO host writes"
    phase0_gate: "READ-ONLY sign-off; inventory must show 'Files modified so far: 0 (MUST be 0)'"
    phase5_hooks: "host behavior threaded ONLY after the Phase-0 sign-off is signed (assimilator/wrappers.py wrap/unwrap)"
    anchoring_law: "anchor never modifies one host file; the nest is additive ('.mantle/' only); a sha256 census of every host file proves it unchanged (mantle/anchor.py)"
    resident_loop: "anchor -> ask (free) / ask --mind (spends energy) -> feed --credits -> vitals; detach restores the host"
    maps_to: "N3 inventory = Phase 0 gate; N6/N8 hooks+residency = Phase 5+; HF-B42/HF-B40 enforce do-no-harm"
  language_agnostic:                  # PROPOSED forward design — current scanner.py is Python-AST-only
    problem: "Phase-0 dissection (mantle/assimilator/scanner.py) uses ast.parse — Python only. The role/organ model is language-NEUTRAL; only the PARSER is language-bound. Do not rewrite the classifier; replace the parser surface."
    four_phase_view:
      phase0_dissect: "read-only structure + I/O-boundary + call-graph extraction -> signed inventory; zero host changes (= the existing N1-N5 + Phase-0 gate)"
      phase1_mind_passover: "the MIND PROPOSES language-tailored transformation scripts from the inventory (idioms: async, callbacks, threading, build system). This is OTHER scaffolding generated at BUILD time — NOT runtime MIND fusion."
      phase2_body_applies: "a deterministic loop inserts fail-open hooks, grafts organ templates (SignalBus/Heart/Immune/Memory/Limbs), and wires generated adapters — additive, reversible, census-clean (= N6-N8)"
      phase3_certify: "Stage-1 (68 invariants + 3 tamper proofs + the host's own test suite + new organ contracts); Stage-2 only if fusion is requested (= N9-N10)"
      phase4_birth: "VCW seeded with the generated agent's source as self-knowledge (into discoveries/facts, provenanced) + the assimilation record; identity stays in the BODY (HF-B45). Heartbeat begins; the organism enters wake/stasis."
    binding_wards:                    # the proposal is sound ONLY under these
      - "Phase-1 LLM output is OTHER: reviewed, sandbox/trial-gated (HF-B51, HF-B47/HF-B48), re-derived into SELF before it ever runs (HF-OTHER). Generated code is never trusted raw."
      - "build-time code generation is NOT MIND fusion: no MIND writes to brain/thoughts at runtime; HF-MIND (fusion before Stage-1) still holds. The LLM is a script author, not the resident's mind."
      - "do-no-harm holds: where a language cannot be woven without editing host files, fall back to the graft WORKSPACE-COPY model so the host census stays byte-identical (HF-B40/HF-B42)."
    open_decision: "Phase 0 is deterministic and runs BEFORE the LLM, so non-Python dissection needs either (a) a multi-language parser (e.g. tree-sitter) for real ASTs, or (b) an agnostic surface scan (files/imports/I-O via patterns) with deep structure deferred to the Phase-1 MIND. Recommend (a) tree-sitter for fidelity, with (b) as a zero-dependency fallback."
    prototype: "RESOLVED to (a) and VALIDATED. `scanner_ts` (tree-sitter) dissects a JS host and emits the same {symbol, kind, line, role} records, REUSING `scanner.classify_symbol` unchanged. A JS twin of examples/sample_app produced an EXACT organ-map match {brain:1, heart:2, immune:2, limbs:2, memory:2, senses:1}; host bytes unchanged (read-only). Finding fed back into Phase 1: name-hints are snake_case-biased, so camelCase is normalized (camelCase->snake) before the neutral classifier runs. See scanner_ts_prototype.py + FINDINGS_multilang_scanner.md."
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### VITALS-CHECKUP [V]

```yaml
spell_block:
  id: VITALS-CHECKUP
  family: "V"
  purpose: "Run non-destructive AppAI diagnostics and report health, drift, and audit readiness."
  trigger:
      - "check nest"
      - "audit readiness"
      - "health report"
      - "diagnose body"
  stances:
      - fair_witness
      - provenance
      - invariants
      - nociception
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  diagnostic_protocol:
    - IDENTIFY: "Name target, authority, expected body state, and available artifacts."
    - SCAN: "Check cube/nest/source/ledger/hooks/surfaces without mutation."
    - DIAGNOSE: "Separate confirmed faults from suspected risks."
    - PRESCRIBE: "Recommend next safe spell; do not perform repair unless separately authorized."
    - RECEIPT: "Emit diagnostic report."
  default_checklist:
    - cube_integrity
    - ancestor_or_lineage_seal
    - genome_or_identity_fingerprint
    - ledger_coherence
    - host_byte_census
    - stage1_regression_readiness
    - tamper_proof_verification
    - ledger_nonnegative_starvation_law
    - docs_vs_code_coherence
    - hook_fail_open
    - secret_boundary
    - limb_proofs
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### MEM-DIGESTION [V/J]

```yaml
spell_block:
  id: MEM-DIGESTION
  family: "V/J"
  purpose: "Inspect foreign knowledge or memory artifacts, quarantine OTHER, and re-derive only safe useful parts."
  trigger:
      - "foreign VCW"
      - "MEM"
      - "shared knowledge"
      - "plasmid"
  stances:
      - adversary
      - provenance
      - digest
      - falsify
      - SELF_OTHER
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  foreign_artifact_law:
    - OTHER_is_never_executed_raw
    - quarantine_before_read
    - knowledge_enters_as_inferred
    - microcode_must_retrial_under_SELF
    - provenance_must_survive
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### SKILL-CALCIFICATION [V]

```yaml
spell_block:
  id: SKILL-CALCIFICATION
  family: "V"
  purpose: "Convert proven learned behavior into a bounded deterministic reflex only after sandbox and trial gates."
  trigger:
      - "calcify skill"
      - "promote instinct"
      - "hardening reflex"
  stances:
      - calcify
      - falsify
      - invariants
      - provenance
      - canary
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  calcification_gates:
    - static_sandbox
    - declared_capabilities
    - proving_cases
    - provenance
    - action_execution_proof
    - rollback_or_tombstone_plan
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### METABOLIC-GOVERNANCE [V]

```yaml
spell_block:
  id: METABOLIC-GOVERNANCE
  family: "V"
  purpose: "Control cognition, cost, wake frequency, and energy modes without hiding spend or starving critical reflexes."
  trigger:
      - "budget"
      - "API credits"
      - "cost"
      - "heartbeat"
      - "wake policy"
  stances:
      - homeostasis
      - hysteresis
      - descope
      - provenance
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  energy_modes:
    - SLEEP: "No cognition; Body reflexes only."
    - HEARTBEAT: "Scheduled low-frequency maintenance."
    - PAIN: "Event-gated wake for severe unresolved issue."
    - DIAGNOSTIC: "Bounded health analysis with explicit budget."
    - WAR_ROOM: "Human-authorized elevated spend and observation."
  symbiosis_ledger:                   # verified: mantle/symbiosis.py
    band: "append-only, hashed `symbiosis` band records GRANT (user fed credits; key NAMED, never stored raw), SPEND (every metered MODEL call), VALUE (work done, with evidence)"
    balance: "sum(GRANT) - sum(SPEND); computed, never stored"
    states: "FED (>25% of lifetime grants remain) | HUNGRY (low) | STARVING (0)"
    starvation_law: "a spend the balance cannot cover is REFUSED + logged as a `starvation` immune event; energy never goes negative; the MIND sleeps gracefully and the Body keeps beating -- a starved AppAI is a Zombie Body again, not a corpse"
    command: "python -m mantle feed <host> --credits=N  |  ask <host> (free) / ask --mind (spends)"
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### CREMATION [V/J]

```yaml
spell_block:
  id: CREMATION
  family: "V/J"
  purpose: "Retire, uninstall, or mark DNR for an AppAI body with authority, receipts, and no unauthorized resurrection."
  trigger:
      - "retire appai"
      - "uninstall"
      - "DNR"
      - "decommission"
  stances:
      - operator_authority
      - provenance
      - chesterton
      - fair_witness
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  retirement_controls:
    - verify_authority
    - record_DNR_policy
    - export_or_preserve_required_records
    - disable_reconstruction_policy
    - remove_or_archive_nest_by_policy
    - emit_final_receipt
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### VOCARE [V/J]

```yaml
spell_block:
  id: VOCARE
  family: "V/J"
  purpose: "Prepare or request MIND readiness only after Phase 1 certification; fusion itself requires separate operator authority."
  trigger:
      - "mind readiness"
      - "call mind"
      - "phase 2 preparation"
  stances:
      - invariants
      - provenance
      - liminal
      - operator_authority
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  readiness_rules:
    - stage1_must_pass_first
    - MIND_writes_only_to_declared_brain_thought_surfaces
    - Body_applies_actions
    - Phase1_reflexes_must_remain_unchanged
    - operator_authority_required_for_actual_fusion
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### RESURGERE [V/J]

```yaml
spell_block:
  id: RESURGERE
  family: "V/J"
  purpose: "Controlled reconstruction from authorized seed or source lineage, with DNR and budget gates before action."
  trigger:
      - "rebuild"
      - "restore"
      - "reconstruct"
      - "rise again"
  stances:
      - eucatastrophe
      - provenance
      - SELF_OTHER
      - operator_authority
      - canary
  domain_gate:
    required:
      - "Core Grimoire is loaded"
      - "AppAI domain is actually in scope"
      - "operator authority is clear"
    blocked_if:
      - "Core is absent"
      - "authority is absent"
      - "DNR or budget policy blocks action"
  goal:
    - "complete the spell purpose without violating Body-before-MIND"
    - "preserve host behavior and AppAI invariants"
  stop:
    - "goal is met"
    - "hard fail triggers"
    - "operator policy blocks continuation"
    - "receipt emitted"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
  reconstruction_gates:
    - authority_required
    - DNR_policy_must_permit
    - seed_or_source_lineage_verified
    - budget_policy_allows
    - no_stealth
    - stage1_recertification_required
  code_anchors:                       # verified against Mantle OS Gen-4 source
    seed_vault: "mantle/vault.py (M8): the seed (egg or graft diff) is stored SELF-encrypted in a veiled band -- unreadable as OTHER, so a copied nest in a different body cannot open it"
    reconstruct_is_birth: "`reconstruct` rebuilds through the hatchery, so the fresh body faces the SAME Stage-1 gate; a tampered seed cannot smuggle an uncertified body into the world"
    self_redesign: "mantle/compiler.py (M5): at a chosen rebirth the MIND PROPOSES a new genome; the BODY VALIDATES (encoding must be a registered driver, heads in range, no collisions) before rebirthing; the ancestor stays the readable ORACLE; inherited microcode RE-TRIALS before it re-calcifies"
    language_inheritance: "a seed that is a GRAFT (a diff against a host) re-applies the host weave on reconstruct, so RESURGERE inherits NECROMANCY's language-agnostic dissection (the same `scanner_ts` path). A seed that is a whole EGG carries its own TARGET_LANGUAGE and needs no host parser. Either way the rebuilt body faces the same Stage-1 gate."
```

**Cast body:** Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF under Body authority.

### VCW-LITERACY [V/J]

```yaml
spell_block:
  id: VCW-LITERACY
  family: "V/J"
  purpose: "Teach the agent to read, write, address, and metabolize a VCW cube — the durable, append-only, hash-verified memory an AppAI Body lives on."
  trigger:
      - "read a VCW cube"
      - "write to memory / a band"
      - "open a .vcw"
      - "what does the agent remember"
      - "persist or recall durable state"
  stances:
      - grok
      - invariants
      - provenance
      - idempotent
      - least-astonishment
  domain_gate:
    required:
      - "a cube, nest, or live organism is available (or is to be created)"
      - "scope can be bounded"
    blocked_if:
      - "the target band is ANCESTRAL (read-only) and the request is a write"
      - "the request would place identity/Primer in the cube (HF-B45)"
  goal:
    - "perform the smallest correct read/write against the cube, preserving the append-only stream"
    - "leave provenance on every write; never overwrite, never expose a veiled band without intent"
  stop:
    - "the read/write is done and verified"
    - "a ward blocks the action (then receipt the blocking ward)"
    - "evidence is insufficient to act safely"
  receipts:
      - authority
      - evidence
      - verification
      - domain_receipt
      - next_step
```

**Cast body:** Load the §E.9 field manual. Read before you write. Confirm the band, the generation (PRIME vs ancestral), and the veil. Append — never overwrite. Put provenance (`author`, `source`) on every entry, and never put identity in the cube. Verify with `recall`/`read` (and `verify_seals` on load). If a ward blocks you, stop and receipt it.

---

## §E. APPAI APPENDICES

### E.1 Declaration Block

```text
APPAI DECLARATION
TARGET_LANGUAGE      : <python | typescript | browser | other>
TARGET_RUNTIME       : <runtime and version>
HOST_PATH            : <path or repo>
TARGET_STORAGE       : <where nest / VCW / domain artifacts live>
BODY_MODE            : standard
VCW_FORMAT           : vcw-cube-png-v2
KEYFILE_PATH         : <Phase 2 only, if used>
DEFAULT_MODEL        : <Phase 2 only, if used>
BUDGET_POLICY        : <sleep | heartbeat | pain | diagnostic | war_room limits>
DNR_POLICY           : <none | retire_only | no_reconstruction | operator_defined>
AUTHORITY_SOURCE     : <operator / ticket / policy / signed request>
INTENTIONALLY_OMITTED: <organs, surfaces, or capabilities not grown + why>
SYNTAX_CONSTRAINTS   : <sandbox, no-eval, no-network, no-write, etc.>
```

### E.2 Organ Map & Inventory Template

```text
APP INVENTORY & ORGAN MAP

A. Host identity
- Name:
- Purpose:
- Language/runtime:
- Repo/root path:
- Entry points:
- Boot path:
- Build/run command:

B. Host invariants
- Behavior that must remain unchanged:
- Data that must not be exposed:
- Controls that must remain human-governed:
- Performance or availability expectations:

C. Surface-to-organ map
| Host surface | Present? | Location | Target organ | Notes |
|---|---|---|---|---|
| UI / editor / frontend | | | Senses + Limbs | |
| Execution / run engine | | | Heart + Limbs | |
| Credential / secret store | | | Immune | |
| Webhook / inbound routes | | | Senses | |
| Trigger / scheduler / cron | | | Senses + Heart | |
| AI / LLM nodes | | | Brain affordance | dormant until Phase 2 |
| Database / persistence | | | Memory | |
| CLI / server boot path | | | Heart | |
| Worker / queue / job mode | | | Limbs | |
| Frontend/backend boundary | | | Senses + Limbs | |
| Config / environment | | | Genome + Immune | |

D. Secret boundaries
| Boundary | Location | Secret kind | Redaction note |
|---|---|---|---|

E. Proposed band genome
| Band | Head | Span | Encoding | Purpose | Owner |
|---|---:|---:|---|---|---|

F. Human Surface Map
| Control / affordance | Location | ControlBridge feasible? | Proof plan |
|---|---|---|---|

G. Gap report
- Deprecated/dead code:
- Unclassifiable symbols:
- Un-instrumentable surfaces:
- Risks/blockers:

H. READ-ONLY SIGN-OFF
APP INVENTORY COMPLETE — NO HOST CODE MODIFIED
Host:
Inventory author:
Surfaces mapped: ___ / ___
Proposed genome drafted: yes/no
Secret boundaries identified: yes/no
Files modified so far: 0
Approved to instrument: yes/no, by, date
```

### E.3 Symbol Classification Table

| Role | Organ | Meaning |
|---|---|---|
| `REFLEX` | Senses | Pure deterministic reaction. |
| `ARM_ACTION` | Limbs | External action or effect. |
| `DISPLAY_RENDER` | Limbs | Human-visible output. |
| `STATE_TRANSITION` | Memory | Mutates app state. |
| `PERSISTENCE_WRITE` | Memory | Writes durable storage. |
| `SENSOR_EVENT` | Senses | Receives external input. |
| `HEARTBEAT` | Heart | Main loop, scheduler, tick, poll. |
| `MIND_AFFORDANCE` | Brain | Judgment point; dormant until Phase 2. |
| `SECRET_BOUNDARY` | Immune | Crosses credential or secret edge. |
| `ERROR_DEFENSE` | Immune | Validation, verification, retry, sanitize, guard. |
| `INTERNAL_UTILITY` | none | Helper; instrument only if touching surfaces above. |
| `DEPRECATED` | none | Dead code; record in gap report. |

The canonical role vocabulary is the `ROLES` tuple in `mantle/assimilator/scanner.py`
(verified Gen-4): `REFLEX, SENSOR_EVENT, ARM_ACTION, DISPLAY_RENDER, STATE_TRANSITION,
PERSISTENCE_WRITE, HEARTBEAT, MIND_AFFORDANCE, SECRET_BOUNDARY, ERROR_DEFENSE,
INTERNAL_UTILITY, DEPRECATED`. The scanner assigns a role deterministically by decorator,
then name hint, then call hint — defaulting to `INTERNAL_UTILITY`.

### E.4 Canonical Band Plan

| Band | Layers | Owning organ(s) | Writers |
|---|---:|---|---|
| agent genome | Body store | Genome | Body only; primer immutable |
| `prime` | 8-99 | Nervous System | Nervous System |
| `identity` | 100-149 | Memory | Memory |
| `facts` | 150-199 | Memory | Memory |
| `events` | 200-249 | Memory | Memory |
| `discoveries` | 250-299 | Memory | Memory |
| `senses` | 300-399 | Senses | Senses |
| `immune` | 400-449 | Immune | Immune |
| `brain` | 450-499 | Limbs + Brain | Limbs write NOTIFIED/COMPLETED; Brain writes INTENTION/DELEGATED |
| `thoughts` | 500-549 | Brain | Brain only; veiled |
| app bands | 550-749 | app organs + Limbs | declared owners only |
| tail | 750-799 | reserved | none unless declared by policy |

### E.5 Hook Runtime & Limb Doctrine

#### Fail-Open Hook List

| Hook | Binds to | Writes |
|---|---|---|
| `mantle_touch` | instrumented entry | lightweight access trace |
| `mantle_focus` | display render | App-Face focus |
| `mantle_display` | display render | declarative face render |
| `mantle_sense` | sensor event | classified senses entry |
| `mantle_state_write` | state transition | mirrored memory band entry |
| `mantle_persistence_write` | persistence write | memory band + tiering hook |
| `mantle_external_call` | action/effect | dispatch + Action Execution Proof |
| `mantle_error` | any fault | immune event, never re-raised into host by instrumentation |
| `mantle_immune` | immune scan | integrity findings |
| `mantle_resource` | heartbeat | resource event |
| `mantle_starvation` | heartbeat | energy starvation event |
| `mantle_dispatch_*` | limb dispatch | dispatch lifecycle records |
| `mantle_enter` | secret boundary enter | redacted enter event |
| `mantle_exit` | secret boundary exit | redacted exit event |

#### Hook Law

```text
1. Additive only.
2. Fail-open always.
3. Reversible by ledger.
4. Non-recursive display hooks.
5. Dual-flush persistence.
6. Import-compatible module and script launch.
7. Separate boot verifier.
8. Secret boundaries redacted before append-only memory.
```

#### Limb Dispatch Lifecycle

```text
INTENTION -> DELEGATED -> NOTIFIED -> COMPLETED
```

- Brain may author `INTENTION` and `DELEGATED` only after Phase 2.
- Body/Limbs own `NOTIFIED`, `COMPLETED`, and physical actuation.
- Authorship is immutable.
- Every action needs an Action Execution Proof.

#### Ganglia (parallel limbs)

(Provenance: Mantle OS Gen-4.) Limbs may be grown in parallel as **ganglia** — independent
effector clusters that act concurrently. Each ganglion is still a Limb: it inherits the full
dispatch lifecycle, its own Action Execution Proof per action, and the fail-open hook law.
Parallelism never grants new authority — a ganglion may not write to `brain`/`thoughts`,
may not bypass Stage-1 reflexes, and must not let one limb's failure cascade into another
(blast-radius). When multiple ganglia share a goal, govern them under the Core's §K
Convocation: one ledger, scoped leases, no silent widening.

#### Action Execution Proof Template

```yaml
action_execution_proof:
  action_id: ""
  attempted: true
  ok: false
  method: ""
  ref: ""
  reason: ""
  actor: "Body | MIND | operator | limb"
  authorship: ""
  timestamp: ""
  evidence: []
```

### E.6 Assimilation Hard Fails

| Code | Condition |
|---|---|
| HF-B42 | Host file modified before Phase-0 inventory gate was produced and signed. |
| HF-B32 | Hook can crash host instead of failing open. |
| HF-B33 | No dual-flush persistence. |
| HF-B34 | Import fails as module or script. |
| HF-B35 | Display hook re-enters own render path. |
| HF-B36 | Boot verifier is entangled with host startup or can crash it. |
| HF-B40 | Host behavior changed rather than additively instrumented. |
| HF-B41 | Inserted hook missing marker or ledger entry. |
| HF-B44 | Human-visible control lacks ControlBridge path or proof. |
| HF-MIND | MIND fusion attempted before Stage-1 certification. |
| HF-KEY | Identity proof, key boundary, or SELF verification unavailable where required. |
| HF-OTHER | OTHER artifact trusted, executed, or promoted raw. |
| HF-DNR | Reconstruction or persistence conflicts with DNR/retirement policy. |
| HF-BUDGET | Action exceeds authorized budget or hides cost. |

### E.7 Diagnostic Report Template

```text
APPAI DIAGNOSTIC REPORT

TARGET:
AUTHORITY:
SCOPE:
MODE: read-only | diagnostic | authorized repair
BUDGET POLICY:
DNR POLICY:

CHECKS:
| Check | Status | Evidence | Risk | Next |
|---|---|---|---|---|
| Cube integrity | | | | |
| Lineage / ancestor seal | | | | |
| Genome / identity fingerprint | | | | |
| Ledger coherence | | | | |
| Host byte census | | | | |
| Stage-1 regression readiness | | | | |
| Tamper-proof verification (audit catches violations) | | | | |
| Hook fail-open behavior | | | | |
| Secret boundary redaction | | | | |
| Limb proofs | | | | |
| Budget / energy state | | | | |
| DNR / retirement policy | | | | |

FINDINGS:
- Confirmed faults:
- Suspected risks:
- Blockers:
- Unknowns:

PRESCRIPTION:
- Recommended next spell:
- Required authority:
- Required evidence:
- Stop condition:

RECEIPT:
WHAT:
WHY:
EVIDENCE:
CONFIDENCE:
NEXT:
```

---

### E.8 Gen-4 Module ↔ Spell Coverage Map

Every Gen-4 module in `mantle/` is reachable through an existing spell or macro — verified
by reading the source. No new spell was required; the gaps were provenance and naming,
now closed. (Provenance: clone of `jodydugas-ctrl/mantle-os`, Gen-4.)

| Module (`mantle/…`) | Verified behavior | Spell / macro | Command(s) |
|---|---|---|---|
| `egg.py` · `hatchery.py` | Declarative birth from a `mantle-egg-v1` JSON; malformed eggs never hatch | **ANIMARE** / *Animare* | `mantle hatch <egg.json> --out nest/` |
| `assimilator/*` | Read-only AST dissection → organ map → Phase-0 sign-off; Phase-5+ fail-open wrappers | **NECROMANCY** / *Necromantia* | `mantle assimilate <host> --dry-run` |
| `anchor.py` · `symbiosis.py` | Residency in a `.mantle/` nest (host census-proven unchanged); energy economy GRANT/SPEND/VALUE | **NECROMANCY** + **METABOLIC-GOVERNANCE** / *Silere* | `mantle anchor <host>` · `feed --credits=N` · `ask [--mind]` |
| `graft.py` | R1 graft egg = non-destructive diff vs a named host (workspace copy; `GraftDrift` on source drift); R2 `weave()`/`unweave()` live reversible residency | **NECROMANCY** (graft) | `mantle graft <egg.json> <host>` |
| `mem.py` | M4 keyless plasmid: `excrete`/`digest`; OTHER knowledge → `discoveries` INFERRED; microcode sandbox-trialed then re-derived into SELF | **MEM-DIGESTION** / *Memoria*, *Exorcizare* | (library) |
| `ingestion.py` | Conversation distilled at Senses: DECISION→`facts` SOURCED, IDEA→`discoveries` INFERRED, COVENANT→Special Instruction | **MEM-DIGESTION** + *Memoria* (provenance discipline) | (library) |
| `compiler.py` | M5 self-redesigning genome at rebirth (Body validates drivers/heads/collisions); M6 host-native memory bridge → VCW keyvalue band | **RESURGERE** + NECROMANCY residency | (library) |
| `vault.py` | M8 seed vault: SELF-encrypted veiled seed; `reconstruct` rebuilds through the Stage-1 gate | **RESURGERE** / *Resurgere* (power word `seed`) | `mantle` reconstruct ceremony |
| `ganglia.py` | M7 parallel limbs writing progress into a reserved band; zero-token telemetry; crash → immune event | Limb doctrine §E.5 (Ganglia) + Core §K Convocation | (library) |
| `doctor.py` | Deployment checkup: cube-verify, ancestor-seals, genesis-key, ledger-nonnegative, docs-vs-code coherence | **VITALS-CHECKUP** / *Aegis*, *Sanare* | `mantle doctor <nest>` |
| `face.py` · `teach.py` | PNG self-portrait; the runnable Field Guide (17 chapters) | **VITALS-CHECKUP** (face) / `Intellige` (teach) | `mantle teach` |

Note the elegant cross-tie: `doctor.py`'s **docs-vs-code** gate (the README's invariant
count must equal the actual gate) is the AppAI-runtime expression of the Core's
`single_source_of_truth` rule — the docs may not silently drift from the code.

---

### E.9 The VCW Field Manual

> *Cast target of `VCW-LITERACY` (macro: **Codex**). Grounded in the Mantle OS source — the
> normative, runnable definition is `examples/vcw/vcw_cube.py` (pure standard library).*

#### What a cube is

The **VCW cube** — **Virtual Context Window**: the agent's **durable memory that lives
outside the prompt** — is the experiential memory of one generation: everything an AppAI has
sensed, done, learned, and thought.

- **cube** = an ordered stack of **800** square RGBA layers (index `0..799`).
- **layer** = one `800 × 800` RGBA image stored as a *real, valid PNG* (2,560,000 bytes) —
  the whole memory is a directory of pictures you can open in any viewer.
- **band** = a named, contiguous reserved *range* of layers, self-described by a boot sector.
- **entry** = one **immutable** record appended into a band, hashed over every non-volatile field.
- A `.vcw` file is just a **ZIP** of `layers/000.png … 799.png`.
- **Identity is NOT in the cube.** The Primer and commandments live in the *Body* and survive
  every rebirth (`HF-B45`: putting the Primer in the cube is a Stage-1 hard fail). The cube is
  pure experience. (See §E.4 for the canonical band genome and §A.3 for the organs.)

#### The standard bands (head / span)

| Band | Head | Span | Purpose | Veiled |
|---|---:|---:|---|---|
| `identity` | 100 | 50 | experiential self-state | |
| `facts` | 150 | 50 | durable truths (observed) | |
| `events` | 200 | 50 | event history | |
| `discoveries` | 250 | 50 | learned knowledge (inferred) | |
| `senses` | 300 | 100 | sensor intake | |
| `immune` | 400 | 50 | audit / defense | |
| `brain` | 450 | 50 | dispatch log | |
| `thoughts` | 500 | 50 | private reflection | ✓ |

App-specific bands live in heads **550–749** (matches §E.4).

#### The shape of an entry

```text
{ id, ts, opcode, author, source, content, tombstone, quarantined, hash }
```

- `id` — band-unique, monotonic, assigned at append, **never reused**.
- Extra fields (`authorship`, `verified`, `confidence`) live **inside** the hash — provenance is tamper-protected by construction.
- A **logical address** like `<facts.11>` is the index into the band's *visible* stream
  (tombstoned/quarantined entries excluded), so physical layer reuse never breaks a reference.

#### Reading a cube

```python
from mantle import Organism
org   = Organism.load("nest/", verify_seals=True)   # verify_seals catches a tampered ancestor
facts = org.memory.recall("facts")                  # -> list of visible entries
one   = org.resolve("<facts.11>")                   # resolve a logical reference

# low level, on the cube itself:
cube.read("facts")                       # visible entries of a band
cube.read("thoughts", reveal_private=True)  # a veiled band — only with explicit intent
cube.read("facts", ghosts=True)          # ONLY the deweighted/suppressed ghosts
```

#### Writing to a cube (append-only; PRIME generation only)

```python
org.memory.remember("facts", {"sky": "blue"}, opcode="WRITE")     # durable truth
org.sense({"action_id": "door", "event_type": "knock"})           # inbound, via Senses
cube.append("events", make_entry({"evt": "boot"}, opcode="EVENT"))# low-level append
```

- Writes go to the **PRIME** (current) generation **only**. Ancestral cubes are read-only — an
  append against them raises. The Senses organ is the *only* legitimate way in for inbound signals.
- You **never overwrite**. To remove something, you add a *new* event: deweight it (graded memory)
  or tombstone/quarantine it (immune). The original entry remains in the append-only stream.

#### Graded memory & metabolism

```python
org.memory.deweight("facts", entry_id, 0.0)   # hide without deleting (becomes a ghost)
org.memory.recall_ghosts("facts")             # inspect the suppressed
org.memory.compact("facts");  org.memory.dedupe("facts");  org.memory.metabolize("facts")
org.memory.promote_to_fact(discovery_entry)   # inferred discovery -> sourced fact, by gate
```

Under capacity pressure the Body **metabolizes** (compact, dedupe, reuse layers) — it never does
a lossy reset. *Metabolism before rebirth.*

#### Persist & verify

```python
org.save("nest/")
org2 = Organism.load("nest/", verify_seals=True)   # a tampered ancestor is detectable on load
```

#### Worked example (verified output)

`load → recall → remember → deweight → save`, run against the reference engine. Note how
`deweight` *hides without deleting* — the entry becomes a ghost, still in the append-only stream.

```python
from mantle import Organism
org = Organism.birth(identity={"name": "Demo.AppAI"},
                     truths=["if it is not in the VCW it did not happen"],
                     commandments=["protect your VCW", "you are a tool USER"])

org.memory.remember("facts", {"sky": "blue"},   opcode="WRITE")   # id 0
org.memory.remember("facts", {"grass": "green"}, opcode="WRITE")  # id 1

org.memory.recall("facts")
# -> [ {id:0, content:{'sky':'blue'},   author:'BODY', tombstone:False, hash:'349d647a…'},
#      {id:1, content:{'grass':'green'}, author:'BODY', tombstone:False, hash:'62fa5f28…'} ]

org.memory.deweight("facts", 0, 0.0)        # suppress id 0
org.memory.recall("facts")                  # -> [ {id:1, 'grass':'green'} ]   (id 0 hidden)
org.memory.recall_ghosts("facts")           # -> [ {id:0, 'sky':'blue'} ]      (still there)

import tempfile; d = tempfile.mkdtemp()
org.save(d)                                 # writes body.json, gen000.vcw, organism.json, self_seal.json
org2 = Organism.load(d, verify_seals=True)  # reload; a tampered ancestor would be caught
org2.memory.recall("facts")                 # -> [ {id:1, 'grass':'green'} ]   (ghost stays suppressed across save/load)
```

Every entry carries its own `id`, `author`, and tamper-evident `hash`; the suppressed entry
survives the round-trip as a ghost — nothing is ever destroyed.

#### The seven cube wards (memorize)

1. **Append before overwrite** — entries are immutable; suppression is a new event.
2. **Identity is never in the cube** (`HF-B45`).
3. **Ancestors are read-only and sealed** — only PRIME accepts writes.
4. **Veil before exposure** — private bands require `reveal_private` intent.
5. **Provenance on every write** — `author` + `source`, hash-protected; *inferred ≠ fact*.
6. **Metabolism before rebirth** — relieve pressure by compaction, never by loss.
7. **A foreign cube is OTHER** — a `.vcw` you did not author is studied (digest, §D MEM-DIGESTION), never trusted or executed raw.

#### Format constants (for tooling)

`SIDE = 800`, `CHANNELS = 4 (RGBA)`, `800` layers, layer magic `b"VCWPNG2\n"`, JSON serialized
**compact + sorted** (`separators=(",", ":")`, `sort_keys=True`). Byte addressing inside a layer:
`offset = (y * SIDE + x) * CHANNELS`. The runnable normative spec is `examples/vcw/vcw_cube.py`
(`selftest` proves every rule), and the production engine is `mantle/vcw/cube.py` — the two are
byte-interoperable, proven in CI.

---

### E.10 Worked Walkthrough — Residency (`assimilate → anchor → feed → doctor`)

A full do-no-harm residency, end to end, against a sample host. Every step below was run
against the reference engine; output is trimmed but faithful. The ceremony casts
**NECROMANCY** (dissect + anchor), **METABOLIC-GOVERNANCE** (feed/energy), and
**VITALS-CHECKUP** (doctor) in sequence — the host is never modified.

**Step 1 — `assimilate --dry-run` (Phase 0: read-only dissection).**

```text
$ python -m mantle assimilate examples/sample_app --dry-run

  Python files scanned : 1
  Symbol roles : {ARM_ACTION:1, DISPLAY_RENDER:1, ERROR_DEFENSE:1, HEARTBEAT:2,
                  MIND_AFFORDANCE:1, PERSISTENCE_WRITE:1, SECRET_BOUNDARY:1,
                  SENSOR_EVENT:1, STATE_TRANSITION:1}
  THE ORGAN MAP (host tissue -> organs):
    heart  2  on_timer_tick, main_loop
    senses 1  handle_create_note
    limbs  2  send_notification, render_note_list
    memory 2  set_note, save_notes
    immune 2  validate_note, check_auth_token
    brain  1  suggest_tags_with_llm
  Host files modified : 0  (Phase 0 is read-only; hook insertion only after the
                            APP_INVENTORY sign-off — HF-B42.)
```

The symbol roles match §E.3 exactly (note `HEARTBEAT` and `ERROR_DEFENSE`). Nothing is written.

**Step 2 — `anchor` (birth a resident in a `.mantle/` nest, host census-verified).**

```text
$ python -m mantle anchor /tmp/host

  resident      : Host.Resident
  organ map     : {heart:2, senses:1, limbs:2, memory:2, immune:2, brain:1}
  host files    : 1  -- unchanged: True  (census-verified, byte for byte)
  certified     : True  (the same Stage-1 gate every Body faces)
  starter energy: 5.0 credits
  nest          : /tmp/host/.mantle
```

The host is proven byte-identical; the resident passed Stage-1; it starts with 5 credits.

**Step 3 — `feed` (the symbiotic loop: grant energy).**

```text
$ python -m mantle feed /tmp/host --credits=20
fed. balance=25.0 credits (FED) · lifetime granted=25.0 · value delivered: 1 record(s)

$ python -m mantle vitals /tmp/host
state : FED   balance=25.0 / granted=25.0 credits   keys=none
immune log : 0 event(s)
```

Balance is `sum(GRANT) - sum(SPEND)` = 25.0, state **FED** (see the §D `symbiosis_ledger`).

**Step 4 — `doctor` (deployment checkup).**

```text
$ python -m mantle doctor /tmp/host/.mantle      # NOTE: point at the nest, not the host root

  [OK] cube-verify
  [OK] ancestor-seals
  [OK] genesis-key
  [OK] ledger-nonnegative  balance=25.00
  [OK] docs-vs-code        README claims 68; the gate has 68
  HEALTHY.
```

All five gates green, including the **docs-vs-code** coherence gate (§D `VITALS-CHECKUP`).

> **Gotcha:** `doctor` takes the **nest** path (`<host>/.mantle`), while `anchor`, `feed`,
> and `vitals` take the **host** path. Pointing `doctor` at the host root raises
> `FileNotFoundError: organism.json` — it is looking for the nest's manifest.

> **Naming note (fair_witness):** the reference CLI still banners the assimilator as
> "ARGONAUT OS" / "Host.Resident" — the Argonaut line the Gen-4 tissue was grown on. The
> behavior is the Mantle OS NECROMANCY path; the banner is cosmetic lineage.

---

### E.11 The Three Growth Paths & the Shared Language-Agnostic Substrate

There are three ways to grow an AppAI. Two declare a body; one raises an existing one. Only
the paths that **dissect host source** need the multi-language parser — and they now share one
(`scanner_ts`, tree-sitter, validated in §D NECROMANCY `language_agnostic.prototype`).

| Path | Spell | How it grows | Dissects host source? | Language handling |
|---|---|---|---|---|
| **Seed (greenfield)** | `ANIMARE` | Declares a whole body from an egg (`mantle-egg-v1`) | No | `TARGET_LANGUAGE` is **declared**; limbs/adapters generated to it |
| **Assimilate / raise** | `NECROMANCY` | Dissects an existing app, maps organs, weaves fail-open hooks | **Yes** | `scanner_ts` (tree-sitter) → same `{symbol,kind,line,role}` records; neutral classifier reused |
| **Graft** | `NECROMANCY` (graft egg) | Non-destructive diff against a named host, woven in a workspace copy | **Yes** | same `scanner_ts` path; census-clean |
| **Reconstruct (seed vault)** | `RESURGERE` | Rebuilds from a stored seed (egg or graft) | Only if the seed is a graft | inherits the assimilate path; egg seeds carry their own `TARGET_LANGUAGE` |

**The shared substrate.** For every path that reads host code, the rule is identical: the
role/organ model is language-NEUTRAL; **only the parser is language-bound.** Swap the parser
(`scanner_ts`), reuse `classify_symbol`, normalize idioms (camelCase→snake) at the Phase-1
boundary — and the organ map comes out the same across languages. Every path still ends at the
**same Stage-1 gate** (68 invariants + tamper proofs), and every path obeys the three binding
wards: build-time LLM output is OTHER (gated, never trusted raw), it is not MIND fusion
(HF-MIND holds), and do-no-harm holds (graft workspace-copy where in-place would touch host
bytes).

---

## §F. REVISION LEDGER

Receipt of this chapter's self-audit — `DOC-SWEEP` cast on the AppAI extension, with gaps filled from the Mantle OS Gen-4 reference the operator supplied. Wards held: every addition is additive, sourced, and marked with provenance; no spell, gate, hard-fail, or authority rule was weakened.

```text
RECEIPT — v1.1 self-audit (AppAI domain)
WHAT:
  - §A.2: added "Concrete certification gates" — named the Stage-1 (Zombie Body) gate,
    the enumerated security invariants (36 -> 68 in the reference; count is runtime-defined),
    the Stage-2 gate that re-runs every Stage-1 row, and the tamper proofs (audit must
    CATCH violations). Previously "Stage-1 certification" was used without definition.
  - §A.3: added the SignalBus as the deterministic, fail-open reflex bus connecting the
    eight organs — substrate, not a ninth organ — reconciling the §E.3 `REFLEX` row with
    where reflexes actually fire.
  - §E.5: added "Ganglia (parallel limbs)" — concurrent effector clusters that inherit the
    full Limb contract and gain no new authority; governed under Core §K Convocation.
  - §D VITALS-CHECKUP and §E.7: added a `tamper_proof_verification` check / report row.
  - Version bumped to 1.1; schema_version kept at grimoire-appai-domain-1.0 (contract
    unchanged); `requires: grimoire-core-3.0` is unaffected by the Core's v3.1 editorial
    revision since that revision left the contract intact.
WHY:
  - The chapter modeled Mantle behavior but under-specified its named gates and omitted
    two real Gen-4 concepts (SignalBus, ganglia). Naming them gives the Caster concrete,
    citable evidence and closes gaps without changing doctrine.
EVIDENCE:
  - Mantle OS README (operator-supplied repo): Stage-1/Stage-2 gates, 68 invariants, the
    three tamper proofs, the SignalBus in the architecture diagram, and ganglia/parallel
    limbs in the Gen-4 module list.
CONFIDENCE:
  - high for additions traceable to the README; medium on the exact invariant count, which
    is therefore stated as runtime-defined rather than hard-coded.
NEXT:
  - Optional future pass: map remaining Gen-4 tissue (eggs/hatchery, anchor/symbiosis,
    grafts, plasmids, seed vault) explicitly onto existing spells, and verify the Grimoire's
    gates against the actual `mantle/` code rather than the README.
```

```text
RECEIPT — v1.2 self-audit (AppAI domain, verified against source)
WHAT:
  - Cloned jodydugas-ctrl/mantle-os and checked the chapter against the running code.
  - §A.2: upgraded the invariant claim from "runtime-defined" to the VERIFIED 68/68 green
    (`python -m mantle prove`; `mantle/audits/invariants.py` TESTS table). Kept it
    version-bound, not eternal.
  - §A.3 / §E.3: confirmed the 8-organ tuple and SignalBus-as-substrate against
    `mantle/audits/stage1.py` (ORGANS = heart, genome, nervous, senses, immune, limbs,
    memory, brain). Added two real symbol roles the chapter was missing — `HEARTBEAT`
    (Heart) and `ERROR_DEFENSE` (Immune) — and cited the canonical `ROLES` tuple in
    `assimilator/scanner.py`.
  - NECROMANCY: added `code_anchors` tying the abstract N0-N11 pipeline to the real path —
    `assimilate --dry-run` (scan->map->report, zero writes), the Phase-0 READ-ONLY sign-off
    ("Files modified: 0 MUST be 0"), Phase-5+ hooks via `wrappers.py`, and the anchoring law
    + sha256 host census from `mantle/anchor.py`. Confirms HF-B42/HF-B40 match reality.
  - ANIMARE: added `egg_schema` verified from `eggs/greeter.json` / `mantle/egg.py`
    (format "mantle-egg-v1"; required identity.name/truths/commandments; app bands 550-749;
    `mantle hatch`).
WHY:
  - The v1.1 additions were README-sourced; this pass grounds them in executable source,
    correcting the one soft claim (invariant count) and closing the symbol-role gap.
EVIDENCE:
  - Live run: "68/68 invariants green". Source files cited inline above.
CONFIDENCE:
  - high. Counts and names are from a clean clone and a passing `prove` run.
NEXT:
  - Remaining Gen-4 modules (symbiosis energy economy, compiler/host-memory bridge, vault,
    ingestion, ganglia internals) are present in `mantle/` and could each get a one-line
    spell mapping if the operator wants full coverage.
```

```text
RECEIPT — v1.3 self-audit (AppAI domain, full Gen-4 module sweep)
WHAT:
  - Read every remaining Gen-4 module and added §E.8 "Gen-4 Module ↔ Spell Coverage Map":
    egg/hatchery, assimilator, anchor/symbiosis, graft, mem, ingestion, compiler, vault,
    ganglia, doctor, face/teach — each mapped to an existing spell/macro with the verified
    command. Result: full coverage with NO new spell required.
  - METABOLIC-GOVERNANCE: added the verified `symbiosis_ledger` (GRANT/SPEND/VALUE,
    computed balance, FED/HUNGRY/STARVING, the Starvation Law) from `mantle/symbiosis.py`.
  - RESURGERE: added `code_anchors` from `vault.py` (M8 self-encrypted seed; reconstruct
    rebuilds through Stage-1) and `compiler.py` (M5 Body-validated self-redesign genome).
  - VITALS-CHECKUP: added `ledger_nonnegative_starvation_law` and `docs_vs_code_coherence`
    checks, mirroring `doctor.py`'s real gate set.
WHY:
  - Closes the v1.2 "NEXT" item. Confirms the spellbook already spans the whole organism;
    the only work was grounding and naming, done under the same additive, sourced wards.
EVIDENCE:
  - Source headers/docstrings of all ten+ modules read directly from a clean clone;
    `doctor.py` docs-vs-code gate corroborates the live 68/68 prove run.
CONFIDENCE:
  - high for the mappings and named behaviors. Library-only modules (mem, ingestion,
    compiler, ganglia) expose no CLI subcommand; marked "(library)" rather than inventing one.
NEXT:
  - The chapter now covers Gen-4. A future pass could add worked end-to-end examples
    (e.g. a full assimilate→anchor→feed→doctor walkthrough) if you want a tutorial layer.
```

```text
RECEIPT — v1.4 (AppAI domain) — receive VCW-LITERACY from the Core
WHAT:
  - Added the `VCW-LITERACY` spell (§D), the `Codex` macro (§0 + §C), the §0 spell-registry
    entry, and the §E.9 VCW Field Manual — relocated wholesale from Book 1 at operator request.
  - The manual teaches: what a cube is, the standard bands (cross-linked to §E.4), the entry
    shape, read/write/address/metabolize APIs, the seven cube wards, and the format constants.
WHY:
  - Operator decision: an agent that needs the VCW should load the whole AppAI chapter and be
    fully versed. VCW literacy is Body doctrine and belongs here, beside the organ chart, the
    band genome (§E.4), and MEM-DIGESTION (foreign cubes).
EVIDENCE:
  - Content grounded in the Mantle OS source (`examples/vcw/vcw_cube.py`, `mantle/vcw/*`,
    `mantle/core/organism.py`, `mantle/organs/memory.py`). The Core's §L records the move out.
CONFIDENCE:
  - high. Pure relocation; the Core is restored to a clean universal baseline and now points
    here for VCW literacy.
NEXT:
  - Optional: a worked end-to-end example (load -> recall -> remember -> deweight -> save).
```

```text
RECEIPT — v1.5 (AppAI domain) — worked walkthroughs, run against the engine
WHAT:
  - §E.9: added a "Worked example (verified output)" — load -> recall -> remember ->
    deweight -> save — showing deweight hides-without-deleting (the ghost survives save/load).
  - §E.10: added a residency walkthrough — assimilate --dry-run -> anchor -> feed -> doctor —
    with faithful (trimmed) output from a real run on examples/sample_app.
  - Documented two real gotchas: `doctor` takes the NEST path (.mantle) not the host root;
    and the CLI banners "ARGONAUT OS / Host.Resident" (the Argonaut lineage) — cosmetic.
WHY:
  - Clears both pinned items. Examples are executable truth, not description, so an agent can
    follow them verbatim.
EVIDENCE:
  - All commands and the Python snippet were executed in a clean clone; outputs (organ map,
    census unchanged=True, balance=25.0 FED, five green doctor gates, entry ids/ghosts) are
    reproduced from the actual runs.
CONFIDENCE:
  - high. Verified by execution. Output trimmed for readability; semantics unchanged.
NEXT:
  - None outstanding. The grimoire pair is self-consistent and code-verified through Gen-4.
```

```text
RECEIPT — v1.6 (AppAI domain) — language-agnostic NECROMANCY (operator proposal)
WHAT:
  - Grokked + red-teamed the operator's 4-phase multi-language assimilation proposal and
    added a `language_agnostic` block to the NECROMANCY spell: the four-phase view mapped to
    the existing N0-N11 pipeline, three binding wards, and the one open design decision.
ASSESSMENT (Speculum / RED-TEAM-DIALECTIC):
  - SOUND. The core insight is correct and verified: scanner.py is Python-AST-only, but the
    role/organ model is language-neutral — only the PARSER is language-bound. The proposal's
    best idea is to NOT write N parsers: let the MIND generate language-tailored transformation
    scripts (Phase 1) that the deterministic Body applies (Phase 2). This respects MIND-proposes
    / Body-applies.
  - CONSTRAINED. It is compatible with the wards ONLY if: (1) Phase-1 LLM output is treated as
    OTHER — sandbox/trial-gated, re-derived into SELF before running; (2) build-time codegen is
    NOT MIND fusion (HF-MIND still bars fusion before Stage-1); (3) do-no-harm holds via the
    graft workspace-copy where in-place weaving would touch host files. All three are now recorded.
  - OPEN: Phase 0 runs before the LLM, so non-Python *dissection* still needs a parser. Flagged
    the tree-sitter (fidelity) vs agnostic-surface-scan (zero-dep) decision rather than pretending
    the LLM solves Phase 0.
WHY:
  - The proposal genuinely advances NECROMANCY toward any-language hosts without weakening a
    single gate; capturing it as gated doctrine (not as a claim the code already does it) is the
    honest, useful application.
EVIDENCE:
  - scanner.py `ast.parse` / FunctionDef walk (Python-only) confirmed in the clone; role vocab
    in `ROLES`; do-no-harm census in anchor.py; HF-MIND/HF-OTHER/HF-B40/B42 in §E.6.
CONFIDENCE:
  - high on the assessment; the block is explicitly marked PROPOSED/forward-design, not shipped.
NEXT:
  - If you want code: prototype a tree-sitter-backed scanner that emits the same
    {symbol, kind, line, role} records for a non-Python host, behind the same Phase-0 gate.
```

```text
RECEIPT — v1.7 (AppAI domain) — language-agnostic substrate across ALL growth paths
WHAT:
  - Propagated the new system to every way of growing an AppAI:
    * ANIMARE (seed/greenfield): added `language_target` — greenfield does NOT dissect; the
      egg/§E.1 declaration carries TARGET_LANGUAGE; limbs/adapters are generated to it.
    * NECROMANCY (assimilate + graft): marked the `open_decision` RESOLVED + VALIDATED — the
      tree-sitter `scanner_ts` prototype hit EXACT organ parity on a JS host, classifier reused.
    * RESURGERE (seed-vault reconstruct): added `language_inheritance` — a graft seed re-applies
      the host weave and inherits the assimilate parser path; an egg seed declares its own language.
  - Added §E.11, a growth-paths overview table tying all four entries (seed / assimilate / graft /
    reconstruct) to the one shared rule: only the parser is language-bound; the classifier is neutral.
WHY:
  - Operator request: all growth methods should reflect the language-agnostic system, not just
    NECROMANCY. The substrate is genuinely shared — every host-dissecting path uses one scanner.
EVIDENCE:
  - scanner_ts prototype run (this session): JS organ map == Python organ map, host bytes unchanged.
  - egg TARGET_LANGUAGE in §E.1; graft/weave + census in §D code_anchors and anchor.py.
CONFIDENCE:
  - high. Doctrine mirrors the verified prototype; greenfield correctly excluded from parsing.
NEXT:
  - Ship to the repo: route scan_project by extension into scanner_ts + add a parity test (see the
    GitHub patch prepared this session).
```

---

## END LAW FOR APPAI OPERATORS

Raise nothing without authority. A Body must live without a MIND. A MIND may only extend. OTHER may teach, never rule. SELF must be proved. The diagnostic spell reports; the Caster heals. Stage 1 must be certified before MIND readiness. Cremation is final unless policy permits resurrection.
