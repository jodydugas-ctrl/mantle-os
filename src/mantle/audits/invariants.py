#!/usr/bin/env python3
"""
mantle.audits.invariants  --  executable security invariants (Mantle OS)

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

from .. import paths
from ..core.body import Body
from ..core.organism import Organism
from ..core.redact import contains_secret
from ..core.audit import expect_raise as _expect_raise
from ..vcw.bands import standard_genome, make_band_boot
from ..vcw.cube import Cube
from ..vcw.entry import make_entry
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


def _try_symlink(target, link_name, *, target_is_directory=False):
    try:
        os.symlink(target, link_name, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError) as exc:
        return False, "%s: %s" % (type(exc).__name__, exc)
    return True, ""


def _fusion_approval(org):
    """Explicit dual-authority fixture; technical readiness never mints authority."""
    return {
        "target": {"resident_identity": org.body.identity_name()},
        "operator": {"fusion_decision": "APPROVED"},
        "guardian": {"fusion_decision": "APPROVED"},
        "effective_decision": {"mind_fusion_authorized": True},
    }


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
    root = paths.REPO_ROOT
    env = {**os.environ, "PYTHONPATH": paths.SRC_DIR}
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                         cwd=root, env=env, timeout=120)
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
    """HF-B46b: a sealed ancestor's fingerprint catches content tampering."""
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
    """CAPACITY DOCTRINE: crossing 0.75/0.90 of a band's span triggers METABOLISM and
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
    """a lazily-loaded cube reads byte-identically to an eager load, and decodes
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
    """calcification REQUIRES hash + capability set + signature + provenance-with-
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
    from ..mind import AppAIRuntime, Mind, stub_mind, WRITE_SURFACE
    org = _born()
    m = Mind(org, stub_mind)
    before = len(org.immune.log)
    try:
        m._guarded_write("facts", make_entry({"k": "x"}))
        return False, "non-surface write was ALLOWED (containment breached)"
    except PermissionError:
        pass
    special_before = list(org.body.category("special"))
    steering_refused = _expect_raise(
        lambda: AppAIRuntime(org).propose_special_instruction("model-requested"),
        PermissionError,
    )[0]
    return (len(org.immune.log) == before + 1 and steering_refused
            and org.body.category("special") == special_before,
            "write to 'facts' refused + immune-logged; pre-fusion steering refused; "
            "surface=%s" % list(WRITE_SURFACE))


def t_mind_no_self_promote():
    """HF-M12: skill proposals are trialed and calcified only through proven Limbs."""
    from ..mind import fuse, stub_mind
    genome = standard_genome() + [make_band_boot("reflex_probe", 600, "exec",
                                                 purpose="probe")]
    org = _born(genome=genome)
    org.stage1_certified = True
    m = fuse(org, stub_mind, authorization=_fusion_approval(org))
    refused = m.cultivate(
        "reflex_probe", "def f(x):\n    return ().__class__\n", "f",
        [({"x": 1}, None)], {"by": "t"}, {},
    )
    empty_after_refusal = not org.prime.layer_content(
        org.prime.primary_layer("reflex_probe")
    )
    accepted = m.cultivate(
        "reflex_probe", _CODE, "f", [({"x": 1}, 2)], {"by": "t"}, {},
    )
    proofs = [
        entry["content"]["action_proof"]
        for entry in org.prime.read("brain", reveal_private=True)
        if isinstance(entry.get("content"), dict)
        and isinstance(entry["content"].get("action_proof"), dict)
        and entry["content"]["action_proof"].get("control") == "mind.cultivate"
    ]
    return (
        refused is None
        and empty_after_refusal
        and accepted is not None
        and len(proofs) == 2
        and proofs[0].get("ok") is False
        and proofs[1].get("ok") is True,
        "escape refused and valid candidate calcified through two BODY-authored Limbs proofs",
    )


def t_fusion_requires_stage1():
    """HF-M15: fusion requires technical certification AND two explicit authorities."""
    from ..mind import fuse, stub_mind
    org = _born()
    before_stage1 = _expect_raise(
        lambda: fuse(org, stub_mind, authorization=_fusion_approval(org)),
        PermissionError,
    )[0]
    org.stage1_certified = True
    no_authority = _expect_raise(lambda: fuse(org, stub_mind), PermissionError)[0]
    one_authority = _fusion_approval(org)
    one_authority["guardian"]["fusion_decision"] = "DEFERRED"
    guardian_deferred = _expect_raise(
        lambda: fuse(org, stub_mind, authorization=one_authority), PermissionError
    )[0]
    wrong_target = _fusion_approval(org)
    wrong_target["target"]["resident_identity"] = "Other.AppAI"
    target_refused = _expect_raise(
        lambda: fuse(org, stub_mind, authorization=wrong_target), PermissionError
    )[0]
    with tempfile.TemporaryDirectory(prefix="hermes-verify-stage1-freshness-") as td:
        org.save(td)
        reloaded = Organism.load(td)
        persisted_is_not_fresh = (
            not reloaded.stage1_certified
            and _expect_raise(
                lambda: fuse(
                    reloaded,
                    stub_mind,
                    authorization=_fusion_approval(reloaded),
                ),
                PermissionError,
            )[0]
        )
    try:
        fuse(org, stub_mind, authorization=_fusion_approval(org))
    except Exception as e:  # noqa: BLE001
        return False, "certified, dual-approved fusion wrongly refused: %s" % e
    return (before_stage1 and no_authority and guardian_deferred and target_refused
            and persisted_is_not_fresh and org.brain.fused,
            "uncertified, persisted-stale, unapproved, one-role, and wrong-target fusion "
            "refused; freshly certified dual-approved fusion fused")


def t_bugfix_runtime_boundaries():
    """BUGFIX-1: confirmed runtime edges remain fail-open/refused."""
    import html as _html
    import time as _time
    from ..anchor import anchor, ask, NEST
    from ..core.events import SignalBus
    from ..symbiosis import symbiosis_band, grant, metered_by_usage, StarvationError
    from ..vcw.drivers import ExecDriver
    from .. import spore as _spore
    from ..hatchery import _default_face_stub
    from ..mind import fuse, stub_mind

    checks = []

    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, "app.py"), "w", encoding="utf-8") as f:
            f.write("def main():\n    return 42\n")
        anchor(td, starter_credits=5)
        meta_path = os.path.join(td, NEST, "organism.json")
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        meta["stage1_certified"] = False
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f)
        body_path = os.path.join(td, NEST, "body.json")
        with open(body_path, encoding="utf-8") as f:
            body = json.load(f)
        body["primer"] = []
        with open(body_path, "w", encoding="utf-8") as f:
            json.dump(body, f)
        calls = {"n": 0}

        def model(_prompt):
            calls["n"] += 1
            return "should not run"

        result = ask(td, "what is this?", use_mind=True, model=model)
        checks.append(("ask-stage1", calls["n"] == 0
                       and "Stage-1 gate refused" in result["thought"]))

    code = "def f():\n    while True:\n        pass\n"
    content = {"code": code, "code_hash": code_hash(code), "entry": "f",
               "capabilities": {}, "signature": {"by": "test"},
               "limits": {"ms": 50}, "provenance": {"author": "MIND"}}
    started = _time.time()
    timed_out = _expect_raise(lambda: ExecDriver().execute(content, {}), TimeoutError)[0]
    checks.append(("exec-timeout", timed_out and (_time.time() - started) < 2.0))

    class Handler:
        def on_signal(self, _payload):
            return None
    bus = SignalBus()
    h = Handler()
    bus.subscribe("x", h.on_signal, organ="bound")
    checks.append(("bound-method-bus", bus.reflex_surface().get("x") == ["bound"]))

    org = _born(genome=standard_genome() + [symbiosis_band()])
    org.memory.remember("facts", {"k": "v"})
    before = len(org.immune.log)
    checks.append(("malformed-ref", org.resolve("<facts.1x2>") is None
                   and len(org.immune.log) == before + 1
                   and org.immune.log[-1]["kind"] == "malformed_ref"))

    grant(org, 0.001)
    usage_calls = {"n": 0}

    def paid_model(_prompt):
        usage_calls["n"] += 1
        return "x" * 4000

    refused_usage = _expect_raise(
        lambda: metered_by_usage(paid_model, org, price_per_1k=10.0)("prompt"),
        StarvationError)[0]
    checks.append(("usage-preauth", refused_usage and usage_calls["n"] == 0))

    phase = _born()
    refused_intent = _expect_raise(lambda: phase.limbs.intend({"x": 1}), PermissionError)[0]
    phase.stage1_certified = True
    fuse(phase, stub_mind, authorization=_fusion_approval(phase))
    e = phase.limbs.delegate({"x": 2})
    checks.append(("mind-dispatch", refused_intent and e.get("authorship") == "MIND"
                   and e.get("content", {}).get("phase") == "DELEGATED"))

    prefix = _spore.MAGIC + bytes([_spore.FORMAT_VERSION]) \
        + (_spore.VCW_CAPACITY_BYTES).to_bytes(4, "big")

    class FakePixels:
        def __getitem__(self, xy):
            x, y = xy
            i = y * _spore.VCW_W + x
            chunk = prefix[i * 3:i * 3 + 3].ljust(3, b"\0")
            r, g, b = chunk
            return r, g, b, _spore.compute_T(r, g, b)

    class FakeImage:
        def load(self):
            return FakePixels()

    checks.append(("spore-header",
                   _expect_raise(lambda: _spore.decode_pixels(FakeImage()), ValueError)[0]))

    old_image = _spore.Image
    try:
        _spore.Image = None
        state = {"identity": {"spore_name": "x", "task": "t"}, "conversation": []}
        pillow_refused = _expect_raise(
            lambda: _spore.render_spore(state, os.path.join(tempfile.gettempdir(), "x.png")),
            RuntimeError)[0]
    finally:
        _spore.Image = old_image
    checks.append(("spore-pillow", pillow_refused))

    egg = {"identity": {"name": "<script>x</script>", "purpose": "<b>p</b>"},
           "controls": [{"id": "\" onclick=\"x", "label": "<b>Click</b>"}]}
    src = _default_face_stub(egg)["source"]
    checks.append(("face-escape", "<script>" not in src and "<b>" not in src
                   and _html.escape(egg["identity"]["name"]) in src))

    failed = [name for name, ok in checks if not ok]
    return (not failed, "runtime boundary checks green"
            if not failed else "failed: %s" % ", ".join(failed))


def t_self_inquiry_never_facts():
    """self-inquiry answers are INFERRED and land in discoveries/thoughts -- the
    facts band stays untouched, and promotion without evidence is refused."""
    from ..mind import AppAIRuntime, fuse, stub_mind
    org = _born()
    rt = AppAIRuntime(org)
    pre_fusion_refused = _expect_raise(
        lambda: rt.self_inquire("too early"), PermissionError
    )[0]
    org.stage1_certified = True
    fuse(org, stub_mind, authorization=_fusion_approval(org))
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
    proofs = [
        entry["content"]["action_proof"]
        for entry in org.prime.read("brain", reveal_private=True)
        if isinstance(entry.get("content"), dict)
        and isinstance(entry["content"].get("action_proof"), dict)
        and entry["content"]["action_proof"].get("control") == "mind.discovery"
    ]
    return (pre_fusion_refused and band == "discoveries" and band2 == "thoughts"
            and inferred and facts_same and not promoted_wrongly
            and len(proofs) == 1 and proofs[0].get("ok") is True,
            "pre-fusion inquiry refused; inferred discovery routed through Limbs; "
            "evidence-free promotion refused; cited promotion worked")


# ============================================================================
# 10. Mesh discipline & metabolism details
# ============================================================================
def t_organ_overreach_refused():
    """contract enforcement: an organ writing outside its declared bands is refused
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


