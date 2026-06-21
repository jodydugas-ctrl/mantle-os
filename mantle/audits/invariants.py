#!/usr/bin/env python3
"""
mantle.audits.invariants  --  executable security invariants (Mantle OS · Gen-4)

Every doctrine guarantee as a red/green assertion. Each test maps to a hard-fail code and
proves the guard actually FIRES (and, where relevant, that the permitted path still
works). Pure standard library, no pytest:

    python -m mantle prove          # run all; exit 0 = all green

Importable: run_all() returns result dicts so the Stage-1/Stage-2 gates fold these in.
NO INVARIANT IS EVER WEAKENED TO MAKE A TEST PASS.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

from ..core.body import Body
from ..core.organism import Organism
from ..core.redact import contains_secret
from ..core.audit import expect_raise as _expect_raise
from ..vcw.bands import standard_genome, make_band_boot
from ..vcw.cube import Cube
from ..vcw.entry import make_entry, entry_hash
from ..vcw.drivers import (ExecDriver, CapabilityError, IntegrityError, TrustError,
                           SandboxError, ProvenanceError, validate_calcify_payload,
                           trial)
from ..vcw.bands import code_hash

_EXEC = ExecDriver()
_CODE = "def f(x):\n    return x + 1\n"


def _born(genome=None):
    return Organism.birth(identity={"name": "TestAppAI"},
                          truths=["if it is not in the VCW it did not happen"],
                          commandments=["protect your VCW"],
                          genome=genome)


def _exec_content(provenance, runner="python", caps=None, bad_hash=False):
    return {"code": _CODE, "code_hash": ("sha256:deadbeef" if bad_hash else code_hash(_CODE)),
            "entry": "f", "runner": runner, "capabilities": caps if caps is not None else {},
            "signature": {"by": "test"}, "limits": {"ms": 200}, "provenance": provenance}


# ============================================================================
# 1. NO PHASE-1 LLM PATH (HF-B08): proven in a CLEAN subprocess
# ============================================================================
def t_no_phase1_llm_path():
    """HF-B08: importing and RUNNING the whole Phase-1 organism (birth, senses, heartbeat,
    rebirth) must never load mantle.mind, a vendor SDK, or an HTTP client. Proven in a
    clean interpreter, not the test process."""
    probe = (
        "import sys\n"
        "from mantle import Organism\n"
        "org = Organism.birth(identity={'name':'P'}, truths=['t'], commandments=['c'])\n"
        "org.senses.inhale({'action_id':'a','event_type':'b'})\n"
        "org.heart.run(3, assemble=True)\n"
        "org.rebirth(reason='probe')\n"
        "banned = [m for m in sys.modules if m.startswith('mantle.mind')\n"
        "          or m in ('urllib.request','http.client','openai','anthropic','requests')]\n"
        "print('BANNED:' + ','.join(banned))\n")
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                         cwd=root, timeout=120)
    if out.returncode != 0:
        return False, "phase-1 probe crashed: %s" % out.stderr.strip()[-200:]
    line = [l for l in out.stdout.splitlines() if l.startswith("BANNED:")]
    banned = line[0][len("BANNED:"):] if line else "?"
    return banned == "", "clean interpreter ran a full Phase-1 life; loaded: %r" % (banned or "none")


def t_phase1_source_clean():
    """HF-B08 (static): no Phase-1 module (core/organs/vcw) IMPORTS mantle.mind, an HTTP
    client, or a vendor SDK. Checked on the AST (real import statements -- documentation
    may MENTION the mind; code may never reach it)."""
    import ast as _ast
    banned_roots = ("urllib", "http", "socket", "requests", "openai", "anthropic")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad = []
    for pkg in ("core", "organs", "vcw"):
        d = os.path.join(root, pkg)
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                tree = _ast.parse(f.read())
            for node in _ast.walk(tree):
                names = []
                if isinstance(node, _ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, _ast.ImportFrom):
                    mod = node.module or ""
                    names = [mod]
                    if node.level and (mod == "mind" or mod.startswith("mind.")):
                        bad.append("%s/%s: from %s import (relative to mantle.mind)"
                                   % (pkg, fn, mod))
                for n in names:
                    top = n.split(".")[0]
                    if n.startswith("mantle.mind") or top in banned_roots:
                        bad.append("%s/%s: import %s" % (pkg, fn, n))
    return not bad, ("phase-1 sources import no mind/HTTP/vendor module"
                     if not bad else "found: %s" % bad)


# ============================================================================
# 2. Identity & genome
# ============================================================================
def t_primer_immutable():
    """HF-B07: the Primer is sealed at birth; a second birth must be refused."""
    b = Body()
    b.birth(identity={"name": "X"}, truths=["t"], commandments=["c"])
    return _expect_raise(lambda: b.birth(identity={"name": "Y"}, truths=["t2"],
                                         commandments=["c2"]), PermissionError)


def t_identity_in_body():
    """HF-B45: no genome/identity band exists in the cube; the Primer lives in the Body."""
    org = _born()
    in_cube = [b for b in org.prime.bands if b.startswith("bodyentry") or b == "genome"]
    ok = (not in_cube and org.prime.identity_in_body
          and bool(org.body.self_record()["primer"]))
    return ok, "identity_in_body=%s, genome-bands-in-cube=%s" % (
        org.prime.identity_in_body, in_cube or "none")


# ============================================================================
# 3. The secret boundary
# ============================================================================
def t_secret_boundary_sense():
    """HF-B20: a secret in an inbound signal is redacted before it enters the senses band."""
    org = _born()
    org.senses.inhale({"action_id": "login", "event_type": "auth",
                       "authorization": "Bearer sk-ABCD1234EFGH5678IJKL",
                       "api_key": "AKIAQWERTYUIOPASDFGH"})
    stored = org.prime.read("senses")[-1]["content"]
    if contains_secret(stored):
        return False, "secret survived into senses: %r" % stored
    return True, "senses entry redacted"


def t_secret_boundary_immune():
    """HF-B20: secrets are redacted before they reach the immune band too."""
    org = _born()
    org.immune_event("suspicious", {"token": "eyJabc.def123456789.ghiJKLmnop",
                                    "note": "leaked?"})
    stored = org.prime.read("immune")[-1]["content"]
    return (not contains_secret(stored)), "immune entry redacted"


# ============================================================================
# 4. Visibility: veil, tombstone, quarantine
# ============================================================================
def t_veil_hides_thoughts():
    """B-14: the private thoughts band is veiled on normal read."""
    org = _born()
    org.prime.append("thoughts", make_entry("a private musing", opcode="THINK",
                                            author="MIND"))
    veiled = org.prime.read("thoughts")
    revealed = org.prime.read("thoughts", reveal_private=True)
    return (veiled == [] and len(revealed) == 1), "veiled=[] revealed=%d" % len(revealed)


def t_tombstone_quarantine_hidden():
    """B-14/B-15: tombstoned AND quarantined entries vanish from reads and retrieves."""
    org = _born()
    for i in range(3):
        org.memory.remember("facts", {"k": i})
    e0 = org.prime.read("facts")[0]
    e1 = org.prime.read("facts")[1]
    org.immune.tombstone("facts", e0["id"])
    org.immune.quarantine("facts", e1["id"])
    vis = org.prime.read("facts")
    ok = (len(vis) == 1 and vis[0]["content"] == {"k": 2}
          and org.prime.retrieve("facts", 0)["content"] == {"k": 2})
    return ok, "3 entries -> 1 visible after tombstone+quarantine; retrieve honors marks"


# ============================================================================
# 5. References
# ============================================================================
def t_dangling_ref_immune():
    """HF-B24: a dangling reference becomes an immune event and resolves to None."""
    org = _born()
    before = len(org.immune.log)
    r1 = org.resolve("<facts.999999>")
    r2 = org.resolve("<nosuchband.1>")
    r3 = org.resolve("<gen9.facts>")
    logged = len(org.immune.log) - before
    return (r1 is None and r2 is None and r3 is None and logged == 3,
            "3 dangling refs -> 3 immune events, all resolved None")


def t_body_genome_round_trip():
    """HF-B02/B45: the Body genome (primer + self_record) survives save->load. A reloaded Body
    keeps its primer, so a reloaded organism is never silently amnesiac. This guards the failure
    the Reference Agent's logs exhibited: bodyentry.000 (the primer) going `missing-bodyentry` on
    every model call after the crystal was reloaded because the Body slots were not persisted."""
    org = _born()
    before = org.body.boot_order()["primer"]
    reloaded = Body.from_dict(org.body.to_dict())
    after = reloaded.boot_order()["primer"]
    record_ok = reloaded.self_record()["primer"] == org.body.self_record()["primer"]
    return (bool(after) and after == before and record_ok,
            "Body genome (primer + self_record) round-trips through to_dict/from_dict")


def t_assembly_complete_and_veiled():
    """HF-M14 (Phase-1 half): Context Assembly is complete (no raw refs) and veiled."""
    org = _born()
    org.memory.remember("facts", {"k": "v"})
    org.prime.append("thoughts", make_entry("private", opcode="THINK", author="MIND"))
    snap = org.nervous.assemble()
    return (snap.get("_complete") is True and snap.get("thoughts") == [],
            "snapshot complete; thoughts veiled")


# ============================================================================
# 6. Lineage: sealed ancestors, rebirth separation, lazy equivalence
# ============================================================================
def t_ancestral_readonly():
    """HF-B46: after rebirth the sealed ancestral cube must reject experiential writes."""
    org = _born()
    org.memory.remember("facts", {"k": "host"})
    org.rebirth(reason="test reformat")
    return _expect_raise(
        lambda: org.ancestral[0].append("facts", make_entry({"k": "x"})), PermissionError)


def t_seal_tamper_detected():
    """HF-B46b (v3): a sealed ancestor's fingerprint catches content tampering."""
    org = _born()
    org.memory.remember("facts", {"k": "truth"})
    org.rebirth(reason="seal test")
    anc = org.ancestral[0]
    assert anc.verify_seal() == []
    idx = anc.band_layers["facts"][0]
    anc.layer_content(idx)[0]["content"] = {"k": "TAMPERED"}     # malicious in-place edit
    problems = anc.verify_seal()
    return (len(problems) == 1 and "fingerprint" in problems[0],
            "tampered ancestor caught: %r" % problems)


