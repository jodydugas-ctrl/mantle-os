# APPAI CHAPTER

## Companion to the Grimoire (the chapter)

**Version:** 1.0.0
**File:** `The Grimoire AppAI Chapter.md`  
**Audience:** LLM agents, AppAI builders, Mantle-style runtimes, and agent orchestrators.  
**Purpose:** Domain-specific spells for AppAI work: birth, assimilation, residency, memory, limbs, diagnostics, metabolism, controlled reconstruction, and retirement.

---

## PREREQUISITE & EXTENSION RULE

This file extends the Core Grimoire (Version 1.0.0, `The Grimoire.md`). Load the Core first. This project is exactly two files: the Grimoire (book) and this AppAI Chapter.

**Version lock:** the Grimoire and the AppAI Chapter are version-locked — they always carry the same version number. Advancing either advances both; a version bump to one re-stamps the other to match in the same pass, even if its content did not otherwise change. The Core's `CONCORD` spell performs and verifies this lock. Current version: **1.0.0**.

If the Core is missing, refuse AppAI mutation and operate only in `Intellige` mode: read, model, explain, and stop. Do not assimilate, hook, graft, anchor, fuse, reconstruct, cremate, or modify.

AppAI macros inherit the Core's Prerequisite Autocast Rule. Where a domain spell requires intimate comprehension of its target — for example `NECROMANCY` reading a host, or `MEM-DIGESTION` inspecting a foreign artifact — the agent auto-casts `Intellige` on that target first if it has not already been done this session, rather than asking the operator to do so. This is read-only and never weakens Core or AppAI wards.

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
7. §F Project Map — `mantle-os` reference implementation
8. End Law

---

## §0. MACHINE-READABLE DOMAIN REGISTRY

```yaml
schema_version: grimoire-appai-domain-1.0.0
kind: domain_extension
requires: grimoire-core-1.0.0
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
    purpose: "guard AppAI boundaries, authority, and cast compliance"
    expands_to: {spell: GUARDIAN-REVIEW, overlay: appai_guardian_overlay, stances: [fair_witness, adversary, provenance, falsify, invariants, SELF_OTHER]}
    binding: "Custodia remains one macro. AppAI adds domain gates as an overlay; it does not create a second Custodia-like command. Use Aegis when a separate threat-model pass is needed."
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
appai_power_registry:
  nociception: "Treat severe unresolved Body distress as a localized wake signal."
  calcify: "Promote only proven behavior into deterministic reflex."
  digest: "Quarantine OTHER, inspect it, and re-derive safe value into SELF."
  SELF_OTHER: "Distinguish Body-proved SELF from all foreign OTHER artifacts."
  residency: "Operate as a bounded resident of a host without breaking the host."
  zombie_body: "A certified Phase-1 Body alive without a MIND."
  veil: "Hide private, quarantined, or tombstoned memory from ordinary reads."
  seed: "Minimal authorized identity or reconstruction material, policy-gated."
appai_guardian_overlay:
  inherits: "Core GUARDIAN-REVIEW"
  principle: "In AppAI work, Guardian review must additionally protect Body-before-MIND, SELF/OTHER boundaries, host behavior, budget/DNR policy, and Action Execution Proofs."
  required_for:
    - "MIND readiness or fusion decisions"
    - "host hooks, grafts, anchors, or residency changes"
    - "OTHER digestion or skill calcification"
    - "limb/effectful actions"
    - "reconstruction, cremation, DNR, budget, or identity operations"
  appai_gates:
    - body_before_mind
    - self_other_boundary
    - host_preservation
    - action_execution_proof
    - dnr_budget_authority
    - lineage_and_seed_provenance
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

### A.6 AppAI Guardian Overlay

Core `GUARDIAN-REVIEW` applies to all AppAI casts that are high-risk, effectful, authority-sensitive, or verification-claiming. In this chapter, **Custodia** means: first audit Grimoire compliance, then audit AppAI boundary law.

The AppAI Guardian asks:

```text
Did the Caster obey the Grimoire, and did the cast preserve the organism's lawful boundaries?
```

Required AppAI checks:

```yaml
appai_custodia_checks:
  body_before_mind:
    - Phase 1 remains deterministic
    - MIND does not apply effects directly
    - MIND readiness is not treated as fusion authority
  self_other_boundary:
    - OTHER is quarantined before trust
    - OTHER code or microcode is not executed raw
    - safe value is re-derived into SELF
  host_preservation:
    - hooks are additive, fail-open, and reversible
    - host behavior is preserved unless explicitly authorized and verified
  action_execution_proof:
    - every limb/effectful action has actor, method, result, reason, and evidence
  authority_and_policy:
    - operator authority, DNR policy, and budget policy are explicit
    - identity, seed, or reconstruction material has provenance
