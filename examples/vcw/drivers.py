#!/usr/bin/env python3
"""
drivers.py  --  Concrete payload protocols for the VCW (Mantle v2.1)

Four drivers, registered into the Body's registry on import:

  log-json          append-only list of immutable, hashed entries (the v2.0 default)
  keyvalue          a small mutable map (mutated hot, snapshotted on flush)
  calendar-spatial  data stored AS COLORS AT COORDINATES -- a real RGBA canvas you can open
                    as an image. Coordinates encode days; colors encode meaning.
  exec              an executable REFLEX LAYER: organism-grown code the Body can run with no
                    MIND, gated by a content hash and a declared capability set.

These prove that the boot sector -- not hard-coded logic -- decides how a layer behaves.
"""
from __future__ import annotations

import ast
import threading
import time
from datetime import date
from typing import Any, Dict, List, Tuple

from vcw_cube import SIDE, CHANNELS, LAYER_BYTES
from boot import Driver, register, code_hash
from entry import entry_hash as _entry_hash   # the one entry hasher (covers extras incl. authorship)


# ============================================================================
# log-json : append-only immutable entries
# ============================================================================
def make_entry(content: Any, opcode: str = "WRITE", author: str = "BODY",
               source: str = "", **extra) -> Dict[str, Any]:
    e = {"id": None, "ts": time.time(), "opcode": opcode, "author": author,
         "source": source, "content": content, "tombstone": False, "quarantined": False}
    e.update(extra)               # e.g. authorship, verified, confidence -- now INSIDE the hash
    e["hash"] = _entry_hash(e)
    return e


@register
class LogJsonDriver(Driver):
    name = "log-json"

    def empty(self, params):
        return []

    def read(self, content, params, reveal_private=False):
        return [e for e in content
                if not e.get("tombstone") and not e.get("quarantined")]

    def retrieve(self, content, params, address):
        # address is an entry index into the VISIBLE entries
        vis = self.read(content, params)
        i = int(address)
        return vis[i] if 0 <= i < len(vis) else None

    def append(self, content, params, value):
        e = value if isinstance(value, dict) and "hash" in value else make_entry(value)
        e = dict(e)
        e["id"] = len(content)
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
    """params = {
         "epoch": "2026-01-01",
         "palette": { "ff0000": "urgent", "0066ff": "work", "00aa00": "personal" }
       }
    A date maps to a cell (x = weekday 0..6, y = week index since epoch). The cell's
    pixel RGBA stores the appointment color; alpha 0 means 'free'.
    """
    name = "calendar-spatial"

    def empty(self, params):
        return bytearray(LAYER_BYTES)  # all zero = an empty (all-free) canvas

    # -- coordinate math ---------------------------------------------------
    def coord_for_date(self, params, iso: str) -> Tuple[int, int]:
        epoch = date.fromisoformat(params["epoch"])
        d = date.fromisoformat(iso)
        days = d.toordinal() - epoch.toordinal() + epoch.weekday()
        return d.weekday(), days // 7        # (x = day-of-week, y = week index)

    def _palette_inverse(self, params) -> Dict[str, str]:
        return {v: k for k, v in params.get("palette", {}).items()}

    def _offset(self, x: int, y: int) -> int:
        return (y * SIDE + x) * CHANNELS

    # -- the three verbs ---------------------------------------------------
    def read(self, content, params, reveal_private=False):
        # enumerate every non-free cell as {coord, color, meaning}
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
        # address is a coordinate tuple (x, y)
        x, y = address
        off = self._offset(int(x), int(y))
        r, g, b, a = content[off:off + CHANNELS]
        if not a:
            return "free"
        return params.get("palette", {}).get("%02x%02x%02x" % (r, g, b), "unknown")

    def append(self, content, params, value):
        # value = (iso_date, meaning)
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
# exec : an executable reflex layer (learning -> instinct)
# ============================================================================
SAFE_BUILTINS = {n: __builtins__[n] if isinstance(__builtins__, dict) else getattr(__builtins__, n)
                 for n in ("abs", "min", "max", "sum", "round", "len", "range", "float",
                           "int", "str", "bool", "list", "dict", "tuple", "enumerate",
                           "sorted", "map", "filter", "zip", "all", "any")}


class CapabilityError(Exception):
    pass


class IntegrityError(Exception):
    pass


