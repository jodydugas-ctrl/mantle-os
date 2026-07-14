#!/usr/bin/env python3
"""
mantle.vcw.drivers  --  concrete payload protocols (Mantle OS)

Four drivers, registered on import:

  log-json          append-only list of immutable, hashed entries
  keyvalue          a small mutable map (mutated hot, snapshotted on flush)
  calendar-spatial  data stored AS COLORS AT COORDINATES -- a real RGBA canvas
  exec              an executable REFLEX LAYER: organism-grown code the Body runs with no
                    MIND, behind hash + capability + provenance/trust + sandbox gates

These prove the boot sector -- not hard-coded logic -- decides how a layer behaves.
"""
from __future__ import annotations

import ast
import base64
import builtins
import pickle
import subprocess
import sys
from datetime import date
from typing import Any, Dict, List, Tuple

from .png import SIDE, CHANNELS, LAYER_BYTES
from .bands import Driver, register, code_hash
from .entry import make_entry, visible

__all__ = [
    "make_entry", "LogJsonDriver", "KeyValueDriver", "CalendarSpatialDriver", "ExecDriver",
    "CapabilityError", "IntegrityError", "TrustError", "SandboxError", "ProvenanceError",
    "validate_skill_code", "validate_calcify_payload", "provenance_is_trusted", "trial",
    "register_runner", "get_runner",
]


# ============================================================================
# log-json : append-only immutable entries
# ============================================================================
@register
class LogJsonDriver(Driver):
    name = "log-json"

    def empty(self, params):
        return []

    def read(self, content, params, reveal_private=False):
        return visible(content)

    def retrieve(self, content, params, address):
        vis = self.read(content, params)
        i = int(address)
        return vis[i] if 0 <= i < len(vis) else None

    def append(self, content, params, value):
        e = value if isinstance(value, dict) and "hash" in value else make_entry(value)
        e = dict(e)
        if e.get("id") is None:                    # the cube assigns band-unique ids;
            e["id"] = len(content)                 # standalone driver use falls back to position
        content.append(e)
        return content


# ============================================================================
# keyvalue : a small mutable map
# ============================================================================
@register
class KeyValueDriver(Driver):
    name = "keyvalue"

    def empty(self, params):
        return {}

    def read(self, content, params, reveal_private=False):
        return dict(content)

    def retrieve(self, content, params, address):
        return content.get(str(address))

    def append(self, content, params, value):
        k, v = value
        content[str(k)] = v
        return content


# ============================================================================
# calendar-spatial : data stored as colors at coordinates (a real RGBA canvas)
# ============================================================================
@register
class CalendarSpatialDriver(Driver):
    """params = {"epoch": "2026-01-01", "palette": {"ff0000": "urgent", ...}}
    A date maps to a cell (x = weekday 0..6, y = week index since epoch); the cell's RGBA
    stores the appointment color; alpha 0 means 'free'."""
    name = "calendar-spatial"

    def empty(self, params):
        return bytearray(LAYER_BYTES)

    def coord_for_date(self, params, iso: str) -> Tuple[int, int]:
        epoch = date.fromisoformat(params["epoch"])
        d = date.fromisoformat(iso)
        days = d.toordinal() - epoch.toordinal() + epoch.weekday()
        return d.weekday(), days // 7

    def _palette_inverse(self, params) -> Dict[str, str]:
        return {v: k for k, v in params.get("palette", {}).items()}

    def _offset(self, x: int, y: int) -> int:
        return (y * SIDE + x) * CHANNELS

    def read(self, content, params, reveal_private=False):
        out = []
        palette = params.get("palette", {})
        for i in range(0, LAYER_BYTES, CHANNELS):
            r, g, b, a = content[i:i + CHANNELS]
            if a:
                hexc = "%02x%02x%02x" % (r, g, b)
                pix = i // CHANNELS
                out.append({"x": pix % SIDE, "y": pix // SIDE,
                            "color": hexc, "meaning": palette.get(hexc, "unknown")})
        return out

    def retrieve(self, content, params, address):
        x, y = address
        off = self._offset(int(x), int(y))
        r, g, b, a = content[off:off + CHANNELS]
        if not a:
            return "free"
        return params.get("palette", {}).get("%02x%02x%02x" % (r, g, b), "unknown")

    def append(self, content, params, value):
        iso, meaning = value
        x, y = self.coord_for_date(params, iso)
        hexc = self._palette_inverse(params).get(meaning)
        if hexc is None:
            raise ValueError("meaning %r not in palette" % meaning)
        off = self._offset(x, y)
        content[off:off + CHANNELS] = bytes.fromhex(hexc) + b"\xff"
        return content

    def get_date(self, content, params, iso: str):
        return self.retrieve(content, params, self.coord_for_date(params, iso))


# ============================================================================
# exec : the executable reflex layer (learning -> instinct)
# ============================================================================
SAFE_BUILTINS = {n: __builtins__[n] if isinstance(__builtins__, dict) else getattr(__builtins__, n)
                 for n in ("abs", "min", "max", "sum", "round", "len", "range", "float",
                           "int", "str", "bool", "list", "dict", "tuple", "enumerate",
                           "sorted", "map", "filter", "zip", "all", "any")}