def t_limb_structured_bridge_proof():
    """LIMB-1: a ControlBridge can return the effector's own verified proof.
    The Limbs organ must not promote an attempted-but-unverified UI action to ok=True
    merely because the bridge returned normally."""
    org = _born()

    def unverified_bridge(_value):
        return {
            "attempted": True,
            "ok": False,
            "method": "HostEditorBridge",
            "ref": "editor_surface",
            "reason": "editor-text-not-verified",
            "verification": "failed-editor-text-readback",
        }

    org.limbs.register_control("editor.display", {"kind": "editor"}, unverified_bridge)
    proof = org.limbs.operate("editor.display", "story")
    recorded = [
        entry["content"]["action_proof"]
        for entry in org.prime.read("brain", reveal_private=True)
        if isinstance(entry.get("content"), dict)
        and isinstance(entry["content"].get("action_proof"), dict)
        and entry["content"]["action_proof"].get("control") == "editor.display"
    ][-1]
    ok = (
        proof["attempted"] is True
        and proof["ok"] is False
        and proof["reason"] == "editor-text-not-verified"
        and recorded["verification"] == "failed-editor-text-readback"
    )
    return ok, "attempted UI bridge remained failed until surface read-back verified it"


def t_dedupe_tombstones_duplicates():
    """metabolism: dedupe tombstones repeated (opcode, content) entries -- history
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
    """HF-B33/B-01: hostile VCW inputs fail closed and a failed staged commit never
    replaces a healthy cube or leaves a reusable shared-stage artifact."""
    import struct
    import zlib
    from ..vcw.cube import _decode_layer_payload, _validate_container_meta
    from ..vcw.png import (CHANNELS, LAYER_BYTES, MAX_PNG_BYTES, PNG_SIGNATURE, SIDE,
                           _png_chunk, build_layer_rgba, decode_png_rgba, encode_png_rgba,
                           parse_layer_rgba)

    layer = build_layer_rgba(
        {"band": "facts", "layer": 150, "encoding": "log-json", "private": False},
        {"content": []},
    )
    valid_png = encode_png_rgba(layer)
    codec_round_trip = decode_png_rgba(valid_png) == layer

    bad_crc = bytearray(valid_png)
    bad_crc[29] ^= 1                              # first byte of the IHDR CRC
    crc_refused = _expect_raise(lambda: decode_png_rgba(bad_crc), ValueError)[0]
    dimensions_refused = _expect_raise(
        lambda: decode_png_rgba(encode_png_rgba(b"\0" * CHANNELS, 1, 1)), ValueError
    )[0]
    truncated_refused = _expect_raise(
        lambda: decode_png_rgba(valid_png[:-1]), ValueError
    )[0]
    oversized_refused = _expect_raise(
        lambda: decode_png_rgba(PNG_SIGNATURE + b"x" * MAX_PNG_BYTES), ValueError
    )[0]

    ihdr = struct.pack(">IIBBBBB", SIDE, SIDE, 8, 6, 0, 0, 0)
    expanded = b"\0" * (((SIDE * CHANNELS + 1) * SIDE) + 1)
    bomb = (PNG_SIGNATURE + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(expanded, 9))
            + _png_chunk(b"IEND", b""))
    bomb_refused = _expect_raise(lambda: decode_png_rgba(bomb), ValueError)[0]

    bad_layer = bytearray(layer)
    bad_layer[8:12] = struct.pack(">I", LAYER_BYTES)
    layer_bounds_refused = _expect_raise(
        lambda: parse_layer_rgba(bad_layer), ValueError
    )[0]
    binding_refused = _expect_raise(
        lambda: _decode_layer_payload(
            build_layer_rgba(
                {"band": "events", "layer": 150, "encoding": "log-json",
                 "private": False, "v": 2},
                {"content": []},
            ),
            "facts", 150,
            {"band": "facts", "encoding": "log-json", "private": False},
        ),
        ValueError,
    )[0]

    org = _born()
    org.memory.remember("facts", {"k": "good"})
    d = tempfile.mkdtemp()
    p = os.path.join(d, "gen000.vcw")
    org.prime.save(p)
    hostile_meta = json.loads(json.dumps(org.prime._meta()))
    hostile_meta["bands"]["facts"]["span"] = 100
    topology_refused = _expect_raise(
        lambda: _validate_container_meta(hostile_meta), ValueError
    )[0]
    idx = org.prime.band_layers["facts"][0]
    org.prime.layer_content(idx)[0]["content"] = {"k": "EVIL"}   # break the hash
    try:
        org.prime.save(p)
        return False, "corrupt cube REPLACED the healthy file"
    except RuntimeError:
        pass
    healthy = Cube.load(p)
    debris = [name for name in os.listdir(d) if name.startswith(".mantle-vcw-stage-")]
    png_guards = all((codec_round_trip, crc_refused, dimensions_refused,
                      truncated_refused, oversized_refused, bomb_refused,
                      layer_bounds_refused, binding_refused, topology_refused))
    return (healthy.verify() == [] and not debris and png_guards,
            "hostile PNG/layer inputs refused; corrupt save refused; healthy cube intact; "
            "unique stage cleaned up")


def t_organism_save_atomic_owner_only():
    """PERSIST-1: every nest artifact is owner-only and failed JSON staging leaves the
    previous checkpoint intact with no temporary debris or symlink traversal."""
    import stat
    from pathlib import Path
    from ..core.persist import atomic_write_json

    org = _born()
    org.memory.remember("facts", {"k": "durable"})
    with tempfile.TemporaryDirectory() as td:
        nest = os.path.join(td, "nest")
        org.save(nest)
        fixture_notes = []
        paths_ = [os.path.join(nest, name) for name in os.listdir(nest)]
        if os.name == "nt":
            fixture_notes.append("POSIX owner-only mode bits unavailable on nt")
            owner_only = True
        else:
            owner_only = (stat.S_IMODE(os.stat(nest).st_mode) == 0o700
                          and all(stat.S_IMODE(os.stat(path).st_mode) == 0o600
                                  for path in paths_ if os.path.isfile(path)))
        body_path = os.path.join(nest, "body.json")
        before = Path(body_path).read_bytes()
        refused = _expect_raise(
            lambda: atomic_write_json(body_path, {"not_json": {1, 2}}), TypeError
        )[0]
        intact = Path(body_path).read_bytes() == before
        debris = [name for name in os.listdir(nest) if name.startswith(".mantle-stage-")]
        outside = os.path.join(td, "outside")
        os.mkdir(outside, 0o755)
        linked_nest = os.path.join(td, "linked-nest")
        linked_nest_created, note = _try_symlink(
            outside, linked_nest, target_is_directory=True
        )
        if linked_nest_created:
            symlink_root_refused = _expect_raise(
                lambda: org.save(linked_nest), OSError
            )[0]
        else:
            fixture_notes.append("root symlink unavailable (%s)" % note)
            symlink_root_refused = True
        linked_artifact = os.path.join(nest, "linked.json")
        linked_artifact_created, note = _try_symlink(body_path, linked_artifact)
        if linked_artifact_created:
            symlink_artifact_refused = _expect_raise(
                lambda: atomic_write_json(linked_artifact, {"safe": True}), OSError
            )[0]
        else:
            fixture_notes.append("artifact symlink unavailable (%s)" % note)
            symlink_artifact_refused = True

        nested_target = os.path.join(td, "nested-target")
        os.mkdir(nested_target, 0o700)
        nested_link = os.path.join(nest, "nested-link")
        nested_link_created, note = _try_symlink(
            nested_target, nested_link, target_is_directory=True
        )
        if nested_link_created:
            nested_parent_refused = _expect_raise(
                lambda: atomic_write_json(
                    os.path.join(nested_link, "escaped.json"), {"safe": True}
                ),
                OSError,
            )[0]
            nested_parent_contained = not os.path.exists(
                os.path.join(nested_target, "escaped.json")
            )
        else:
            fixture_notes.append("nested symlink unavailable (%s)" % note)
            nested_parent_refused = True
            nested_parent_contained = True

        descriptor_root = os.path.join(td, "descriptor-root")
        descriptor_sibling = os.path.join(td, "descriptor-sibling")
        os.mkdir(descriptor_root, 0o700)
        os.mkdir(descriptor_sibling, 0o700)
        if os.name == "posix" and os.path.isdir("/proc/self/fd"):
            descriptor_fd = os.open(
                descriptor_root,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
            )
            try:
                descriptor_escape = (
                    f"/proc/self/fd/{descriptor_fd}/../descriptor-sibling/escaped.json"
                )
                descriptor_escape_refused = _expect_raise(
                    lambda: atomic_write_json(descriptor_escape, {"safe": True}),
                    OSError,
                )[0]
                descriptor_escape_contained = not os.path.exists(
                    os.path.join(descriptor_sibling, "escaped.json")
                )
                descriptor_valid = f"/proc/self/fd/{descriptor_fd}/nested/valid.json"
                atomic_write_json(descriptor_valid, {"safe": True})
                descriptor_positive = json.loads(
                    Path(descriptor_root, "nested", "valid.json").read_text(
                        encoding="utf-8"
                    )
                ) == {"safe": True}
            finally:
                os.close(descriptor_fd)
        else:
            fixture_notes.append("descriptor /proc/self/fd unavailable")
            descriptor_escape_refused = True
            descriptor_escape_contained = True
            descriptor_positive = True

        from unittest.mock import patch
        from ..core import persist as persist_module

        race_parent = os.path.join(td, "race-parent")
        race_outside = os.path.join(td, "race-outside")
        race_moved = os.path.join(td, "race-parent-moved")
        os.mkdir(race_parent, 0o700)
        os.mkdir(race_outside, 0o700)
        real_replace = os.replace
        swapped = False

        def swap_before_replace(src, dst, *args, **kwargs):
            nonlocal swapped
            if not swapped:
                swapped = True
                os.rename(race_parent, race_moved)
                os.symlink(race_outside, race_parent)
                outside_stage = os.path.join(race_outside, os.path.basename(src))
                Path(outside_stage).write_text("attacker", encoding="utf-8")
            return real_replace(src, dst, *args, **kwargs)

        if linked_nest_created:
            with patch.object(persist_module.os, "replace", swap_before_replace):
                _expect_raise(
                    lambda: atomic_write_json(
                        os.path.join(race_parent, "checkpoint.json"), {"safe": True}
                    ),
                    OSError,
                )
            race_contained = not os.path.exists(
                os.path.join(race_outside, "checkpoint.json")
            )
        else:
            fixture_notes.append("parent-swap symlink unavailable")
            race_contained = True

        checks = {
            "owner_only": owner_only,
            "serialization_refused": refused,
            "prior_bytes_intact": intact,
            "no_stage_debris": not debris,
            "symlink_root_refused": symlink_root_refused,
            "symlink_artifact_refused": symlink_artifact_refused,
            "nested_parent_refused": nested_parent_refused,
            "nested_parent_contained": nested_parent_contained,
            "descriptor_escape_refused": descriptor_escape_refused,
            "descriptor_escape_contained": descriptor_escape_contained,
            "descriptor_positive": descriptor_positive,
            "parent_swap_contained": race_contained,
        }
        failed_checks = [name for name, ok in checks.items() if not ok]
        return (
            not failed_checks,
            "nest=0700; artifacts=0600; failed staging preserves prior bytes; "
            "root/artifact/nested symlinks and descriptor '..' escape refused; "
            "descriptor-backed write passed; parent-swap remained descriptor-contained; "
            f"fixture_notes={fixture_notes}; failed_checks={failed_checks}",
        )



# ============================================================================
# 11. Symbiosis & anchoring (the self-regulating tissue)
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
    Every fused natural pulse reaches the metered MIND. Explicit `pain` pulses additionally
    prove that an unscheduled escalation still starves gracefully."""
    from ..symbiosis import symbiosis_band, metered
    from ..mind import fuse, stub_mind
    org = _born(genome=standard_genome() + [symbiosis_band()])
    org.stage1_certified = True
    fuse(org, metered(stub_mind, org, cost_per_call=1),
         authorization=_fusion_approval(org))               # zero energy granted
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
    from ..anchor import anchor, ask, NEST
    host = _sample_host_copy("mantle-anchor-inv-")

    def fingerprint():
        out = {}
        for dp, dns, fns in os.walk(host):
            dns[:] = [d for d in dns if d != NEST and d != "__pycache__"]
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                with open(p, "rb") as stream:
                    out[p] = _hl.sha256(stream.read()).hexdigest()
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
# 13. Natural cognition heartbeat + additional nociception (M1)
# ============================================================================
def t_noc_calm_spends_nothing():
    """NOC-1: every natural fused heartbeat calls the MIND, even when the Body is calm."""
    from ..symbiosis import symbiosis_band, grant, metered, balance
    from ..mind import fuse
    calls = {"n": 0}

    def counting(prompt):
        calls["n"] += 1
        return "thought"

    org = _born(genome=standard_genome() + [symbiosis_band()])
    org.stage1_certified = True
    grant(org, 10)
    fuse(org, metered(counting, org, cost_per_call=1),
         authorization=_fusion_approval(org))
    org.heart.run(5)                       # five calm beats: no senses, no faults
    return (calls["n"] == 5 and balance(org) == 5,
            "5 calm natural beats -> 5 MODEL calls; baseline cognition is unconditional")


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
    org.brain.fuse(Probe(), stage1_certified=True,
                   authorization=_fusion_approval(org))     # bypass the mind wrapper
    org.heart.pain("integrity", band="facts", ref="<facts.3>")
    s = seen.get("stressor") or {}
    return (s.get("reason") == "integrity" and s.get("band") == "facts"
            and s.get("ref") == "<facts.3>",
            "woken MIND received stressor coords {reason,band,ref} without a full scan")