```

AppAI Custodia may return PASS, REVISE, HALT, or ESCALATE. ESCALATE is required when fusion, destructive retirement, resurrection, host behavior change, budget expansion, or unresolved SELF/OTHER trust depends on operator judgment.

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
| **Custodia** | guard the organism and audit the cast | Core `GUARDIAN-REVIEW` with AppAI Guardian Overlay | single macro; no secret leakage, SELF/OTHER first, Body-before-MIND |
| **Memoria** | inspect memory | `MEM-DIGESTION` or read-only memory review | provenance required |
| **Exorcizare** | quarantine unsafe OTHER | `MEM-DIGESTION` with adversarial stance | OTHER never executes raw |
| **Ossificare** | harden this learned skill | `SKILL-CALCIFICATION` | trial before reflex |
| **Resurgere** | rise again | `RESURGERE` | DNR, authority, budget gates first |
| **Cremare** | retire permanently | `CREMATION` | final unless policy permits resurrection |
| **Aegis** | shield and audit | `VITALS-CHECKUP + THREAT-MODEL` | non-destructive first |
| **Vocare** | call the MIND | `VOCARE` | readiness only until authorized fusion |
| **Silere** | sleep cognition | `METABOLIC-GOVERNANCE` | Body reflexes remain awake |
| **Sanare** | heal the Body | `VITALS-CHECKUP + ERROR-SWEEP` | diagnose before repair |

Extension macros refine Core macros only inside AppAI domain. They never weaken Core wards.

Command surface rule: AppAI inherits the Core rule that Latin Title Case names are the stable human-facing macro layer, lowercase power words are internal stances, and UPPERCASE spell identifiers are procedural labels. AppAI must not create near-duplicate commands for Core macros. If a Core macro needs AppAI behavior, this chapter supplies an overlay under the same macro or uses a clearly distinct Latin macro such as Aegis.

---

## §D. APPAI SPELLBOOK

### Default Spell Envelope (applies to every AppAI spell unless overridden)

Every spell block below inherits this envelope by reference (`inherits: appai_default_spell_envelope`).

```yaml
appai_default_spell_envelope:
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
      - guardian_decision_when_required
      - next_step
```

**Universal AppAI cast body (applies to every spell unless the block states its own):**
Run the domain gate first. Preserve Phase 1 determinism. Treat the MIND as bounded and
optional. Treat OTHER as evidence only until digested, verified, and re-derived into SELF
under Body authority.

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
  inherits: appai_default_spell_envelope
  greenfield_sequence:
    - declaration
    - egg_or_body_plan
    - organ_manifests
    - band_plan
    - reflexes
    - stage1_gate
    - mind_readiness_report_only
```

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
  inherits: appai_default_spell_envelope
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
```

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
  inherits: appai_default_spell_envelope
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
    - hook_fail_open
    - secret_boundary
    - limb_proofs
```

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
  inherits: appai_default_spell_envelope
  foreign_artifact_law:
    - OTHER_is_never_executed_raw
    - quarantine_before_read
    - knowledge_enters_as_inferred
    - microcode_must_retrial_under_SELF
    - provenance_must_survive
```

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
  inherits: appai_default_spell_envelope
  calcification_gates:
    - static_sandbox
    - declared_capabilities
    - proving_cases
    - provenance
    - action_execution_proof
    - rollback_or_tombstone_plan
```

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
  inherits: appai_default_spell_envelope
  energy_modes:
    - SLEEP: "No cognition; Body reflexes only."
    - HEARTBEAT: "Scheduled low-frequency maintenance."
    - PAIN: "Event-gated wake for severe unresolved issue."
    - DIAGNOSTIC: "Bounded health analysis with explicit budget."
    - WAR_ROOM: "Human-authorized elevated spend and observation."