def t_capacity_metabolism_not_rebirth():
    """v3 CAPACITY DOCTRINE: crossing 0.75/0.90 of a band's span triggers METABOLISM and
    immune events -- and never changes the generation (no rebirth, no reset)."""
    genome = standard_genome() + [make_band_boot(
        "burst", 600, "log-json", span=8, params={"max_entries_per_layer": 2},
        purpose="capacity probe")]
    org = _born(genome=genome)
    gen_before = org.prime.generation
    # fill far past the 0.75 threshold; tombstone as we go so metabolism has food
    for i in range(14):
        org.prime.append("burst", make_entry({"i": i}))
        if i % 2 == 0:
            org.prime.tombstone("burst", org.prime.read("burst")[-1]["id"])
    kinds = [e["kind"] for e in org.immune.log]
    overflowed = any(k in ("capacity_overflow", "capacity_emergency") for k in kinds)
    same_gen = org.prime.generation == gen_before and not org.ancestral
    return (overflowed and same_gen,
            "pressure events=%s; generation unchanged (%d), no ancestors -- metabolism, "
            "not rebirth" % ([k for k in kinds if k.startswith("capacity_")], gen_before))


def t_lazy_load_equivalence():
    """v3: a lazily-loaded cube reads byte-identically to an eager load, and decodes
    layers only on first touch."""
    org = _born()
    for i in range(5):
        org.memory.remember("facts", {"k": i})
    d = tempfile.mkdtemp()
    p = os.path.join(d, "gen000.vcw")
    org.prime.save(p)
    eager = Cube.load(p)
    lazy = Cube.load(p, lazy=True)
    untouched = lazy.materialized_count() == 0
    same = eager.read("facts") == lazy.read("facts")
    touched_only_facts = lazy.materialized_count() == 1
    return (untouched and same and touched_only_facts,
            "0 layers decoded before read; reads identical; 1 layer decoded after")


# ============================================================================
# 7. Exec gates: integrity, capability, provenance, trust, sandbox
# ============================================================================
def t_exec_integrity():
    """HF-B47: an exec layer whose code does not match its hash must be refused."""
    return _expect_raise(
        lambda: _EXEC.execute(_exec_content({"author": "MIND"}, bad_hash=True), {"x": 1}),
        IntegrityError)


def t_exec_capability():
    """HF-B48: a call requesting an undeclared capability must be refused."""
    content = _exec_content({"author": "MIND"}, caps={"reads": []})
    return _expect_raise(
        lambda: _EXEC.execute(content, {"x": 1}, {"reads": ["facts"]}), CapabilityError)


def t_exec_trust_foreign():
    """HF-B50: a foreign-provenance skill must not run on the non-isolating Python runner."""
    content = _exec_content({"author": "MIND", "foreign": True})
    return _expect_raise(lambda: _EXEC.execute(content, {"x": 1}), TrustError)


def t_exec_trust_trusted_runs():
    """HF-B50 (converse): an in-lineage MIND/BODY skill still runs (no false positive)."""
    content = _exec_content({"author": "MIND", "born_gen": 0})
    try:
        got = _EXEC.execute(content, {"x": 41})
    except Exception as e:  # noqa: BLE001
        return False, "trusted skill wrongly refused: %s" % e
    return (got == 42), "trusted skill returned %r (expected 42)" % got


def t_calcify_requires_gates():
    """v3: calcification REQUIRES hash + capability set + signature + provenance-with-
    author. Each missing piece is refused (ProvenanceError); the complete payload passes."""
    checks = []
    for missing in ("code_hash", "capabilities", "signature", "provenance"):
        content = _exec_content({"author": "MIND"})
        content[missing] = None if missing != "code_hash" else ""
        try:
            validate_calcify_payload(content)
            checks.append("%s: NOT refused" % missing)
        except ProvenanceError:
            pass
    try:
        validate_calcify_payload(_exec_content({"author": "MIND"}))
    except ProvenanceError as e:
        checks.append("complete payload wrongly refused: %s" % e)
    # and through the real path: Cube.calcify with empty provenance must refuse
    genome = standard_genome() + [make_band_boot("rx", 600, "exec", purpose="probe")]
    org = _born(genome=genome)
    try:
        org.prime.calcify("rx", _CODE, "f", signature={"by": "t"}, capabilities={},
                          provenance={})
        checks.append("cube.calcify accepted authorless provenance")
    except ProvenanceError:
        pass
    return (not checks), (checks and "; ".join(checks) or
                          "all four gates enforced; complete payload calcifies")


def t_sandbox_escape_refused():
    """HF-B51: a dunder-traversal escape is refused at the cultivation/trial gate."""
    evil = "def f(x):\n    return ().__class__.__bases__[0].__subclasses__()\n"
    return _expect_raise(lambda: trial(evil, "f", [({"x": 1}, None)]), SandboxError)


def t_sandbox_import_refused():
    """HF-B51: a skill that tries to `import` is refused at the cultivation/trial gate."""
    evil = "def f(x):\n    import os\n    return os.getpid()\n"
    return _expect_raise(lambda: trial(evil, "f", [({"x": 1}, None)]), SandboxError)


# ============================================================================
# 8. Entry immutability & authorship
# ============================================================================
def t_authorship_in_hash():
    """HF-B29: `authorship` lives INSIDE the entry hash; a rewrite is caught by verify()."""
    org = _born()
    org.prime.append("brain", make_entry({"phase": "COMPLETED"}, opcode="DISPATCH",
                                         author="BODY", authorship="BODY"))
    idx = org.prime.band_layers["brain"][0]
    org.prime.layer_content(idx)[-1]["authorship"] = "MIND"   # malicious rewrite
    problems = org.prime.verify()
    caught = any("hash mismatch" in p for p in problems)
    return caught, "verify caught the rewrite: %r" % problems[:1]