class CapabilityError(Exception):
    """A call requested a band/limb/net the layer never declared (HF-B48)."""


class IntegrityError(Exception):
    """The exec layer's code does not match its promoted hash (HF-B47)."""


class ProvenanceError(Exception):
    """A calcify payload is missing its hash, capability set, signature, or provenance --
    a skill without a verifiable origin and bounds may never become an instinct."""


class SandboxError(Exception):
    """The candidate contains a STATIC escape vector (import / dunder traversal / forbidden
    builtin) and must never be calcified (HF-B51). The Python runner's restricted namespace
    is not a hard sandbox; the cheapest reliable defense is refusal at cultivation time."""


class TrustError(Exception):
    """An untrusted/foreign-provenance exec layer was asked to run on a non-isolating runner
    (HF-B50). Such code must run on the 'wasm' runner (hard sandbox) instead."""


_FORBIDDEN_NAMES = frozenset({
    "eval", "exec", "compile", "__import__", "open", "globals", "locals", "vars",
    "getattr", "setattr", "delattr", "input", "breakpoint", "memoryview", "exit", "quit",
    "help", "__builtins__",
})


def validate_skill_code(code: str) -> None:
    """Static gate for a Python skill: reject `import`, dunder attribute access, and forbidden
    builtins. Raises SandboxError on the first violation."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise SandboxError("skill does not parse: %s" % e)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise SandboxError("skill may not import modules")
        if isinstance(node, ast.Attribute) and isinstance(node.attr, str) \
                and node.attr.startswith("__") and node.attr.endswith("__"):
            raise SandboxError("skill may not access dunder attribute %r (escape vector)"
                               % node.attr)
        if isinstance(node, ast.Name) and node.id in _FORBIDDEN_NAMES:
            raise SandboxError("skill may not reference %r" % node.id)


def validate_calcify_payload(content: Dict[str, Any]) -> None:
    """The calcification gate beyond the code itself: a skill may not become an instinct
    without (1) a content hash, (2) a declared capability set, (3) a signature, and
    (4) provenance naming its author. Raises ProvenanceError on the first gap."""
    if not content.get("code_hash"):
        raise ProvenanceError("calcify refused: no code_hash (integrity gate)")
    if content.get("capabilities") is None:
        raise ProvenanceError("calcify refused: no declared capability set")
    if content.get("signature") is None:
        raise ProvenanceError("calcify refused: no signature")
    prov = content.get("provenance")
    if not prov or not prov.get("author"):
        raise ProvenanceError("calcify refused: provenance must name an author")


TRUSTED_AUTHORS = frozenset({"MIND", "BODY"})


def provenance_is_trusted(provenance: Dict[str, Any]) -> bool:
    """Trusted only if authored by this organism's own MIND/BODY and not flagged foreign.
    Trust governs which RUNNER may run it, not whether it runs at all."""
    p = provenance or {}
    return (p.get("author") in TRUSTED_AUTHORS) and not p.get("foreign", False)


# ---- pluggable exec runners ------------------------------------------------
_RUNNERS: Dict[str, "ExecRunner"] = {}


def register_runner(cls):
    inst = cls() if isinstance(cls, type) else cls
    _RUNNERS[inst.name] = inst
    return cls


def get_runner(name: str) -> "ExecRunner":
    if name not in _RUNNERS:
        raise NotImplementedError(
            "no exec runner %r registered (have: %s). To enable WASM, register an "
            "ExecRunner(name='wasm')." % (name, ", ".join(sorted(_RUNNERS))))
    return _RUNNERS[name]


class ExecRunner:
    """Executes a calcified exec layer's payload. Gates are applied by ExecDriver BEFORE a
    runner runs; a runner only builds the environment, calls the entry, enforces the limit."""
    name = "base"

    def run(self, content: Dict[str, Any], args: Dict[str, Any],
            granted: Dict[str, Any]) -> Any:
        raise NotImplementedError


@register_runner
class PythonExecRunner(ExecRunner):
    """The default runner: restricted namespace + wall-clock limit. NOT a hard sandbox --
    untrusted skills must use the wasm runner."""
    name = "python"

    def run(self, content, args, granted):
        declared = max(1, int(content.get("limits", {}).get("ms", 200))) / 1000.0
        # The hard kill is applied to the child process as a whole. On Windows, process
        # startup itself can exceed the old in-thread 200 ms default, so keep a small
        # floor while preserving caller-requested larger budgets.
        limit = max(declared, 1.0)
        payload = {
            "code": content["code"],
            "entry": content["entry"],
            "args": args,
            "safe_builtins": sorted(SAFE_BUILTINS),
        }
        runner = r"""
import base64
import builtins
import pickle
import sys

payload = pickle.loads(base64.b64decode(sys.stdin.buffer.read()))
safe = {name: getattr(builtins, name) for name in payload["safe_builtins"]}
g = {"__builtins__": safe}
loc = {}
try:
    exec(payload["code"], g, loc)
    fn = loc.get(payload["entry"]) or g.get(payload["entry"])
    if fn is None:
        raise NameError("entry %r not defined by exec layer" % payload["entry"])
    out = {"ok": True, "result": fn(**payload["args"])}