class SandboxError(Exception):
    """Raised when a candidate Python skill contains a STATIC escape vector and so must never be
    calcified into a reflex (HF-B51). The Python runner's restricted namespace is not a hard
    sandbox: it is trivially escaped at runtime via dunder traversal
    (`().__class__.__bases__[0].__subclasses__()` reaches `os`/`subprocess`) or an `import`. The
    capability/integrity/trust gates fire at EXECUTE time, but the cheapest, most reliable defense
    is to refuse such code at CULTIVATION time -- before it ever becomes an instinct. This is a
    static AST check, complementary to the hard-sandbox `wasm` runner seam (the eventual answer for
    untrusted or foreign code)."""


# Names a skill may never reference, and dunder attribute access (the namespace-escape vectors).
_FORBIDDEN_NAMES = frozenset({
    "eval", "exec", "compile", "__import__", "open", "globals", "locals", "vars",
    "getattr", "setattr", "delattr", "input", "breakpoint", "memoryview", "exit", "quit",
    "help", "__builtins__",
})


def validate_skill_code(code: str) -> None:
    """Static gate for a Python skill: reject `import`, dunder attribute access, and forbidden
    builtins. Raises SandboxError on the first violation; returns None if the code is clean.
    (Applies to the `python` runner; a `wasm` skill is a compiled module checked by its sandbox.)"""
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


class TrustError(Exception):
    """Raised when an untrusted/foreign-provenance exec layer is asked to run on a
    non-isolating runner (the Python runner). Such code must run on the 'wasm' runner
    (a hard sandbox) instead. See HF-B50."""
    pass


# Authors whose calcified skills are considered in-lineage/trusted on the Python runner.
TRUSTED_AUTHORS = frozenset({"MIND", "BODY"})


def provenance_is_trusted(provenance: Dict[str, Any]) -> bool:
    """A skill is trusted only if it was authored by this organism's own MIND/BODY and is
    not flagged foreign (e.g. a GRAFT-imported skill). Trust governs which RUNNER may run it,
    not whether it runs at all: untrusted code may still run on an isolating ('wasm') runner."""
    p = provenance or {}
    return (p.get("author") in TRUSTED_AUTHORS) and not p.get("foreign", False)


# ---- pluggable exec runners ------------------------------------------------
# Gates (hash + capability) are applied by ExecDriver BEFORE a runner runs. A runner only builds
# the execution environment, calls the entry point, and enforces the time limit. This is the seam
# where a portable, hard-sandboxed WASM runner drops in later (see the exec-wasm contract below).
_RUNNERS: Dict[str, "ExecRunner"] = {}


def register_runner(cls):
    inst = cls() if isinstance(cls, type) else cls
    _RUNNERS[inst.name] = inst
    return cls


def get_runner(name: str) -> "ExecRunner":
    if name not in _RUNNERS:
        raise NotImplementedError(
            "no exec runner %r registered (have: %s). To enable WASM, register an "
            "ExecRunner(name='wasm') -- see the exec-wasm contract in vcw/GUIDE.md."
            % (name, ", ".join(sorted(_RUNNERS))))
    return _RUNNERS[name]


class ExecRunner:
    """Executes a calcified exec layer's payload. Subclasses implement run(); gates are already
    applied by ExecDriver, so a runner only builds the environment, calls the entry, and enforces
    the time limit."""
    name = "base"

    def run(self, content: Dict[str, Any], args: Dict[str, Any],
            granted: Dict[str, Any]) -> Any:
        raise NotImplementedError


@register_runner
class PythonExecRunner(ExecRunner):
    """The default runner: executes Python source in a restricted namespace with a wall-clock
    limit. Pure stdlib. A 'restricted' namespace is NOT a hard sandbox -- for untrusted skills or
    cross-substrate portability, use the wasm runner instead."""
    name = "python"

    def run(self, content, args, granted):
        g = {"__builtins__": SAFE_BUILTINS}
        loc: Dict[str, Any] = {}
        exec(content["code"], g, loc)              # defines the entry function
        fn = loc.get(content["entry"]) or g.get(content["entry"])
        if fn is None:
            raise IntegrityError("entry %r not defined by exec layer" % content["entry"])
        result: List[Any] = []
        err: List[BaseException] = []

        def _run():
            try:
                result.append(fn(**args))
            except BaseException as e:             # noqa: BLE001 -- sandboxed
                err.append(e)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=content.get("limits", {}).get("ms", 200) / 1000.0)
        if t.is_alive():
            raise TimeoutError("exec layer exceeded its time budget")
        if err:
            raise err[0]
        return result[0] if result else None