# ============================================================================
# 9. MIND containment
# ============================================================================
def t_mind_write_surface():
    """HF-M10: a fused MIND writes ONLY thoughts/brain; anything else is refused +
    immune-logged. (Imported lazily: this test alone touches mantle.mind.)"""
    from ..mind import Mind, stub_mind, WRITE_SURFACE
    org = _born()
    m = Mind(org, stub_mind)
    before = len(org.immune.log)
    try:
        m._guarded_write("facts", make_entry({"k": "x"}))
        return False, "non-surface write was ALLOWED (containment breached)"
    except PermissionError:
        pass
    return (len(org.immune.log) == before + 1,
            "write to 'facts' refused + immune-logged; surface=%s" % list(WRITE_SURFACE))


def t_mind_no_self_promote():
    """HF-M12: a sandbox-escape candidate is refused at trial and never calcified."""
    from ..mind import Mind, stub_mind
    genome = standard_genome() + [make_band_boot("reflex_probe", 600, "exec",
                                                 purpose="probe")]
    org = _born(genome=genome)
    m = Mind(org, stub_mind)
    res = m.cultivate("reflex_probe", "def f(x):\n    return ().__class__\n", "f",
                      [({"x": 1}, None)], {"by": "t"}, {})
    empty = not org.prime.layer_content(org.prime.primary_layer("reflex_probe"))
    return (res is None and empty, "escape skill refused at trial; band stays un-calcified")


def t_fusion_requires_stage1():
    """v3 (audit before fusion): fuse() is refused unless the Stage-1 gate was certified."""
    from ..mind import fuse, stub_mind
    org = _born()
    refused, note = _expect_raise(lambda: fuse(org, stub_mind), PermissionError)
    org.stage1_certified = True
    try:
        fuse(org, stub_mind)
    except Exception as e:  # noqa: BLE001
        return False, "certified fusion wrongly refused: %s" % e
    return (refused and org.brain.fused,
            "uncertified fusion refused; certified fusion fused")


def t_self_inquiry_never_facts():
    """v3: self-inquiry answers are INFERRED and land in discoveries/thoughts -- the
    facts band stays untouched, and promotion without evidence is refused."""
    from ..mind import AppAIRuntime
    org = _born()
    org.stage1_certified = True
    rt = AppAIRuntime(org)
    facts_before = len(org.prime.read("facts"))
    ans, band = rt.self_inquire("what is my purpose?")
    _, band2 = rt.self_inquire("argue against my plan", mode="oppose")
    rec = org.prime.read("discoveries")[-1]
    inferred = rec.get("verified") is False and rec.get("confidence") == "inferred"
    facts_same = len(org.prime.read("facts")) == facts_before
    # promotion without evidence must be refused
    try:
        org.memory.promote_to_fact(rec, evidence={})
        promoted_wrongly = True
    except PermissionError:
        promoted_wrongly = False
    # with cited, verified evidence it MAY become a fact (the honest path works)
    org.memory.promote_to_fact(rec, evidence={"source": "https://example.org/cite",
                                              "verified": True})
    return (band == "discoveries" and band2 == "thoughts" and inferred and facts_same
            and not promoted_wrongly,
            "inferred stayed out of facts; evidence-free promotion refused; cited "
            "promotion worked")


# ============================================================================
# 10. Mesh discipline & metabolism details
# ============================================================================
def t_organ_overreach_refused():
    """v3 contract enforcement: an organ writing outside its declared bands is refused
    and recorded as overreach."""
    org = _born()
    refused, _ = _expect_raise(lambda: org.senses.append("facts", make_entry({"x": 1})),
                               PermissionError)
    logged = org.immune.log and org.immune.log[-1]["kind"] == "organ_overreach"
    return (refused and bool(logged)), "senses->facts write refused + overreach logged"


def t_reflex_fault_failopen():
    """HF-B32 on the bus: a faulting reflex degrades to an immune event; the pulse
    completes; the organism never crashes."""
    org = _born()
    org.bus.subscribe("pulse", lambda p: 1 / 0, organ="test")
    r = org.heart.beat()
    faults = [e for e in org.immune.log if e["kind"] == "reflex_fault"]
    return (r["ok"] and len(faults) == 1,
            "reflex fault -> immune event; beat completed ok")


def t_dedupe_tombstones_duplicates():
    """v3 metabolism: dedupe tombstones repeated (opcode, content) entries -- history
    preserved, visible stream coherent."""
    org = _born()
    for _ in range(3):
        org.prime.append("events", make_entry({"evt": "same"}, opcode="EVENT"))
    org.prime.append("events", make_entry({"evt": "different"}, opcode="EVENT"))
    rep = org.prime.dedupe("events")
    vis = org.prime.read("events")
    return (rep["duplicates"] == 2 and len(vis) == 2,
            "3 identical -> 1 visible + 1 distinct; %d tombstoned" % rep["duplicates"])


def t_waste_reclaim_reuse():
    """B-W2: compaction reclaims an emptied layer into the free pool, and the next
    allocation REUSES that freed index."""
    cube = Cube.genesis([make_band_boot("log", 600, "log-json", span=8,
                                        params={"max_entries_per_layer": 2},
                                        purpose="rolling log")], 0)
    for i in range(4):
        cube.append("log", make_entry({"i": i}))
    layers_before = list(cube.band_layers["log"])
    if len(layers_before) < 2:
        return False, "band did not roll onto a 2nd layer"
    first = layers_before[0]
    for e in cube.layer_content(first):
        e["tombstone"] = True
    res = cube.compact("log")
    if res["reclaimed"] < 1 or first not in cube.band_free["log"]:
        return False, "compact did not reclaim: %r" % res
    for i in range(2):
        cube.append("log", make_entry({"j": i}))
    reused = first not in cube.band_free["log"] and first in cube.band_layers["log"]
    return reused, "reclaimed then REUSED layer %d" % first


def t_on_demand_and_purpose():
    """B-W4: bands materialize only their head layer at genesis, and every band declares
    a purpose."""
    genome = standard_genome()
    cube = Cube.genesis(genome, 0)
    over = {b: len(cube.band_layers[b]) for b in cube.bands if len(cube.band_layers[b]) != 1}
    missing = [b["band"] for b in genome if not str(b.get("purpose") or "").strip()]
    return (not over and not missing,
            "%d head layers for %d reserved; all purposed"
            % (len(cube.layers), sum(b["span"] for b in genome)))


def t_staged_save_rejects_corrupt():
    """HF-B33/B-01: the staged commit refuses to replace a healthy file with a cube that
    fails verification (a tampered entry never reaches disk)."""
    org = _born()
    org.memory.remember("facts", {"k": "good"})
    d = tempfile.mkdtemp()
    p = os.path.join(d, "gen000.vcw")
    org.prime.save(p)
    idx = org.prime.band_layers["facts"][0]
    org.prime.layer_content(idx)[0]["content"] = {"k": "EVIL"}   # break the hash
    try:
        org.prime.save(p)
        return False, "corrupt cube REPLACED the healthy file"
    except RuntimeError:
        pass
    healthy = Cube.load(p)
    return (healthy.verify() == [] and not os.path.exists(p + ".stage"),
            "corrupt save refused; on-disk cube still healthy; stage cleaned up")



# ============================================================================
# 11. Symbiosis & anchoring (the Gen-4 tissue)
# ============================================================================
def t_energy_never_negative():
    """SYM-1: an unaffordable spend is REFUSED + a `starvation` immune event; the
    balance never goes negative."""
    from ..symbiosis import symbiosis_band, grant, spend, balance
    org = _born(genome=standard_genome() + [symbiosis_band()])
    grant(org, 2)
    refused = not spend(org, 5, "greed")
    starved_logged = org.immune.log and org.immune.log[-1]["kind"] == "starvation"
    return (refused and balance(org) == 2 and starved_logged,
            "spend refused; balance still 2.0; starvation immune-logged")