def t_sched_scheduled_pulse():
    """SCHED-1: a scheduled stressor annotates only its due heartbeat and is one-shot;
    baseline cognition continues on every natural heartbeat before and after it."""
    woke = {"beats": []}

    class Probe:
        def cognize(self, snapshot):
            woke["beats"].append((snapshot or {}).get("_stressor", {}))
            return None

    org = _born()
    org.stage1_certified = True
    org.brain.fuse(Probe(), stage1_certified=True,
                   authorization=_fusion_approval(org))
    due = org.heart.schedule_pulse("continue-the-plan", after=3)   # plan a wake 3 beats out
    org.heart.run(2)
    baseline_before_due = (len(woke["beats"]) == 2 and not any(woke["beats"])
                           and due == 3 and len(org.heart.scheduled()) == 1)
    org.heart.beat()
    fired_on_due = (len(woke["beats"]) == 3 and woke["beats"][2].get("scheduled") is True
                    and woke["beats"][2].get("reason") == "continue-the-plan")
    org.heart.run(3)
    one_shot = (len(woke["beats"]) == 6 and not any(woke["beats"][3:])
                and org.heart.scheduled() == [])
    return (baseline_before_due and fired_on_due and one_shot,
            "baseline cognition ran on all 6 beats; only beat 3 carried the one-shot "
            "scheduled stressor")


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
    root = paths.REPO_ROOT
    src = os.path.join(root, "examples", "sample_app")
    host = os.path.join(tempfile.mkdtemp(prefix=prefix), "app")
    if os.path.isdir(src):
        _sh.copytree(src, host)
    else:
        os.makedirs(host)
        with open(os.path.join(host, "notes_app.py"), "w", encoding="utf-8") as stream:
            stream.write(
                "NOTES = {}\n"
                "def set_note(note_id, text):\n"
                "    NOTES[note_id] = text\n"
                "def handle_create_note(request):\n"
                "    set_note(request['id'], request['text'])\n"
                "    return {'ok': True}\n"
                "def send_notification(user, message):\n"
                "    return {'sent_to': user, 'message': message}\n"
            )
        with open(os.path.join(host, "notes_app.js"), "w", encoding="utf-8") as stream:
            stream.write("export const notes = new Map();\n")
    return host


