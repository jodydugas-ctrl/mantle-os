#!/usr/bin/env python3
"""
mantle.audits.invariants  --  executable security invariants (Mantle v3)

Every doctrine guarantee as a red/green assertion. Each test maps to a hard-fail code and
proves the guard actually FIRES (and, where relevant, that the permitted path still
works). Pure standard library, no pytest:

    python -m mantle prove          # run all; exit 0 = all green

Importable: run_all() returns result dicts so the Stage-1/Stage-2 gates fold these in.
NO INVARIANT IS EVER WEAKENED TO MAKE A TEST PASS.
"""
from __future__ import annotations

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