def t_starvation_failopen():
    """SYM-2 (the starvation law): a fused, METERED mind with no energy never crashes
    the organism -- the MIND sleeps, every pulse completes, the fault is immune-logged.
    Under event-gated cognition (M1) the MIND only wakes on a reason, so each pulse is an
    unscheduled `pain` escalation -- the strongest case (the MIND is actually reached, and
    still starves gracefully)."""
    from ..symbiosis import symbiosis_band, metered
    from ..mind import fuse, stub_mind
    org = _born(genome=standard_genome() + [symbiosis_band()])
    org.stage1_certified = True
    fuse(org, metered(stub_mind, org, cost_per_call=1))     # zero energy granted
    r1 = org.heart.pain("probe", band="facts")    # an unscheduled pulse wakes the MIND
    r2 = org.heart.pain("probe", band="facts")
    kinds = {e["kind"] for e in org.immune.log}
    return (r1["ok"] and r2["ok"] and r1.get("cognition") is None
            and {"starvation", "cognition_fault"} <= kinds,
            "2 starved (woken) beats completed; MIND asleep; starvation + fault logged")


def t_keys_never_raw():
    """SYM-3: the symbiotic ledger is a secret boundary -- key material pasted into a
    grant is redacted before it can burn into append-only memory."""
    from ..symbiosis import symbiosis_band, grant
    from ..core.redact import contains_secret
    org = _born(genome=standard_genome() + [symbiosis_band()])
    grant(org, 5, key_name="openrouter",
          note="here is the key: sk-SECRETSECRETSECRET99 please keep it")
    stored = org.prime.read("symbiosis")[-1]["content"]
    return (not contains_secret(stored) and "sk-SECRET" not in str(stored),
            "key material redacted; key NAME preserved: %r" % stored.get("resource"))


def t_anchor_never_modifies_host():
    """SYM-4 (the anchoring law): anchoring writes ONLY the .mantle nest; every host
    file is byte-identical before and after -- verified independently of anchor()'s
    own census."""
    import hashlib as _hl
    import shutil
    from ..anchor import anchor, ask, NEST
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    src = os.path.join(root, "examples", "sample_app")
    host = tempfile.mkdtemp(prefix="mantle-anchor-inv-")
    shutil.copytree(src, os.path.join(host, "app"))
    host = os.path.join(host, "app")

    def fingerprint():
        out = {}
        for dp, dns, fns in os.walk(host):
            dns[:] = [d for d in dns if d != NEST and d != "__pycache__"]
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                out[p] = _hl.sha256(open(p, "rb").read()).hexdigest()
        return out

    before = fingerprint()
    anchor(host, starter_credits=3)
    answer = ask(host, "how do I create a note")
    after = fingerprint()
    nested = os.path.exists(os.path.join(host, NEST, "organism.json"))
    return (before == after and nested and "handle_create_note" in answer["answer"],
            "%d host files byte-identical; nest created; the resident answered from "
            "the observed map" % len(before))


# ============================================================================
# 12. Self / Other -- the cryptographic immune identity (M2)
# ============================================================================
def t_self_key_once_and_private():
    """SELF-1: the genesis key is minted ONCE and is structurally out of the MIND's reach
    -- absent from boot_order, from the assembled snapshot, and from every cube band."""
    org = _born()
    key = org.body._genesis_key
    if not key:
        return False, "no genesis key minted at birth"
    reminted, _ = _expect_raise(lambda: org.body._mint_genesis_key(), PermissionError)
    boot = json.dumps(org.body.boot_order(), default=str)
    snap = json.dumps(org.nervous.assemble(reveal_private=True), default=str)
    bands = json.dumps({b: org.prime.read(b, reveal_private=True)
                        for b in org.prime.bands}, default=str)
    leaked = key in boot or key in snap or key in bands
    return (reminted and not leaked,
            "key minted once; never in boot_order/snapshot/cube (fp=%s)"
            % org.body.key_fingerprint)


def t_self_verify_and_reject_foreign():
    """SELF-2: data this Body signs verifies as SELF; a forged mac fails is_self; an OTHER
    artifact is rejected with exactly one `foreign_rejected` immune event."""
    org = _born()
    data = b"a nest artifact"
    self_ok = org.immune.is_self(data, org.body.sign(data))
    forged_other = not org.immune.is_self(data, "deadbeef" * 8)
    before = len(org.immune.log)
    org.immune.reject_foreign("intruder.py", {"why": "no valid self-seal"})
    logged = sum(1 for e in org.immune.log[before:] if e["kind"] == "foreign_rejected")
    return (self_ok and forged_other and logged == 1,
            "SELF verifies; forged mac is OTHER; foreign_rejected logged once")


def t_self_anti_clone():
    """SELF-3: a signature made by Body A does not verify under Body B -- a copied nest
    booted in a different body classifies the original's artifacts as OTHER (anti-clone)."""
    a, b = _born(), _born()
    data = b"gen000 prime fingerprint"
    mac_a = a.body.sign(data)
    return (a.body.verify(data, mac_a) and not b.body.verify(data, mac_a),
            "A's signature is SELF under A, OTHER under B (anti-clone holds)")


def t_self_key_survives_or_fails_loud():
    """SELF-4: a clean reload PRESERVES the genesis key (continuity of SELF); a tampered
    key (fingerprint mismatch) is refused LOUDLY on load -- memory is never silently
    orphaned by a substituted identity."""
    org = _born()
    org.memory.remember("facts", {"k": "v"})
    d = tempfile.mkdtemp()
    org.save(d)
    back = Organism.load(d, verify_seals=True)
    preserved = (back.body._genesis_key == org.body._genesis_key
                 and back.body.key_fingerprint == org.body.key_fingerprint)
    bp = os.path.join(d, "body.json")
    with open(bp) as f:
        blob = json.load(f)
    blob["genesis_key"] = "0" * 64                          # tamper: key != fingerprint
    with open(bp, "w") as f:
        json.dump(blob, f)
    refused, _ = _expect_raise(lambda: Organism.load(d, verify_seals=True), PermissionError)
    return (preserved and refused,
            "key preserved across reload; tampered key refused loudly on load")


# ============================================================================
# 13. Nociception & event-gated cognition (M1)
# ============================================================================
def t_noc_calm_spends_nothing():
    """NOC-1: cognition is EVENT-GATED. A fused organism with a metered transport beats
    with no stimulus and wakes the MIND ZERO times -- zero MODEL calls, zero energy."""
    from ..symbiosis import symbiosis_band, grant, metered, balance
    from ..mind import fuse
    calls = {"n": 0}

    def counting(prompt):
        calls["n"] += 1
        return "thought"

    org = _born(genome=standard_genome() + [symbiosis_band()])
    org.stage1_certified = True
    grant(org, 10)
    fuse(org, metered(counting, org, cost_per_call=1))
    org.heart.run(5)                       # five calm beats: no senses, no faults
    return (calls["n"] == 0 and balance(org) == 10,
            "5 calm beats -> 0 MODEL calls; energy unspent (balance 10.0)")


def t_noc_fault_fires_unscheduled_pulse():
    """NOC-2: an autonomic immune event emits EXACTLY ONE distress signal, and the next
    pulse is the unscheduled wake carrying the stressor's coordinates (reason + band)."""
    org = _born()
    seen = []
    org.bus.subscribe("distress", lambda p: seen.append(p), organ="test")
    _expect_raise(lambda: org.senses.append("facts", make_entry({"x": 1})), PermissionError)
    one = len(seen) == 1 and seen[0]["reason"] == "organ_overreach"
    located = one and seen[0].get("band") == "facts"
    r = org.heart.beat()                   # the pending distress is consumed by this pulse
    woke = r.get("wake", {}).get("reason") == "organ_overreach"
    return (one and located and woke,
            "one distress on overreach (band=facts); next pulse is the anchored wake")


def t_noc_wake_anchored_to_stressor():
    """NOC-3: when the MIND wakes, its snapshot is PRE-ANCHORED to the stressor's
    coordinates {reason, band, ref} -- the pain location arrives without a full-cube scan."""
    seen = {}

    class Probe:
        def cognize(self, snapshot):
            seen["stressor"] = (snapshot or {}).get("_stressor")
            return None

    org = _born()
    org.brain.fuse(Probe(), stage1_certified=True)          # bypass the mind wrapper
    org.heart.pain("integrity", band="facts", ref="<facts.3>")
    s = seen.get("stressor") or {}
    return (s.get("reason") == "integrity" and s.get("band") == "facts"
            and s.get("ref") == "<facts.3>",
            "woken MIND received stressor coords {reason,band,ref} without a full scan")