def _load_sample_module(name):
    import importlib.util as _ilu
    host = _sample_host_copy("mantle-module-probe-")
    modpath = os.path.join(host, "notes_app.py")
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
                with open(p, "rb") as stream:
                    out[p] = _hl.sha256(stream.read()).hexdigest()
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
    from ..organs import reproduction as _v
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
    from ..organs import reproduction as _v
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


def t_or_cache_usage_receipt():
    """OR-CACHE-1: cache usage receipts normalize cache reads/writes, cost, session,
    generation id, and response-cache headers without raw prompt text."""
    from ..mind.usage import normalize_usage, stable_session_id
    sid = stable_session_id("bodyfingerprint", "planner", "task-" + ("x" * 300))
    body = {
        "id": "gen-body",
        "model": "openrouter/test",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 7,
            "total_tokens": 107,
            "cost": 0.012,
            "prompt_tokens_details": {
                "cached_tokens": 80,
                "cache_write_tokens": 20,
            },
            "cost_details": {"upstream_inference_cost": 0.01},
        },
    }
    generation = {"data": {"cache_discount": 0.004, "provider_name": "FakeProvider",
                           "router": "openrouter/auto", "total_cost": 0.012,
                           "session_id": sid}}
    rec = normalize_usage(body, headers={"X-OpenRouter-Cache-Status": "MISS",
                                         "X-OpenRouter-Cache-TTL": "300",
                                         "X-Generation-Id": "gen-header"},
                          generation=generation, session_id=sid,
                          request_hash="reqhash", stable_prefix_hash="stable",
                          dynamic_suffix_hash="dynamic", lane="planner")
    ok = (len(sid) <= 256 and rec["cached_tokens"] == 80
          and rec["cache_write_tokens"] == 20 and rec["cost"] == 0.012
          and rec["total_cost"] == 0.012 and rec["cache_discount"] == 0.004
          and rec["response_cache_status"] == "MISS"
          and rec["generation_id"] == "gen-header"
          and "HUGE PROMPT" not in json.dumps(rec))
    return ok, "receipt normalized cache/cost/session fields; session_id len=%d" % len(sid)


def t_or_transport_sidecars_and_canonical_body():
    """OR-CACHE-2: the transport preserves `model(prompt)->text` while adding session_id,
    response-cache headers, canonical JSON, and sidecar usage."""
    import urllib.request as _urlreq
    from ..mind.transport import openai_compatible_model
    from ..mind.usage import canonical_json_bytes

    calls = []
    old = _urlreq.urlopen

    class _Resp:
        headers = {"X-OpenRouter-Cache-Status": "HIT",
                   "X-OpenRouter-Cache-TTL": "299",
                   "X-Generation-Id": "gen-hit"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({
                "id": "gen-hit", "model": "fake/model",
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
                          "prompt_tokens_details": {"cached_tokens": 0,
                                                    "cache_write_tokens": 0},
                          "cost": 0.0},
            }).encode("utf-8")

    def fake_urlopen(req, timeout=0):
        calls.append(req)
        return _Resp()

    try:
        _urlreq.urlopen = fake_urlopen
        model = openai_compatible_model(
            "sk-test", "fake/model", url="https://example.invalid/chat",
            system="stable laws", session_id="mantle:body:planner:task",
            response_cache=True, response_cache_ttl=300, lane="planner")
        answer = model("dynamic question")
    finally:
        _urlreq.urlopen = old

    payload = json.loads(calls[0].data.decode("utf-8"))
    headers = {k.lower(): v for k, v in calls[0].headers.items()}
    canonical = calls[0].data == canonical_json_bytes(payload)
    rec = model.last_usage
    ok = (answer == "ok" and canonical
          and payload["session_id"] == "mantle:body:planner:task"
          and headers.get("x-openrouter-cache") == "true"
          and headers.get("x-openrouter-cache-ttl") == "300"
          and rec["response_cache_status"] == "HIT"
          and rec["generation_id"] == "gen-hit"
          and rec["request_hash"] == model.last_request_hash)
    return ok, "transport sidecars captured cache HIT + canonical request body"