@register_runner
class WasmExecRunner(ExecRunner):
    """DOCUMENTED EXTENSION POINT -- a prepared seam, intentionally NOT built (keeps the codec
    pure-stdlib). A WASM runner gives skills two things the Python runner cannot: a HARD sandbox
    (no ambient FS/net/process; only host imports you grant) and PORTABILITY across any Body with
    a wasm runtime (software or hardware), so a calcified skill inherits across the lineage.

    exec-wasm contract (what an implementer fills in):
        content["runner"]   == "wasm"
        content["language"]  -- source language the skill was authored in (informational)
        content["runtime"]   -- target wasm runtime, e.g. "wasi-preview1"
        content["code"]      -- base64-encoded .wasm module (code_hash covers it, unchanged)
        content["entry"]     -- exported function to call
        capabilities/limits  -- enforced identically; instantiate the module with ONLY the imports
                                implied by `granted`, and apply `limits["ms"]`.
    To build: add a wasm runtime dependency (e.g. wasmtime), instantiate with granted imports,
    call `entry(args)`, enforce the time limit, return the result -- then this stub goes away."""
    name = "wasm"

    def run(self, content, args, granted):
        raise NotImplementedError(
            "exec-wasm is a prepared seam, not yet built. Register a real ExecRunner(name='wasm') "
            "with a wasm runtime to enable portable, hard-sandboxed skills. See vcw/GUIDE.md.")


@register
class ExecDriver(Driver):
    """content = {
         "code": "<source or base64 module>", "code_hash": "sha256:...", "entry": "fn_name",
         "language": "python", "runner": "python",   # 'python' (default) | 'wasm' (prepared seam)
         "signature": {...},
         "capabilities": {"reads": [...], "writes": [...], "limbs": [...], "net": false},
         "limits": {"ms": 200}, "provenance": {...}
       }
    The Body invokes this layer via execute(); it never runs unless the hash matches and the call
    stays within declared capabilities. Execution itself is delegated to a pluggable ExecRunner
    selected by `runner` (default 'python'); the gates here are runner-agnostic.
    """
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

    # -- execution (called by the Body, not by append/read) ----------------
    def execute(self, content: Dict[str, Any], args: Dict[str, Any],
                granted: Dict[str, Any] = None) -> Any:
        # 1. integrity gate: the code must match the hash its boot sector was promoted with
        if code_hash(content["code"]) != content["code_hash"]:
            raise IntegrityError("exec layer hash mismatch -- refusing to run")
        # 2. capability gate: the call may not request a band/limb the layer did not declare
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
        # 3. trust gate (HF-B50): a non-isolating runner (the Python runner is NOT a hard
        #    sandbox) may run only TRUSTED, in-lineage code. Untrusted/foreign skills must use
        #    the isolating 'wasm' runner. An explicit local override exists for controlled use
        #    (e.g. the `trial` proving step, which is how a skill EARNS trust before calcify).
        runner_name = content.get("runner", "python")
        if (runner_name != "wasm"
                and not provenance_is_trusted(content.get("provenance", {}))
                and not granted.get("allow_untrusted_local")):
            prov = content.get("provenance", {})
            raise TrustError(
                "untrusted-provenance exec layer (author=%r, foreign=%r) refused on "
                "non-isolating runner %r -- run it on the 'wasm' runner (hard sandbox), or "
                "earn trust via trial+calcify. Local override: granted={'allow_untrusted_local': True}."
                % (prov.get("author"), prov.get("foreign", False), runner_name))
        # 4. dispatch to the selected runner (default 'python'; 'wasm' is a prepared seam)
        return get_runner(runner_name).run(content, args, granted)


def trial(code: str, entry: str, cases: List[Tuple[Dict[str, Any], Any]]) -> Dict[str, Any]:
    """Run a candidate skill against (args, expected) cases in the sandbox. Used by the
    calcification pipeline BEFORE a skill is allowed into an exec layer. The static sandbox gate
    runs FIRST: code that could escape the namespace never even reaches the proving step."""
    validate_skill_code(code)
    drv = ExecDriver()
    candidate = {"code": code, "code_hash": code_hash(code), "entry": entry,
                 "capabilities": {}, "limits": {"ms": 200}}
    passed = 0
    detail = []
    for args, expected in cases:
        try:
            # trial IS the controlled proving step that earns trust, so it runs the candidate
            # locally even though it has no provenance yet (allow_untrusted_local).
            got = drv.execute(candidate, args, {"allow_untrusted_local": True})
            ok = (got == expected)
        except Exception as e:                   # noqa: BLE001
            got, ok = "ERROR:%s" % e, False
        passed += ok
        detail.append({"args": args, "expected": expected, "got": got, "ok": ok})
    return {"cases": len(cases), "passed": passed, "ok": passed == len(cases), "detail": detail}