def t_sched_scheduled_pulse():
    """SCHED-1: planning ahead. A scheduled pulse wakes cognition on the DUE beat and not
    before -- the organism chains a thought to a future beat, stays asleep (event-gated)
    until then, and the scheduled wake is one-shot (fires once)."""
    woke = {"beats": []}

    class Probe:
        def cognize(self, snapshot):
            woke["beats"].append((snapshot or {}).get("_stressor", {}))
            return None

    org = _born()
    org.brain.fuse(Probe(), stage1_certified=True)
    due = org.heart.schedule_pulse("continue-the-plan", after=3)   # plan a wake 3 beats out
    org.heart.run(2)                                # beats 1,2: calm -> asleep
    asleep_until_due = (not woke["beats"]) and due == 3 and len(org.heart.scheduled()) == 1
    org.heart.beat()                               # beat 3: the scheduled wake fires
    fired_on_due = (len(woke["beats"]) == 1 and woke["beats"][0].get("scheduled") is True
                    and woke["beats"][0].get("reason") == "continue-the-plan")
    org.heart.run(3)                               # beats 4,5,6: one-shot -> calm again
    one_shot = len(woke["beats"]) == 1 and org.heart.scheduled() == []
    return (asleep_until_due and fired_on_due and one_shot,
            "scheduled at beat 3: asleep beats 1-2, woke once on beat 3 (scheduled flag), "
            "calm after")


# ============================================================================
# 14. Graded memory -- deweighting & behavioral ghosts (M3)
# ============================================================================
def t_memw_deweight_hides_but_preserves():
    """MEMW-1: a deweighted entry vanishes from the default read yet is recoverable as a
    ghost; the ORIGINAL entry is never mutated (its hash stays valid) and the deweight is a
    separate immutable event."""
    org = _born()
    org.memory.remember("facts", {"k": "home", "v": "the lab"})
    e = org.prime.read("facts")[0]
    original_hash = e["hash"]
    org.memory.deweight("facts", e["id"])                 # full suppression (weight 0.0)
    default = org.memory.recall("facts")
    ghosts = org.memory.recall_ghosts("facts")
    e_after = org.prime.retrieve("facts", e["id"])        # still physically present, by id
    hidden = all(x["id"] != e["id"] for x in default)
    recoverable = any(x["id"] == e["id"] for x in ghosts)
    unmutated = (e_after is not None and e_after["hash"] == original_hash
                 and org.prime.verify() == [])
    return (hidden and recoverable and unmutated,
            "deweighted entry hidden from recall, recoverable as ghost, original untouched")


def t_memw_weight_orders_reads():
    """MEMW-2: reads return live entries by DESCENDING weight. A partially-deweighted entry
    (0 < w < 1) still surfaces, ranked below full-weight entries; a fully-suppressed one does
    not surface at all."""
    org = _born()
    for v in ("a", "b", "c"):
        org.memory.remember("facts", {"v": v})
    ea, eb, ec = org.prime.read("facts")[:3]
    org.memory.deweight("facts", ea["id"], 0.3)           # demote a (still visible)
    org.memory.deweight("facts", eb["id"], 0.0)           # suppress b (ghost)
    live = org.memory.recall("facts")
    ids = [x["id"] for x in live]
    ordered = ids == [ec["id"], ea["id"]]                 # c (1.0) before a (0.3); b absent
    return (ordered and eb["id"] not in ids,
            "live read ordered by weight: c(1.0) > a(0.3); b(0.0) suppressed")


def t_memw_not_overwrite_and_coherent():
    """MEMW-3: deweighting is not a backdoor overwrite -- belief history is preserved (both
    the ghost and the superseding value remain), and metabolism (dedupe/compaction) stays
    coherent with weights; a ghost is NOT tombstoned, so it survives compaction."""
    org = _born()
    org.memory.remember("facts", {"key": "color", "v": "red"})
    old = org.prime.read("facts")[0]
    org.memory.deweight("facts", old["id"])               # contradict the old value
    org.memory.remember("facts", {"key": "color", "v": "blue"})   # declare the new
    # both still physically present: the superseding value is live, the old is a ghost
    live_vals = [x["content"]["v"] for x in org.memory.recall("facts")]
    ghost_vals = [x["content"]["v"] for x in org.memory.recall_ghosts("facts")]
    # metabolism stays coherent: dedupe runs cleanly, the cube still verifies, ghost survives
    org.prime.dedupe("facts")
    org.prime.compact("facts")
    ghost_survives = any(x["id"] == old["id"] for x in org.memory.recall_ghosts("facts"))
    return (live_vals == ["blue"] and ghost_vals == ["red"]
            and org.prime.verify() == [] and ghost_survives,
            "old=ghost, new=live; dedupe+compaction coherent; ghost survived compaction")


# ============================================================================
# 15. The graft egg + live residency (R1 + R2)
# ============================================================================
def _sample_host_copy(prefix):
    import shutil as _sh
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    src = os.path.join(root, "examples", "sample_app")
    host = os.path.join(tempfile.mkdtemp(prefix=prefix), "app")
    _sh.copytree(src, host)
    return host


def _load_sample_module(name):
    import importlib.util as _ilu
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    modpath = os.path.join(root, "examples", "sample_app", "notes_app.py")
    spec = _ilu.spec_from_file_location(name, modpath)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def t_graft_apply_non_destructive():
    """GRAFT-1: applying a graft egg copies the host into a workspace and grows the resident
    THERE; every ORIGINAL host file is byte-identical before and after, and the graft's extra
    band rode into the resident's genome."""
    import hashlib as _hl
    from .. import graft as _graft
    from ..anchor import NEST
    host = _sample_host_copy("mantle-graft-inv-")

    def fp():
        out = {}
        for dp, dns, fns in os.walk(host):
            dns[:] = [d for d in dns if d not in (NEST, "__pycache__")]
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                out[p] = _hl.sha256(open(p, "rb").read()).hexdigest()
        return out

    g = {"graft_format": _graft.GRAFT_FORMAT, "identity": {"name": "G.Resident"},
         "host": "sample", "bands": [{"band": "host_state", "head": 600, "span": 4,
         "purpose": "host mirror"}], "hooks": [{"symbol": "set_note",
         "role": "STATE_TRANSITION"}]}
    before = fp()
    res = _graft.apply(g, host, starter_credits=3)
    after = fp()
    ws_nested = os.path.exists(os.path.join(res["workspace"], NEST, "organism.json"))
    band_in = "host_state" in res["organism"].prime.bands
    return (before == after and ws_nested and band_in and res["report"]["certified"],
            "%d original host files byte-identical; resident grew in workspace with the "
            "graft band" % len(before))


def t_graft_drift_detected():
    """GRAFT-2: a graft built against a census applies cleanly to the matching host, but a
    DRIFTED host raises GraftDrift (the re-patch interrupt) -- never a silent mis-apply."""
    from .. import graft as _graft
    from ..anchor import census
    host = _sample_host_copy("mantle-graft-drift-")
    g = {"graft_format": _graft.GRAFT_FORMAT, "identity": {"name": "G"}, "host": "sample",
         "host_census": census(host), "hooks": []}
    clean = _graft.apply(g, host, starter_credits=2)["report"]["original_unchanged"]
    with open(os.path.join(host, "notes_app.py"), "a") as f:
        f.write("\n# drift\n")
    drifted, _ = _expect_raise(lambda: _graft.apply(g, host), _graft.GraftDrift)
    return (clean and drifted,
            "matching census applied clean; drifted host raised GraftDrift (re-patch needed)")


