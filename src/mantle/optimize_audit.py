#!/usr/bin/env python3
"""
mantle.optimize_audit  --  repository-wide optimization inventory receipts

This is the first executable bone of the whole-repository optimization protocol:
it inventories the source tree, classifies every non-VCS file, records basic
metrics, detects Python imports/public symbols, labels tokenizer counts as
measured or unverifiable, and writes protocol-named artifacts outside the source
tree by default. It does not mutate project files.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import paths

TEXT_EXTS = {
    ".cfg", ".css", ".gitignore", ".html", ".ini", ".js", ".json", ".md", ".py",
    ".svg", ".toml", ".txt", ".yaml", ".yml",
}
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".zip"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "node_modules"}
COMMAND_RE = re.compile(r"python\s+-m\s+mantle(?:\s+[A-Za-z0-9_.-]+)*")
PATH_RE = re.compile(r"(?:(?:src|documents|examples|\.github)/[A-Za-z0-9_./ -]+)")
ENV_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
REQUIRED_ARTIFACTS = (
    "FILE_INVENTORY",
    "CHANGE_LEDGER",
    "MERGE_MAP",
    "ALIAS_REGISTRY",
    "COVERAGE_MATRIX",
    "ALIGNMENT_MATRIX",
    "TOKEN_REPORT",
    "TEST_REPORT",
    "PERFORMANCE_REPORT",
    "SKIP_BLOCK_REPORT",
    "FINAL_RECEIPT",
)


def _rel(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def _git_lines(root: str, *args: str) -> List[str]:
    try:
        p = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True,
                           timeout=30)
    except Exception:
        return []
    if p.returncode != 0:
        return []
    return [x.strip().replace("\\", "/") for x in p.stdout.splitlines() if x.strip()]


def _tracked(root: str) -> set:
    return set(_git_lines(root, "ls-files"))


def _status_untracked(root: str) -> set:
    return {x[3:] for x in _git_lines(root, "status", "--short")
            if x.startswith("?? ")}


def iter_repo_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield os.path.join(dirpath, name)


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _decode(data: bytes, ext: str) -> Tuple[bool, Optional[str], Optional[str]]:
    if ext.lower() in BINARY_EXTS or b"\x00" in data[:4096]:
        return False, None, None
    try:
        return True, "utf-8", data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return True, "utf-8-sig", data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return False, None, None


def _language(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".py": "python", ".md": "markdown", ".txt": "text", ".json": "json",
        ".toml": "toml", ".yaml": "yaml", ".yml": "yaml", ".html": "html",
        ".js": "javascript", ".svg": "svg", ".css": "css",
    }.get(ext, ext[1:] or "unknown")


def _category(rel: str, text: bool) -> str:
    p = rel.lower()
    if not text:
        return "N binary/media"
    if p.startswith(".github/") or p in {".gitignore", "pyproject.toml"}:
        return "E configuration"
    if p.startswith("src/mantle/audits/") or p.startswith("examples/tests/"):
        return "B test"
    if p == "src/mantle/cli.py" or p.startswith("src/mantle/check.py"):
        return "G CLI or public interface"
    if p.startswith("src/"):
        return "A production source"
    if p.startswith("documents/grimoire/"):
        return "C machine-only prompt or doctrine"
    if p.startswith("documents/"):
        return "D human-facing documentation"
    if p.startswith("examples/"):
        return "H example or fixture"
    if p in {"readme.md", "contributing.md", "license"}:
        return "D human-facing documentation"
    return "Q unknown"


def _subsystem(rel: str) -> str:
    parts = rel.split("/")
    if rel.startswith("src/mantle/"):
        return "/".join(parts[:3]) if len(parts) > 2 else "src/mantle"
    if rel.startswith("documents/grimoire/"):
        return "documents/grimoire"
    return parts[0] if parts else ""


def _purpose(rel: str, category: str) -> str:
    if rel == "README.md":
        return "repository overview and checked certification-count anchor"
    if rel.endswith("pyproject.toml"):
        return "package metadata and dependency declaration"
    if rel.startswith("documents/grimoire/"):
        return "canonical Grimoire doctrine"
    if rel.startswith("src/mantle/audits/"):
        return "certification and invariant proof"
    if rel.startswith("src/mantle/"):
        return "MantleOS runtime implementation"
    if rel.startswith("examples/tests/"):
        return "example smoke or parity test"
    return category.split(" ", 1)[1] if " " in category else category


def _python_details(text: str) -> Tuple[List[str], List[str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [], []
    imports, public = [], []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append("." * node.level + (node.module or ""))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                public.append(node.name)
    return sorted(set(imports)), sorted(public)


def _module_name(rel: str) -> Optional[str]:
    if not rel.startswith("src/") or not rel.endswith(".py"):
        return None
    mod = rel[4:-3].replace("/", ".")
    return mod[:-9] if mod.endswith(".__init__") else mod


def _clean_path_ref(raw: str) -> str:
    ref = raw.replace("\\", "/").strip().strip("`'\";,:)]")
    ref = ref.replace("%20", " ")
    for ext in (".md", ".py", ".json", ".html", ".yaml", ".yml", ".toml", ".txt",
                ".svg", ".png", ".js"):
        i = ref.lower().find(ext)
        if i >= 0:
            return ref[:i + len(ext)].strip().strip("`'\";,:)]")
    for marker in (" --", " #", " |", ")", "]"):
        if marker in ref:
            ref = ref.split(marker, 1)[0]
    parts = ref.split()
    if parts:
        ref = parts[0]
    return ref.rstrip("/.")


def _command_name(command: str) -> Optional[str]:
    parts = command.split()
    try:
        i = parts.index("mantle")
    except ValueError:
        return None
    if i + 1 >= len(parts):
        return None
    name = parts[i + 1].strip("`'\".,):]").replace("_", "-")
    if not name or name.startswith("--") or name in {"...", "<command>", "<op>"}:
        return None
    return name


def _status_rows(root: str) -> List[Dict[str, str]]:
    rows = []
    for line in _git_lines(root, "status", "--short"):
        if len(line) < 4:
            continue
        rows.append({"status": line[:2], "path": line[3:]})
    return rows


def _token_counts(text: Optional[str]) -> Tuple[Dict[str, Optional[int]], Optional[str]]:
    if text is None:
        return {"cl100k": None, "o200k": None}, None
    try:
        import tiktoken  # type: ignore
    except Exception:
        return {"cl100k": None, "o200k": None}, "tiktoken unavailable"
    counts = {}
    for name, enc_name in (("cl100k", "cl100k_base"), ("o200k", "o200k_base")):
        try:
            counts[name] = len(tiktoken.get_encoding(enc_name).encode(text))
        except Exception:
            counts[name] = None
    return counts, None


def inventory_file(path: str, root: str, tracked: set, untracked: set) -> Dict[str, Any]:
    rel = _rel(path, root)
    data = _read_bytes(path)
    ext = os.path.splitext(rel)[1].lower()
    is_text, enc, text = _decode(data, ext)
    category = _category(rel, is_text)
    imports: List[str] = []
    public: List[str] = []
    if is_text and rel.endswith(".py") and text is not None:
        imports, public = _python_details(text)
    commands = sorted(set(COMMAND_RE.findall(text or "")))
    path_refs = sorted(set(_clean_path_ref(x) for x in PATH_RE.findall(text or "")
                           if _clean_path_ref(x)))
    env_vars = sorted(set(x for x in ENV_RE.findall(text or "")
                          if "_" in x and not x.startswith("HF_")))
    tokens, token_note = _token_counts(text)
    return {
        "path": rel,
        "category": category,
        "tracked": rel in tracked,
        "untracked": rel in untracked,
        "text": is_text,
        "encoding": enc,
        "language": _language(rel),
        "generated": False,
        "generator": None,
        "purpose": _purpose(rel, category),
        "subsystem": _subsystem(rel),
        "imports": imports,
        "public_symbols": public,
        "referenced_commands": commands,
        "referenced_paths": path_refs,
        "environment_variables": env_vars,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "lines": 0 if text is None else text.count("\n") + (1 if text else 0),
        "words": 0 if text is None else len(re.findall(r"\S+", text)),
        "tokens": tokens,
        "token_status": token_note or ("measured" if text is not None else "not-text"),
        "optimization_eligibility": "inventory-only" if not is_text else "eligible-for-pass-review",
        "risk": "high" if rel.startswith("src/mantle/core/") else "normal",
        "proof_path": "PYTHONPATH=src python -m mantle check",
}


def _derived_maps(report: Dict[str, Any]) -> Dict[str, Any]:
    from .cli import known_commands

    files = report["files"]
    path_set = {f["path"] for f in files}
    dir_set = set()
    for path in path_set:
        parts = path.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dir_set.add("/".join(parts[:i]))
    module_paths = {m: f["path"] for f in files for m in [_module_name(f["path"])] if m}
    import_graph = {f["path"]: f["imports"] for f in files if f["imports"]}
    importers: Dict[str, List[str]] = {}
    for path, imports in import_graph.items():
        for imp in imports:
            importers.setdefault(imp, []).append(path)
    public_api = {f["path"]: f["public_symbols"] for f in files if f["public_symbols"]}
    commands = sorted({cmd for f in files for cmd in f["referenced_commands"]})
    known = set(known_commands())
    command_refs = []
    for f in files:
        for cmd in f["referenced_commands"]:
            name = _command_name(cmd)
            command_refs.append({"from": f["path"], "command": cmd,
                                 "name": name, "exists": name is None or name in known})
    env_vars = sorted({v for f in files for v in f["environment_variables"]})
    path_refs = []
    for f in files:
        for ref in f["referenced_paths"]:
            norm = ref.replace("\\", "/").strip("/")
            exists = norm in path_set or norm in dir_set
            weak_fragment = not exists and "." not in os.path.basename(norm)
            if weak_fragment or norm.endswith("_"):
                continue
            path_refs.append({"from": f["path"], "ref": norm, "exists": exists})
    sha_groups: Dict[str, List[str]] = {}
    for f in files:
        sha_groups.setdefault(f["sha256"], []).append(f["path"])
    duplicates = [{"sha256": sha, "paths": paths_}
                  for sha, paths_ in sorted(sha_groups.items())
                  if len(paths_) > 1]
    return {
        "module_paths": module_paths,
        "import_graph": import_graph,
        "importers": {k: sorted(v) for k, v in sorted(importers.items())},
        "public_api": public_api,
        "cli_commands": commands,
        "cli_command_references": command_refs,
        "known_cli_commands": sorted(known),
        "environment_variables": env_vars,
        "path_references": path_refs,
        "duplicate_hashes": duplicates,
    }


def _alias_registry() -> Dict[str, Any]:
    aliases = [
        {"token": "Body", "namespace": "AppAI ontology",
         "definition": "deterministic organism runtime that owns effects and memory"},
        {"token": "MIND", "namespace": "AppAI ontology",
         "definition": "optional Phase-2 reasoning layer; proposes bounded intentions"},
        {"token": "SELF", "namespace": "identity boundary",
         "definition": "artifact the Body can prove inside its identity boundary"},
        {"token": "OTHER", "namespace": "identity boundary",
         "definition": "unproven evidence; quarantined before trust"},
        {"token": "VCW", "namespace": "storage substrate",
         "definition": "visual computation/witness memory grammar"},
        {"token": "SPOREAGENT", "namespace": "reproduction lifecycle",
         "definition": "agent-readable launch artifact around a spore source receipt"},
    ]
    folded = [a["token"].casefold() for a in aliases]
    collisions = [token for token, count in Counter(folded).items() if count > 1]
    return {
        "canonical_source": "documents/grimoire plus MantleOS doctrine",
        "aliases": aliases,
        "collision_audit": {
            "casefold_collisions": collisions,
            "status": "PASS" if not collisions else "REVISE",
        },
        "tokenizer_status": "UNVERIFIABLE when tiktoken unavailable",
    }


def _coverage_matrix(report: Dict[str, Any]) -> List[Dict[str, str]]:
    files = {f["path"] for f in report["files"]}
    rows = [
        ("Stage-1 Zombie Body gate", "python -m mantle audit", "src/mantle/audits/stage1.py"),
        ("Stage-2 MIND gate", "python -m mantle audit-mind", "src/mantle/audits/stage2.py"),
        ("Security invariant suite", "python -m mantle prove", "src/mantle/audits/invariants.py"),
        ("Whole certification", "python -m mantle check", "src/mantle/check.py"),
        ("Optimization inventory", "python -m mantle optimize-audit", "src/mantle/optimize_audit.py"),
        ("SPORE purity", "python examples/spore/audit_spore.py", "examples/spore/audit_spore.py"),
        ("VCW conformance", "python examples/spore/vcw_conformance.py",
         "examples/spore/vcw_conformance.py"),
    ]
    return [{"concept": c, "proof": proof, "file": path,
             "status": "present" if path in files else "missing"}
            for c, proof, path in rows]


def _change_ledger(report: Dict[str, Any]) -> List[Dict[str, str]]:
    rows = []
    status = _status_rows(report["repo_root"])
    for item in status:
        rows.append({
            "path": item["path"],
            "status": item["status"],
            "receipt": "working-tree change present; verify with git diff and mantle check",
        })
    if not rows:
        rows.append({"path": "*", "status": "clean",
                     "receipt": "no working-tree changes at audit time"})
    return rows


def _merge_map(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "baseline",
        "merges_performed_by_this_audit": [],
        "compatibility_aliases_detected": [
            {"old": "optimize_audit", "new": "optimize-audit",
             "surface": "CLI", "mode": "underscore compatibility alias"}
        ],
        "duplicate_hashes": report["maps"]["duplicate_hashes"],
    }


def _test_report(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "audit-artifact declaration",
        "environment": {"python": sys.version.split()[0], "branch": report["branch"],
                         "head": report["head"]},
        "commands": [
            {"command": "PYTHONPATH=src python -m mantle optimize-audit",
             "coverage": "artifact generation", "result": "run by caller when generated"},
            {"command": "PYTHONPATH=src python -m mantle prove",
             "coverage": "security invariants", "result": "required final proof"},
            {"command": "PYTHONPATH=src python -m mantle check",
             "coverage": "full certification", "result": "required final proof"},
        ],
        "note": "This command does not run the suite; it records the proof path to keep inventory non-mutating.",
    }


def _performance_report(report: Dict[str, Any]) -> Dict[str, Any]:
    total_bytes = sum(f["bytes"] for f in report["files"])
    total_lines = sum(f["lines"] for f in report["files"])
    return {
        "status": "baseline-only",
        "metrics": {"files": report["file_count"], "bytes": total_bytes, "lines": total_lines},
        "benchmarks": [],
        "confidence": "low; no benchmark command is run by optimize-audit",
    }


def strict_failures(report: Dict[str, Any], artifacts: Optional[Dict[str, str]] = None
                    ) -> List[str]:
    """Machine-checkable whole-project alignment failures for --strict mode."""
    failures: List[str] = []
    unknown = report["categories"].get("Q unknown", 0)
    if unknown:
        failures.append("%d unknown-category files" % unknown)
    missing = report.get("tracked_missing") or []
    if missing:
        failures.append("%d tracked files missing from disk" % len(missing))
    stale_paths = [r for r in report["maps"]["path_references"] if not r["exists"]]
    if stale_paths:
        failures.append("%d unresolved path references" % len(stale_paths))
    stale_commands = [r for r in report["maps"]["cli_command_references"] if not r["exists"]]
    if stale_commands:
        failures.append("%d unresolved Mantle CLI references" % len(stale_commands))
    if report["alias_registry"]["collision_audit"]["status"] != "PASS":
        failures.append("alias registry collision audit failed")
    missing_coverage = [r for r in report["coverage_matrix"] if r["status"] != "present"]
    if missing_coverage:
        failures.append("%d missing proof surfaces" % len(missing_coverage))
    if artifacts is not None:
        missing_artifacts = [name for name, path in artifacts.items() if not os.path.exists(path)]
        if missing_artifacts:
            failures.append("missing artifacts: %s" % ", ".join(missing_artifacts))
        if set(artifacts) != set(REQUIRED_ARTIFACTS):
            failures.append("artifact set does not match REQUIRED_ARTIFACTS")
    return failures


def build_inventory(root: str = paths.REPO_ROOT) -> Dict[str, Any]:
    root = os.path.abspath(root)
    tracked = _tracked(root)
    untracked = _status_untracked(root)
    files = [inventory_file(path, root, tracked, untracked)
             for path in sorted(iter_repo_files(root), key=lambda p: _rel(p, root).lower())]
    categories = Counter(f["category"] for f in files)
    token_status = Counter(f["token_status"] for f in files)
    tracked_missing = sorted(x for x in tracked
                             if not os.path.exists(os.path.join(root, x.replace("/", os.sep))))
    report = {
        "schema": "mantle-optimization-inventory-v1",
        "repo_root": root,
        "head": (_git_lines(root, "rev-parse", "HEAD") or ["unknown"])[0],
        "branch": (_git_lines(root, "branch", "--show-current") or ["unknown"])[0],
        "file_count": len(files),
        "tracked_count": len(tracked),
        "tracked_missing": tracked_missing,
        "categories": dict(sorted(categories.items())),
        "token_status": dict(sorted(token_status.items())),
        "files": files,
    }
    report["maps"] = _derived_maps(report)
    report["alias_registry"] = _alias_registry()
    report["coverage_matrix"] = _coverage_matrix(report)
    report["change_ledger"] = _change_ledger(report)
    report["merge_map"] = _merge_map(report)
    report["test_report"] = _test_report(report)
    report["performance_report"] = _performance_report(report)
    return report


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_artifacts(report: Dict[str, Any], out_dir: str) -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    files = report["files"]
    artifacts = {name: os.path.join(out_dir, name + (".json" if name in {
        "FILE_INVENTORY", "CHANGE_LEDGER", "MERGE_MAP", "ALIAS_REGISTRY",
        "COVERAGE_MATRIX", "TOKEN_REPORT", "TEST_REPORT", "PERFORMANCE_REPORT",
    } else ".md")) for name in REQUIRED_ARTIFACTS}
    _write(artifacts["FILE_INVENTORY"], json.dumps(report, indent=2, sort_keys=True))
    _write(artifacts["CHANGE_LEDGER"],
           json.dumps(report["change_ledger"], indent=2, sort_keys=True))
    _write(artifacts["MERGE_MAP"], json.dumps(report["merge_map"], indent=2, sort_keys=True))
    _write(artifacts["ALIAS_REGISTRY"],
           json.dumps(report["alias_registry"], indent=2, sort_keys=True))
    _write(artifacts["COVERAGE_MATRIX"],
           json.dumps(report["coverage_matrix"], indent=2, sort_keys=True))
    _write(artifacts["TOKEN_REPORT"], json.dumps({
        "token_status": report["token_status"],
        "files": [{"path": f["path"], "tokens": f["tokens"],
                   "token_status": f["token_status"], "bytes": f["bytes"],
                   "lines": f["lines"], "words": f["words"]} for f in files],
    }, indent=2, sort_keys=True))
    _write(artifacts["TEST_REPORT"],
           json.dumps(report["test_report"], indent=2, sort_keys=True))
    _write(artifacts["PERFORMANCE_REPORT"],
           json.dumps(report["performance_report"], indent=2, sort_keys=True))
    skipped = [f for f in files if not f["text"] or f["category"].startswith("N ")]
    _write(artifacts["SKIP_BLOCK_REPORT"],
           "# Skip / Block Report\n\n"
           + "\n".join("- `%s`: %s" % (f["path"], f["optimization_eligibility"])
                       for f in skipped) + "\n")
    stale_paths = [r for r in report["maps"]["path_references"] if not r["exists"]]
    stale_commands = [r for r in report["maps"]["cli_command_references"] if not r["exists"]]
    _write(artifacts["ALIGNMENT_MATRIX"],
           "# Alignment Matrix\n\n"
           "Status: baseline alignment map; full semantic convergence remains pending.\n\n"
           "Referenced path rows: %d; unresolved by normalized file/dir match: %d.\n\n"
           "Referenced Mantle CLI rows: %d; unresolved command names: %d.\n\n"
           % (len(report["maps"]["path_references"]), len(stale_paths),
              len(report["maps"]["cli_command_references"]), len(stale_commands))
           + ("" if not stale_commands else "Unresolved command examples:\n"
              + "\n".join("- `%s` in `%s`" % (r["command"], r["from"])
                          for r in stale_commands[:20]) + "\n\n")
           + "Proof surfaces:\n"
           + "\n".join("- %s: %s (%s)" % (r["concept"], r["proof"], r["status"])
                       for r in report["coverage_matrix"])
           + "\n\n"
           "Categories:\n"
           + "\n".join("- %s: %s" % item for item in sorted(report["categories"].items()))
           + "\n")
    _write(artifacts["FINAL_RECEIPT"],
           "# Optimization Audit Receipt\n\n"
           "WHAT: generated the required whole-repository optimization protocol artifacts.\n"
           "\nWHY: whole-repository optimization requires file inventory before mutation.\n"
           "\nEVIDENCE: %d files inventoried on `%s` at `%s`.\n"
           "\nCONFIDENCE: medium for inventory coverage; token counts remain unverifiable without tiktoken.\n"
           "\nTOKEN_DELTA: not applicable; baseline artifact pass only.\n"
           "\nCOMPLEXITY_DELTA: adds one stdlib-only audit module and one CLI route.\n"
           "\nPERFORMANCE_DELTA: no runtime path affected; audit cost is file traversal.\n"
           "\nFILES: %d inventoried; %d artifact files written.\n"
           "\nTESTS: run `python -m mantle prove` and `python -m mantle check` after changes.\n"
           "\nPUBLIC_API_CHANGES: adds `python -m mantle optimize-audit`.\n"
           "\nBEHAVIOR_CHANGES: none to organism runtime behavior.\n"
           "\nPRESERVED_INVARIANTS: Body-before-MIND, SELF/OTHER, cache, lineage, host preservation.\n"
           "\nRISKS: artifact path references are literal-string checks, not full semantic proof.\n"
           "\nOPEN_QUESTIONS: tokenizer measurement needs optional tiktoken authority.\n"
           "\nBLOCKERS: full protocol completion still needs chunk-by-chunk optimization passes.\n"
           "\nALIGNMENT_RESULT: REVISE; baseline maps generated, convergence pending.\n"
           "\nGUARDIAN_RESULT: REVISE; safe to continue in smaller passes.\n"
           % (report["file_count"], report["branch"], report["head"],
              report["file_count"], len(artifacts)))
    return artifacts


def default_out_dir(root: str = paths.REPO_ROOT) -> str:
    return os.path.join(tempfile.gettempdir(), "mantle-os-optimization-artifacts")


def main(argv=None) -> int:
    argv = list(argv or [])
    out_dir = default_out_dir()
    strict = "--strict" in argv
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            print("usage: python -m mantle optimize-audit [--out DIR] [--json]")
            return 2
        out_dir = argv[i + 1]
    for arg in argv:
        if arg.startswith("--out="):
            out_dir = arg.split("=", 1)[1]
    report = build_inventory()
    artifacts = write_artifacts(report, out_dir)
    failures = strict_failures(report, artifacts)
    if "--json" in argv:
        print(json.dumps({"ok": True, "out_dir": out_dir, "artifacts": artifacts,
                          "file_count": report["file_count"],
                          "categories": report["categories"],
                          "token_status": report["token_status"],
                          "strict": {"ok": not failures, "failures": failures}},
                         indent=2, sort_keys=True))
    else:
        print("MANTLE OPTIMIZATION AUDIT")
        print("  files      : %d" % report["file_count"])
        print("  branch/head: %s %s" % (report["branch"], report["head"][:12]))
        print("  artifacts  : %s" % out_dir)
        for name, path in artifacts.items():
            print("    %-16s %s" % (name, path))
        if report["token_status"].get("tiktoken unavailable"):
            print("  tokens     : UNVERIFIABLE (tiktoken unavailable)")
        if strict:
            print("  strict     : %s" % ("PASS" if not failures else "FAIL"))
            for failure in failures:
                print("               - %s" % failure)
    return 1 if strict and failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
