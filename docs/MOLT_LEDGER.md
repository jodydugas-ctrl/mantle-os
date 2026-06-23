# THE MOLT LEDGER

*A running record of every molt the egg goes through, so the eventual merge into Mantle OS
`main` is a **documented diff**, not archaeology. One section per molt records: the delta to
the **shared inherited anatomy** (`core/` · `vcw/` · `organs/` — the code that is byte-identical
to Mantle except docstrings), any **new modules** (Argonaut-only tissue), the **new invariants**
that prove it, and the **format/compat verdict** (does the on-disk cube format `vcw-cube-png-v2`
and the `body.json` / nest layout still read backward-compatibly?).*

**Why this matters:** the plan is to evolve the egg through the *entire* `NEXT_MOLT.md` roadmap
and then merge it into `main` as a single rebirth/inheritance event. This ledger is the merge
manifest. The cube format is a shared contract ("an Argonaut reads a Mantle cube and vice
versa"); when a molt breaks it, that must be a **conscious decision** recorded here, with a
format-tag bump and a migration — never an accident discovered at merge time.

**Legend — format/compat verdict:**
`COMPAT` = old cubes/nests still read; `VARIANT` = a new artifact kind added alongside, no
change to organism cubes; `SUPERSEDED` = format tag bumped, migration provided.

---

## Molt 1 — M2 (self/other) + M1 (nociception / event-gated cognition)  ·  ✅ shipped

**Shared-anatomy delta**
- `core/body.py` — a one-time **genesis key** (`secrets.token_hex`) minted in `birth()`;
  `sign()`/`verify()` (HMAC-SHA256); `key_fingerprint` (public id); persisted in
  `to_dict`/`from_dict` but **kept out of `boot_order()` and `self_record()`** (so it never
  enters the MIND's snapshot); `key_fingerprint_consistent()` guard.
- `core/organism.py` — `_self_seal_payload()` (Primer + Prime fingerprint); `save()` writes a
  `self_seal.json` sidecar; `load(verify_seals=True)` raises `autoimmune_risk` on a
  tampered/inconsistent key and immune-logs a non-verifying self-seal. New bus subscriptions:
  Heart ← `significant` (Senses) and `distress` (Immune).
- `organs/immune.py` — `is_self()` / `reject_foreign()` (SELF/OTHER); `AUTONOMIC_KINDS` +
  `_nociceptor()` emitting `distress {reason, band, ref}`; contract reflexes/audit extended.
- `organs/heart.py` — **event-gated cognition**: `_wake` state; `on_significant`/`on_distress`
  handlers; `pain(reason, band, ref)` unscheduled pulse; `beat(wake=...)` cognizes only on a
  pending wake and anchors `snapshot["_stressor"]`; contract updated.
- `audits/invariants.py` — `import json`; **SELF-1..4**, **NOC-1..3** added to `TESTS`;
  `t_starvation_failopen` (SYM-2) adapted to the event-gated model (same guarantee, wakes via
  `pain()`).

**New modules:** none (organ-level additions only — ports cleanly to Mantle).

**New invariants:** SELF-1 key-once-and-private · SELF-2 self-verify/reject-foreign ·
SELF-3 anti-clone · SELF-4 key-survives-or-fails-loud · NOC-1 calm-spends-nothing ·
NOC-2 fault-fires-unscheduled-pulse · NOC-3 wake-anchored-to-stressor. **(36 → 43 green.)**

**Docs:** `teach.py` + `FIELD_GUIDE.md` chapters *Self & Other* and *Pain & the Unscheduled
Heartbeat*; `NEXT_MOLT.md` shipped-banner + sequence; `ARGONAUT.md` (new tissue + principle);
`README.md` count + principle. New principle: **"Containment before reach."**

**Format/compat verdict:** `COMPAT`.
- Cube `.vcw` format **unchanged** (`vcw-cube-png-v2`); `examples/vcw_cube.py selftest` +
  `interop.py` pass.
- `body.json` gains `genesis_key` + `key_fingerprint`; a legacy keyless `body.json` loads
  fine (`has_key=False`, consistent). Nest gains an additive `self_seal.json` (absent ⇒
  skipped on load). No breaking change.

**Merge note for `main`:** all five touched files are shared anatomy → port near-directly.
The new principle and Field-Guide chapters carry over.

---

## Molt 2 — M3 graded memory (deweighting / behavioral ghosts)  ·  ✅ shipped

**Shared-anatomy delta**
- `vcw/entry.py` — graded-memory primitives: `DEWEIGHT_OPCODE`, `GHOST_THRESHOLD`,
  `effective_weights()` (id → weight from append-only DEWEIGHT events, last wins), and
  `weight_overlay(entries, ghosts=False)` (drops deweight bookkeeping, hides ghosts by
  default / returns ghosts-only when asked, orders by descending weight; **no-op for a cube
  with no deweight activity**).
- `vcw/cube.py` — `read()` applies `weight_overlay` on the log-json stream and gains a
  `ghosts=False` kw; new `deweight(band, id, weight=0.0)` appends a DEWEIGHT event (never
  mutates the target; refuses on a sealed cube).
- `organs/memory.py` — `deweight()` and `recall_ghosts()` methods; `recall()` doc clarified
  (weight-ordered); contract reflexes/audit extended.
- `audits/invariants.py` — **MEMW-1..3** added to `TESTS`.

**New modules:** none (substrate + organ additions only — ports cleanly to Mantle).

**New invariants:** MEMW-1 deweight-hides-but-preserves · MEMW-2 weight-orders-reads ·
MEMW-3 deweight-not-overwrite (belief history + dedupe/compaction coherence). **(43 → 46 green.)**

**Docs:** `teach.py` + `FIELD_GUIDE.md` chapter *Graded Memory*; `NEXT_MOLT.md` shipped-banner
+ sequence; `README.md`/`ARGONAUT.md`/`FIELD_GUIDE.md` invariant count 43→46.

**Format/compat verdict:** `COMPAT`.
- A deweight is an ordinary appended entry; the entry hash rule (`VOLATILE_FIELDS`) is
  unchanged. An old cube with no DEWEIGHT events reads identically (`weight_overlay`
  short-circuits to the raw stream). Cube `.vcw` format **unchanged** (`vcw-cube-png-v2`);
  `vcw_cube.py selftest` + `interop.py` pass.
- `retrieve(band, id)` deliberately still returns ghosts (they are physically present and
  recoverable by id) — only the default *stream* hides them.

**Merge note for `main`:** all touched files are shared anatomy → port near-directly. The
overlay is opt-in by data (no deweight events ⇒ no behavior change), so it is safe to carry
into `main` even before any organism uses it.

---

## Molt 3 — R1 graft egg + R2 live residency  ·  ✅ shipped

**Shared-anatomy delta**
- `mantle/anchor.py` — `anchor()` gains an additive `extra_bands` parameter (graft bands
  ride into the resident's genome); default behavior unchanged.
- `audits/invariants.py` — **GRAFT-1..3**, **RESID-1..2** added to `TESTS` (+ two helpers
  `_sample_host_copy`, `_load_sample_module`).

**New modules / Argonaut-only tissue**
- `mantle/graft.py` — the graft egg (`mantle-graft-egg-v1`): `validate_graft`/`load_graft`,
  `graft_bands`, `apply()` (copy host → workspace → `anchor()` the copy → census-prove the
  original untouched; `GraftDrift` raised on census drift), and R2 `weave()`/`unweave()` over a
  host namespace using the existing `assimilator.Assimilation` wrappers.
- `mantle/cli.py` — `graft <graft-egg> <host>` command.
- `eggs/notes_graft.json` — a sample graft egg targeting `examples/sample_app`.

**New invariants:** GRAFT-1 apply-non-destructive · GRAFT-2 drift-detected · GRAFT-3
graft-validates · RESID-1 wrap-preserves+lives · RESID-2 detach-restores. **(46 → 51 green.)**

**Docs:** `teach.py` + `FIELD_GUIDE.md` chapter *Graft & Living Residency*; `NEXT_MOLT.md`
shipped-banner + sequence; counts 46→51 across README/ARGONAUT/FIELD_GUIDE.

**Format/compat verdict:** `COMPAT`.
- Purely additive: a new egg *kind* (graft egg), a new module, a new CLI verb, and an opt-in
  `anchor(extra_bands=...)` arg. No change to the organism cube format (`vcw-cube-png-v2`);
  the original host is never modified (census-proven); weaving is in-memory and reversible.

**Merge note for `main`:** `graft.py` is new tissue (carry whole). The one-line `anchor.py`
change and the invariants port directly. R2 reuses the assimilator wrappers that already exist
in `main`.

---

## Molt 4 — M4 MEM VCW (the keyless knowledge plasmid)  ·  ✅ shipped

**Shared-anatomy delta**
- `audits/invariants.py` — **MEM-1..3** added to `TESTS`.
- (No change to `core/`/`vcw/`/`organs/` — M4 composes the existing substrate.)

**New modules / Argonaut-only tissue**
- `mantle/mem.py` — `mem_genome()`, `is_mem_vcw()`, `excrete()` (write a keyless cube with
  `mem_data` + `mem_code` log-json bands), `digest()` (knowledge → `discoveries` inferred
  `foreign-MEM`; microcode → sandbox `trial`; re-derive into SELF only on the finder's own
  trial; a sandbox escape → `foreign_code_rejected` immune event, never adopted). Reuses
  `Cube.genesis`, `trial`/`SandboxError`, `calcify`, `invoke_reflex`.

**New invariants:** MEM-1 keyless-portable-other · MEM-2 foreign-code-sandboxed ·
MEM-3 knowledge-inferred-not-fact. **(51 → 54 green.)**

**Docs:** `teach.py` + `FIELD_GUIDE.md` chapter *The MEM VCW*; `NEXT_MOLT.md` shipped-banner +
sequence; counts 51→54.

**Format/compat verdict:** `VARIANT`.
- A MEM VCW is a NEW kind of artifact (a keyless, lineage-free cube) built on the SAME
  substrate (`vcw-cube-png-v2`) via `Cube.genesis` — organism cubes are unchanged; a MEM file
  has no `body.json` sidecar. `vcw_cube.py selftest` + `interop.py` still pass.

**Merge note for `main`:** `mem.py` is new tissue (carry whole); the invariants port directly.
No shared-anatomy edits to reconcile.

---

## Molt 5 — M5 self-redesigning VCW + M6 memory bridge (the Compiler-class leap)  ·  ✅ shipped

**Shared-anatomy delta**
- `audits/invariants.py` — **BOOT-1..3**, **BRIDGE-1..2** added to `TESTS`.
- (No edits to `core/`/`vcw/`/`organs/`: M5 reuses the existing `rebirth(new_genome=...)` and
  the driver registry; M6 reuses the existing `keyvalue` driver.)

**New modules / Argonaut-only tissue**
- `mantle/compiler.py` — M5: `validate_genome`/`propose_genome` (encoding must be a
  registered driver; head 550-749; no collisions), `adopt_genome` (validate → rebirth into
  `standard_genome()` + re-fitted bands; ancestor = oracle), `re_derive` (inherited microcode
  re-trials before re-calcify, else `re_derive_refused`). M6: `HostMemoryBridge` (a host
  key/value API backed by a VCW keyvalue band; redacts at the boundary).

**New invariants:** BOOT-1 self-redesign-rebirth · BOOT-2 unsafe-genome-refused ·
BOOT-3 inherited-microcode-re-trials · BRIDGE-1 host-write-round-trip · BRIDGE-2
no-secret-crosses. **(54 → 59 green.)**

**Docs:** `teach.py` + `FIELD_GUIDE.md` chapter *Self-Redesigning VCW & Memory Bridge*;
`NEXT_MOLT.md` shipped-banner + sequence; counts 54→59.

**Format/compat verdict:** `COMPAT` — **the anticipated `vcw-cube-png-v3` supersession did NOT
occur.** A re-fitted genome uses REGISTERED drivers and lives in the per-cube boot-sector
*data*, not the PNG container format. The on-disk format remains `vcw-cube-png-v2`;
`vcw_cube.py selftest` + `interop.py` pass. (The plan's M5 format watchpoint is hereby resolved
to COMPAT.)

**Merge note for `main`:** `compiler.py` is new tissue (carry whole); invariants port directly.
No shared-anatomy edits — M5/M6 compose `rebirth`, the driver registry, and the keyvalue driver
that already exist in `main`.

---

## Molt 6 — M7 ganglia + M8 seed vault  ·  ✅ shipped

**Shared-anatomy delta**
- `core/body.py` — `seal_bytes()`/`open_bytes()` (XOR stream cipher keyed by the genesis key,
  via a `_keystream` in sha256 counter mode) so the seed vault can SELF-encrypt. The key stays
  inside the Body (never to the MIND/cube), consistent with M2.
- `audits/invariants.py` — **GANG-1..2**, **VAULT-1..2** added to `TESTS`.

**New modules / Argonaut-only tissue**
- `mantle/ganglia.py` — `ganglion_band()`, `Ganglion` (runs `task(report, *args)` in a
  thread; `report` appends redacted PROGRESS entries; a fault → `ganglion_fault` immune event;
  `progress()` is the parent's zero-token read).
- `mantle/vault.py` — `vault_band()` (private/veiled), `store_seed`/`open_seed` (SELF-encrypt
  the seed under the genesis key), `reconstruct` (rebuild via the hatchery gate). `VaultError`.

**New invariants:** GANG-1 progress-zero-token · GANG-2 crashed-fail-open ·
VAULT-1 self-encrypted-other-cannot · VAULT-2 reconstruct-gates. **(59 → 63 green.)**

**Docs:** `teach.py` + `FIELD_GUIDE.md` chapter *Ganglia & the Seed Vault*; `NEXT_MOLT.md`
shipped-banner + sequence; counts 59→63.

**Format/compat verdict:** `COMPAT`.
- Additive: new bands (`ganglion`/`vault`) and two new `Body` methods. `body.json` schema is
  unchanged (the key already persisted since Molt 1; `seal_bytes` derives from it at runtime).
  Cube format `vcw-cube-png-v2` unchanged; `selftest` + `interop` pass.

**Merge note for `main`:** `ganglia.py` + `vault.py` are new tissue (carry whole). The two
`Body` methods are a small additive shared-anatomy change that ports directly. Invariants port
directly. Note: `seal_bytes` is an XOR stream cipher (confidentiality vs OTHER), not AEAD — the
seal/sign path (Molt 1) provides the integrity check; fine for the vault's threat model.

---

## Molt 7 — §3 resilience (real metering · ingestion · doctor)  ·  ✅ shipped  ·  ROADMAP COMPLETE

**Shared-anatomy delta**
- `symbiosis.py` — `metered_by_usage()` (energy from actual token usage; starvation law
  intact), `metering_summary()` (calls, burn rate, starvation horizon), `_rough_tokens`.
- `cli.py` — `doctor <organism-dir>` command.
- `audits/invariants.py` — **METER-1**, **INGEST-1**, **DOCTOR-1** added to `TESTS`.

**New modules / Argonaut-only tissue**
- `mantle/ingestion.py` — `ingest()` (conversation → Senses → decisions=sourced facts,
  ideas=inferred discoveries) + `record_covenant()` (operator intent → Special Instruction).
- `mantle/doctor.py` — `checkup()` (cube-verify · ancestor-seals · genesis-key · ledger ·
  **docs-vs-code coherence gate**: README invariant count == `len(TESTS)`).

**New invariants:** METER-1 usage-priced · INGEST-1 conversation-distilled ·
DOCTOR-1 deployment-checkup. **(63 → 66 green.)** Note: DOCTOR-1 is partly self-referential —
it asserts the README's claimed count equals the live gate, so the docs count is now gate-locked.

**Docs:** `teach.py` + `FIELD_GUIDE.md` chapter *Resilience*; `NEXT_MOLT.md` shipped-banner +
"ROADMAP COMPLETE"; counts 63→66.

**§4 polish — DEFERRED (non-gating cosmetics, honestly noted):** a living HTML face and a v4
poster were in §4. The deterministic PNG self-portrait (`face.py`) already exists and is
proven; an HTML face and a printed poster add no invariant and no capability, so they are
deferred rather than rushed. Field-Guide chapters were consolidated per-molt as we went.

**Format/compat verdict:** `COMPAT`. Additive modules + one symbiosis function + a CLI verb;
no `core`/`vcw`/`organs` schema change. Cube format `vcw-cube-png-v2` unchanged.

**Merge note for `main`:** `ingestion.py` + `doctor.py` are new tissue (carry whole); the
`symbiosis.py` additions and the invariants port directly. The doctor's docs-vs-code gate
should be re-pointed at Mantle's own README count at merge time.

---

## Roadmap summary (the merge manifest at a glance)

| Molt | Items | New invariants | Format | New modules (carry whole) | Shared-anatomy edits |
|---|---|---|---|---|---|
| 1 | M2 self/other · M1 nociception | SELF-1..4, NOC-1..3 | COMPAT | — | body, organism, immune, heart |
| 2 | M3 graded memory | MEMW-1..3 | COMPAT | — | vcw/entry, vcw/cube, organs/memory |
| 3 | R1 graft egg · R2 residency | GRAFT-1..3, RESID-1..2 | COMPAT | graft.py | anchor (extra_bands) |
| 4 | M4 MEM VCW | MEM-1..3 | VARIANT | mem.py | — |
| 5 | M5 self-redesign · M6 bridge | BOOT-1..3, BRIDGE-1..2 | COMPAT | compiler.py | — |
| 6 | M7 ganglia · M8 seed vault | GANG-1..2, VAULT-1..2 | COMPAT | ganglia.py, vault.py | body (seal/open_bytes) |
| 7 | §3 metering · ingestion · doctor | METER-1, INGEST-1, DOCTOR-1 | COMPAT | ingestion.py, doctor.py | symbiosis, cli |
| + | scheduled heartbeat (`schedule_pulse`) | SCHED-1 | COMPAT | — | organs/heart, mind/runtime |
| + | post-review guard: Body genome survives reload | HF-B02 (`t_body_genome_round_trip`) | COMPAT | — | audits/invariants | (locks the save→load primer round-trip an external log review surfaced as a demo bug) |
| 9 | M9 phenotype — wearable app-faces | PHENO-1..5 | COMPAT | phenotype.py | egg, hatchery, organism (rebirth helper), cli, teach |

**Net:** 36 → **73 invariants green**; cube on-disk format **unchanged** (`vcw-cube-png-v2`) the
whole way — the anticipated v3 supersession never occurred. Shared-anatomy edits are small and
additive; the bulk of the new capability is in new modules that carry whole into `main`.

*Post-merge addition: a **scheduled heartbeat** — `Heart.schedule_pulse(reason, after=N | at=K)`
(+ `scheduled`/`cancel_pulse`, and `AppAIRuntime.schedule_pulse`). The organism plans a wake on a
FUTURE beat to chain thoughts and run a task only as often as it needs, staying asleep
(event-gated) until due. The `later` companion to nociception's `pain` (`now`). Proven by SCHED-1;
teach/Field-Guide chapter "Planning Ahead"; examples updated descriptively.*

---

## Molt 9 — M9 phenotype: wearable app-faces stored in the VCW

**The leap.** One stable organism (Body + append-only cube + eight organs) can now express MANY
front-facing surfaces — a spreadsheet, a CLI, a calculator, a phone shell — as interchangeable
**phenotypes**. A *face* is a whole front-end whose source is **sealed under the genesis key** into a
private VCW band. The Compiler does not run apps; it **wears** them. Same self, different expressed
morphology — the *invariant substrate* (nervous system + VCW) never changes; only the *swappable
layer* (the face) does.

**New module `mantle/phenotype.py`** — modeled on the seed vault (`vault.py`), one band richer:
- two reserved PRIVATE bands — `phenotypes` (head 640, the SELF-encrypted source, one ciphertext
  chunk per layer, large faces span layers) and `phenotype_log` (head 660, the append-only
  wear-events);
- `express` (seal a face), `list_faces` (a key-free catalog), `open_face` (SELF-only + integrity),
  `wear` (return a host boot manifest), `shed`, `active_face`, and `snapshot`/`restore`/
  `rebirth_with_faces` for rebirth survival.

**The default (origin) face.** Every hatched organism is BORN wearing its origin surface — sealed in
its VCW from the first breath (`hatchery.incubate` seeds it from the egg's optional `face` block, or
a generated stub). Even if no other face is added, the organism always holds an encrypted copy of
its own source: a self-reconstruction / security guarantee, the sibling of the seed vault. The
genesis key persists across `rebirth()`, so carried-forward faces stay openable; the old generation
keeps its own readable copy in the sealed ancestor.

**Laws (all proven red/green):**
- `PHENO-1` SELF opens its own face; the source round-trips byte-identical; a tampered seal is refused.
- `PHENO-2` an OTHER body (different genesis key) cannot read/wear a sealed face.
- `PHENO-3` wearing is append-only — the active face is the latest wear-event; the cube still coheres.
- `PHENO-4` the default face is present after birth and survives a chosen rebirth.
- `PHENO-5` a face may only plug into controls the nervous system can drive (socket conformance).

**Surfaces touched (shared anatomy, all additive):** `egg.py` (optional `face` block — data, never
exec'd, so no gauntlet), `hatchery.py` (always seed a default face + carry the phenotype bands),
`core/organism.py` is **untouched** (rebirth survival lives in `phenotype.rebirth_with_faces`, so core
stays pure), `cli.py` (`face-list`/`face-save`/`face-wear`), `audits/invariants.py` (PHENO-1..5),
`teach.py` + `FIELD_GUIDE.md` (chapter "Wearing a Face"). New artifacts: `eggs/calculator.json` (an
egg that declares its origin face) and `examples/phenotype_demo.py` (the whole story, end to end).

**Format/compat verdict:** `COMPAT`. A new app band + `log-json` entries; no `core`/`vcw`/`organs`
schema change. Cube format `vcw-cube-png-v2` unchanged.

**Design note (intentional):** SELF-encryption was chosen over raw cross-body portability — faces are
bound to the organism's genesis key, so a copied nest in a *foreign* body cannot wear them. The Body
ABI holds within the organism's own lineage (the key persists across rebirth), not across foreign
bodies. Portable, signed-but-cleartext faces remain a possible future variant.

**Net after Molt 9:** 68 → **73 invariants green**; teach 17 → **18 chapters**; format COMPAT.