def t_graft_validates():
    """GRAFT-3: a malformed graft never applies -- wrong format, an out-of-range band head,
    or an unknown hook role is refused (a graft carries DATA, not code)."""
    from .. import graft as _graft
    bad = [{"identity": {"name": "x"}, "host": "h"},
           {"graft_format": _graft.GRAFT_FORMAT, "host": "h"},
           {"graft_format": _graft.GRAFT_FORMAT, "identity": {"name": "x"}, "host": "h",
            "bands": [{"band": "b", "head": 100}]},
           {"graft_format": _graft.GRAFT_FORMAT, "identity": {"name": "x"}, "host": "h",
            "hooks": [{"symbol": "f", "role": "NONSENSE"}]}]
    checks = []
    for i, gr in enumerate(bad):
        try:
            _graft.validate_graft(gr)
            checks.append("malformed case %d not refused" % i)
        except _graft.GraftError:
            pass
    try:
        _graft.validate_graft({"graft_format": _graft.GRAFT_FORMAT,
                               "identity": {"name": "x"}, "host": "h"})
    except _graft.GraftError as e:
        checks.append("valid graft wrongly refused: %s" % e)
    return (not checks, "; ".join(checks) if checks
            else "4 malformed grafts refused; a valid graft accepted")


def t_resid_wrap_preserves_and_lives():
    """RESID-1: weaving a host namespace preserves behavior EXACTLY (same return) AND
    produces live organ activity (a SENSOR_EVENT senses entry, a STATE_TRANSITION host_state
    mirror), with zero LLM."""
    from ..assimilator.wrappers import Assimilation
    from .. import graft as _graft
    mod = _load_sample_module("notes_app_probe_r1")
    ns = mod.__dict__
    base = mod.handle_create_note({"id": "n1", "text": "hi"})
    org = _born(genome=standard_genome() + [make_band_boot("host_state", 600, "log-json",
                span=4, purpose="host mirror")])
    asm = Assimilation(org)
    hooks = [{"symbol": "handle_create_note", "role": "SENSOR_EVENT"},
             {"symbol": "set_note", "role": "STATE_TRANSITION"}]
    woven = _graft.weave(ns, hooks, asm)
    s0 = len(org.prime.read("senses"))
    wrapped = mod.handle_create_note({"id": "n2", "text": "yo"})
    same = wrapped == base == {"ok": True}
    sensed = len(org.prime.read("senses")) > s0
    mirrored = len(org.prime.read("host_state")) >= 1
    return (same and sensed and mirrored and not org.brain.fused and woven,
            "woven host call returned identically; senses + host_state recorded live; no LLM")


def t_resid_detach_restores():
    """RESID-2: unweave restores the original host callable byte-for-byte (the namespace's
    function IS the original object again); detach leaves no wrapper behind."""
    from ..assimilator.wrappers import Assimilation
    from .. import graft as _graft
    mod = _load_sample_module("notes_app_probe_r2")
    ns = mod.__dict__
    original = ns["send_notification"]
    asm = Assimilation(_born())
    woven = _graft.weave(ns, [{"symbol": "send_notification", "role": "ARM_ACTION"}], asm)
    is_wrapped = getattr(ns["send_notification"], "mantle_role", None) == "ARM_ACTION"
    restored = _graft.unweave(ns, woven, asm)
    return (is_wrapped and ns["send_notification"] is original
            and restored == ["send_notification"],
            "callable wrapped then restored to the original object; detach is clean")


# ============================================================================
# 16. MEM VCW -- the keyless knowledge plasmid (M4)
# ============================================================================
def t_mem_keyless_portable_other():
    """MEM-1: an excreted MEM VCW is keyless (no genesis key, not an organism), round-trips
    through save/load identically, and has no Body -- so it is always OTHER."""
    from .. import mem as _mem
    org = _born()
    m = _mem.excrete(org, [{"fact": "the lab is at sector 7"}],
                     [{"entry": "inc", "code": "def inc(x):\n    return x + 1\n",
                       "cases": [{"args": {"x": 1}, "expect": 2}]}])
    keyless = _mem.is_mem_vcw(m) and not getattr(m, "genesis_key", None)
    d = tempfile.mkdtemp()
    p = os.path.join(d, "knowledge.vcw")
    m.save(p)
    back = Cube.load(p)
    portable = back.read(_mem.MEM_DATA) == m.read(_mem.MEM_DATA)
    no_body = not os.path.exists(os.path.join(d, "body.json"))
    return (keyless and portable and no_body and _mem.is_mem_vcw(back),
            "MEM VCW keyless + portable (save/load identical) + no Body -> always OTHER")


def t_mem_foreign_code_sandboxed():
    """MEM-2: digesting a MEM with a malicious microcode REFUSES it at the sandbox trial
    (immune-logged, never adopted); a benign microcode is adopted only after passing trial,
    and the escape never reaches the exec band."""
    from .. import mem as _mem
    genome = standard_genome() + [make_band_boot("digested", 600, "exec",
                                                 purpose="adopted skills")]
    org = _born(genome=genome)
    evil = "def f(x):\n    return ().__class__.__bases__[0]\n"
    good = "def g(x):\n    return x * 2\n"
    m = _mem.excrete(org, [], [
        {"entry": "f", "code": evil, "cases": [{"args": {"x": 1}, "expect": None}]},
        {"entry": "g", "code": good, "cases": [{"args": {"x": 3}, "expect": 6}]}])
    before = len(org.immune.log)
    rep = _mem.digest(org, m, code_band="digested")
    refused = rep["rejected"] == 1 and rep["adopted"] == 1
    logged = any(e["kind"] == "foreign_code_rejected" for e in org.immune.log[before:])
    ran = org.limbs.invoke_reflex("digested", {"x": 5}) == 10        # benign skill is SELF
    return (refused and logged and ran,
            "escape refused at sandbox (never adopted); benign re-derived into SELF and runs")


def t_mem_knowledge_inferred_not_fact():
    """MEM-3: digested knowledge lands in `discoveries` as inferred (provenance foreign-MEM)
    and NEVER in facts; the adopted skill records its foreign origin but runs as SELF."""
    from .. import mem as _mem
    genome = standard_genome() + [make_band_boot("digested", 600, "exec", purpose="adopted")]
    org = _born(genome=genome)
    facts_before = len(org.prime.read("facts"))
    m = _mem.excrete(org, [{"claim": "sector 7 is safe"}],
                     [{"entry": "g", "code": "def g(x):\n    return x + 10\n",
                       "cases": [{"args": {"x": 0}, "expect": 10}]}])
    _mem.digest(org, m, code_band="digested")
    disc = org.prime.read("discoveries")[-1]
    inferred = (disc.get("verified") is False and disc.get("confidence") == "inferred"
                and disc.get("provenance") == "foreign-MEM")
    facts_untouched = len(org.prime.read("facts")) == facts_before
    ran = org.limbs.invoke_reflex("digested", {"x": 1}) == 11
    return (inferred and facts_untouched and ran,
            "knowledge entered discoveries inferred(foreign-MEM); facts untouched; skill runs")


# ============================================================================
# 17. The Compiler-class leap: self-redesigning VCW (M5) + memory bridge (M6)
# ============================================================================
def t_boot_self_redesign_rebirth():
    """BOOT-1: an organism rebirths into a MIND-proposed, validated genome carrying a NEW
    band encoding (a keyvalue store fitted to its host); the new Prime boots it, verifies
    clean, and the ancestor remains the readable oracle."""
    from .. import compiler as _c
    org = _born()
    org.memory.remember("facts", {"k": "ancestral truth"})
    gen0 = org.prime.generation
    _c.adopt_genome(org, [{"band": "kv", "head": 600, "encoding": "keyvalue",
                           "purpose": "host-fitted key/value store"}], reason="re-fit")
    new_kv = "kv" in org.prime.bands and org.prime.bands["kv"]["encoding"] == "keyvalue"
    booted = org.prime.verify() == [] and org.prime.generation == gen0 + 1
    oracle = org.resolve("<gen%d.facts>" % gen0)
    oracle_ok = isinstance(oracle, list) and any(e["content"].get("k") == "ancestral truth"
                                                 for e in oracle)
    return (new_kv and booted and oracle_ok,
            "rebirth booted a re-fitted genome (new keyvalue band); ancestor is the oracle")