```

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
  inherits: appai_default_spell_envelope
  retirement_controls:
    - verify_authority
    - record_DNR_policy
    - export_or_preserve_required_records
    - disable_reconstruction_policy
    - remove_or_archive_nest_by_policy
    - emit_final_receipt
```

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
  inherits: appai_default_spell_envelope
  readiness_rules:
    - stage1_must_pass_first
    - MIND_writes_only_to_declared_brain_thought_surfaces
    - Body_applies_actions
    - Phase1_reflexes_must_remain_unchanged
    - operator_authority_required_for_actual_fusion
```

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
  inherits: appai_default_spell_envelope
  reconstruction_gates:
    - authority_required
    - DNR_policy_must_permit
    - seed_or_source_lineage_verified
    - budget_policy_allows
    - no_stealth
    - stage1_recertification_required
```


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
| `MIND_AFFORDANCE` | Brain | Judgment point; dormant until Phase 2. |
| `SECRET_BOUNDARY` | Immune | Crosses credential or secret edge. |
| `INTERNAL_UTILITY` | none | Helper; instrument only if touching surfaces above. |
| `DEPRECATED` | none | Dead code; record in gap report. |

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

## §F. PROJECT MAP — `mantle-os` REFERENCE IMPLEMENTATION

This chapter's doctrine is implemented and demonstrated in the **Mantle OS** project. The repo is the working reference: every spell below has real, runnable code and examples there.

- Repository: `https://github.com/jodydugas-ctrl/mantle-os` (branch `main`).
- Acquire tool-free (no GitHub API or token needed): `git clone https://github.com/jodydugas-ctrl/mantle-os.git` — see the Core's `PARITY-CLONE` / `Replicare` for acquisition doctrine.
- Python package root: `src/mantle/`. CLI entry: `python -m mantle <command>` (`src/mantle/cli.py`, `src/mantle/demos.py`).

### F.1 Spell → implementation

| Spell | Primary code | Docs / examples / CLI |
|---|---|---|
| `ANIMARE` (birth from egg) | `src/mantle/egg.py`, `src/mantle/hatchery.py`, eggs in `examples/eggs/*.json` | `documents/guides/Organism_Lifecycle.md`; CLI `hatch` |
| `NECROMANCY` (assimilate / anchor a host) | `src/mantle/assimilator/` (`scanner.py`, `scanner_ts.py`, `organ_map.py`, `report.py`, `wrappers.py`), `src/mantle/anchor.py`, `src/mantle/graft.py`, `src/mantle/symbiosis.py` | `Mantle_Assimilator.md`, `documents/guides/Assimilation_Guide.md`; `examples/sample_app/`; CLI `anchor`, `graft` |
| `VITALS-CHECKUP` (diagnostics) | `src/mantle/doctor.py`, `src/mantle/audits/` (`stage1.py`, `invariants.py`) | `documents/guides/Audit_Guide.md`, `Mantle_Part1_Body_Audit.md`; CLI `vitals`, `doctor` |
| `MEM-DIGESTION` (ingest / quarantine OTHER) | `src/mantle/ingestion.py`, `src/mantle/mem.py`, `src/mantle/vcw/metabolism.py`, `src/mantle/core/redact.py`, `src/mantle/organs/immune.py` | CLI `feed` |
| `SKILL-CALCIFICATION` (harden reflex) | `src/mantle/hatchery.py` (INSTINCTS gauntlet: sandbox → trial → calcify), `src/mantle/compiler.py`, `src/mantle/phenotype.py`, `src/mantle/teach.py` | `examples/phenotype_demo.py` |
| `METABOLIC-GOVERNANCE` (energy / cost / wake) | `src/mantle/organs/heart.py`, `src/mantle/symbiosis.py`, `src/mantle/vcw/metabolism.py`, `src/mantle/mind/runtime.py` | `documents/Mantle_Urge_System.md`, `documents/Mantle_VCW_Tiers.md` |
| `CREMATION` (retire / DNR) | policy-enforced, no single module: `src/mantle/vault.py` (DNR & reconstruction policy), `src/mantle/organs/immune.py` (tombstone / redact), `src/mantle/organs/genome.py` (lineage) | `documents/Mantle_Doctrine.md` |
| `VOCARE` (MIND readiness, Phase 2) | `src/mantle/mind/` (`mind.py`, `containment.py`, `runtime.py`, `inner_voice.py`, `transport.py`), `src/mantle/audits/stage2.py`, `src/mantle/organs/brain.py` | `Mantle_Part2_Mind.md`, `Mantle_Part2_Mind_Audit.md`; CLI `mind`, `audit-mind` |
| `RESURGERE` (reconstruct from seed) | `src/mantle/vault.py` (seed → `reconstruct()`), `src/mantle/hatchery.py` (`incubate`) | `documents/guides/Organism_Lifecycle.md` |

