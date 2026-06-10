# Mantle OS v3 — Organ Contracts

Every organ declares a machine-readable `OrganContract` (see `mantle/organs/contract.py`):
name, role, bands it may **read**/**write**, reflex surface, Phase-1 state, Phase-2
extension, audit obligations, and fail mode (always `fail-open`). Contracts are enforced:
an organ writing outside its declared bands gets `PermissionError` + an `organ_overreach`
immune event. Inspect them live: `org.manifests()` or `AppAIRuntime.inspect_body()`.

The mesh rules (absolute):

- Organs hold **no references to each other** — only the SignalBus and their own bands.
- **Inbound** = Senses only. **Outbound** = Limbs only. **Failure** = Immune only.
- The Brain socket is the only Phase-2 organ; nothing in Phase 1 imports `mantle.mind`.

| Organ | Role | Writes | Phase 1 | Key reflexes | Key audit obligations |
|---|---|---|---|---|---|
| **Heart** | clock & circulation | — | active | tick, pulse-check, circulate, dual-flush | runs with no LLM; fixed pulse order; missed pulse → immune |
| **Genome** | identity & lineage (Body-resident) | discoveries (inheritance) | active | boot-order, seal-primer, inherit | Primer immutable, never in the cube; rebirth chosen, ancestry retained |
| **Nervous** | routing, refs, Context Assembly | — | active | resolve, assemble, route | deterministic; no unresolved ref ever leaves; dangling → immune |
| **Senses** | perception (afferent) — the inbound boundary | senses | active | classify, inhale, reflex-arc, map-surface, drain | LLM-free classifier; one entry per signal; REFLEX never touches brain band; redaction at the boundary |
| **Immune** | defense & repair — the failure boundary | immune | active | event, scan, quarantine, tombstone, redact | heartbeat scan; secrets never stored; marks hidden from reads; no silent failure |
| **Limbs** | action (efferent) — the outbound boundary | brain | dormant→active | notify, complete, operate, prove, invoke-reflex | authorship immutable (in hash); Body never authors INTENTION; every effector use proven |
| **Memory** | recall & metabolism | identity, facts, events, discoveries | active | remember, recall, allocate, compact, dedupe, overflow, promote | immutable+hashed; veil honored; capacity→metabolism at 0.75/0.90, never rebirth; inference never auto-promoted |
| **Brain** | cognition socket (Phase 2) | thoughts, brain | **dormant** | none — it reasons | fusion only after Stage-1; writes only thoughts+brain; cannot touch Genome or self-promote |

## The pulse (where the contracts meet)

```
heart.beat():
  1. tick            -> bus signal `pulse`
  2. sense intake    -> senses.drain()             (the inbound boundary)
  3. context assembly-> nervous.assemble()         (deterministic, veiled)
  4. reflex execution-> bus subscribers            (registration order, fail-open)
  5. immune scan     -> immune.scan()              (hashes, coherence, seals)
  6. checkpoint      -> heart.circulate()          (staged atomic save)
  [Phase 2 only] the SAME snapshot is offered to brain.cognize()
```

## Growing an application organ

1. Subclass `Organ`, declare an `OrganContract` with an app band in 550–749.
2. Add the band to the genome at birth: `make_band_boot("my_band", 600, span=20,
   purpose="…")`.
3. Implement reflexes as deterministic, no-LLM methods; write only via `self.append`.
4. Subscribe to bus signals (`pulse`, `sense`, `significant`, `dispatch`, `pressure`,
   `checkpoint`) instead of reaching into other organs.
5. State the audit obligations in the contract; add a red/green invariant for each.
6. If it needs judgment, that is a `phase2_extension` — never a Phase-1 dependency.