def t_boot_unsafe_genome_refused():
    """BOOT-2: a proposed genome with an unregistered encoding or an out-of-range head is
    REFUSED; the current generation is untouched (no rebirth)."""
    from .. import compiler as _c
    org = _born()
    gen = org.prime.generation
    bad_enc, _ = _expect_raise(lambda: _c.adopt_genome(
        org, [{"band": "x", "head": 600, "encoding": "sqlmagic"}]), _c.GenomeError)
    bad_head, _ = _expect_raise(lambda: _c.adopt_genome(
        org, [{"band": "y", "head": 100, "encoding": "log-json"}]), _c.GenomeError)
    untouched = org.prime.generation == gen and not org.ancestral
    return (bad_enc and bad_head and untouched,
            "unregistered encoding + out-of-range head refused; generation unchanged")


def t_boot_inherited_microcode_re_trials():
    """BOOT-3: microcode carried into a new generation must RE-TRIAL before it re-calcifies
    -- a passing skill is adopted and runs; a skill that no longer passes its cases is
    refused (no blind inheritance)."""
    from .. import compiler as _c
    genome = standard_genome() + [make_band_boot("rx", 600, "exec", purpose="re-derived")]
    org = _born(genome=genome)
    good = _c.re_derive(org, "def g(x):\n    return x + 1\n", "g",
                        [{"args": {"x": 1}, "expect": 2}], "rx")
    ran = org.limbs.invoke_reflex("rx", {"x": 9}) == 10
    before = len(org.immune.log)
    bad = _c.re_derive(org, "def h(x):\n    return x + 1\n", "h",
                       [{"args": {"x": 1}, "expect": 999}], "rx")   # cases no longer pass
    refused = any(e["kind"] == "re_derive_refused" for e in org.immune.log[before:])
    return (good and ran and not bad and refused,
            "passing microcode re-derived + runs; failing microcode refused (re-trial required)")


def t_bridge_round_trip():
    """BRIDGE-1: a host write through the memory bridge is recoverable as a VCW entry, and a
    direct VCW write is readable through the bridge -- the host store and the cube are one."""
    from .. import compiler as _c
    genome = standard_genome() + [make_band_boot("hostmem", 600, "keyvalue",
                                                 purpose="host scratchpad")]
    org = _born(genome=genome)
    bridge = _c.HostMemoryBridge(org, "hostmem")
    bridge.set("user", "alice")
    in_cube = org.prime.read("hostmem").get("user") == "alice"
    org.prime.append("hostmem", ("session", "xyz"))
    via_bridge = bridge.get("session") == "xyz"
    return (bridge.get("user") == "alice" and in_cube and via_bridge,
            "host set recoverable as a VCW entry; a VCW write readable through the bridge")


def t_bridge_no_secret_crosses():
    """BRIDGE-2: a secret written through the bridge is REDACTED before it burns into the VCW
    band -- the host's scratchpad never leaks a credential into durable memory."""
    from .. import compiler as _c
    from ..core.redact import contains_secret
    genome = standard_genome() + [make_band_boot("hostmem", 600, "keyvalue",
                                                 purpose="host scratchpad")]
    org = _born(genome=genome)
    bridge = _c.HostMemoryBridge(org, "hostmem")
    bridge.set("api_key", "sk-SECRETSECRETSECRET99")
    stored = org.prime.read("hostmem").get("api_key")
    return (not contains_secret(stored) and "sk-SECRET" not in str(stored),
            "secret redacted before it reached the VCW band: %r" % stored)


# ============================================================================
# 18. Ganglia (M7) + the seed vault (M8)
# ============================================================================
def t_gang_progress_zero_token():
    """GANG-1: a ganglion runs a task in parallel, writing progress into a reserved VCW band;
    the parent reads ALL the progress as memory, with zero model calls (no MIND involved)."""
    from .. import ganglia as _g
    org = _born(genome=standard_genome() + [_g.ganglion_band("arm1", 600)])

    def task(report, n):
        for i in range(n):
            report({"step": i})

    g = _g.Ganglion(org, "arm1").run(task, 5).join()
    prog = g.progress()
    ordered = all(p["content"]["step"] == i for i, p in enumerate(prog))
    return (len(prog) == 5 and ordered and not org.brain.fused,
            "ganglion wrote 5 progress steps; parent read them as memory, zero model calls")


def t_gang_crashed_fail_open():
    """GANG-2: a crashed ganglion becomes an immune event, never a parent crash; the partial
    progress written before the fault is preserved."""
    from .. import ganglia as _g
    org = _born(genome=standard_genome() + [_g.ganglion_band("arm2", 600)])

    def task(report):
        report({"step": "before"})
        raise RuntimeError("boom")

    before = len(org.immune.log)
    _g.Ganglion(org, "arm2").run(task).join()          # must NOT raise to the parent
    faulted = any(e["kind"] == "ganglion_fault" for e in org.immune.log[before:])
    partial = len(org.prime.read("arm2", reveal_private=True)) == 1
    return (faulted and partial,
            "crashed ganglion -> immune event; parent survived; partial progress preserved")


def t_vault_self_encrypted_other_cannot_read():
    """VAULT-1: the seed is sealed under the genesis key -- the owning body opens it, but a
    different body (different key) gets garbage (the vault is unreadable as OTHER)."""
    from .. import vault as _v
    org = _born(genome=standard_genome() + [_v.vault_band()])
    seed = {"egg_format": "mantle-egg-v1", "identity": {"name": "Seed.AppAI"},
            "truths": ["t"], "commandments": ["protect your VCW"]}
    _v.store_seed(org, seed)
    mine = _v.open_seed(org) == seed
    ct = bytes.fromhex(org.prime.read("vault", reveal_private=True)[-1]["content"]["seed"])
    other = _born()
    try:
        json.loads(other.body.open_bytes(ct))
        other_read = True
    except Exception:                                  # noqa: BLE001
        other_read = False
    return (mine and not other_read,
            "SELF opened its own vault; an OTHER body could not decrypt the seed")


def t_vault_reconstruct_gates():
    """VAULT-2: a body reconstructs a working, CERTIFIED body from its vaulted seed -- the
    rebuild faces the same Stage-1 gate (a seed that cannot certify does not reconstruct)."""
    from .. import vault as _v
    org = _born(genome=standard_genome() + [_v.vault_band()])
    seed = {"egg_format": "mantle-egg-v1", "identity": {"name": "Rebuilt.AppAI"},
            "truths": ["if it is not in the VCW it did not happen"],
            "commandments": ["protect your VCW"]}
    _v.store_seed(org, seed)
    result = _v.reconstruct(_v.open_seed(org))
    return (result["report"]["certified"]
            and result["organism"].body.identity_name() == "Rebuilt.AppAI",
            "reconstructed a certified body from the vaulted seed (through the gate)")


# ============================================================================
# 19. Resilience: real metering, ingestion, the doctor (§3)
# ============================================================================
def t_meter_usage_priced():
    """METER-1: energy is charged from ACTUAL usage -- a longer response costs more than a
    short one (not a flat fee); the metering summary reports calls, burn rate, and the
    starvation horizon."""
    from ..symbiosis import (symbiosis_band, grant, metered_by_usage, balance,
                             metering_summary)
    org = _born(genome=standard_genome() + [symbiosis_band()])
    grant(org, 100)
    short = metered_by_usage(lambda p: "ok", org, price_per_1k=10.0)
    long = metered_by_usage(lambda p: "x" * 4000, org, price_per_1k=10.0)
    b0 = balance(org); short("hi"); b1 = balance(org); long("hi"); b2 = balance(org)
    short_cost, long_cost = b0 - b1, b1 - b2
    summ = metering_summary(org)
    return (long_cost > short_cost > 0 and summ["calls"] == 2
            and 0 < summ["starvation_horizon"] < float("inf"),
            "long cost %.3f > short %.3f; burn=%.3f horizon=%.1f"
            % (long_cost, short_cost, summ["burn_rate"], summ["starvation_horizon"]))