### F.2 Egg & assimilation (the vital substrate)

Birth and assimilation share **one substrate, two casts**:

- **Egg (declarative birth):** an AppAI declared entirely as data — `src/mantle/egg.py`; incubated to a certified organism by `src/mantle/hatchery.py`; sample eggs in `examples/eggs/calculator.json`, `examples/eggs/greeter.json`, `examples/eggs/notes_graft.json`.
- **Assimilation (raise an existing app):** read-only host dissection in `src/mantle/assimilator/scanner.py` (plus `scanner_ts.py` for TS/JS) → assimilation map `organ_map.py` → Phase-0 inventory artifacts `report.py` → fail-open hook runtime `wrappers.py` (where `mantle_touch`, `mantle_sense`, `mantle_display`, `mantle_state_write`, `mantle_external_call` live) → residency via `src/mantle/anchor.py` and graft eggs via `src/mantle/graft.py`.
- **Stage-1 gate (the same gate for both paths):** `src/mantle/audits/stage1.py` with `src/mantle/audits/invariants.py`; the hard-fail codes (HF-B32, HF-B40, HF-MIND, …) are enforced here.

### F.3 Organs → modules

| Organ (§A.3) | Module |
|---|---|
| Heart | `src/mantle/organs/heart.py` |
| Genome | `src/mantle/organs/genome.py` |
| Nervous System | `src/mantle/organs/nervous.py` |
| Senses | `src/mantle/organs/senses.py` |
| Immune | `src/mantle/organs/immune.py` |
| Limbs | `src/mantle/organs/limbs.py` |
| Memory | `src/mantle/organs/memory.py` |
| Brain | `src/mantle/organs/brain.py` |
| Organ contract | `src/mantle/organs/contract.py`; atlas `documents/Mantle_Organ_Atlas.md`, `documents/guides/Organ_Contracts.md` |

### F.4 VCW cube, bands & hooks

- **Cube substrate:** `src/mantle/vcw/cube.py`, `png.py`, `entry.py`, `indexes.py`, `drivers.py`; metabolism / compaction `src/mantle/vcw/metabolism.py`. Guides: `documents/guides/VCW_Guide.md`, `documents/Mantle_VCW_Tiers.md`, `examples/vcw/`.
- **Band plan (§E.4):** `src/mantle/vcw/bands.py` — boot sectors, driver registry, the reserved band genome, and capacity thresholds.
- **Fail-open hooks (§E.5):** `src/mantle/assimilator/wrappers.py`. **MIND containment (§A.5):** `src/mantle/mind/containment.py` (the MIND may write only `thoughts` / `brain`). **Limb dispatch & Action Execution Proof (§E.5):** `src/mantle/organs/limbs.py`.

### F.5 Working examples & in-repo doctrine

- Runnable: `python -m mantle demo` (narrated Phase-1 life), `examples/sample_app/` (assimilation target), `examples/vcw/` (cube), `examples/phenotype_demo.py`, parity tests in `examples/tests/`.
- In-repo doctrine: `documents/guides/`, `Mantle_Part1_Body.md` / `Mantle_Part2_Mind.md` (and their audits), `documents/Mantle_Doctrine.md`. The canonical Grimoire lives at `documents/grimoire/` — the Core (`The Grimoire.md`) and this chapter (`The Grimoire AppAI Chapter.md`), both at **Version 1.0.0**; this file is the canonical, current chapter.

---

## END LAW FOR APPAI OPERATORS

Raise nothing without authority. A Body must live without a MIND. A MIND may only extend. OTHER may teach, never rule. SELF must be proved. The diagnostic spell reports; the Caster heals. Stage 1 must be certified before MIND readiness. Cremation is final unless policy permits resurrection.