except BaseException as e:
    out = {"ok": False, "error_type": type(e).__name__, "error": str(e)}
sys.stdout.buffer.write(base64.b64encode(pickle.dumps(out, protocol=4)))
"""
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-c", runner],
                input=base64.b64encode(pickle.dumps(payload, protocol=4)),
                capture_output=True,
                timeout=limit,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError("exec layer exceeded its time budget")
        if proc.returncode != 0:
            raise RuntimeError("exec runner failed: %s" % proc.stderr.decode("utf-8", "replace"))
        out = pickle.loads(base64.b64decode(proc.stdout))
        if out.get("ok"):
            return out.get("result")
        exc = getattr(builtins, out.get("error_type", ""), RuntimeError)
        if not isinstance(exc, type) or not issubclass(exc, BaseException):
            exc = RuntimeError
        raise exc(out.get("error", "exec layer failed"))


@register_runner
class WasmExecRunner(ExecRunner):
    """DOCUMENTED EXTENSION POINT -- a prepared seam, intentionally NOT built (keeps the core
    pure-stdlib). A WASM runner gives a hard sandbox + portability across any Body with a wasm
    runtime. Contract: content["runner"]=="wasm", content["code"]=base64 .wasm module
    (code_hash covers it unchanged), instantiate with ONLY the imports implied by `granted`,
    apply limits["ms"]."""
    name = "wasm"

    def run(self, content, args, granted):
        raise NotImplementedError(
            "exec-wasm is a prepared seam, not yet built. Register a real ExecRunner("
            "name='wasm') with a wasm runtime to enable portable, hard-sandboxed skills.")


@register
class ExecDriver(Driver):
    """content = {code, code_hash, entry, language, runner, signature, capabilities,
                  limits, provenance}
    The Body invokes via execute(); it never runs unless the hash matches, the call stays
    within declared capabilities, and the provenance/trust gate admits the runner."""
    name = "exec"

    def empty(self, params):
        return {}

    def read(self, content, params, reveal_private=False):
        # the code is readable; the reflex is described, not auto-run
        return {k: content.get(k) for k in
                ("entry", "language", "signature", "capabilities", "limits", "provenance")}

    def retrieve(self, content, params, address):
        return content.get(str(address))

    def append(self, content, params, value):
        raise PermissionError("exec layers are installed via CALCIFY, not append")

    def execute(self, content: Dict[str, Any], args: Dict[str, Any],
                granted: Dict[str, Any] = None) -> Any:
        # 1. integrity gate: code must match the hash it was promoted with
        if code_hash(content["code"]) != content["code_hash"]:
            raise IntegrityError("exec layer hash mismatch -- refusing to run")
        # 2. capability gate: the call may not exceed the declared capability set
        granted = granted or {}
        caps = content.get("capabilities", {})
        for kind in ("reads", "writes", "limbs"):
            asked = set(granted.get(kind, []))
            allowed = set(caps.get(kind, []))
            if not asked <= allowed:
                raise CapabilityError("exec layer exceeded %s capability: %s not in %s"
                                      % (kind, asked - allowed, allowed))
        if granted.get("net") and not caps.get("net"):
            raise CapabilityError("exec layer requested net without capability")
        # 3. trust gate (HF-B50): non-isolating runners run only trusted, in-lineage code.
        runner_name = content.get("runner", "python")
        if (runner_name != "wasm"
                and not provenance_is_trusted(content.get("provenance", {}))
                and not granted.get("allow_untrusted_local")):
            prov = content.get("provenance", {})
            raise TrustError(
                "untrusted-provenance exec layer (author=%r, foreign=%r) refused on "
                "non-isolating runner %r -- run it on the 'wasm' runner, or earn trust via "
                "trial+calcify. Local override: granted={'allow_untrusted_local': True}."
                % (prov.get("author"), prov.get("foreign", False), runner_name))
        # 4. dispatch to the selected runner
        return get_runner(runner_name).run(content, args, granted)


def trial(code: str, entry: str, cases: List[Tuple[Dict[str, Any], Any]]) -> Dict[str, Any]:
    """Run a candidate skill against (args, expected) cases. The static sandbox gate runs
    FIRST: code that could escape the namespace never reaches the proving step. Used by the
    calcification pipeline BEFORE a skill is allowed into an exec layer."""
    validate_skill_code(code)
    drv = ExecDriver()
    candidate = {"code": code, "code_hash": code_hash(code), "entry": entry,
                 "capabilities": {}, "limits": {"ms": 200}}
    passed = 0
    detail = []
    for args, expected in cases:
        try:
            # trial IS the controlled proving step that earns trust (allow_untrusted_local)
            got = drv.execute(candidate, args, {"allow_untrusted_local": True})
            ok = (got == expected)
        except Exception as e:                   # noqa: BLE001
            got, ok = "ERROR:%s" % e, False
        passed += ok
        detail.append({"args": args, "expected": expected, "got": got, "ok": ok})
    return {"cases": len(cases), "passed": passed, "ok": passed == len(cases), "detail": detail}