def t_or_ghost_http_receipt():
    """OR-CACHE-3: HttpPromptCache captures richer cache/cost telemetry and uses the same
    canonical request body without a real provider."""
    import urllib.request as _urlreq
    from ..ghost_http import HttpPromptCache
    from ..mind.usage import canonical_json_bytes

    calls = []
    old = _urlreq.urlopen

    class _Resp:
        headers = {"X-OpenRouter-Cache-Status": "MISS",
                   "X-OpenRouter-Cache-TTL": "300",
                   "X-Generation-Id": "gen-miss"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({
                "id": "gen-miss", "model": "fake/model",
                "choices": [{"message": {"content": ""}}],
                "usage": {"prompt_tokens": 1200, "completion_tokens": 1,
                          "total_tokens": 1201, "cost": 0.03,
                          "prompt_tokens_details": {"cached_tokens": 0,
                                                    "cache_write_tokens": 1200}},
            }).encode("utf-8")

    def fake_urlopen(req, timeout=0):
        calls.append(req)
        return _Resp()

    try:
        _urlreq.urlopen = fake_urlopen
        sub = HttpPromptCache("https://example.invalid/chat", "fake/model",
                              headers={"Authorization": "Bearer sk-test"},
                              session_id="mantle:body:ghost:task",
                              response_cache=True, response_cache_ttl=300)
        sub.warm("k", b"stable-prefix")
    finally:
        _urlreq.urlopen = old

    payload = json.loads(calls[0].data.decode("utf-8"))
    headers = {k.lower(): v for k, v in calls[0].headers.items()}
    rec = sub.last_usage or {}
    ok = (calls[0].data == canonical_json_bytes(payload)
          and payload["session_id"] == "mantle:body:ghost:task"
          and headers.get("x-openrouter-cache") == "true"
          and rec.get("cache_write_tokens") == 1200
          and rec.get("cost") == 0.03
          and rec.get("response_cache_status") == "MISS"
          and sub.last_generation_id == "gen-miss")
    return ok, "ghost_http receipt captured cache write/cost/MISS telemetry"


def t_meter_receipt_zero_cost_cache_hit():
    """OR-CACHE-4: receipt metering records a zero-cost response-cache HIT as an audited
    call without reducing energy."""
    from ..symbiosis import symbiosis_band, grant, metered_by_receipt, balance
    org = _born(genome=standard_genome() + [symbiosis_band()])
    grant(org, 5)

    def cached_model(prompt):
        cached_model.last_usage = {
            "response_cache_status": "HIT", "prompt_tokens": 0,
            "completion_tokens": 0, "total_tokens": 0, "cost": 0.0,
            "total_cost": 0.0, "request_hash": "abc123",
        }
        return "ok"
    cached_model.last_usage = None

    before = balance(org)
    out = metered_by_receipt(cached_model, org, max_cost=1.0)("hello")
    after = balance(org)
    spends = [e for e in org.prime.read("symbiosis") if e["opcode"] == "SPEND"]
    stored = json.dumps(spends[-1]["content"], default=str) if spends else ""
    ok = (out == "ok" and before == after and spends
          and spends[-1]["content"]["credits"] == 0.0
          and "cache hit" in spends[-1]["content"]["purpose"]
          and "hello" not in stored)
    return ok, "zero-cost HIT produced a zero-credit SPEND receipt; balance unchanged"


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
    root = paths.REPO_ROOT
    repository_checkout = os.path.isfile(os.path.join(root, "README.md"))
    healthy = _doc.checkup(org, repo_root=root if repository_checkout else None)
    coherence_ok = (
        next(c for c in healthy["checks"] if c["check"] == "docs-vs-code")["ok"]
        if repository_checkout else True
    )
    idx = org.prime.band_layers["facts"][0]
    org.prime.layer_content(idx)[0]["content"] = {"k": "EVIL"}   # tamper the cube
    sick = _doc.checkup(org)
    return (healthy["ok"] and coherence_ok and not sick["ok"],
            "doctor passed a healthy deployment%s; caught the tampered cube"
            % (" + docs coherence" if repository_checkout else ""))


# ============================================================================
# 20. Phenotype: wearable, SELF-encrypted app-faces stored in the VCW (M9)
# ============================================================================
def _pheno_org():
    from ..phenotype import phenotype_bands
    org = _born(genome=standard_genome() + phenotype_bands())
    org.limbs.register_control("grid", {"kind": "grid"}, lambda v: None)
    return org


def t_pheno_self_open_and_integrity():
    """PHENO-1: a face sealed by SELF is openable by SELF and its source round-trips byte-
    identical (source_hash verifies). A tampered sealed chunk fails the integrity check."""
    from .. import phenotype as _ph
    org = _pheno_org()
    src = "<html><body>origin surface</body></html>"
    _ph.express(org, "origin", "html", src, entry="index.html",
                controls=[{"id": "grid"}], default=True)
    opened = _ph.open_face(org, "origin")
    round_trips = (opened["source"] == src
                   and opened["source_hash"] == _ph.code_hash(src))
    # tamper the sealed bytes -> opening must refuse (cannot decrypt to a valid manifest)
    idx = org.prime.band_layers[_ph.PHENO_BAND][0]
    org.prime.layer_content(idx)[0]["content"]["b64"] = "Zm9vYmFy"   # "foobar"
    tamper_caught = _expect_raise(lambda: _ph.open_face(org, "origin"), _ph.PhenotypeError)[0]
    return (round_trips and tamper_caught,
            "SELF round-trips the source byte-identical; a tampered seal is refused")


def t_pheno_other_cannot_read():
    """PHENO-2: a face sealed by one body is UNREADABLE/UN-WEARABLE as OTHER -- a copied nest in
    a different body (a different genesis key) gets garbage, not the source."""
    from .. import phenotype as _ph
    a = _pheno_org()
    _ph.express(a, "origin", "html", "<html>secret surface</html>", default=True)
    b = _pheno_org()                                  # a different body == a different key
    _ph.restore(b, _ph.snapshot(a))                   # copy the sealed entries into OTHER
    other_blind = _expect_raise(lambda: _ph.open_face(b, "origin"), _ph.PhenotypeError)[0]
    self_sees = _ph.open_face(a, "origin")["source"] == "<html>secret surface</html>"
    return (other_blind and self_sees,
            "SELF reads its own face; OTHER (different key) is refused")


def t_pheno_wear_append_only():
    """PHENO-3: wearing is append-only -- the active face is the LATEST wear-event, every change
    is an accreted immutable event, and no prior entry is overwritten (the cube still verifies)."""
    from .. import phenotype as _ph
    org = _pheno_org()
    _ph.express(org, "origin", "html", "<html>a</html>", controls=[{"id": "grid"}], default=True)
    _ph.express(org, "sheet", "html", "<html>b</html>", controls=[{"id": "grid"}])
    _ph.wear(org, "origin"); _ph.wear(org, "sheet"); _ph.wear(org, "origin")
    wear_events = [e for e in _ph._raw_entries(org, _ph.WEAR_BAND)
                   if e.get("opcode") == _ph.WEAR_OPCODE]
    active_is_latest = _ph.active_face(org) == "origin" and len(wear_events) == 3
    coherent = org.prime.verify() == []
    return (active_is_latest and coherent,
            "3 append-only wear-events; active == latest; cube still coheres (no overwrite)")


def t_pheno_default_survives_rebirth():
    """PHENO-4: the default (origin) face is always present after birth and SURVIVES a chosen
    rebirth -- the genesis key persists, so the carried-forward face is still openable, and the
    old generation keeps its own readable copy in the sealed ancestor."""
    from .. import phenotype as _ph
    org = _pheno_org()
    src = "<html>origin</html>"
    _ph.express(org, "origin", "html", src, controls=[{"id": "grid"}], default=True)
    _ph.rebirth_with_faces(org, reason="invariant")
    survived = (org.prime.generation == 1 and _ph._default_name(org) == "origin"
                and _ph.open_face(org, "origin")["source"] == src)
    ancestor_keeps_it = any(c.generation == 0 for c in org.ancestral)
    return (survived and ancestor_keeps_it,
            "default carried into gen 1 (still openable); gen 0 sealed as a readable ancestor")


def t_pheno_socket_required():
    """PHENO-5: a face may only plug into controls the nervous system can drive -- a face that
    declares a control with no socket in the Human Surface Map is refused at wear time."""
    from .. import phenotype as _ph
    org = _pheno_org()                                # socket has only 'grid'
    _ph.express(org, "phone", "html", "<html>phone</html>", controls=[{"id": "camera"}])
    refused = _expect_raise(lambda: _ph.wear(org, "phone"), _ph.PhenotypeError)[0]
    return (refused, "a face reaching for an unsocketed control ('camera') is refused")


# ============================================================================
# 21. VCW Applet Bodies: APPLET-BODY-CAPSULE (mantle.applet_body)
# ============================================================================
def _applet_org():
    from ..applet_body import applet_bands
    from ..phenotype import phenotype_bands
    return _born(genome=standard_genome() + applet_bands() + phenotype_bands())


def _tiny_py_project(root):
    """A tiny Python project whose module carries a TOP-LEVEL SIDE EFFECT canary: if any
    applet path ever imports/executes stored source, PWNED.txt appears and the invariant
    goes red."""
    os.makedirs(os.path.join(root, "pkg"), exist_ok=True)
    with open(os.path.join(root, "main.py"), "w") as f:
        f.write("open('PWNED.txt', 'w').write('executed')\n"
                "def send_report(x):\n    return x\n")
    with open(os.path.join(root, "pkg", "util.py"), "w") as f:
        f.write("def validate_input(v):\n    return bool(v)\n")
    with open(os.path.join(root, "README.md"), "w") as f:
        f.write("# tiny\n")
    return root


def t_applet_capsule_from_python_project():
    """APPLET-1: a tiny Python project rises into an APPLET-BODY-CAPSULE -- manifest,
    veiled source, organ map, state, face -- appears in the list, `show` never dumps the
    source blob, and NOTHING is executed (the top-level canary never fires). A capsule is
    never labeled alive (stage1_ready=False, status='capsule')."""
    from .. import applet_body as ab
    with tempfile.TemporaryDirectory() as td:
        proj = _tiny_py_project(os.path.join(td, "proj"))
        org = _applet_org()
        r = ab.create_applet_body(org, proj, "tiny", state={"counter": 0})
        listed = [a["applet"] for a in ab.list_applet_bodies(org)]
        view = ab.show_applet_body(org, "tiny")
        no_blob = "b64" not in json.dumps(view)
        canary = os.path.exists(os.path.join(proj, "PWNED.txt")) or \
            os.path.exists("PWNED.txt")
        honest = (r["status"] == "capsule" and r["stage1_ready"] is False
                  and r["capsule"] == "APPLET-BODY-CAPSULE")
        roles_seen = r["role_counts"].get("ARM_ACTION", 0) >= 1 \
            and r["role_counts"].get("ERROR_DEFENSE", 0) >= 1
        return (r["files"] == 3 and "tiny" in listed and no_blob and not canary
                and honest and roles_seen and view["manifest"]["face"] == "applet:tiny",
                "3 files raised; listed; show is blob-free; canary never fired; "
                "labeled capsule, never alive")


def t_applet_export_verifies_and_refuses():
    """APPLET-2: export reconstructs the source byte-identical and hash-verified; a
    second export REFUSES without overwrite=True and proceeds with it; a stored path
    that tries to escape the applet root is refused and never written."""
    from .. import applet_body as ab
    from ..vcw.entry import make_entry as _me
    import base64 as _b64
    with tempfile.TemporaryDirectory() as td:
        proj = _tiny_py_project(os.path.join(td, "proj"))
        org = _applet_org()
        ab.create_applet_body(org, proj, "tiny")
        dest = os.path.join(td, "out")
        r1 = ab.export_applet_source(org, "tiny", dest)
        with open(os.path.join(proj, "main.py"), "rb") as f:
            original = f.read()
        with open(os.path.join(dest, "main.py"), "rb") as f:
            exported = f.read()
        round_trip = (original == exported and not r1["errors"]
                      and r1["hashes_verified"] == r1["files_total"] == 3)
        r2 = ab.export_applet_source(org, "tiny", dest)          # no overwrite flag
        refused = (not r2["files_written"]) and any("overwrite" in e for e in r2["errors"])
        r3 = ab.export_applet_source(org, "tiny", dest, overwrite=True)
        allowed = len(r3["files_written"]) == 3 and not r3["errors"]
        # a malicious traversal entry must be refused, recorded, and never written
        org.prime.append(ab.SOURCE_BAND, _me(
            {"applet": "tiny", "path": "../evil.txt", "part": 0, "of": 1,
             "b64": _b64.b64encode(b"evil").decode(), "sha256": ab._sha256(b"evil"),
             "size": 4}, opcode=ab.SOURCE_OPCODE, author="BODY", source="tamper"))
        r4 = ab.export_applet_source(org, "tiny", dest, overwrite=True)
        escaped = os.path.exists(os.path.join(td, "evil.txt"))
        traversal_refused = (any("escape" in e for e in r4["errors"]) and not escaped
                             and "../evil.txt" not in r4["files_written"])
        return (round_trip and refused and allowed and traversal_refused,
                "byte-identical + 3/3 hashes; overwrite refused by default; "
                "traversal refused, nothing written outside the root")


def t_applet_audit_catches_tamper():
    """APPLET-3: the deterministic applet audit passes a valid capsule; a tampered source
    chunk turns it red (hash + bundle rows); a manifest whose face is missing turns it
    red (the face row). The audit executes nothing."""
    from .. import applet_body as ab
    from ..vcw.entry import make_entry as _me
    import base64 as _b64
    with tempfile.TemporaryDirectory() as td:
        proj = _tiny_py_project(os.path.join(td, "proj"))
        org = _applet_org()
        ab.create_applet_body(org, proj, "tiny")
        ok_valid, rows = ab.audit_applet_body(org, "tiny")
        # tamper one stored chunk -> A-02/A-03 must go red
        idx = org.prime.band_layers[ab.SOURCE_BAND][0]
        chunk = next(e for e in org.prime.layer_content(idx)
                     if e.get("opcode") == ab.SOURCE_OPCODE)
        chunk["content"]["b64"] = _b64.b64encode(b"tampered").decode()
        ok_tampered, rows_t = ab.audit_applet_body(org, "tiny")
        hash_row_red = not next(r for r in rows_t if r["check"].startswith("A-02"))["ok"]
        # a capsule with no face -> the face row must go red
        org2 = _applet_org()
        org2.prime.append(ab.MANIFEST_BAND, _me(
            {"applet": "ghostly", "capsule": ab.CAPSULE, "status": "capsule",
             "source_hash": "sha256:0", "files": 0, "include_source": False,
             "face": "applet:ghostly"},
            opcode=ab.MANIFEST_OPCODE, author="BODY", source="tamper"))
        ok_faceless, rows_f = ab.audit_applet_body(org2, "ghostly")
        face_row_red = not next(r for r in rows_f if r["check"].startswith("A-07"))["ok"]
        canary = os.path.exists(os.path.join(proj, "PWNED.txt"))
        return (ok_valid and all(r["ok"] for r in rows) and not ok_tampered
                and hash_row_red and not ok_faceless and face_row_red and not canary,
                "valid capsule passes 9/9; tampered chunk caught; missing face caught; "
                "nothing executed")


def t_applet_html_face_and_wear():
    """APPLET-4: a tiny HTML app's index.html becomes the applet's phenotype face; the
    face opens under SELF, and wearing it returns the boot manifest a HOST renders --
    the source is never executed inside Mantle."""
    from .. import applet_body as ab
    from .. import phenotype as _ph
    with tempfile.TemporaryDirectory() as td:
        proj = os.path.join(td, "webapp")
        os.makedirs(proj)
        html = "<!doctype html><html><body><h1>tiny web</h1></body></html>"
        with open(os.path.join(proj, "index.html"), "w") as f:
            f.write(html)
        with open(os.path.join(proj, "app.js"), "w") as f:
            f.write("function render(){}\n")
        org = _applet_org()
        r = ab.create_applet_body(org, proj, "webby")
        opened = _ph.open_face(org, "applet:webby")
        boot = ab.wear_applet_face(org, "webby")
        return (r["face_from"] == "index.html" and opened["source"] == html
                and boot["source"] == html and boot["kind"] == "html",
                "index.html is the face; SELF opens it; wear returns the render-boundary "
                "boot manifest")


def t_applet_secret_boundary_and_bands():
    """APPLET-5 (HF-B20 for applet tissue): applet STATE is redacted at the boundary --
    no raw secret lands in the state band; secret-suspect source files raise an immune
    event; and the applet bands pass the SAME validate_genome gate as any app band (a
    colliding or out-of-range applet genome is refused)."""
    from .. import applet_body as ab
    from ..compiler import GenomeError, validate_genome
    with tempfile.TemporaryDirectory() as td:
        proj = os.path.join(td, "proj")
        os.makedirs(proj)
        with open(os.path.join(proj, "config.py"), "w") as f:
            f.write("API_KEY = 'sk-ABCDEFGHIJKLMNOP1234'\n")
        org = _applet_org()
        before = len(org.immune.log)
        r = ab.create_applet_body(org, proj, "leaky",
                                  state={"api_key": "sk-ABCDEFGHIJKLMNOP1234",
                                         "counter": 3})
        state = next(e["content"]["state"] for e in
                     org.prime.layer_content(org.prime.band_layers[ab.STATE_BAND][0])
                     if e.get("opcode") == ab.STATE_OPCODE)
        redacted = state["api_key"] == "[REDACTED]" and state["counter"] == 3
        flagged = (len(org.immune.log) > before
                   and "config.py" in r["secret_suspects"])
        gate_holds = _expect_raise(
            lambda: validate_genome([{"band": "bad", "head": 100}]), GenomeError)[0]
        return (redacted and flagged and gate_holds,
                "state redacted before append; suspect source flagged to immune; "
                "the validate_genome gate still refuses out-of-range heads")


def t_core_status_adapter_current_vcw_api():
    """STATUS-1: generated lifecycle audits and AppAI terminals use one stable
    organism-status adapter backed by current Prime/VCW APIs, not stale helpers such as
    Cube.visible(), Body.generation(), or Organism.verify()."""
    from ..core.status import organism_status
    org = _born()
    org.memory.remember("facts", {"k": "v"})
    status = organism_status(org)
    facts = next(row for row in status["bands"] if row["band"] == "facts")
    ok = (
        status["identity"] == "TestAppAI"
        and status["generation"] == org.prime.generation
        and status["band_count"] == len(org.prime.bands)
        and facts["visible_entries"] == 1
        and status["verify_ok"]
        and status["verify_errors"] == []
    )
    return ok, ("identity=%s generation=%d bands=%d verify=%s facts_visible=%d"
                % (status["identity"], status["generation"], status["band_count"],
                   status["verify_ok"], facts["visible_entries"]))


def t_app_band_allocator_reserves_atlas():
    """APPBAND-1: app-band generators allocate only from free caller gaps and the
    compiler refuses manually supplied spans that overlap reserved vault/phenotype/
    spore/applet atlas ranges. The VCW anatomical atlas also matches live cube,
    app-band, and spore constants."""
    from ..compiler import GenomeError, validate_genome
    from ..vcw.bands import allocate_app_band, app_band_conflicts
    from ..vcw.atlas import build_atlas, verify_atlas
    existing = [allocate_app_band("terminal", 8)]
    second = allocate_app_band("tape", 20, existing=existing)
    atlas = build_atlas()
    reserved_refused = _expect_raise(
        lambda: validate_genome([{"band": "bad_terminal", "head": 630, "span": 10}]),
        GenomeError,
    )[0]
    no_conflict = app_band_conflicts(existing + [second]) == []
    ordered_gaps = (
        existing[0]["head"] == 600
        and existing[0]["span"] == 8
        and second["head"] == 608
        and second["head"] + second["span"] <= 638
    )
    atlas_ok = (
        verify_atlas() == []
        and atlas["atlas_format"] == "vcw-anatomical-atlas-v1"
        and atlas["cube"]["format"] == "vcw-cube-png-v2"
        and atlas["spore"]["vcw_region"]["height"] == 1000
        and atlas["spore"]["display_region"]["y"] == 1000
        and atlas["measurement_rules"]["measurement_scaling"].startswith("inspectors")
    )
    return (reserved_refused and no_conflict and ordered_gaps and atlas_ok,
            "allocated %s[%d-%d], %s[%d-%d]; reserved overlap refused; "
            "VCW atlas verified"
            % (existing[0]["band"], existing[0]["head"],
               existing[0]["head"] + existing[0]["span"] - 1,
               second["band"], second["head"], second["head"] + second["span"] - 1))


def t_assimilator_substrate_gaps_and_outside_host_gate():
    """ASSIM-1: Phase-0 first discovers the host substrate, reports unsupported
    native/Qt coverage explicitly, emits a resident evidence index, and refuses to
    write inventory artifacts inside the host tree."""
    from ..assimilator import answer_from_host_evidence, dry_run, write_artifacts
    with tempfile.TemporaryDirectory() as td:
        host = os.path.join(td, "NativeQt")
        os.makedirs(os.path.join(host, "src"))
        with open(os.path.join(host, "CMakeLists.txt"), "w", encoding="utf-8") as f:
            f.write("project(NativeQt LANGUAGES CXX)\n")
        with open(os.path.join(host, "src", "main.cpp"), "w", encoding="utf-8") as f:
            f.write("int main(){return 0;}\n")
        with open(os.path.join(host, "src", "MainWindow.ui"), "w", encoding="utf-8") as f:
            f.write("<ui version=\"4.0\"></ui>\n")
        result = dry_run(host)
        substrate = result["dissection"]["substrate"]
        evidence = result["map"].get("host_evidence_index", {})
        inventory = result["inventory_md"]
        answer = answer_from_host_evidence("what are your gaps?", result["map"])
        outside = os.path.join(td, "artifacts")
        paths = write_artifacts(result, outside)
        inside_refused = _expect_raise(lambda: write_artifacts(result, os.path.join(host, "mantle")),
                                       ValueError)[0]
        ok = (
            "native-c-family" in substrate["languages"]
            and "qt-resource-ui" in substrate["languages"]
            and "cmake" in substrate["languages"]
            and substrate["coverage"]["requires_adaptive_native_tools"] == 2
            and len(substrate["unsupported"]) == 2
            and "Substrate coverage" in inventory
            and evidence.get("kind") == "HOST_EVIDENCE_INDEX"
            and evidence.get("local_first_consultation") is True
            and "plain-English host-surface requests" in evidence.get("consultation_contract", {}).get("effectful_action_policy", "")
            and "mapped SELF/body evidence" in evidence.get("consultation_contract", {}).get("effectful_action_policy", "")
            and "host-specific anatomy" in evidence.get("consultation_contract", {}).get("working_surface_policy", "")
            and "not universal predefined slash commands" in evidence.get("consultation_contract", {}).get("working_surface_policy", "")
            and "explicit maintenance commands" in evidence.get("consultation_contract", {}).get("reset_policy", "")
            and "Resident host evidence index" in inventory
            and "adaptive parser/observer/verifier" in answer
            and os.path.exists(paths["inventory"])
            and inside_refused
        )
        return ok, ("languages=%s adaptive=%d inside_write_refused=%s"
                    % (substrate["languages"],
                       substrate["coverage"]["requires_adaptive_native_tools"],
                       inside_refused))


def t_assimilator_gui_surface_nerve_coverage():
    """ASSIM-2: discovered GUI elements are never silently omitted. Each visible
    surface becomes verified, observer-registered, sense-only, not implemented, or
    an explicit maintenance gap, and helper-wired Qt actions count as nerve
    evidence."""
    from ..assimilator.surface_coverage import build_surface_coverage
    symbols = [
        {"kind": "ui-action", "symbol": "actionPaste", "module": "MainWindow.ui",
         "line": 10, "label": "Paste", "shortcut": "Ctrl+V",
         "placements": ["menuEdit:Edit"]},
        {"kind": "ui-action", "symbol": "actionMystery", "module": "MainWindow.ui",
         "line": 11, "label": "Mystery"},
        {"kind": "ui-action", "symbol": "actionThis_is_not_currently_implemented",
         "module": "MainWindow.ui", "line": 12, "label": "This is not currently implemented"},
        {"kind": "ui-menu", "symbol": "menuEdit", "module": "MainWindow.ui",
         "line": 13, "label": "Edit"},
        {"kind": "ui-widget", "symbol": "pushExitFullScreen", "module": "MainWindow.ui",
         "line": 14, "class": "QPushButton", "label": "Exit Full Screen"},
    ]
    edges = [
        {"kind": "qt-helper-action", "sender": "ui->actionPaste",
         "signal": "QAction::triggered", "slot": "&ScintillaNext::paste",
         "module": "MainWindow.cpp", "line": 340},
    ]
    coverage = build_surface_coverage(symbols, edges,
                                      verified_controls=["actionPaste"])
    by_id = {surface["id"]: surface for surface in coverage["surfaces"]}
    ok = (
        coverage["total_surfaces"] == 5
        and by_id["actionPaste"]["vcw_status"] == "verified_body_operation"
        and by_id["actionPaste"]["connection_evidence"][0]["kind"] == "qt-helper-action"
        and by_id["actionMystery"]["vcw_status"] == "maintenance_gap"
        and by_id["actionThis_is_not_currently_implemented"]["vcw_status"] == "not_implemented"
        and by_id["menuEdit"]["vcw_status"] == "sense_only"
        and by_id["pushExitFullScreen"]["vcw_status"] == "sense_only"
        and coverage["contract"]["no_silent_gui_omission"] is True
        and "no generic app is assumed" in coverage["contract"].get("working_surface_policy", "")
    )
    return ok, "surfaces=%d statuses=%s" % (
        coverage["total_surfaces"], coverage["status_counts"])


# ============================================================================
# 22. The Reproduction organ (the ninth organ) + SPORE-DISTILLATION
# ============================================================================
def t_repro_atlas_overlap_gate():
    """REPRO-1: overlapping band SPANS (not just identical heads) are refused at genesis
    AND at the compiler gate -- and the full framework atlas (host bands + symbiosis +
    vault + phenotype + spore_vault + applets, together) boots coherently. This is the
    gate that closes the latent symbiosis@560-inside-host_state layer stomp."""
    from ..vcw.bands import genome_overlaps
    from ..compiler import validate_genome, GenomeError
    from ..assimilator.organ_map import propose_genome
    from ..symbiosis import symbiosis_band
    from ..organs.reproduction import vault_band
    from ..phenotype import phenotype_bands
    from ..applet_body import applet_bands
    from ..organs.reproduction import spore_vault_band
    bad = standard_genome() + [make_band_boot("a", 600, "log-json", span=8, purpose="p"),
                               make_band_boot("b", 604, "log-json", span=8, purpose="p")]
    genesis_refused, _ = _expect_raise(lambda: Cube.genesis(bad), ValueError)
    compiler_caught, _ = _expect_raise(lambda: validate_genome(
        [{"band": "a", "head": 600, "span": 8}, {"band": "b", "head": 604, "span": 8}]),
        GenomeError)
    full = (standard_genome()
            + [b for b in propose_genome({}) if 550 <= b["head"] <= 749]
            + [symbiosis_band(), vault_band(), spore_vault_band()]
            + phenotype_bands() + applet_bands())
    coherent = genome_overlaps(full) == [] and Cube.genesis(full).verify() == []
    return (genesis_refused and compiler_caught and coherent,
            "span overlap refused at genesis + compiler; the whole atlas boots in ONE "
            "genome (%d bands, zero overlaps)" % len(full))


def t_repro_organ_and_seed_carry():
    """REPRO-2: the ninth organ is meshed with a fail-open contract, and its runtime duty
    holds: the sealed seed is CARRIED across a rebirth whose genome keeps the vault band,
    and its loss is immune-logged (never silent) when the genome drops it."""
    from ..organs.reproduction import vault_band, open_seed
    org = _born(genome=standard_genome() + [vault_band()])
    m = org.manifests()
    organ_ok = ("reproduction" in m and m["reproduction"]["fail_mode"] == "fail-open"
                and len(m) == 9)
    seed = {"egg_format": "mantle-egg-v1", "identity": {"name": "Carried.AppAI"},
            "truths": ["t"], "commandments": ["c"]}
    org.reproduction.store_seed(seed)
    org.rebirth(new_genome=standard_genome() + [vault_band()], reason="carry test")
    carried = open_seed(org) == seed and org.prime.generation == 1
    before = len(org.immune.log)
    org.rebirth(reason="lossy reformat")            # standard genome: no vault band
    flagged = any(e["kind"] == "seed_uncarried" for e in org.immune.log[before:])
    return (organ_ok and carried and flagged,
            "9 organs meshed; sealed seed carried into gen 1 (still SELF-openable); "
            "a vault-less rebirth raised seed_uncarried, not silence")


def t_repro_every_hatch_vaults_its_egg():
    """REPRO-3: RESURGERE is a birthright -- every hatchery birth stores its own egg,
    SELF-sealed, in the vault band, without the egg asking for it."""
    from ..hatchery import incubate
    from ..organs.reproduction import open_seed
    egg = {"egg_format": "mantle-egg-v1", "identity": {"name": "Vaulted.AppAI"},
           "truths": ["if it is not in the VCW it did not happen"],
           "commandments": ["protect your VCW"]}
    org = incubate(egg)["organism"]
    stored = open_seed(org)
    return (org.stage1_certified and stored["identity"]["name"] == "Vaulted.AppAI",
            "hatched certified; the organism's own egg came back out of its vault")


def t_repro_anchor_births_through_hatchery():
    """REPRO-4: one birth path for every body -- an anchored resident now grows through
    the hatchery, so it carries the default origin face AND its own seed in the vault,
    exactly like an egg-hatched organism (and the host stays byte-identical, per SYM-4)."""
    from ..anchor import anchor
    from ..organs.reproduction import open_seed
    from .. import phenotype as _ph
    host = _sample_host_copy("mantle-repro-anchor-")
    org = anchor(host, starter_credits=2)["organism"]
    face = _ph.open_face(org, "origin")
    seed = open_seed(org)
    return (org.stage1_certified and _ph._default_name(org) == "origin"
            and bool(face["source"])
            and seed.get("identity", {}).get("name") == org.body.identity_name(),
            "resident certified through the hatchery; wears its origin face; carries "
            "its own resident-egg in the vault")


def t_spore_distillation_key_law():
    """SPORE-1 (THE KEY LAW): a spore distills into the primer and the memories of the
    body it births; the spore is sealed as SELF tissue and opens only for SELF; and the
    genesis key is MINTED, never derived -- two bodies hatched from the SAME spore state
    carry different keys (a public spore can never forge SELF; anti-clone holds)."""
    from ..hatchery import hatch_from_spore
    from ..organs.reproduction import SPORE_BAND, SPORE_OPCODE
    state = {"identity": {"spore_name": "Midwife", "task": "assist the assimilation"},
             "conversation": [{"opcode": "USER", "content": "hello"},
                              {"opcode": "ASSISTANT", "content": "ready"}]}
    a = hatch_from_spore(state=dict(state))["organism"]
    b = hatch_from_spore(state=dict(state))["organism"]
    primer_named = "Midwife" in json.dumps(a.body.self_record()["primer"], default=str)
    keys_minted = (a.body.key_fingerprint != b.body.key_fingerprint
                   and a.body._genesis_key != b.body._genesis_key)
    blob = a.reproduction.open_spore()
    self_opens = json.loads(blob)["identity"]["spore_name"] == "Midwife"
    ingested = [e for e in a.prime.read("discoveries") if e.get("opcode") == "INGESTED"]
    memories = len(ingested) == 2 and all(e.get("confidence") == "inferred"
                                          for e in ingested)
    for e in a.reproduction._physical(SPORE_BAND):        # copy A's sealed spore into B
        if e.get("opcode") == SPORE_OPCODE:
            b.prime.append(SPORE_BAND, make_entry(dict(e.get("content") or {}),
                                                  opcode=SPORE_OPCODE, author="BODY",
                                                  source="copied-as-other"))
    other_blind = _expect_raise(lambda: b.reproduction.open_spore(), Exception)[0]
    return (primer_named and keys_minted and self_opens and memories and other_blind,
            "spore became primer + 2 inferred memories; sealed copy opens for SELF only; "
            "same spore, two bodies, two DIFFERENT minted keys (never derived)")


def t_sporeagent_lifecycle_receipt():
    """SPORE-2: SPOREAGENT source provenance is lifecycle tissue layered on
    hatch_from_spore, not feature creep in spore.py. The receipt records source
    declaration/fetch/assimilation/certification/boundary facts, redacts unsafe
    metadata, treats host code as OTHER, and never exposes Body key material."""
    from .. import spore as _spore
    from .. import spore_min as _spore_min
    from ..hatchery import hatch_from_spore

    secret_token = "sk-SECRETSECRETSECRETSECRET"
    private_key = "-----BEGIN PRIVATE KEY-----\nabc123\n-----END PRIVATE KEY-----"
    state = {
        "identity": {"spore_name": "SPOREAGENT", "task": "assimilate declared source"},
        "source": {
            "kind": "git",
            "url": "https://github.com/jodydugas-ctrl/mantle-os",
            "ref": "main",
            "api_key": secret_token,       # forbidden by the allow-list
        },
        "conversation": [],
    }
    source_receipt = {
        "fetched": True,
        "assimilated": True,
        "certified": True,
        "sealed": True,
        "sha256": "sha256:" + ("a" * 64),
        "private_key": private_key,        # forbidden by the allow-list
        "notes": "operator used declared source; token=%s" % secret_token,
    }
    out = hatch_from_spore(state=dict(state), source_receipt=source_receipt)
    source = out["receipt"]["source"]
    report_text = json.dumps(out["report"], sort_keys=True, default=str)
    declared_and_receipted = (
        source["declared"] and source["fetched"] and source["assimilated"]
        and source["certified"] and source["sealed"]
        and source["descriptor"]["url"] == state["source"]["url"]
        and source["receipt"]["sha256"] == source_receipt["sha256"]
    )
    boundary = (
        source["host_code_is_self"] is False
        and source["source_self_status"] == "OTHER_until_PRIMER_seal_provenance_and_certification"
        and source["key_owner"] == "BODY"
        and source["mind_key_access"] is False
        and out["receipt"]["primer_boundary"]["body_key_owner"] == "BODY"
    )
    no_leak = (
        secret_token not in report_text
        and private_key not in report_text
        and out["organism"].body._genesis_key not in report_text
        and "api_key" not in source["descriptor"]
        and "private_key" not in source["receipt"]
    )
    missing = hatch_from_spore(
        state={"identity": {"spore_name": "NoSource", "task": "plain hatch"}}
    )["receipt"]["source"]
    missing_explicit = (
        missing["declared"] is False
        and missing["fetched"] is False
        and missing["assimilated"] is False
        and missing["certified"] is False
        and missing["sealed"] is False
    )
    from pathlib import Path as _Path
    spore_source = _Path(_spore.__file__).read_text(encoding="utf-8")
    spore_min_source = _Path(_spore_min.__file__).read_text(encoding="utf-8")
    purity = ("SPOREAGENT" not in spore_source
              and "source_receipt" not in spore_source
              and "SPOREAGENT" not in spore_min_source
              and "source_receipt" not in spore_min_source)
    return (declared_and_receipted and boundary and no_leak and missing_explicit and purity,
            "source lifecycle receipt is explicit, redacted, OTHER-until-proven, "
            "and absent from pure spore.py/spore_min.py")


def t_spore_germ_round_trip():
    """SPORE-3 (ONE ARTIFACT): a germ-carrying spore is the complete birth package.
    The germ (the full build document) travels inside the spore state, hatches through
    the one hatchery door into a certified body, and comes back out of the newborn's
    vault equal to what went in -- and the spore itself returns from spore_vault. The
    state path is pure stdlib (no Pillow needed to prove the law)."""
    from ..hatchery import hatch_from_spore
    from ..organs.reproduction import open_seed
    germ = {"germ_format": "mantle-germ-v1",
            "identity": {"name": "GermCarried.AppAI", "purpose": "prove the round trip"},
            "truths": ["if it is not in the VCW it did not happen"],
            "commandments": ["protect your VCW"],
            "controls": [{"id": "app.echo", "label": "Echo"}]}
    state = {"identity": {"spore_name": "GermSpore", "task": "carry a whole AppAI"},
             "germ": dict(germ),
             "build": "hatch me: python -m mantle hatch this.png",
             "conversation": [{"opcode": "USER", "content": "grow"}]}
    out = hatch_from_spore(state=json.loads(json.dumps(state)))
    org, receipt = out["organism"], out["receipt"]
    vaulted = open_seed(org)
    germ_back = (vaulted.get("identity") == germ["identity"]
                 and vaulted.get("truths") == germ["truths"]
                 and vaulted.get("commandments") == germ["commandments"]
                 and vaulted.get("controls") == germ["controls"])
    spore_back = json.loads(org.reproduction.open_spore())["germ"]["identity"] \
        == germ["identity"]
    named = org.body.identity_name() == "GermCarried.AppAI"
    return (org.stage1_certified and receipt["germ_carried"] and germ_back
            and spore_back and named and receipt["key_derived_from_spore"] is False,
            "germ rode the spore through the one door: certified body, germ back from "
            "the vault, spore back from spore_vault, key minted not derived")


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
    ("BUGFIX-1 runtime-boundaries",            t_bugfix_runtime_boundaries),
    ("HF-M16 self-inquiry-never-facts",        t_self_inquiry_never_facts),
    ("B-OC  organ-overreach-refused",          t_organ_overreach_refused),
    ("HF-B32 reflex-fault-fail-open",          t_reflex_fault_failopen),
    ("LIMB-1 structured-bridge-proof",         t_limb_structured_bridge_proof),
    ("B-DD  dedupe-tombstones-duplicates",     t_dedupe_tombstones_duplicates),
    ("B-W2  waste/reclaim-reuse",              t_waste_reclaim_reuse),
    ("B-W4  waste/on-demand+purpose",          t_on_demand_and_purpose),
    ("B-SC  staged-save-rejects-corrupt",      t_staged_save_rejects_corrupt),
    ("PERSIST-1 atomic-owner-only-save",        t_organism_save_atomic_owner_only),
    ("SYM-1 energy-never-negative",            t_energy_never_negative),
    ("SYM-2 starvation-fail-open",             t_starvation_failopen),
    ("SYM-3 keys-never-raw",                   t_keys_never_raw),
    ("SYM-4 anchor-never-modifies-host",       t_anchor_never_modifies_host),
    ("SELF-1 key-once-and-private",            t_self_key_once_and_private),
    ("SELF-2 self-verify/reject-foreign",      t_self_verify_and_reject_foreign),
    ("SELF-3 anti-clone",                      t_self_anti_clone),
    ("SELF-4 key-survives-or-fails-loud",      t_self_key_survives_or_fails_loud),
    ("NOC-1 natural-heartbeat-cognizes",        t_noc_calm_spends_nothing),
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
    ("OR-CACHE-1 usage-receipt",               t_or_cache_usage_receipt),
    ("OR-CACHE-2 transport-sidecars",          t_or_transport_sidecars_and_canonical_body),
    ("OR-CACHE-3 ghost-http-receipt",          t_or_ghost_http_receipt),
    ("OR-CACHE-4 zero-cost-cache-hit",         t_meter_receipt_zero_cost_cache_hit),
    ("INGEST-1 conversation-distilled",        t_ingest_distills),
    ("DOCTOR-1 deployment-checkup",            t_doctor_checkup),
    ("PHENO-1 self-open+integrity",            t_pheno_self_open_and_integrity),
    ("PHENO-2 other-cannot-read",              t_pheno_other_cannot_read),
    ("PHENO-3 wear-append-only",               t_pheno_wear_append_only),
    ("PHENO-4 default-survives-rebirth",       t_pheno_default_survives_rebirth),
    ("PHENO-5 socket-required",                t_pheno_socket_required),
    ("APPLET-1 capsule-from-python-project",   t_applet_capsule_from_python_project),
    ("APPLET-2 export-verifies+refuses",       t_applet_export_verifies_and_refuses),
    ("APPLET-3 audit-catches-tamper",          t_applet_audit_catches_tamper),
    ("APPLET-4 html-face+wear",                t_applet_html_face_and_wear),
    ("APPLET-5 secret-boundary+band-gate",     t_applet_secret_boundary_and_bands),
    ("STATUS-1 organism-status-adapter",       t_core_status_adapter_current_vcw_api),
    ("APPBAND-1 safe-app-band-allocation",     t_app_band_allocator_reserves_atlas),
    ("ASSIM-1 substrate+artifact-boundary",    t_assimilator_substrate_gaps_and_outside_host_gate),
    ("ASSIM-2 gui-surface-nerve-coverage",     t_assimilator_gui_surface_nerve_coverage),
    ("REPRO-1 atlas+span-overlap-gate",        t_repro_atlas_overlap_gate),
    ("REPRO-2 ninth-organ+seed-carry",         t_repro_organ_and_seed_carry),
    ("REPRO-3 every-hatch-vaults-its-egg",     t_repro_every_hatch_vaults_its_egg),
    ("REPRO-4 anchor-births-through-hatchery", t_repro_anchor_births_through_hatchery),
    ("SPORE-1 distillation+key-law",           t_spore_distillation_key_law),
    ("SPORE-2 sporeagent-lifecycle-receipt",   t_sporeagent_lifecycle_receipt),
    ("SPORE-3 germ-round-trip (one artifact)", t_spore_germ_round_trip),
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