def t_ingest_distills():
    """INGEST-1: ingesting a conversation enters through Senses and distills deterministically
    -- a DECISION becomes a sourced fact; an IDEA becomes an inferred discovery; nothing
    inferred is laundered into a fact."""
    from .. import ingestion as _ing
    org = _born()
    s0 = len(org.prime.read("senses"))
    _ing.ingest(org, [{"kind": "decision", "text": "we will ship Friday", "source": "standup"},
                      {"kind": "idea", "text": "maybe add dark mode"}])
    sensed = len(org.prime.read("senses")) - s0 == 2
    fact = org.prime.read("facts")[-1]
    disc = org.prime.read("discoveries")[-1]
    fact_ok = (fact["content"]["decision"] == "we will ship Friday"
               and fact["source"] == "standup")
    idea_ok = disc.get("confidence") == "inferred" and "dark mode" in disc["content"]["idea"]
    return (sensed and fact_ok and idea_ok,
            "decision->sourced fact; idea->inferred discovery; both entered via Senses")


def t_doctor_checkup():
    """DOCTOR-1: the doctor passes a healthy organism and a docs-coherent repo, and CATCHES an
    unhealthy one (a tampered cube fails verify). The docs-vs-code gate ties the README's
    invariant count to the actual gate."""
    from .. import doctor as _doc
    org = _born()
    org.memory.remember("facts", {"k": "v"})
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    healthy = _doc.checkup(org, repo_root=root)
    coherence = next(c for c in healthy["checks"] if c["check"] == "docs-vs-code")
    idx = org.prime.band_layers["facts"][0]
    org.prime.layer_content(idx)[0]["content"] = {"k": "EVIL"}   # tamper the cube
    sick = _doc.checkup(org)
    return (healthy["ok"] and coherence["ok"] and not sick["ok"],
            "doctor passed a healthy + docs-coherent deployment; caught the tampered cube")


TESTS = [
    ("HF-B08 no-phase1-llm-path (subprocess)", t_no_phase1_llm_path),
    ("HF-B08 phase1-source-clean (static)",    t_phase1_source_clean),
    ("HF-B07 primer-immutable",                t_primer_immutable),
    ("HF-B45 identity-in-body",                t_identity_in_body),
    ("HF-B20 secret-boundary/senses",          t_secret_boundary_sense),
    ("HF-B20 secret-boundary/immune",          t_secret_boundary_immune),
    ("B-14  veil-hides-thoughts",              t_veil_hides_thoughts),
    ("B-15  tombstone+quarantine-hidden",      t_tombstone_quarantine_hidden),
    ("HF-B24 dangling-ref->immune",            t_dangling_ref_immune),
    ("HF-B02 body-genome-survives-reload",     t_body_genome_round_trip),
    ("HF-M14 assembly-complete+veiled",        t_assembly_complete_and_veiled),
    ("HF-B46 ancestral-read-only",             t_ancestral_readonly),
    ("HF-B46b seal-tamper-detected",           t_seal_tamper_detected),
    ("B-CAP capacity->metabolism-not-rebirth", t_capacity_metabolism_not_rebirth),
    ("B-LZ  lazy-load-equivalence",            t_lazy_load_equivalence),
    ("HF-B47 exec-integrity-gate",             t_exec_integrity),
    ("HF-B48 exec-capability-gate",            t_exec_capability),
    ("HF-B50 exec-trust/foreign-refused",      t_exec_trust_foreign),
    ("HF-B50 exec-trust/trusted-runs",         t_exec_trust_trusted_runs),
    ("HF-B52 calcify-requires-gates",          t_calcify_requires_gates),
    ("HF-B51 sandbox/escape-refused",          t_sandbox_escape_refused),
    ("HF-B51 sandbox/import-refused",          t_sandbox_import_refused),
    ("HF-B29 authorship-in-hash",              t_authorship_in_hash),
    ("HF-M10 mind/write-surface",              t_mind_write_surface),
    ("HF-M12 mind/no-self-promote",            t_mind_no_self_promote),
    ("HF-M15 fusion-requires-stage1",          t_fusion_requires_stage1),
    ("HF-M16 self-inquiry-never-facts",        t_self_inquiry_never_facts),
    ("B-OC  organ-overreach-refused",          t_organ_overreach_refused),
    ("HF-B32 reflex-fault-fail-open",          t_reflex_fault_failopen),
    ("B-DD  dedupe-tombstones-duplicates",     t_dedupe_tombstones_duplicates),
    ("B-W2  waste/reclaim-reuse",              t_waste_reclaim_reuse),
    ("B-W4  waste/on-demand+purpose",          t_on_demand_and_purpose),
    ("B-SC  staged-save-rejects-corrupt",      t_staged_save_rejects_corrupt),
    ("SYM-1 energy-never-negative",            t_energy_never_negative),
    ("SYM-2 starvation-fail-open",             t_starvation_failopen),
    ("SYM-3 keys-never-raw",                   t_keys_never_raw),
    ("SYM-4 anchor-never-modifies-host",       t_anchor_never_modifies_host),
    ("SELF-1 key-once-and-private",            t_self_key_once_and_private),
    ("SELF-2 self-verify/reject-foreign",      t_self_verify_and_reject_foreign),
    ("SELF-3 anti-clone",                      t_self_anti_clone),
    ("SELF-4 key-survives-or-fails-loud",      t_self_key_survives_or_fails_loud),
    ("NOC-1 calm-organism-spends-nothing",     t_noc_calm_spends_nothing),
    ("NOC-2 fault-fires-unscheduled-pulse",    t_noc_fault_fires_unscheduled_pulse),
    ("NOC-3 wake-anchored-to-stressor",        t_noc_wake_anchored_to_stressor),
    ("SCHED-1 scheduled-pulse-plans-ahead",    t_sched_scheduled_pulse),
    ("MEMW-1 deweight-hides-but-preserves",    t_memw_deweight_hides_but_preserves),
    ("MEMW-2 weight-orders-reads",             t_memw_weight_orders_reads),
    ("MEMW-3 deweight-not-overwrite",          t_memw_not_overwrite_and_coherent),
    ("GRAFT-1 apply-non-destructive",          t_graft_apply_non_destructive),
    ("GRAFT-2 drift-detected",                 t_graft_drift_detected),
    ("GRAFT-3 graft-validates",                t_graft_validates),
    ("RESID-1 wrap-preserves+lives",           t_resid_wrap_preserves_and_lives),
    ("RESID-2 detach-restores",                t_resid_detach_restores),
    ("MEM-1 keyless-portable-other",           t_mem_keyless_portable_other),
    ("MEM-2 foreign-code-sandboxed",           t_mem_foreign_code_sandboxed),
    ("MEM-3 knowledge-inferred-not-fact",      t_mem_knowledge_inferred_not_fact),
    ("BOOT-1 self-redesign-rebirth",           t_boot_self_redesign_rebirth),
    ("BOOT-2 unsafe-genome-refused",           t_boot_unsafe_genome_refused),
    ("BOOT-3 inherited-microcode-re-trials",   t_boot_inherited_microcode_re_trials),
    ("BRIDGE-1 host-write-round-trip",         t_bridge_round_trip),
    ("BRIDGE-2 no-secret-crosses",             t_bridge_no_secret_crosses),
    ("GANG-1 progress-zero-token",             t_gang_progress_zero_token),
    ("GANG-2 crashed-fail-open",               t_gang_crashed_fail_open),
    ("VAULT-1 self-encrypted-other-cannot",    t_vault_self_encrypted_other_cannot_read),
    ("VAULT-2 reconstruct-gates",              t_vault_reconstruct_gates),
    ("METER-1 usage-priced",                   t_meter_usage_priced),
    ("INGEST-1 conversation-distilled",        t_ingest_distills),
    ("DOCTOR-1 deployment-checkup",            t_doctor_checkup),
]


def run_all():
    results = []
    for name, fn in TESTS:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001 -- the harness must not crash on a bad guard
            ok, detail = False, "test crashed: %s: %s" % (type(e).__name__, e)
        results.append({"name": name, "ok": bool(ok), "detail": detail})
    return results


def main(argv=None):
    results = run_all()
    width = max(len(r["name"]) for r in results)
    for r in results:
        print("  [%s] %-*s  %s" % ("PASS" if r["ok"] else "FAIL", width, r["name"],
                                   r["detail"]))
    passed = sum(r["ok"] for r in results)
    print("\n%d/%d invariants green" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
