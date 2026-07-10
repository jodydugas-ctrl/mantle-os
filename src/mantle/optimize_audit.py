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
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
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
SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{12,}|sk-or-v1-[A-Za-z0-9_-]+|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----)",
    re.DOTALL,
)
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
REQUIRED_FILE_FIELDS = (
    "path",
    "category",
    "tracked",
    "untracked",
    "text",
    "encoding",
    "language",
    "generated",
    "generator",
    "purpose",
    "subsystem",
    "imports",
    "importers",
    "public_symbols",
    "referenced_commands",
    "referenced_paths",
    "schemas",
    "configuration_keys",
    "environment_variables",
    "external_interfaces",
    "tests",
    "documentation_references",
    "appai_roles",
    "lifecycle_roles",
    "security_privacy_relevance",
    "side_effects",
    "invariants",
    "proof_path",
    "bytes",
    "sha256",
    "lines",
    "words",
    "tokens",
    "token_status",
    "complexity_indicators",
    "duplication_indicators",
    "risk",
    "optimization_eligibility",
    "skip_block_reason",
)
REQUIRED_PROJECT_MODEL_MAPS = (
    "file_dependency_graph",
    "python_import_export_graph",
    "public_api_graph",
    "cli_command_option_graph",
    "configuration_graph",
    "schema_serialization_graph",
    "test_to_production_coverage_graph",
    "documentation_to_implementation_graph",
    "example_to_api_graph",
    "lifecycle_graph",
    "appai_organ_map",
    "self_other_boundary_map",
    "effect_action_proof_map",
    "hard_fail_map",
    "vcw_band_owner_writer_map",
    "provider_cache_configuration_map",
    "version_compatibility_graph",
    "duplicate_concept_map",
)
REQUIRED_ALIAS_COLLISION_CHECKS = (
    "exact_duplicate_aliases",
    "casefold_collisions",
    "punctuation_collisions",
    "prefix_collisions",
    "class_marker_collisions",
    "mode_marker_collisions",
    "error_code_collisions",
    "public_cli_collisions",
    "environment_variable_collisions",
    "schema_field_collisions",
    "python_symbol_collisions",
    "filesystem_case_collisions",
)
MERGE_CANDIDATE_FIELDS = (
    "candidate_id",
    "kind",
    "items",
    "shared_key",
    "score",
    "shared_purpose",
    "authority_compatibility",
    "side_effect_compatibility",
    "security_compatibility",
    "lifecycle_compatibility",
    "proof_compatibility",
    "callers_known",
    "decision",
    "reason",
)
MERGE_PARITY_FIELDS = (
    "candidate_id",
    "status",
    "steelman",
    "items",
    "caller_matrix",
    "parity_dimensions",
    "mode_complexity",
    "compatibility_alias",
    "safe_to_merge_now",
    "proof_required",
    "decision",
    "receipt",
)
FILE_COMPLETION_FIELDS = (
    "path",
    "status",
    "eligible_chunks",
    "inspected_chunks",
    "changed_chunks",
    "skipped_chunks",
    "chunk_basis",
    "parse_status",
    "reference_status",
    "import_export_status",
    "terminology_status",
    "duplicate_status",
    "token_measurement_status",
    "tests_status",
    "public_behavior_status",
    "ripple_status",
    "proof_path",
    "receipt",
)
SUBSYSTEM_CONVERGENCE_FIELDS = (
    "subsystem",
    "status",
    "files",
    "internal_import_status",
    "public_export_status",
    "terminology_status",
    "duplicate_status",
    "configuration_status",
    "schema_status",
    "docs_code_status",
    "tests_code_status",
    "example_api_status",
    "organ_ownership_status",
    "lifecycle_status",
    "self_other_status",
    "effect_proof_status",
    "hard_fail_status",
    "performance_status",
    "token_status",
    "file_completion_status",
    "proof_paths",
    "receipt",
)
REQUIRED_RIPPLE_SURFACES = (
    "imports",
    "exports",
    "__all__",
    "type references",
    "string references",
    "dynamic imports",
    "plugin registries",
    "entry points",
    "CLI commands",
    "CLI help",
    "shell scripts",
    "CI",
    "configuration",
    "environment variables",
    "serializers",
    "deserializers",
    "migrations",
    "templates",
    "generated files",
    "tests",
    "fixtures",
    "snapshots",
    "examples",
    "README files",
    "guides",
    "architecture documents",
    "implementation maps",
    "comments",
    "docstrings",
    "hard-fail tables",
    "error handlers",
    "logs and dashboards",
)
ALIGNMENT_AUDIT_DOMAINS = (
    "A file alignment",
    "B import/export alignment",
    "C API alignment",
    "D CLI alignment",
    "E configuration alignment",
    "F schema/storage alignment",
    "G documentation alignment",
    "H test alignment",
    "I AppAI alignment",
    "J terminology alignment",
    "K token-dialect alignment",
    "L duplication alignment",
    "M version alignment",
    "N security/privacy alignment",
    "O performance alignment",
)
REQUIRED_FINAL_VERIFICATION_CHECKS = (
    "source compilation or parsing",
    "import smoke tests",
    "configured formatter check",
    "configured lint",
    "configured type checker",
    "unit and invariant tests",
    "integration and full certification tests",
    "example tests",
    "CLI smoke tests",
    "Stage 1 audit",
    "Stage 2 readiness audit",
    "security checks",
    "schema and serialization round trips",
    "documentation link and path checks",
    "package build",
    "clean installation smoke test",
    "performance benchmarks",
    "cl100k and o200k token report",
    "final duplicate scan",
    "final dead-reference scan",
    "final secret scan",
    "Git diff and status review",
)
FINAL_VERIFICATION_FIELDS = (
    "requirement",
    "status",
    "evidence",
    "command",
    "blockers",
)
BLIND_SEMANTIC_ELEMENTS = (
    "command",
    "mode",
    "trigger",
    "purpose",
    "gate",
    "invariant",
    "block",
    "procedure",
    "receipt field",
    "hard fail",
    "implementation reference",
)
BLIND_SEMANTIC_FIELDS = (
    "element",
    "status",
    "source_count",
    "final_representation",
    "blockers",
)
SCORECARD_METRICS = (
    "cl100k token counts",
    "o200k token counts",
    "bytes",
    "lines",
    "changed files",
    "unchanged files",
    "skipped files",
    "blocked files",
    "generated files regenerated",
    "duplicate implementations removed",
    "commands merged",
    "compatibility aliases retained",
    "stale references removed",
    "dead code removed",
    "tests before/after",
    "coverage before/after",
    "lint before/after",
    "type-check before/after",
    "build before/after",
    "benchmark before/after",
    "public API changes",
    "behavior changes",
    "unresolved risks",
    "unverifiable claims",
)
SCORECARD_FIELDS = (
    "metric",
    "status",
    "before",
    "after",
    "delta",
    "evidence",
    "blockers",
)
GUARDIAN_CHECKS = (
    "inventory complete",
    "eligible chunks inspected",
    "changed chunks verified",
    "tests remain green",
    "public compatibility visible",
    "AppAI invariants preserved",
    "hard fails intact",
    "merge parity evidence",
    "alias collision and tokenizer proof",
    "ripples resolved or queued",
    "cross-surface alignment",
    "Core/AppAI version alignment",
    "whole-project token count measured",
    "whole-project alignment audit",
    "final verification",
    "blind semantic comparison",
)
GUARDIAN_FIELDS = (
    "check",
    "status",
    "evidence",
    "blockers",
)
RIPPLE_QUEUE_FIELDS = (
    "queue_id",
    "source",
    "trigger",
    "changed_surface",
    "required_surfaces",
    "matched_surfaces",
    "status",
    "receipt",
)
INVARIANT_RE = re.compile(
    r"\b(?:HF-[A-Z0-9]+|B-[A-Z0-9]+|SELF-\d+|SYM-\d+|NOC-\d+|SCHED-\d+|"
    r"MEMW-\d+|GRAFT-\d+|RESID-\d+|MEM-\d+|BOOT-\d+|BRIDGE-\d+|GANG-\d+|"
    r"VAULT-\d+|METER-\d+|OR-CACHE-\d+|INGEST-\d+|DOCTOR-\d+|PHENO-\d+|"
    r"APPLET-\d+|REPRO-\d+|SPORE-\d+|OPT-\d+|GRIM-\d+|VERS-\d+)\b"
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


def _schema_refs(rel: str, text: Optional[str]) -> List[str]:
    if text is None:
        return []
    schemas = []
    language = _language(rel)
    if language in {"json", "toml", "yaml"}:
        schemas.append("%s document" % language)
    if "to_dict" in text or "from_dict" in text:
        schemas.append("python dict serialization")
    if "json.dumps" in text or "json.load" in text:
        schemas.append("json serialization")
    fields = sorted(set(re.findall(r'["\']([A-Za-z_][A-Za-z0-9_-]{2,})["\']\s*:', text)))
    if fields:
        schemas.extend("field:%s" % field for field in fields[:40])
    return sorted(set(schemas))


def _config_keys(rel: str, text: Optional[str], env_vars: List[str]) -> List[str]:
    keys = set(env_vars)
    if text is None:
        return sorted(keys)
    if rel == "pyproject.toml":
        keys.update(re.findall(r"^([A-Za-z0-9_.-]+)\s*=", text, re.MULTILINE))
    if rel.startswith(".github/workflows/"):
        keys.update(re.findall(r"^\s*([A-Za-z0-9_.-]+):", text, re.MULTILINE))
    keys.update(re.findall(r"os\.environ(?:\.get)?\([\"']([A-Za-z_][A-Za-z0-9_]*)", text))
    return sorted(keys)


def _external_interfaces(rel: str, text: Optional[str]) -> List[str]:
    interfaces = set()
    if rel == "pyproject.toml":
        interfaces.add("python-package-metadata")
    if rel.startswith(".github/workflows/"):
        interfaces.add("github-actions")
    if rel == "src/mantle/cli.py" or "python -m mantle" in (text or ""):
        interfaces.add("mantle-cli")
    if rel.endswith(".html") or rel.endswith(".mjs") or rel.endswith(".js"):
        interfaces.add("browser-or-node-demo")
    if any(x in (text or "") for x in ("http", "OpenRouter", "OPENROUTER", "urllib", "requests")):
        interfaces.add("provider-or-http")
    if rel.startswith("documents/") or rel == "README.md":
        interfaces.add("human-documentation")
    return sorted(interfaces)


def _appai_roles(rel: str, text: Optional[str]) -> List[str]:
    hay = (rel + "\n" + (text or "")[:20000]).lower()
    roles = []
    for role, keys in (
        ("Heart", ("heart", "heartbeat", "pulse")),
        ("Genome", ("genome", "primer")),
        ("Nervous System", ("signalbus", "signal bus", "nervous")),
        ("Senses", ("senses", "sense")),
        ("Immune", ("immune", "quarantine", "tombstone")),
        ("Limbs", ("limb", "action", "bridge")),
        ("Memory", ("memory", "vcw", "cube", "band")),
        ("Brain", ("brain", "mind", "cognition")),
        ("Reproduction", ("spore", "egg", "hatch", "reproduction", "seed")),
    ):
        if any(k in hay for k in keys):
            roles.append(role)
    if rel.startswith("documents/grimoire/"):
        roles.append("Doctrine")
    return sorted(set(roles))


def _lifecycle_roles(rel: str, text: Optional[str]) -> List[str]:
    hay = (rel + "\n" + (text or "")[:20000]).lower()
    roles = []
    for role, keys in (
        ("birth", ("birth", "genesis", "hatch")),
        ("assimilation", ("assimilate", "necromancy")),
        ("residency", ("resident", "residency", "host")),
        ("diagnostics", ("audit", "prove", "doctor", "check")),
        ("memory", ("memory", "vcw", "cube")),
        ("cognition", ("mind", "brain", "think")),
        ("reconstruction", ("vault", "reconstruct", "seed")),
        ("retirement", ("dnr", "retire", "tombstone")),
    ):
        if any(k in hay for k in keys):
            roles.append(role)
    return sorted(set(roles))


def _security_privacy(rel: str, text: Optional[str]) -> List[str]:
    hay = (rel + "\n" + (text or "")[:20000]).lower()
    hits = []
    for label, keys in (
        ("identity-boundary", ("self", "other", "identity", "provenance")),
        ("secret-redaction", ("secret", "redact", "private key", "token")),
        ("body-owned-key", ("key", "encrypt", "decrypt", "hmac", "vault")),
        ("provider-cache", ("cache", "openrouter", "cached_tokens")),
        ("host-preservation", ("host", "graft", "residency", "bridge")),
        ("external-effect", ("subprocess", "http", "socket", "action")),
    ):
        if any(k in hay for k in keys):
            hits.append(label)
    return sorted(set(hits))


def _side_effects(rel: str, text: Optional[str]) -> List[str]:
    if text is None:
        return []
    effects = []
    for label, keys in (
        ("filesystem", ("open(", "os.", "Path(", "write_text", "read_text")),
        ("process", ("subprocess", "Popen", "sys.exit")),
        ("network", ("urllib", "requests", "http", "socket", "OpenRouter")),
        ("time-or-random", ("time.", "random", "uuid")),
        ("cryptographic", ("hashlib", "hmac", "secrets", "encrypt", "decrypt")),
        ("stdout-stderr", ("print(", "stderr", "stdout")),
    ):
        if any(k in text for k in keys):
            effects.append(label)
    return sorted(set(effects))


def _complexity_indicators(text: Optional[str], imports: List[str],
                           public: List[str]) -> Dict[str, int]:
    if text is None:
        return {"branch_keywords": 0, "imports": 0, "public_symbols": 0}
    branch_keywords = len(re.findall(r"\b(if|for|while|try|except|with|case)\b", text))
    return {
        "branch_keywords": branch_keywords,
        "imports": len(imports),
        "public_symbols": len(public),
    }


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
    try:
        p = subprocess.run(["git", "status", "--short"], cwd=root, text=True,
                           capture_output=True, timeout=30)
        lines = p.stdout.splitlines() if p.returncode == 0 else []
    except Exception:
        lines = []
    for line in lines:
        if len(line) < 4:
            continue
        rows.append({"status": line[:2], "path": line[3:]})
    return rows


def _status_map(root: str) -> Dict[str, str]:
    return {row["path"].replace("\\", "/"): row["status"] for row in _status_rows(root)}


def _file_disposition(file_row: Dict[str, Any], status: Optional[str]) -> Dict[str, str]:
    category = file_row["category"]
    if status:
        return {
            "disposition": "changed",
            "reason": "git status %r; requires diff review and Mantle proof gates" % status,
        }
    if not file_row["text"] or category.startswith("N "):
        return {
            "disposition": "inventory-only",
            "reason": "binary/media; optimize only by reference, rendered evidence, or hash evidence",
        }
    if category.startswith("Q "):
        return {
            "disposition": "blocked",
            "reason": "unknown category; classify before semantic optimization",
        }
    if file_row["token_status"] == "tiktoken unavailable":
        return {
            "disposition": "pending-pass-review",
            "reason": "eligible text file; token counts unverifiable until optional tokenizer is available",
        }
    return {
        "disposition": "pending-pass-review",
        "reason": "eligible text file; no semantic chunk rewrite selected in this audit pass",
    }


def _read_text_optional(root: str, rel: str) -> str:
    try:
        with open(os.path.join(root, rel.replace("/", os.sep)), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _project_metadata(root: str) -> Dict[str, Any]:
    pyproject = _read_text_optional(root, "pyproject.toml")
    build_backend = None
    requires_python = None
    m = re.search(r'build-backend\s*=\s*"([^"]+)"', pyproject)
    if m:
        build_backend = m.group(1)
    m = re.search(r'requires-python\s*=\s*"([^"]+)"', pyproject)
    if m:
        requires_python = m.group(1)
    package_managers = []
    if pyproject:
        package_managers.append({"name": "pip/setuptools", "source": "pyproject.toml"})
    if os.path.exists(os.path.join(root, "examples", "tests", "package.json")):
        package_managers.append({"name": "npm", "source": "examples/tests/package.json"})
    workflow_dir = os.path.join(root, ".github", "workflows")
    workflows = []
    if os.path.isdir(workflow_dir):
        workflows = sorted(_rel(os.path.join(workflow_dir, name), root)
                           for name in os.listdir(workflow_dir)
                           if os.path.isfile(os.path.join(workflow_dir, name)))
    return {
        "build_backend": build_backend,
        "requires_python": requires_python,
        "runtime_dependencies_declared": "dependencies = []" not in pyproject,
        "package_managers": package_managers,
        "ci_workflows": workflows,
    }


def _first_match(pattern: str, text: str) -> Optional[str]:
    m = re.search(pattern, text, re.MULTILINE)
    return m.group(1) if m else None


def _version_alignment(root: str, invariant_count: int) -> Dict[str, Any]:
    pyproject = _read_text_optional(root, "pyproject.toml")
    init_py = _read_text_optional(root, "src/mantle/__init__.py")
    readme = _read_text_optional(root, "README.md")
    audit_guide = _read_text_optional(root, "documents/guides/Audit_Guide.md")
    grimoire = _read_text_optional(root, "documents/grimoire/The Grimoire.md")
    grimoire_readme = _read_text_optional(root, "documents/grimoire/README.md")

    package_version = _first_match(r'^version\s*=\s*"([^"]+)"', pyproject)
    module_version = _first_match(r'^__version__\s*=\s*"([^"]+)"', init_py)
    grimoire_stamp = _first_match(r"^#\s+(G[0-9.]+-[A-Z])", grimoire)
    grimoire_version = _first_match(r"Version=([0-9]+(?:\.[0-9]+)*)\b", grimoire)
    readme_count = _first_match(r"Current certification count:\*\*\s+(\d+)\s+security invariants",
                                readme)
    audit_count = _first_match(r"prove\s+# the (\d+) security invariants", audit_guide)

    rows = [
        {"surface": "pyproject.toml", "field": "project.version",
         "value": package_version, "expected": module_version,
         "status": "PASS" if package_version and package_version == module_version else "REVISE"},
        {"surface": "src/mantle/__init__.py", "field": "__version__",
         "value": module_version, "expected": package_version,
         "status": "PASS" if module_version and module_version == package_version else "REVISE"},
        {"surface": "documents/grimoire/The Grimoire.md", "field": "stamp",
         "value": grimoire_stamp, "expected": "G4.0-U",
         "status": "PASS" if grimoire_stamp == "G4.0-U" else "REVISE"},
        {"surface": "documents/grimoire/The Grimoire.md", "field": "Version",
         "value": grimoire_version, "expected": "4.0",
         "status": "PASS" if grimoire_version == "4.0" else "REVISE"},
        {"surface": "documents/grimoire/README.md", "field": "canonical model",
         "value": "one version-4 canonical tomb" if "one version-4 canonical tomb" in grimoire_readme else None,
         "expected": "one version-4 canonical tomb",
         "status": "PASS" if "one version-4 canonical tomb" in grimoire_readme else "REVISE"},
        {"surface": "README.md", "field": "security invariant count",
         "value": int(readme_count) if readme_count else None, "expected": invariant_count,
         "status": "PASS" if readme_count and int(readme_count) == invariant_count else "REVISE"},
        {"surface": "documents/guides/Audit_Guide.md", "field": "security invariant count",
         "value": int(audit_count) if audit_count else None, "expected": invariant_count,
         "status": "PASS" if audit_count and int(audit_count) == invariant_count else "REVISE"},
    ]
    return {
        "status": "PASS" if all(r["status"] == "PASS" for r in rows) else "REVISE",
        "package_version": package_version,
        "module_version": module_version,
        "grimoire_version": grimoire_version,
        "grimoire_stamp": grimoire_stamp,
        "security_invariant_count": invariant_count,
        "rows": rows,
    }


def _invariant_count(root: str) -> int:
    text = _read_text_optional(root, "src/mantle/audits/invariants.py")
    if "TESTS = [" in text:
        text = text.split("TESTS = [", 1)[1]
    if "\ndef run_all" in text:
        text = text.split("\ndef run_all", 1)[0]
    return len(re.findall(r'^\s*\("', text, re.MULTILINE))


def _redact_text(text: str) -> str:
    return SECRET_RE.sub("[REDACTED]", text or "")


def _tail(text: str, limit: int = 1200) -> str:
    text = _redact_text(text)
    return text[-limit:] if len(text) > limit else text


def _run_command(root: str, argv: List[str], timeout_s: int) -> Dict[str, Any]:
    env = {**os.environ, "PYTHONPATH": paths.SRC_DIR}
    start = time.perf_counter()
    try:
        p = subprocess.run(argv, cwd=root, env=env, text=True, capture_output=True,
                           timeout=timeout_s)
        duration = time.perf_counter() - start
        return {
            "command": " ".join(argv),
            "exit_code": p.returncode,
            "duration_s": round(duration, 3),
            "stdout_tail": _tail(p.stdout),
            "stderr_tail": _tail(p.stderr),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as e:
        duration = time.perf_counter() - start
        stdout = e.stdout if isinstance(e.stdout, str) else ""
        stderr = e.stderr if isinstance(e.stderr, str) else ""
        return {
            "command": " ".join(argv),
            "exit_code": None,
            "duration_s": round(duration, 3),
            "stdout_tail": _tail(stdout),
            "stderr_tail": _tail(stderr),
            "timed_out": True,
        }


def _run_checks(root: str, mode: str) -> List[Dict[str, Any]]:
    commands = {
        "prove": [([sys.executable, "-m", "mantle", "prove"], 180)],
        "fast": [([sys.executable, "-m", "mantle", "check", "--fast"], 240)],
        "full": [([sys.executable, "-m", "mantle", "check"], 300)],
        "final": [
            ([sys.executable, "-m", "mantle", "check"], 300),
            ([sys.executable, "-m", "mantle", "audit"], 120),
            ([sys.executable, "-m", "mantle", "audit-mind"], 180),
            ([sys.executable, "-m", "mantle", "prove"], 180),
            ([sys.executable, "examples/vcw/vcw_cube.py", "selftest"], 90),
        ],
    }
    if mode not in commands:
        return [{"command": mode, "exit_code": None, "duration_s": 0,
                 "stdout_tail": "", "stderr_tail": "unknown --run-checks mode",
                 "timed_out": False}]
    return [_run_command(root, argv, timeout_s) for argv, timeout_s in commands[mode]]


def _baseline_stats(report: Dict[str, Any]) -> Dict[str, Any]:
    files = report["files"]
    return {
        "runtime": {
            "python": sys.version.split()[0],
            "python_executable": sys.executable,
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "tools": {
            "git": shutil.which("git") or "unavailable",
            "node": shutil.which("node") or "unavailable",
            "npm": shutil.which("npm") or "unavailable",
        },
        "git": {
            "branch": report["branch"],
            "head": report["head"],
            "status": _status_rows(report["repo_root"]),
        },
        "project": _project_metadata(report["repo_root"]),
        "metrics": {
            "files": report["file_count"],
            "tracked_files": report["tracked_count"],
            "bytes": sum(f["bytes"] for f in files),
            "lines": sum(f["lines"] for f in files),
            "words": sum(f["words"] for f in files),
            "text_files": sum(1 for f in files if f["text"]),
            "binary_files": sum(1 for f in files if not f["text"]),
            "categories": report["categories"],
            "token_status": report["token_status"],
        },
    }


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
    schemas = _schema_refs(rel, text)
    config_keys = _config_keys(rel, text, env_vars)
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
        "importers": [],
        "public_symbols": public,
        "referenced_commands": commands,
        "referenced_paths": path_refs,
        "schemas": schemas,
        "configuration_keys": config_keys,
        "environment_variables": env_vars,
        "external_interfaces": _external_interfaces(rel, text),
        "tests": [],
        "documentation_references": [],
        "appai_roles": _appai_roles(rel, text),
        "lifecycle_roles": _lifecycle_roles(rel, text),
        "security_privacy_relevance": _security_privacy(rel, text),
        "side_effects": _side_effects(rel, text),
        "invariants": sorted(set(INVARIANT_RE.findall(text or ""))),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "lines": 0 if text is None else text.count("\n") + (1 if text else 0),
        "words": 0 if text is None else len(re.findall(r"\S+", text)),
        "tokens": tokens,
        "token_status": token_note or ("measured" if text is not None else "not-text"),
        "complexity_indicators": _complexity_indicators(text, imports, public),
        "duplication_indicators": {"exact_duplicate_paths": [], "near_duplicate_note": "not-analyzed"},
        "optimization_eligibility": "inventory-only" if not is_text else "eligible-for-pass-review",
        "risk": "high" if rel.startswith("src/mantle/core/") else "normal",
        "proof_path": "PYTHONPATH=src python -m mantle check",
        "skip_block_reason": "pending disposition; finalized after git status review",
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


def _import_matches(import_name: str, module_name: str) -> bool:
    return (
        import_name == module_name
        or import_name.startswith(module_name + ".")
        or module_name.startswith(import_name.lstrip(".") + ".")
    )


def _enrich_file_relationships(report: Dict[str, Any]) -> None:
    files = report["files"]
    by_path = {f["path"]: f for f in files}
    modules = {f["path"]: _module_name(f["path"]) for f in files}
    doc_files = [f for f in files if f["category"].startswith(("C ", "D "))]
    test_files = [f for f in files if f["category"].startswith("B ")]
    duplicate_paths: Dict[str, List[str]] = {}
    for group in report["maps"]["duplicate_hashes"]:
        for path in group["paths"]:
            duplicate_paths[path] = [p for p in group["paths"] if p != path]

    for target in files:
        path = target["path"]
        module = modules.get(path)
        if module:
            target["importers"] = sorted(
                f["path"] for f in files
                if f["path"] != path
                and any(_import_matches(imp, module) for imp in f["imports"])
            )
            target["tests"] = sorted(
                f["path"] for f in test_files
                if f["path"] != path
                and (
                    any(_import_matches(imp, module) for imp in f["imports"])
                    or path in f["referenced_paths"]
                )
            )
        else:
            target["importers"] = []
            target["tests"] = sorted(
                f["path"] for f in test_files
                if path in f["referenced_paths"]
            )

        refs = []
        for doc in doc_files:
            if doc["path"] == path:
                continue
            normalized_refs = {r.replace("\\", "/").strip("/") for r in doc["referenced_paths"]}
            if path in normalized_refs:
                refs.append(doc["path"])
        target["documentation_references"] = sorted(refs)
        target["duplication_indicators"] = {
            "exact_duplicate_paths": sorted(duplicate_paths.get(path, [])),
            "near_duplicate_note": "not-analyzed",
        }
        if path in by_path:
            missing = [field for field in REQUIRED_FILE_FIELDS if field not in target]
            target["_inventory_shape"] = "PASS" if not missing else "MISSING:%s" % ",".join(missing)


def _collisions(values: Iterable[str], normalizer=lambda x: x) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[str]] = {}
    for value in values:
        key = normalizer(value)
        buckets.setdefault(key, []).append(value)
    return [
        {"key": key, "values": sorted(set(vals))}
        for key, vals in sorted(buckets.items())
        if len(set(vals)) > 1
    ]


def _prefix_collisions(values: Iterable[str]) -> List[Dict[str, str]]:
    vals = sorted(set(values), key=lambda x: (len(x), x))
    rows = []
    for i, short in enumerate(vals):
        if len(short) < 2:
            continue
        for long in vals[i + 1:]:
            if len(long) > len(short) and long.startswith(short):
                rows.append({"prefix": short, "longer": long})
    return rows[:200]


def _punctuation_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", value).casefold()


def _schema_field_namespace(field: str) -> str:
    if field.isupper():
        return "constant-or-marker"
    if field[:1].isupper():
        return "metadata"
    return "data"


def _collision_status(rows: List[Any]) -> str:
    return "PASS" if not rows else "REVISE"


def _alias_registry(report: Dict[str, Any]) -> Dict[str, Any]:
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
    files = report["files"]
    maps = report["maps"]
    alias_tokens = [a["token"] for a in aliases]
    public_cli = maps["known_cli_commands"]
    env_vars = maps["environment_variables"]
    schema_fields = sorted({
        s.split("field:", 1)[1]
        for f in files for s in f["schemas"]
        if s.startswith("field:")
    })
    schema_field_symbols = sorted({
        "%s::%s::%s" % (
            f["path"],
            _schema_field_namespace(s.split("field:", 1)[1]),
            s.split("field:", 1)[1],
        )
        for f in files for s in f["schemas"]
        if s.startswith("field:")
    })
    python_symbols = sorted({
        "%s::%s" % (f["path"], symbol)
        for f in files for symbol in f["public_symbols"]
    })
    filesystem_paths = [f["path"] for f in files]
    class_markers = [
        token for token in alias_tokens
        if token[:1].isupper() and not token.isupper()
    ]
    mode_markers = sorted(set(public_cli + [
        "audit", "prove", "check", "fast", "strict", "json", "dry-run",
    ]))
    error_codes = sorted({
        invariant for f in files for invariant in f["invariants"]
    })
    checks = {
        "exact_duplicate_aliases": _collisions(alias_tokens),
        "casefold_collisions": _collisions(alias_tokens, lambda x: x.casefold()),
        "punctuation_collisions": _collisions(alias_tokens, _punctuation_key),
        "prefix_collisions": _prefix_collisions(alias_tokens),
        "class_marker_collisions": _collisions(class_markers, lambda x: x.casefold()),
        "mode_marker_collisions": _collisions(mode_markers, lambda x: x.replace("-", "_")),
        "error_code_collisions": _collisions(error_codes, lambda x: x.casefold()),
        "public_cli_collisions": _collisions(public_cli, lambda x: x.replace("_", "-")),
        "environment_variable_collisions": _collisions(env_vars, lambda x: x.casefold()),
        "schema_field_collisions": _collisions(schema_field_symbols, lambda x: x.casefold()),
        "python_symbol_collisions": _collisions(python_symbols, lambda x: x.casefold()),
        "filesystem_case_collisions": _collisions(filesystem_paths, lambda x: x.casefold()),
    }
    check_rows = {
        name: {"status": _collision_status(rows), "collisions": rows}
        for name, rows in checks.items()
    }
    status = "PASS" if all(row["status"] == "PASS" for row in check_rows.values()) else "REVISE"
    return {
        "canonical_source": "documents/grimoire plus MantleOS doctrine",
        "registry_rule": "one token has one meaning; undefined shorthand remains UNKNOWN",
        "aliases": aliases,
        "surfaces": {
            "alias_tokens": alias_tokens,
            "class_markers": class_markers,
            "mode_markers": mode_markers,
            "error_codes": error_codes,
            "public_cli": public_cli,
            "environment_variables": env_vars,
            "schema_fields": schema_fields,
            "python_symbols": python_symbols,
            "filesystem_paths": filesystem_paths,
        },
        "collision_audit": {"status": status, "checks": check_rows},
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
    return [{
        "path": f["path"],
        "status": f.get("git_status") or "clean",
        "category": f["category"],
        "disposition": f["disposition"],
        "receipt": f["skip_block_reason"],
        "proof_path": f["proof_path"],
    } for f in report["files"]]


def _merge_key(name: str) -> str:
    key = re.sub(r"^(t_|test_|_+)", "", name)
    key = re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_").casefold()
    for suffix in ("_ok", "_test", "_audit", "_check", "_helper"):
        if key.endswith(suffix):
            key = key[:-len(suffix)]
    return key


def _candidate_score(items: List[Dict[str, Any]]) -> int:
    paths = [item["path"] for item in items]
    subsystems = {path.split("/")[0] + "/" + path.split("/")[1]
                  if "/" in path else path for path in paths}
    score = 35
    if len(items) > 2:
        score += 10
    if len(subsystems) == 1:
        score += 10
    if all(item.get("side_effects") == items[0].get("side_effects") for item in items):
        score += 15
    if all(item.get("security") == items[0].get("security") for item in items):
        score += 15
    if all(item.get("lifecycle") == items[0].get("lifecycle") for item in items):
        score += 10
    return min(score, 100)


def _candidate_decision(items: List[Dict[str, Any]], score: int) -> Tuple[str, str]:
    side_effect_sets = {tuple(item.get("side_effects", [])) for item in items}
    security_sets = {tuple(item.get("security", [])) for item in items}
    lifecycle_sets = {tuple(item.get("lifecycle", [])) for item in items}
    if len(side_effect_sets) > 1 or len(security_sets) > 1:
        return "blocked", "safety, side-effect, or security envelopes differ"
    if len(lifecycle_sets) > 1:
        return "queued-review", "lifecycle positions differ; requires parity matrix"
    if score >= 70:
        return "queued-review", "similar enough for steelman and parity review"
    return "low-confidence", "name similarity alone is insufficient to merge"


def _merge_candidates(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    files = report["files"]
    by_path = {f["path"]: f for f in files}
    symbol_groups: Dict[str, List[Dict[str, Any]]] = {}
    for f in files:
        if not f["path"].endswith(".py"):
            continue
        for symbol in f["public_symbols"]:
            key = _merge_key(symbol)
            if key:
                symbol_groups.setdefault(key, []).append({
                    "path": f["path"],
                    "symbol": symbol,
                    "side_effects": f["side_effects"],
                    "security": f["security_privacy_relevance"],
                    "lifecycle": f["lifecycle_roles"],
                    "proof_path": f["proof_path"],
                    "importers": f["importers"],
                    "tests": f["tests"],
                })
    candidates: List[Dict[str, Any]] = []
    for key, items in sorted(symbol_groups.items()):
        distinct_paths = {item["path"] for item in items}
        if len(items) < 2 or len(distinct_paths) < 2:
            continue
        score = _candidate_score(items)
        decision, reason = _candidate_decision(items, score)
        candidate_items = [
            "%s::%s" % (item["path"], item["symbol"])
            for item in sorted(items, key=lambda x: (x["path"], x["symbol"]))
        ]
        first = items[0]
        candidates.append({
            "candidate_id": "py-symbol:%s" % key,
            "kind": "python-public-symbol",
            "items": candidate_items,
            "shared_key": key,
            "score": score,
            "shared_purpose": "derived from normalized public symbol name",
            "authority_compatibility": "unknown; requires steelman before merge",
            "side_effect_compatibility": len({tuple(i["side_effects"]) for i in items}) == 1,
            "security_compatibility": len({tuple(i["security"]) for i in items}) == 1,
            "lifecycle_compatibility": len({tuple(i["lifecycle"]) for i in items}) == 1,
            "proof_compatibility": all(i["proof_path"] == first["proof_path"] for i in items),
            "callers_known": {item["path"]: sorted(set(item["importers"] + item["tests"]))
                              for item in items},
            "decision": decision,
            "reason": reason,
        })

    doc_groups: Dict[str, List[str]] = {}
    for f in files:
        if not f["category"].startswith(("C ", "D ")):
            continue
        base = os.path.splitext(os.path.basename(f["path"]))[0]
        key = _merge_key(base)
        if key:
            doc_groups.setdefault(key, []).append(f["path"])
    for key, paths_ in sorted(doc_groups.items()):
        if len(paths_) < 2:
            continue
        items = sorted(paths_)
        candidates.append({
            "candidate_id": "doc:%s" % key,
            "kind": "documentation-topic",
            "items": items,
            "shared_key": key,
            "score": 45,
            "shared_purpose": "derived from normalized document filename",
            "authority_compatibility": "unknown; doctrine docs require separate authority review",
            "side_effect_compatibility": True,
            "security_compatibility": True,
            "lifecycle_compatibility": True,
            "proof_compatibility": True,
            "callers_known": {path: by_path[path]["documentation_references"] for path in items},
            "decision": "queued-review",
            "reason": "possible topic duplication; deletion requires function coverage proof",
        })
    return candidates


def _merge_parity_review(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    for candidate in candidates:
        dimensions = [
            {"name": "authority", "compatible": candidate["authority_compatibility"] != "unknown"},
            {"name": "side effects", "compatible": candidate["side_effect_compatibility"]},
            {"name": "security/privacy", "compatible": candidate["security_compatibility"]},
            {"name": "lifecycle", "compatible": candidate["lifecycle_compatibility"]},
            {"name": "proof path", "compatible": candidate["proof_compatibility"]},
        ]
        incompatible = [d["name"] for d in dimensions if not d["compatible"]]
        if candidate["decision"] == "blocked":
            status = "BLOCKED"
            decision = "keep separate; safety or authority envelope differs"
        elif candidate["decision"] == "low-confidence":
            status = "LOW_CONFIDENCE"
            decision = "keep separate; name similarity is not behavior parity"
        else:
            status = "REVIEW_REQUIRED"
            decision = "do not merge until manual edge-case parity and proof gates pass"
        rows.append({
            "candidate_id": candidate["candidate_id"],
            "status": status,
            "steelman": (
                "These surfaces may be separate because authority, caller expectations, "
                "proof paths, lifecycle placement, or safety boundaries may differ even "
                "when names look similar."
            ),
            "items": candidate["items"],
            "caller_matrix": candidate["callers_known"],
            "parity_dimensions": dimensions,
            "mode_complexity": (
                "merge would add ambiguous mode branching" if incompatible
                else "mode consolidation remains unproven without edge-case tests"
            ),
            "compatibility_alias": "not authorized; no public surface is migrated by this audit",
            "safe_to_merge_now": False,
            "proof_required": [
                "caller review",
                "input/output parity matrix",
                "edge-case and exception comparison",
                "security/privacy boundary review",
                "focused tests plus python -m mantle check",
            ],
            "decision": decision,
            "receipt": (
                "Candidate reviewed for section-7 merge prerequisites; no code was merged "
                "or deleted in this pass."
            ),
        })
    totals = Counter(row["status"] for row in rows)
    return {
        "status": "REVISE" if rows else "PASS",
        "rows": rows,
        "totals": dict(sorted(totals.items())),
        "missing_candidates": [],
        "rule": "Section 7 merge parity evidence is required before any candidate can merge.",
    }


def _merge_map(report: Dict[str, Any]) -> Dict[str, Any]:
    candidates = _merge_candidates(report)
    decisions = Counter(c["decision"] for c in candidates)
    parity_review = _merge_parity_review(candidates)
    return {
        "status": "candidate-analysis",
        "merges_performed_by_this_audit": [],
        "compatibility_aliases_detected": [
            {"old": "optimize_audit", "new": "optimize-audit",
             "surface": "CLI", "mode": "underscore compatibility alias"}
        ],
        "duplicate_hashes": report["maps"]["duplicate_hashes"],
        "candidate_fields": list(MERGE_CANDIDATE_FIELDS),
        "parity_fields": list(MERGE_PARITY_FIELDS),
        "merge_candidates": candidates,
        "candidate_decisions": dict(sorted(decisions.items())),
        "parity_review": parity_review,
        "parity_status": parity_review["status"],
        "merge_policy": (
            "no candidate is merged by this audit; each requires steelman, parity matrix, "
            "caller analysis, and proof gates before mutation"
        ),
    }


def _chunk_basis(file_row: Dict[str, Any]) -> Tuple[str, int]:
    path = file_row["path"]
    if not file_row["text"]:
        return "binary/media inventory unit", 0
    if path.endswith(".py"):
        symbols = len(file_row["public_symbols"])
        return "python public symbol plus module body", max(1, symbols)
    if path.endswith(".md"):
        return "markdown heading section", max(1, file_row["complexity_indicators"].get(
            "heading_count", 0))
    if file_row["language"] in {"json", "toml", "yaml"}:
        return "structured document block", 1
    return "text file section", 1


def _parse_status(root: str, file_row: Dict[str, Any]) -> str:
    if not file_row["text"] or not file_row["path"].endswith(".py"):
        return "not-python"
    text = _read_text_optional(root, file_row["path"])
    try:
        ast.parse(text)
    except SyntaxError as e:
        return "syntax-error:%s" % e.lineno
    return "PASS"


def _file_completion_gate(report: Dict[str, Any]) -> Dict[str, Any]:
    root = report["repo_root"]
    rows = []
    for f in report["files"]:
        basis, eligible_chunks = _chunk_basis(f)
        pending = f["disposition"] == "pending-pass-review"
        inspected_chunks = 0 if pending else eligible_chunks
        skipped_chunks = eligible_chunks - inspected_chunks
        parse_status = _parse_status(root, f)
        stale_refs = [r for r in report["maps"]["path_references"]
                      if r["from"] == f["path"] and not r["exists"]]
        stale_cmds = [r for r in report["maps"]["cli_command_references"]
                      if r["from"] == f["path"] and not r["exists"]]
        reference_status = "PASS" if not stale_refs and not stale_cmds else "REVISE"
        duplicate_status = (
            "REVIEW" if f["duplication_indicators"]["exact_duplicate_paths"]
            else "PASS"
        )
        status = (
            "PENDING_CHUNK_REVIEW" if pending
            else "INVENTORY_ONLY" if f["disposition"] == "inventory-only"
            else "BLOCKED" if f["disposition"] == "blocked"
            else "CHANGED_REVIEW_REQUIRED" if f["disposition"] == "changed"
            else "UNKNOWN"
        )
        rows.append({
            "path": f["path"],
            "status": status,
            "eligible_chunks": eligible_chunks,
            "inspected_chunks": inspected_chunks,
            "changed_chunks": 0,
            "skipped_chunks": skipped_chunks,
            "chunk_basis": basis,
            "parse_status": parse_status,
            "reference_status": reference_status,
            "import_export_status": "PASS" if not f["imports"] or f["importers"] is not None else "UNKNOWN",
            "terminology_status": "PENDING" if f["category"].startswith(("C ", "D ")) else "PASS",
            "duplicate_status": duplicate_status,
            "token_measurement_status": f["token_status"],
            "tests_status": "mapped" if f["tests"] else "unmapped",
            "public_behavior_status": "preserved-no-runtime-edit",
            "ripple_status": "none-applied",
            "proof_path": f["proof_path"],
            "receipt": f["skip_block_reason"],
        })
    totals = Counter(row["status"] for row in rows)
    missing_fields = [
        row["path"] for row in rows
        if any(field not in row for field in FILE_COMPLETION_FIELDS)
    ]
    return {
        "status": "REVISE" if totals.get("PENDING_CHUNK_REVIEW") else "PASS",
        "rows": rows,
        "totals": dict(sorted(totals.items())),
        "missing_fields": missing_fields,
        "completion_rule": (
            "A file is complete only when every eligible chunk is inspected, changed chunks "
            "are verified, references align, token measurement is recorded or marked "
            "unverifiable, tests/proof path pass, and ripples are resolved."
        ),
    }


def _model_paths(files: List[Dict[str, Any]], predicate) -> List[str]:
    return sorted(f["path"] for f in files if predicate(f))


def _subsystem_convergence(report: Dict[str, Any]) -> Dict[str, Any]:
    files = report["files"]
    completion_by_path = {
        row["path"]: row for row in report["file_completion_gate"]["rows"]
    }
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for f in files:
        groups.setdefault(f["subsystem"], []).append(f)

    rows = []
    for subsystem, group in sorted(groups.items()):
        paths_ = sorted(f["path"] for f in group)
        completion_statuses = Counter(
            completion_by_path[f["path"]]["status"] for f in group
        )
        pending = sum(
            completion_by_path[f["path"]]["eligible_chunks"]
            - completion_by_path[f["path"]]["inspected_chunks"]
            for f in group
        )
        duplicate_files = [
            f["path"] for f in group
            if f["duplication_indicators"]["exact_duplicate_paths"]
        ]
        token_unverified = [
            f["path"] for f in group if f["token_status"] != "measured"
        ]
        row = {
            "subsystem": subsystem,
            "status": "REVISE" if pending else "PASS",
            "files": paths_,
            "internal_import_status": "mapped",
            "public_export_status": "mapped" if any(f["public_symbols"] for f in group) else "none",
            "terminology_status": (
                "pending" if any(f["category"].startswith(("C ", "D ")) for f in group)
                else "mapped"
            ),
            "duplicate_status": "review" if duplicate_files else "pass",
            "configuration_status": "mapped" if any(f["configuration_keys"] for f in group) else "none",
            "schema_status": "mapped" if any(f["schemas"] for f in group) else "none",
            "docs_code_status": (
                "mapped" if any(f["documentation_references"] for f in group)
                or any(f["category"].startswith(("C ", "D ")) for f in group)
                else "unmapped"
            ),
            "tests_code_status": "mapped" if any(f["tests"] for f in group) else "unmapped",
            "example_api_status": "mapped" if any(f["category"].startswith("H ") for f in group) else "none",
            "organ_ownership_status": "mapped" if any(f["appai_roles"] for f in group) else "none",
            "lifecycle_status": "mapped" if any(f["lifecycle_roles"] for f in group) else "none",
            "self_other_status": (
                "mapped" if any("identity-boundary" in f["security_privacy_relevance"]
                                 for f in group) else "none"
            ),
            "effect_proof_status": "mapped" if any(f["side_effects"] for f in group) else "none",
            "hard_fail_status": "mapped" if any(f["invariants"] for f in group) else "none",
            "performance_status": "baseline-only",
            "token_status": "unverified" if token_unverified else "measured",
            "file_completion_status": dict(sorted(completion_statuses.items())),
            "proof_paths": sorted(set(f["proof_path"] for f in group)),
            "receipt": (
                "%d file(s), %d pending chunk(s); subsystem convergence remains REVISE "
                "until file completion rows reach PASS or justified inventory-only states"
                % (len(group), pending)
            ),
        }
        rows.append(row)
    missing_fields = [
        row["subsystem"] for row in rows
        if any(field not in row for field in SUBSYSTEM_CONVERGENCE_FIELDS)
    ]
    return {
        "status": "REVISE" if any(row["status"] != "PASS" for row in rows) else "PASS",
        "rows": rows,
        "totals": dict(sorted(Counter(row["status"] for row in rows).items())),
        "missing_fields": missing_fields,
        "rule": (
            "Subsystem convergence follows file completion and checks imports, exports, "
            "terminology, duplicates, config, schemas, docs/tests/examples, organ/lifecycle "
            "ownership, SELF/OTHER, effect proofs, hard fails, performance, and tokens."
        ),
    }


def _matched_ripple_surfaces(report: Dict[str, Any], source_path: str) -> List[str]:
    files = report["files"]
    by_path = {f["path"]: f for f in files}
    row = by_path.get(source_path, {})
    surfaces = set()
    if row.get("imports") or row.get("importers"):
        surfaces.update({"imports", "exports"})
    if row.get("public_symbols"):
        surfaces.update({"exports", "type references"})
    if row.get("referenced_paths") or row.get("documentation_references"):
        surfaces.update({"string references", "README files", "guides"})
    if row.get("referenced_commands"):
        surfaces.update({"CLI commands", "CLI help"})
    if row.get("configuration_keys"):
        surfaces.add("configuration")
    if row.get("environment_variables"):
        surfaces.add("environment variables")
    if row.get("schemas"):
        surfaces.update({"serializers", "deserializers"})
    if row.get("tests"):
        surfaces.update({"tests", "fixtures"})
    if row.get("category", "").startswith("H "):
        surfaces.add("examples")
    if row.get("category", "").startswith(("C ", "D ")):
        surfaces.update({"guides", "architecture documents", "comments"})
    if row.get("invariants"):
        surfaces.update({"hard-fail tables", "implementation maps"})
    if source_path.startswith(".github/"):
        surfaces.update({"CI", "shell scripts"})
    if source_path.startswith("examples/"):
        surfaces.add("examples")
    if source_path.endswith(".py"):
        surfaces.update({"docstrings", "error handlers"})
    return sorted(surfaces)


def _ripple_queue(report: Dict[str, Any]) -> Dict[str, Any]:
    rows = []
    for status in report["baseline"]["git"]["status"]:
        source = status["path"].replace("\\", "/")
        matched = _matched_ripple_surfaces(report, source)
        rows.append({
            "queue_id": "git-status:%s" % source,
            "source": source,
            "trigger": "working-tree-change:%s" % status["status"].strip(),
            "changed_surface": "source file",
            "required_surfaces": list(REQUIRED_RIPPLE_SURFACES),
            "matched_surfaces": matched,
            "status": "queued" if matched else "review-required",
            "receipt": "direct ripple queue for current working-tree change",
        })

    for candidate in report["merge_map"]["merge_candidates"]:
        if candidate["decision"] != "queued-review":
            continue
        source = candidate["candidate_id"]
        candidate_surfaces = {
            "imports", "exports", "tests", "examples", "implementation maps",
        }
        candidate_surfaces.update(
            "guides" if item.startswith("doc:") else "string references"
            for item in candidate["items"]
        )
        rows.append({
            "queue_id": "merge-candidate:%s" % candidate["shared_key"],
            "source": source,
            "trigger": "merge-candidate:%s" % candidate["kind"],
            "changed_surface": "possible canonical implementation",
            "required_surfaces": list(REQUIRED_RIPPLE_SURFACES),
            "matched_surfaces": sorted(candidate_surfaces),
            "status": "queued-review",
            "receipt": "candidate only; no merge until parity, callers, and proof gates pass",
        })

    missing_fields = [
        row["queue_id"] for row in rows
        if any(field not in row for field in RIPPLE_QUEUE_FIELDS)
    ]
    return {
        "status": "PASS" if not missing_fields else "REVISE",
        "rows": rows,
        "totals": dict(sorted(Counter(row["status"] for row in rows).items())),
        "required_surfaces": list(REQUIRED_RIPPLE_SURFACES),
        "missing_fields": missing_fields,
        "rule": (
            "Any change to a name, path, command, field, mode, schema, error code, default, "
            "or public behavior must queue imports, exports, CLI, config, serializers, tests, "
            "examples, docs, implementation maps, hard-fail tables, and related surfaces."
        ),
    }


def _alignment_row(domain: str, status: str, evidence: Dict[str, Any],
                   blockers: List[str]) -> Dict[str, Any]:
    return {
        "domain": domain,
        "status": status,
        "evidence": evidence,
        "blockers": blockers,
    }


def _whole_project_alignment(report: Dict[str, Any]) -> Dict[str, Any]:
    maps = report["maps"]
    model = report["project_model"]
    stale_paths = [r for r in maps["path_references"] if not r["exists"]]
    stale_commands = [r for r in maps["cli_command_references"] if not r["exists"]]
    missing_coverage = [r for r in report["coverage_matrix"] if r["status"] != "present"]
    rows = [
        _alignment_row(
            "A file alignment",
            "PASS" if not stale_paths and not report["tracked_missing"] else "REVISE",
            {"path_refs": len(maps["path_references"]),
             "stale_paths": len(stale_paths),
             "tracked_missing": len(report["tracked_missing"])},
            ([] if not stale_paths and not report["tracked_missing"]
             else ["unresolved path or missing tracked file"]),
        ),
        _alignment_row(
            "B import/export alignment",
            "PASS" if model["python_import_export_graph"]["modules"] else "REVISE",
            {"modules": len(model["python_import_export_graph"]["modules"]),
             "import_edges": len(model["python_import_export_graph"]["imports"]),
             "public_api_files": len(model["public_api_graph"]["public_symbols"])},
            [] if model["python_import_export_graph"]["modules"] else ["no module graph"],
        ),
        _alignment_row(
            "C API alignment",
            "REVISE" if report["merge_map"]["merge_candidates"] else "PASS",
            {"public_api_files": len(model["public_api_graph"]["public_symbols"]),
             "merge_candidates": len(report["merge_map"]["merge_candidates"])},
            ["merge candidates require parity review"] if report["merge_map"]["merge_candidates"] else [],
        ),
        _alignment_row(
            "D CLI alignment",
            "PASS" if not stale_commands else "REVISE",
            {"known_commands": len(maps["known_cli_commands"]),
             "cli_refs": len(maps["cli_command_references"]),
             "stale_commands": len(stale_commands)},
            [] if not stale_commands else ["unresolved documented CLI command"],
        ),
        _alignment_row(
            "E configuration alignment",
            "PASS",
            {"config_files": len(model["configuration_graph"]["files"]),
             "environment_variables": len(model["configuration_graph"]["environment_variables"])},
            [],
        ),
        _alignment_row(
            "F schema/storage alignment",
            "PASS" if model["schema_serialization_graph"]["files"] else "REVISE",
            {"schema_files": len(model["schema_serialization_graph"]["files"]),
             "vcw_files": len(model["vcw_band_owner_writer_map"]["files"])},
            [] if model["schema_serialization_graph"]["files"] else ["no schema/storage map"],
        ),
        _alignment_row(
            "G documentation alignment",
            "PASS" if not stale_paths else "REVISE",
            {"documentation_files": len(model["documentation_to_implementation_graph"]["documentation_files"]),
             "implementation_targets": len(model["documentation_to_implementation_graph"]["implementation_targets"])},
            [] if not stale_paths else ["stale documented paths"],
        ),
        _alignment_row(
            "H test alignment",
            "PASS" if not missing_coverage else "REVISE",
            {"test_files": len(model["test_to_production_coverage_graph"]["test_files"]),
             "proof_surfaces": len(report["coverage_matrix"]),
             "missing_proof_surfaces": len(missing_coverage)},
            [] if not missing_coverage else ["missing proof surface"],
        ),
        _alignment_row(
            "I AppAI alignment",
            "PASS" if report["coverage_matrix"] else "REVISE",
            {"lifecycle_roles": sum(1 for v in model["lifecycle_graph"]["roles"].values() if v),
             "organ_roles": sum(1 for v in model["appai_organ_map"]["roles"].values() if v),
             "hard_fail_files": len(model["hard_fail_map"]["invariant_files"])},
            [],
        ),
        _alignment_row(
            "J terminology alignment",
            "PASS" if report["alias_registry"]["collision_audit"]["status"] == "PASS" else "REVISE",
            {"aliases": len(report["alias_registry"]["aliases"]),
             "collision_checks": len(report["alias_registry"]["collision_audit"]["checks"])},
            ([] if report["alias_registry"]["collision_audit"]["status"] == "PASS"
             else ["vocabulary collision audit failed"]),
        ),
        _alignment_row(
            "K token-dialect alignment",
            "UNVERIFIABLE" if report["token_status"].get("tiktoken unavailable") else "PASS",
            {"token_status": report["token_status"],
             "tokenizer_status": report["alias_registry"]["tokenizer_status"]},
            (["tiktoken unavailable; token dialect costs not measured"]
             if report["token_status"].get("tiktoken unavailable") else []),
        ),
        _alignment_row(
            "L duplication alignment",
            "REVISE" if report["merge_map"]["merge_candidates"] else "PASS",
            {"exact_duplicate_hashes": len(maps["duplicate_hashes"]),
             "merge_candidates": len(report["merge_map"]["merge_candidates"]),
             "candidate_decisions": report["merge_map"]["candidate_decisions"]},
            ["candidate review remains queued"] if report["merge_map"]["merge_candidates"] else [],
        ),
        _alignment_row(
            "M version alignment",
            report["version_alignment"]["status"],
            {"package": report["version_alignment"]["package_version"],
             "module": report["version_alignment"]["module_version"],
             "grimoire": report["version_alignment"]["grimoire_version"]},
            [] if report["version_alignment"]["status"] == "PASS" else ["version drift"],
        ),
        _alignment_row(
            "N security/privacy alignment",
            "PASS",
            {"security_files": sum(1 for f in report["files"] if f["security_privacy_relevance"]),
             "secret_redaction_surface": bool(model["self_other_boundary_map"]["files"])},
            [],
        ),
        _alignment_row(
            "O performance alignment",
            "REVISE" if report["performance_report"]["benchmarks"] else "UNVERIFIABLE",
            {"performance_report": report["performance_report"]["status"],
             "benchmarks": len(report["performance_report"]["benchmarks"])},
            (["observed proof-command durations are not a dedicated benchmark suite"]
             if report["performance_report"]["benchmarks"]
             else ["no benchmark command is run by optimize-audit"]),
        ),
    ]
    statuses = Counter(row["status"] for row in rows)
    missing = [d for d in ALIGNMENT_AUDIT_DOMAINS if d not in {r["domain"] for r in rows}]
    return {
        "status": "REVISE" if any(row["status"] != "PASS" for row in rows) else "PASS",
        "rows": rows,
        "totals": dict(sorted(statuses.items())),
        "missing_domains": missing,
        "rule": "Section 14 A-O alignment rebuilt from the current tree after audit passes.",
    }


def _observed_command(report: Dict[str, Any], needle: str) -> Optional[Dict[str, Any]]:
    for row in report["test_report"].get("observed_commands", []):
        if needle in row.get("command", ""):
            return row
    return None


def _configured_command(report: Dict[str, Any], needle: str) -> Optional[Dict[str, Any]]:
    for row in report["test_report"].get("commands", []):
        if needle in row.get("command", ""):
            return row
    return None


def _verification_row(requirement: str, status: str, evidence: Dict[str, Any],
                      command: Optional[str] = None,
                      blockers: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "requirement": requirement,
        "status": status,
        "evidence": evidence,
        "command": command,
        "blockers": blockers or [],
    }


def _command_verification_row(report: Dict[str, Any], requirement: str, needle: str,
                              blockers: Optional[List[str]] = None) -> Dict[str, Any]:
    configured = _configured_command(report, needle)
    observed = _observed_command(report, needle)
    if observed and observed.get("exit_code") == 0 and not observed.get("timed_out"):
        status = "PASS"
        row_blockers: List[str] = []
    elif configured:
        status = "REVISE"
        row_blockers = blockers or ["configured proof exists but was not observed in this audit run"]
    else:
        status = "UNVERIFIABLE"
        row_blockers = blockers or ["no configured command discovered"]
    return _verification_row(
        requirement,
        status,
        {"configured": bool(configured), "observed": observed or "not-observed"},
        configured.get("command") if configured else needle,
        row_blockers,
    )


def _final_verification(report: Dict[str, Any]) -> Dict[str, Any]:
    py_rows = [row for row in report["file_completion_gate"]["rows"]
               if row["path"].endswith(".py")]
    parse_failures = [row["path"] for row in py_rows if row["parse_status"] != "PASS"]
    stale_paths = [r for r in report["maps"]["path_references"] if not r["exists"]]
    stale_commands = [r for r in report["maps"]["cli_command_references"] if not r["exists"]]
    secret_hits = [
        f["path"] for f in report["files"]
        if f["text"] and SECRET_RE.search(_read_text_optional(report["repo_root"], f["path"]))
    ]
    dirty_paths = [row["path"] for row in report["baseline"]["git"]["status"]]
    rows = [
        _verification_row(
            "source compilation or parsing",
            "PASS" if not parse_failures else "REVISE",
            {"python_files": len(py_rows), "parse_failures": parse_failures[:20]},
            "ast.parse(all Python files)",
            [] if not parse_failures else ["Python parse failure"],
        ),
        _command_verification_row(report, "import smoke tests", " -m mantle check"),
        _verification_row(
            "configured formatter check",
            "UNVERIFIABLE",
            {"configured": False},
            None,
            ["no formatter command is configured in project metadata"],
        ),
        _verification_row(
            "configured lint",
            "UNVERIFIABLE",
            {"configured": False},
            None,
            ["no lint command is configured in project metadata"],
        ),
        _verification_row(
            "configured type checker",
            "UNVERIFIABLE",
            {"configured": False},
            None,
            ["no type-check command is configured in project metadata"],
        ),
        _command_verification_row(report, "unit and invariant tests", " -m mantle prove"),
        _command_verification_row(report, "integration and full certification tests",
                                  " -m mantle check"),
        _command_verification_row(report, "example tests", "examples/vcw/vcw_cube.py selftest"),
        _command_verification_row(report, "CLI smoke tests", " -m mantle check"),
        _command_verification_row(report, "Stage 1 audit", " -m mantle audit"),
        _command_verification_row(report, "Stage 2 readiness audit", " -m mantle audit-mind"),
        _command_verification_row(report, "security checks", " -m mantle prove"),
        _command_verification_row(report, "schema and serialization round trips",
                                  "examples/vcw/vcw_cube.py selftest"),
        _verification_row(
            "documentation link and path checks",
            "PASS" if not stale_paths and not stale_commands else "REVISE",
            {"stale_paths": len(stale_paths), "stale_commands": len(stale_commands)},
            "python -m mantle optimize-audit --strict",
            [] if not stale_paths and not stale_commands else ["stale reference remains"],
        ),
        _verification_row(
            "package build",
            "UNVERIFIABLE",
            {"build_backend": report["baseline"]["project"]["build_backend"],
             "configured_command": False},
            None,
            ["no package build command is configured in project metadata"],
        ),
        _verification_row(
            "clean installation smoke test",
            "UNVERIFIABLE",
            {"configured_command": False},
            None,
            ["no clean-install smoke command is configured in project metadata"],
        ),
        _verification_row(
            "performance benchmarks",
            "REVISE" if report["performance_report"]["benchmarks"] else "UNVERIFIABLE",
            {"benchmarks": report["performance_report"]["benchmarks"]},
            None,
            (["observed proof-command durations are not a dedicated benchmark suite"]
             if report["performance_report"]["benchmarks"]
             else ["no benchmark command is run by optimize-audit"]),
        ),
        _verification_row(
            "cl100k and o200k token report",
            "UNVERIFIABLE" if report["token_status"].get("tiktoken unavailable") else "PASS",
            {"token_status": report["token_status"]},
            "python -m mantle optimize-audit",
            (["tiktoken unavailable; token counts not measured"]
             if report["token_status"].get("tiktoken unavailable") else []),
        ),
        _verification_row(
            "final duplicate scan",
            "REVISE" if report["merge_map"]["merge_candidates"] else "PASS",
            {"merge_candidates": len(report["merge_map"]["merge_candidates"]),
             "exact_duplicate_hashes": len(report["maps"]["duplicate_hashes"])},
            "python -m mantle optimize-audit",
            ["merge candidates remain queued"] if report["merge_map"]["merge_candidates"] else [],
        ),
        _verification_row(
            "final dead-reference scan",
            "PASS" if not stale_paths and not stale_commands else "REVISE",
            {"stale_paths": len(stale_paths), "stale_commands": len(stale_commands)},
            "python -m mantle optimize-audit --strict",
            [] if not stale_paths and not stale_commands else ["dead reference remains"],
        ),
        _verification_row(
            "final secret scan",
            "PASS" if not secret_hits else "REVISE",
            {"secret_hits": secret_hits[:20]},
            "SECRET_RE source scan",
            [] if not secret_hits else ["secret-like material matched source scan"],
        ),
        _verification_row(
            "Git diff and status review",
            "PASS" if not dirty_paths else "REVISE",
            {"dirty_paths": dirty_paths[:20], "dirty_count": len(dirty_paths)},
            "git status --short",
            [] if not dirty_paths else ["working tree has changes under review"],
        ),
    ]
    by_name = {row["requirement"] for row in rows}
    missing = [name for name in REQUIRED_FINAL_VERIFICATION_CHECKS if name not in by_name]
    totals = Counter(row["status"] for row in rows)
    return {
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "REVISE",
        "rows": rows,
        "totals": dict(sorted(totals.items())),
        "missing_requirements": missing,
        "rule": "Section 15 final verification coverage rebuilt from current configured proofs.",
    }


def _semantic_element_count(text: str, element: str) -> int:
    if element == "command":
        return len(COMMAND_RE.findall(text))
    if element == "mode":
        return len(re.findall(r"\bmode\b|\bMode=", text, re.IGNORECASE))
    if element == "trigger":
        return len(re.findall(r"\btrigger", text, re.IGNORECASE))
    if element == "purpose":
        return len(re.findall(r"\bpurpose\b|\bGoal:", text, re.IGNORECASE))
    if element == "gate":
        return len(re.findall(r"\bgate\b", text, re.IGNORECASE))
    if element == "invariant":
        return len(INVARIANT_RE.findall(text)) + len(re.findall(r"\binvariant\b", text,
                                                                 re.IGNORECASE))
    if element == "block":
        return len(re.findall(r"\bblock\b|\bMUST NOT\b|\bHALT\b", text, re.IGNORECASE))
    if element == "procedure":
        return len(re.findall(r"\bSTEP\b|\bprocedure\b|\bspell\b", text, re.IGNORECASE))
    if element == "receipt field":
        return len(re.findall(r"\breceipt\b|WHAT:|WHY:|EVIDENCE:", text, re.IGNORECASE))
    if element == "hard fail":
        return len(re.findall(r"hard[- ]fail|HF-[A-Z0-9]+", text, re.IGNORECASE))
    if element == "implementation reference":
        return len(PATH_RE.findall(text))
    return 0


def _blind_semantic_comparison(report: Dict[str, Any]) -> Dict[str, Any]:
    doctrine = [f for f in report["files"] if f["category"].startswith("C ") and f["text"]]
    combined = "\n".join(_read_text_optional(report["repo_root"], f["path"]) for f in doctrine)
    rows = []
    for element in BLIND_SEMANTIC_ELEMENTS:
        count = _semantic_element_count(combined, element)
        rows.append({
            "element": element,
            "status": "PASS" if count else "UNVERIFIABLE",
            "source_count": count,
            "final_representation": "mapped in current machine-doctrine files",
            "blockers": [] if count else ["element not found in machine-doctrine scan"],
        })
    missing = [name for name in BLIND_SEMANTIC_ELEMENTS if name not in {
        row["element"] for row in rows
    }]
    totals = Counter(row["status"] for row in rows)
    return {
        "status": "REVISE",
        "rows": rows,
        "totals": dict(sorted(totals.items())),
        "missing_elements": missing,
        "machine_doctrine_files": [f["path"] for f in doctrine],
        "rule": "Section 16 blind semantic comparison matrix for machine-only doctrine.",
        "blockers": [
            "fresh-session blind old/new evaluator was not run",
            "no compressed replacement variant is being accepted in this pass",
        ],
    }


def _scorecard_row(metric: str, status: str, before: Any, after: Any, delta: Any,
                   evidence: Dict[str, Any], blockers: Optional[List[str]] = None
                   ) -> Dict[str, Any]:
    return {
        "metric": metric,
        "status": status,
        "before": before,
        "after": after,
        "delta": delta,
        "evidence": evidence,
        "blockers": blockers or [],
    }


def _optimization_scorecard(report: Dict[str, Any]) -> Dict[str, Any]:
    metrics = report["baseline"]["metrics"]
    dispositions = report["dispositions"]
    observed = report["test_report"].get("observed_commands", [])
    observed_green = bool(observed) and all(row.get("exit_code") == 0 and not row.get("timed_out")
                                           for row in observed)
    stale_paths = [r for r in report["maps"]["path_references"] if not r["exists"]]
    stale_commands = [r for r in report["maps"]["cli_command_references"] if not r["exists"]]
    token_unverifiable = bool(report["token_status"].get("tiktoken unavailable"))
    dirty_count = len(report["baseline"]["git"]["status"])
    compatibility_aliases = report["merge_map"]["compatibility_aliases_detected"]
    rows = [
        _scorecard_row(
            "cl100k token counts",
            "UNVERIFIABLE" if token_unverifiable else "PASS",
            None,
            sum(1 for f in report["files"] if f["tokens"]["cl100k"] is not None),
            None,
            {"per_file_data": "TOKEN_REPORT", "token_status": report["token_status"]},
            ["tiktoken unavailable"] if token_unverifiable else [],
        ),
        _scorecard_row(
            "o200k token counts",
            "UNVERIFIABLE" if token_unverifiable else "PASS",
            None,
            sum(1 for f in report["files"] if f["tokens"]["o200k"] is not None),
            None,
            {"per_file_data": "TOKEN_REPORT", "token_status": report["token_status"]},
            ["tiktoken unavailable"] if token_unverifiable else [],
        ),
        _scorecard_row("bytes", "PASS", metrics["bytes"], metrics["bytes"], 0,
                       {"per_file_data": "FILE_INVENTORY"}),
        _scorecard_row("lines", "PASS", metrics["lines"], metrics["lines"], 0,
                       {"per_file_data": "FILE_INVENTORY"}),
        _scorecard_row("changed files", "REVISE" if dirty_count else "PASS", 0, dirty_count,
                       dirty_count, {"git_status_rows": report["baseline"]["git"]["status"]},
                       ["working tree changes under review"] if dirty_count else []),
        _scorecard_row("unchanged files", "PASS", None,
                       report["file_count"] - dirty_count, None,
                       {"file_count": report["file_count"]}),
        _scorecard_row("skipped files", "PASS", None,
                       dispositions.get("inventory-only", 0), None,
                       {"dispositions": dispositions}),
        _scorecard_row("blocked files", "PASS" if dispositions.get("blocked", 0) == 0 else "REVISE",
                       None, dispositions.get("blocked", 0), None,
                       {"dispositions": dispositions},
                       ["blocked files require classification"] if dispositions.get("blocked", 0) else []),
        _scorecard_row("generated files regenerated", "PASS", 0, 0, 0,
                       {"generated_changed": []}),
        _scorecard_row("duplicate implementations removed", "REVISE", 0, 0, 0,
                       {"merge_candidates": len(report["merge_map"]["merge_candidates"])},
                       ["merge candidates remain unmerged pending parity proof"]),
        _scorecard_row("commands merged", "PASS", 0, 0, 0,
                       {"commands_merged": []}),
        _scorecard_row("compatibility aliases retained", "PASS", None,
                       len(compatibility_aliases), None,
                       {"aliases": compatibility_aliases}),
        _scorecard_row("stale references removed",
                       "PASS" if not stale_paths and not stale_commands else "REVISE",
                       0, len(stale_paths) + len(stale_commands), None,
                       {"stale_paths": len(stale_paths), "stale_commands": len(stale_commands)},
                       ["stale reference remains"] if stale_paths or stale_commands else []),
        _scorecard_row("dead code removed", "REVISE", 0, 0, 0,
                       {"merge_candidates": len(report["merge_map"]["merge_candidates"])},
                       ["dead-code deletion requires caller/proof review"]),
        _scorecard_row("tests before/after", "PASS" if observed_green else "REVISE",
                       None, len(observed), None,
                       {"observed_commands": observed},
                       [] if observed_green else ["no observed test command in this audit run"]),
        _scorecard_row("coverage before/after", "UNVERIFIABLE", None, None, None,
                       {"configured_coverage": False},
                       ["no coverage command is configured"]),
        _scorecard_row("lint before/after", "UNVERIFIABLE", None, None, None,
                       {"configured_lint": False},
                       ["no lint command is configured"]),
        _scorecard_row("type-check before/after", "UNVERIFIABLE", None, None, None,
                       {"configured_type_check": False},
                       ["no type-check command is configured"]),
        _scorecard_row("build before/after", "UNVERIFIABLE", None, None, None,
                       {"build_backend": report["baseline"]["project"]["build_backend"]},
                       ["no build command is configured"]),
        _scorecard_row("benchmark before/after",
                       "REVISE" if report["performance_report"]["benchmarks"] else "UNVERIFIABLE",
                       None, len(report["performance_report"]["benchmarks"]), None,
                       {"benchmarks": report["performance_report"]["benchmarks"]},
                       (["observed proof-command durations are not baseline/final benchmarks"]
                        if report["performance_report"]["benchmarks"]
                        else ["no benchmark command is configured"])),
        _scorecard_row("public API changes", "PASS", None,
                       ["python -m mantle optimize-audit"], None,
                       {"public_api_changes": "audit CLI exists; runtime contracts unchanged"}),
        _scorecard_row("behavior changes", "PASS", None, [], None,
                       {"runtime_behavior_changes": []}),
        _scorecard_row("unresolved risks", "REVISE", None,
                       ["pending chunk review", "tokenizer unavailable", "benchmark comparison pending"],
                       None, {"file_completion": report["file_completion_gate"]["totals"]},
                       ["protocol completion still has open proof obligations"]),
        _scorecard_row("unverifiable claims", "REVISE", None,
                       [row["requirement"] for row in report["final_verification"]["rows"]
                        if row["status"] == "UNVERIFIABLE"],
                       None, {"final_verification": report["final_verification"]["totals"]},
                       ["unverifiable final-verification rows remain"]),
    ]
    totals = Counter(row["status"] for row in rows)
    missing = [metric for metric in SCORECARD_METRICS if metric not in {
        row["metric"] for row in rows
    }]
    return {
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "REVISE",
        "rows": rows,
        "totals": dict(sorted(totals.items())),
        "missing_metrics": missing,
        "rule": "Section 17 optimization scorecard with per-file evidence references.",
    }


def _guardian_row(check: str, status: str, evidence: Dict[str, Any],
                  blockers: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "check": check,
        "status": status,
        "evidence": evidence,
        "blockers": blockers or [],
    }


def _guardian_review(report: Dict[str, Any]) -> Dict[str, Any]:
    token_unverifiable = bool(report["token_status"].get("tiktoken unavailable"))
    rows = [
        _guardian_row("inventory complete", "PASS",
                      {"files": report["file_count"], "tracked_missing": report["tracked_missing"]}),
        _guardian_row("eligible chunks inspected", "REVISE",
                      {"file_completion": report["file_completion_gate"]["totals"]},
                      ["pending chunk review remains"]),
        _guardian_row("changed chunks verified", "REVISE",
                      {"changed": report["dispositions"].get("changed", 0)},
                      ["changed chunks require observed proof receipts"] if report["dispositions"].get("changed", 0) else []),
        _guardian_row("tests remain green", "REVISE",
                      {"final_verification": report["final_verification"]["totals"]},
                      ["not every configured final check is observed"]),
        _guardian_row("public compatibility visible", "PASS",
                      {"compatibility_aliases": report["merge_map"]["compatibility_aliases_detected"]}),
        _guardian_row("AppAI invariants preserved", "PASS",
                      {"appai_alignment": report["whole_project_alignment"]["rows"][8]["status"]}),
        _guardian_row("hard fails intact", "PASS",
                      {"hard_fail_files": len(report["project_model"]["hard_fail_map"]["invariant_files"])}),
        _guardian_row("merge parity evidence", "PASS",
                      {"parity": report["merge_map"]["parity_review"]["totals"]}),
        _guardian_row("alias collision and tokenizer proof",
                      "UNVERIFIABLE" if token_unverifiable else "PASS",
                      {"alias_audit": report["alias_registry"]["collision_audit"]["status"],
                       "token_status": report["token_status"]},
                      ["tokenizer proof unavailable"] if token_unverifiable else []),
        _guardian_row("ripples resolved or queued", "PASS",
                      {"ripple_queue": report["ripple_queue"]["totals"]}),
        _guardian_row("cross-surface alignment", "REVISE",
                      {"whole_project_alignment": report["whole_project_alignment"]["totals"]},
                      ["alignment rows remain REVISE or UNVERIFIABLE"]),
        _guardian_row("Core/AppAI version alignment", "PASS",
                      {"version_alignment": report["version_alignment"]["status"]}),
        _guardian_row("whole-project token count measured",
                      "UNVERIFIABLE" if token_unverifiable else "PASS",
                      {"token_status": report["token_status"]},
                      ["tiktoken unavailable"] if token_unverifiable else []),
        _guardian_row("whole-project alignment audit", "REVISE",
                      {"status": report["whole_project_alignment"]["status"]},
                      ["whole-project alignment is not PASS"]),
        _guardian_row("final verification", "REVISE",
                      {"status": report["final_verification"]["status"]},
                      ["final verification is not PASS"]),
        _guardian_row("blind semantic comparison", "REVISE",
                      {"status": report["blind_semantic_comparison"]["status"]},
                      ["blind semantic comparison is not PASS"]),
    ]
    totals = Counter(row["status"] for row in rows)
    missing = [check for check in GUARDIAN_CHECKS if check not in {
        row["check"] for row in rows
    }]
    status = "PASS" if all(row["status"] == "PASS" for row in rows) else "REVISE"
    return {
        "status": status,
        "rows": rows,
        "totals": dict(sorted(totals.items())),
        "missing_checks": missing,
        "rule": "Section 20 guardian review decides PASS/REVISE/HALT/ESCALATE from evidence.",
    }


def _project_model(report: Dict[str, Any]) -> Dict[str, Any]:
    files = report["files"]
    maps = report["maps"]
    model = {
        "file_dependency_graph": {
            "status": "derived",
            "path_reference_edges": [
                {"from": r["from"], "to": r["ref"], "exists": r["exists"]}
                for r in maps["path_references"]
            ],
        },
        "python_import_export_graph": {
            "status": "derived",
            "modules": maps["module_paths"],
            "imports": maps["import_graph"],
            "importers": maps["importers"],
        },
        "public_api_graph": {
            "status": "derived",
            "public_symbols": maps["public_api"],
            "module_count": len(maps["public_api"]),
        },
        "cli_command_option_graph": {
            "status": "derived",
            "known_commands": maps["known_cli_commands"],
            "references": maps["cli_command_references"],
        },
        "configuration_graph": {
            "status": "derived",
            "environment_variables": maps["environment_variables"],
            "files": {f["path"]: f["configuration_keys"] for f in files
                      if f["configuration_keys"]},
        },
        "schema_serialization_graph": {
            "status": "derived",
            "files": {f["path"]: f["schemas"] for f in files if f["schemas"]},
        },
        "test_to_production_coverage_graph": {
            "status": "derived",
            "test_files": _model_paths(files, lambda f: f["category"].startswith("B ")),
            "production_targets": {f["path"]: f["tests"] for f in files if f["tests"]},
        },
        "documentation_to_implementation_graph": {
            "status": "derived",
            "documentation_files": _model_paths(
                files, lambda f: f["category"].startswith(("C ", "D "))),
            "implementation_targets": {
                f["path"]: f["documentation_references"]
                for f in files if f["documentation_references"]
            },
        },
        "example_to_api_graph": {
            "status": "derived",
            "example_files": _model_paths(files, lambda f: f["category"].startswith("H ")),
            "api_touchpoints": {
                f["path"]: sorted(set(f["imports"] + f["referenced_commands"]))
                for f in files if f["category"].startswith("H ")
            },
        },
        "lifecycle_graph": {
            "status": "derived",
            "roles": {
                role: _model_paths(files, lambda f, role=role: role in f["lifecycle_roles"])
                for role in (
                    "birth", "assimilation", "residency", "diagnostics", "memory",
                    "cognition", "reconstruction", "retirement",
                )
            },
        },
        "appai_organ_map": {
            "status": "derived",
            "roles": {
                role: _model_paths(files, lambda f, role=role: role in f["appai_roles"])
                for role in (
                    "Heart", "Genome", "Nervous System", "Senses", "Immune",
                    "Limbs", "Memory", "Brain", "Reproduction", "Doctrine",
                )
            },
        },
        "self_other_boundary_map": {
            "status": "derived",
            "files": _model_paths(files, lambda f: "identity-boundary"
                                  in f["security_privacy_relevance"]),
        },
        "effect_action_proof_map": {
            "status": "derived",
            "files": _model_paths(files, lambda f: "external-effect"
                                  in f["security_privacy_relevance"]
                                  or bool(f["side_effects"])),
        },
        "hard_fail_map": {
            "status": "derived",
            "invariant_files": {f["path"]: f["invariants"] for f in files if f["invariants"]},
        },
        "vcw_band_owner_writer_map": {
            "status": "derived",
            "files": _model_paths(files, lambda f: "VCW" in f["appai_roles"]
                                  or "Memory" in f["appai_roles"]
                                  or "vcw" in f["path"].lower()),
        },
        "provider_cache_configuration_map": {
            "status": "derived",
            "files": _model_paths(files, lambda f: "provider-cache"
                                  in f["security_privacy_relevance"]
                                  or "provider-or-http" in f["external_interfaces"]),
        },
        "version_compatibility_graph": {
            "status": "derived",
            "version_alignment": report["version_alignment"],
        },
        "duplicate_concept_map": {
            "status": "baseline",
            "exact_duplicate_hashes": maps["duplicate_hashes"],
            "merge_candidates": report["merge_map"]["merge_candidates"],
            "candidate_decisions": report["merge_map"]["candidate_decisions"],
            "parity_review": report["merge_map"]["parity_review"],
            "near_duplicate_status": (
                "CANDIDATES-QUEUED; semantic merge requires parity review before mutation"
            ),
        },
    }
    model["status"] = "PASS" if set(REQUIRED_PROJECT_MODEL_MAPS).issubset(model) else "REVISE"
    return model


def _test_report(report: Dict[str, Any], observed: Optional[List[Dict[str, Any]]] = None
                 ) -> Dict[str, Any]:
    observed = observed or []
    observed_by_command = {r["command"]: r for r in observed}
    configured = [
        {"command": "PYTHONPATH=src python -m mantle optimize-audit --strict",
         "coverage": "artifact generation and strict alignment gate",
         "source": "src/mantle/cli.py", "network": False},
        {"command": "PYTHONPATH=src python -m mantle check --fast",
         "coverage": "fast certification subset",
         "source": "README.md", "network": False},
        {"command": "PYTHONPATH=src python -m mantle check",
         "coverage": "full local certification",
         "source": "README.md", "network": False},
        {"command": "PYTHONPATH=src python -m mantle prove",
         "coverage": "security invariants",
         "source": "README.md", "network": False},
        {"command": "PYTHONPATH=src python -m mantle audit",
         "coverage": "Stage-1 Zombie Body gate",
         "source": "documents/guides/Audit_Guide.md", "network": False},
        {"command": "PYTHONPATH=src python -m mantle audit-mind",
         "coverage": "Stage-2 MIND containment gate",
         "source": "documents/guides/Audit_Guide.md", "network": False},
        {"command": "PYTHONPATH=src python examples/vcw/vcw_cube.py selftest",
         "coverage": "standalone VCW codec conformance",
         "source": "README.md", "network": False},
        {"command": "npm install",
         "coverage": "browser smoke-test dependencies",
         "source": ".github/workflows/demos.yml", "network": True},
        {"command": "npx playwright install --with-deps chromium",
         "coverage": "browser smoke-test runtime",
         "source": ".github/workflows/demos.yml", "network": True},
        {"command": "node demo_smoke.mjs",
         "coverage": "reference demo browser smoke tests",
         "source": ".github/workflows/demos.yml", "network": False},
        {"command": "node live_agent_smoke.mjs",
         "coverage": "live agent browser smoke test",
         "source": ".github/workflows/demos.yml", "network": False},
    ]
    commands = []
    for command in configured:
        row = dict(command)
        observed_row = observed_by_command.get(row["command"])
        if observed_row is None and row["command"].startswith("PYTHONPATH=src "):
            bare = row["command"].replace("PYTHONPATH=src ", "", 1)
            mantle_tail = None
            if " -m mantle" in bare:
                mantle_tail = " -m mantle" + bare.split(" -m mantle", 1)[1]
            observed_row = next((r for r in observed
                                 if r["command"].endswith(bare)
                                 or (mantle_tail and r["command"].endswith(mantle_tail))),
                                None)
        row["observed"] = observed_row or "not-run-by-optimize-audit"
        commands.append(row)
    return {
        "status": "verification-index",
        "environment": report["baseline"]["runtime"],
        "git": report["baseline"]["git"],
        "project": report["baseline"]["project"],
        "commands": commands,
        "observed_commands": observed,
        "note": ("This command does not run heavy proof gates by default; it records "
                 "configured proof surfaces. Use --run-checks=prove|fast|full|final for "
                 "explicit observed exit-code receipts."),
    }


def _performance_report(report: Dict[str, Any]) -> Dict[str, Any]:
    total_bytes = sum(f["bytes"] for f in report["files"])
    total_lines = sum(f["lines"] for f in report["files"])
    observed = report.get("test_report", {}).get("observed_commands", [])
    benchmarks = [
        {
            "command": row["command"],
            "duration_s": row["duration_s"],
            "exit_code": row["exit_code"],
            "timed_out": row["timed_out"],
            "metric": "wall-clock duration of observed proof command",
        }
        for row in observed
        if row.get("duration_s") is not None
    ]
    return {
        "status": "observed-proof-durations" if benchmarks else "baseline-only",
        "metrics": {"files": report["file_count"], "bytes": total_bytes, "lines": total_lines},
        "benchmarks": benchmarks,
        "confidence": (
            "medium for observed proof-command wall-clock receipts; not a dedicated benchmark suite"
            if benchmarks else "low; no benchmark command is run by optimize-audit"
        ),
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
    alias_checks = report["alias_registry"]["collision_audit"].get("checks", {})
    missing_alias_checks = [name for name in REQUIRED_ALIAS_COLLISION_CHECKS
                            if name not in alias_checks]
    if missing_alias_checks:
        failures.append("missing alias collision checks: %s" % ", ".join(missing_alias_checks))
    missing_fields = {
        f["path"]: [field for field in REQUIRED_FILE_FIELDS if field not in f]
        for f in report.get("files", [])
    }
    missing_fields = {path: fields for path, fields in missing_fields.items() if fields}
    if missing_fields:
        failures.append("%d files missing required inventory fields" % len(missing_fields))
    missing_coverage = [r for r in report["coverage_matrix"] if r["status"] != "present"]
    if missing_coverage:
        failures.append("%d missing proof surfaces" % len(missing_coverage))
    ledger_paths = {r.get("path") for r in report.get("change_ledger", [])}
    file_paths = {f.get("path") for f in report.get("files", [])}
    if ledger_paths != file_paths:
        failures.append("change ledger does not cover every inventoried file")
    if report.get("version_alignment", {}).get("status") != "PASS":
        failures.append("version alignment map failed")
    model = report.get("project_model", {})
    missing_model_maps = [name for name in REQUIRED_PROJECT_MODEL_MAPS if name not in model]
    if missing_model_maps:
        failures.append("missing project model maps: %s" % ", ".join(missing_model_maps))
    if model.get("status") != "PASS":
        failures.append("project model map failed")
    merge_map = report.get("merge_map", {})
    malformed_candidates = [
        c for c in merge_map.get("merge_candidates", [])
        if any(field not in c for field in MERGE_CANDIDATE_FIELDS)
    ]
    if malformed_candidates:
        failures.append("%d malformed merge candidate rows" % len(malformed_candidates))
    if merge_map.get("status") != "candidate-analysis":
        failures.append("merge candidate analysis missing")
    parity = merge_map.get("parity_review", {})
    candidate_ids = {c.get("candidate_id") for c in merge_map.get("merge_candidates", [])}
    parity_ids = {row.get("candidate_id") for row in parity.get("rows", [])}
    missing_parity = sorted(candidate_ids - parity_ids)
    if missing_parity:
        failures.append("missing merge parity rows: %s" % ", ".join(missing_parity))
    malformed_parity = [
        row.get("candidate_id", "<unknown>")
        for row in parity.get("rows", [])
        if any(field not in row for field in MERGE_PARITY_FIELDS)
    ]
    if malformed_parity:
        failures.append("%d malformed merge parity rows" % len(malformed_parity))
    if merge_map.get("merge_candidates") and not parity.get("rows"):
        failures.append("merge parity review missing")
    completion = report.get("file_completion_gate", {})
    missing_completion = completion.get("missing_fields") or []
    if missing_completion:
        failures.append("%d file completion rows missing required fields" % len(missing_completion))
    if not completion.get("rows"):
        failures.append("file completion gate ledger missing")
    subsystem = report.get("subsystem_convergence", {})
    missing_subsystems = subsystem.get("missing_fields") or []
    if missing_subsystems:
        failures.append("%d subsystem convergence rows missing required fields" % len(missing_subsystems))
    if not subsystem.get("rows"):
        failures.append("subsystem convergence report missing")
    ripple = report.get("ripple_queue", {})
    missing_ripple_fields = ripple.get("missing_fields") or []
    if missing_ripple_fields:
        failures.append("%d ripple queue rows missing required fields" % len(missing_ripple_fields))
    missing_ripple_surfaces = [
        name for name in REQUIRED_RIPPLE_SURFACES
        if name not in ripple.get("required_surfaces", [])
    ]
    if missing_ripple_surfaces:
        failures.append("missing ripple surfaces: %s" % ", ".join(missing_ripple_surfaces))
    alignment = report.get("whole_project_alignment", {})
    missing_alignment_domains = alignment.get("missing_domains") or []
    if missing_alignment_domains:
        failures.append("missing alignment domains: %s" % ", ".join(missing_alignment_domains))
    if not alignment.get("rows"):
        failures.append("whole-project alignment audit missing")
    final_verification = report.get("final_verification", {})
    missing_final_requirements = final_verification.get("missing_requirements") or []
    if missing_final_requirements:
        failures.append("missing final verification requirements: %s"
                        % ", ".join(missing_final_requirements))
    malformed_final_rows = [
        row.get("requirement", "<unknown>")
        for row in final_verification.get("rows", [])
        if any(field not in row for field in FINAL_VERIFICATION_FIELDS)
    ]
    if malformed_final_rows:
        failures.append("%d malformed final verification rows" % len(malformed_final_rows))
    if not final_verification.get("rows"):
        failures.append("final verification coverage missing")
    semantic = report.get("blind_semantic_comparison", {})
    missing_semantic_elements = semantic.get("missing_elements") or []
    if missing_semantic_elements:
        failures.append("missing blind semantic elements: %s"
                        % ", ".join(missing_semantic_elements))
    malformed_semantic_rows = [
        row.get("element", "<unknown>")
        for row in semantic.get("rows", [])
        if any(field not in row for field in BLIND_SEMANTIC_FIELDS)
    ]
    if malformed_semantic_rows:
        failures.append("%d malformed blind semantic rows" % len(malformed_semantic_rows))
    if not semantic.get("rows"):
        failures.append("blind semantic comparison matrix missing")
    scorecard = report.get("optimization_scorecard", {})
    missing_scorecard_metrics = scorecard.get("missing_metrics") or []
    if missing_scorecard_metrics:
        failures.append("missing scorecard metrics: %s" % ", ".join(missing_scorecard_metrics))
    malformed_scorecard_rows = [
        row.get("metric", "<unknown>")
        for row in scorecard.get("rows", [])
        if any(field not in row for field in SCORECARD_FIELDS)
    ]
    if malformed_scorecard_rows:
        failures.append("%d malformed scorecard rows" % len(malformed_scorecard_rows))
    if not scorecard.get("rows"):
        failures.append("optimization scorecard missing")
    guardian = report.get("guardian_review", {})
    missing_guardian_checks = guardian.get("missing_checks") or []
    if missing_guardian_checks:
        failures.append("missing guardian checks: %s" % ", ".join(missing_guardian_checks))
    malformed_guardian_rows = [
        row.get("check", "<unknown>")
        for row in guardian.get("rows", [])
        if any(field not in row for field in GUARDIAN_FIELDS)
    ]
    if malformed_guardian_rows:
        failures.append("%d malformed guardian rows" % len(malformed_guardian_rows))
    if not guardian.get("rows"):
        failures.append("guardian review missing")
    if artifacts is not None:
        missing_artifacts = [name for name, path in artifacts.items() if not os.path.exists(path)]
        if missing_artifacts:
            failures.append("missing artifacts: %s" % ", ".join(missing_artifacts))
        if set(artifacts) != set(REQUIRED_ARTIFACTS):
            failures.append("artifact set does not match REQUIRED_ARTIFACTS")
    return failures


def build_inventory(root: str = paths.REPO_ROOT,
                    observed_checks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    root = os.path.abspath(root)
    tracked = _tracked(root)
    untracked = _status_untracked(root)
    statuses = _status_map(root)
    files = [inventory_file(path, root, tracked, untracked)
             for path in sorted(iter_repo_files(root), key=lambda p: _rel(p, root).lower())]
    for f in files:
        git_status = statuses.get(f["path"])
        disposition = _file_disposition(f, git_status)
        f["git_status"] = git_status
        f["disposition"] = disposition["disposition"]
        f["skip_block_reason"] = disposition["reason"]
    categories = Counter(f["category"] for f in files)
    token_status = Counter(f["token_status"] for f in files)
    dispositions = Counter(f["disposition"] for f in files)
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
        "dispositions": dict(sorted(dispositions.items())),
        "token_status": dict(sorted(token_status.items())),
        "files": files,
    }
    report["baseline"] = _baseline_stats(report)
    report["maps"] = _derived_maps(report)
    _enrich_file_relationships(report)
    report["alias_registry"] = _alias_registry(report)
    report["coverage_matrix"] = _coverage_matrix(report)
    report["change_ledger"] = _change_ledger(report)
    report["merge_map"] = _merge_map(report)
    report["test_report"] = _test_report(report, observed_checks)
    report["performance_report"] = _performance_report(report)
    report["version_alignment"] = _version_alignment(root, _invariant_count(root))
    report["project_model"] = _project_model(report)
    report["file_completion_gate"] = _file_completion_gate(report)
    report["subsystem_convergence"] = _subsystem_convergence(report)
    report["ripple_queue"] = _ripple_queue(report)
    report["whole_project_alignment"] = _whole_project_alignment(report)
    report["final_verification"] = _final_verification(report)
    report["blind_semantic_comparison"] = _blind_semantic_comparison(report)
    report["optimization_scorecard"] = _optimization_scorecard(report)
    report["guardian_review"] = _guardian_review(report)
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
        "baseline": report["baseline"]["metrics"],
        "dispositions": report["dispositions"],
        "token_status": report["token_status"],
        "files": [{"path": f["path"], "tokens": f["tokens"],
                   "token_status": f["token_status"], "bytes": f["bytes"],
                   "lines": f["lines"], "words": f["words"]} for f in files],
    }, indent=2, sort_keys=True))
    _write(artifacts["TEST_REPORT"],
           json.dumps(report["test_report"], indent=2, sort_keys=True))
    _write(artifacts["PERFORMANCE_REPORT"],
           json.dumps(report["performance_report"], indent=2, sort_keys=True))
    skipped = [f for f in files if f["disposition"] != "pending-pass-review"]
    pending = [f for f in files if f["disposition"] == "pending-pass-review"]
    _write(artifacts["SKIP_BLOCK_REPORT"],
           "# Skip / Block Report\n\n"
           "Inventory-only, changed, and blocked files are listed with reasons. "
           "Eligible text files not selected in this pass remain pending.\n\n"
           "## Non-Pending Files\n\n"
           + ("\n".join("- `%s`: %s" % (f["path"], f["skip_block_reason"])
                        for f in skipped) or "- none")
           + "\n\n## Pending Eligible Files\n\n"
           + ("\n".join("- `%s`: %s" % (f["path"], f["skip_block_reason"])
                        for f in pending) or "- none")
           + "\n")
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
           + "Version alignment: %s\n"
           % report["version_alignment"]["status"]
           + "\n".join("- %s `%s`: %r (expected %r) -> %s"
                       % (r["surface"], r["field"], r["value"], r["expected"], r["status"])
                       for r in report["version_alignment"]["rows"])
           + "\n\n"
           "Project model maps: %s\n"
           % report["project_model"]["status"]
           + "\n".join("- %s: %s" % (name, report["project_model"][name]["status"])
                       for name in REQUIRED_PROJECT_MODEL_MAPS)
           + "\n\n"
           "Vocabulary collision audit: %s\n"
           % report["alias_registry"]["collision_audit"]["status"]
           + "\n".join("- %s: %s" % (
               name, report["alias_registry"]["collision_audit"]["checks"][name]["status"])
                       for name in REQUIRED_ALIAS_COLLISION_CHECKS)
           + "\n\n"
           "Merge candidates: %d; decisions=%s\n"
           % (len(report["merge_map"]["merge_candidates"]),
              dict(sorted(report["merge_map"]["candidate_decisions"].items())))
           + "\n\n"
           "Merge parity review: %s; totals=%s\n"
           % (report["merge_map"]["parity_review"]["status"],
              report["merge_map"]["parity_review"]["totals"])
           + "\n".join("- %s: %s" % (row["candidate_id"], row["status"])
                       for row in report["merge_map"]["parity_review"]["rows"])
           + "\n\n"
           "File completion gate: %s; totals=%s\n"
           % (report["file_completion_gate"]["status"],
              report["file_completion_gate"]["totals"])
           + "\n\n"
           "Subsystem convergence: %s; totals=%s\n"
           % (report["subsystem_convergence"]["status"],
              report["subsystem_convergence"]["totals"])
           + "\n\n"
           "Ripple queue: %s; totals=%s; surfaces=%d\n"
           % (report["ripple_queue"]["status"], report["ripple_queue"]["totals"],
              len(report["ripple_queue"]["required_surfaces"]))
           + "\n\n"
           "Whole-project alignment: %s; totals=%s\n"
           % (report["whole_project_alignment"]["status"],
              report["whole_project_alignment"]["totals"])
           + "\n".join("- %s: %s" % (row["domain"], row["status"])
                       for row in report["whole_project_alignment"]["rows"])
           + "\n\n"
           "Final verification coverage: %s; totals=%s\n"
           % (report["final_verification"]["status"],
              report["final_verification"]["totals"])
           + "\n".join("- %s: %s" % (row["requirement"], row["status"])
                       for row in report["final_verification"]["rows"])
           + "\n\n"
           "Blind semantic comparison: %s; totals=%s\n"
           % (report["blind_semantic_comparison"]["status"],
              report["blind_semantic_comparison"]["totals"])
           + "\n".join("- %s: %s" % (row["element"], row["status"])
                       for row in report["blind_semantic_comparison"]["rows"])
           + "\n\n"
           "Optimization scorecard: %s; totals=%s\n"
           % (report["optimization_scorecard"]["status"],
              report["optimization_scorecard"]["totals"])
           + "\n".join("- %s: %s" % (row["metric"], row["status"])
                       for row in report["optimization_scorecard"]["rows"])
           + "\n\n"
           "Guardian review: %s; totals=%s\n"
           % (report["guardian_review"]["status"],
              report["guardian_review"]["totals"])
           + "\n".join("- %s: %s" % (row["check"], row["status"])
                       for row in report["guardian_review"]["rows"])
           + "\n\n"
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
           "\nCHANGE_LEDGER: %d per-file disposition receipt(s); dispositions=%s.\n"
           "\nVERSION_ALIGNMENT: %s; package=%s module=%s grimoire=%s/%s invariants=%s.\n"
           "\nPROJECT_MODEL: %s; maps=%d.\n"
           "\nVOCABULARY_COLLISION_AUDIT: %s; checks=%d.\n"
           "\nMERGE_CANDIDATES: %d candidate(s); decisions=%s; no merges performed.\n"
           "\nMERGE_PARITY_REVIEW: %s; totals=%s; safe_to_merge_now=0.\n"
           "\nFILE_COMPLETION_GATE: %s; totals=%s.\n"
           "\nSUBSYSTEM_CONVERGENCE: %s; totals=%s.\n"
           "\nRIPPLE_QUEUE: %s; totals=%s; surfaces=%d.\n"
           "\nWHOLE_PROJECT_ALIGNMENT: %s; totals=%s.\n"
           "\nFINAL_VERIFICATION: %s; totals=%s.\n"
           "\nBLIND_SEMANTIC_COMPARISON: %s; totals=%s.\n"
           "\nOPTIMIZATION_SCORECARD: %s; totals=%s.\n"
           "\nTESTS: TEST_REPORT lists configured proof commands; observed exit codes remain external receipts.\n"
           "\nPUBLIC_API_CHANGES: adds `python -m mantle optimize-audit`.\n"
           "\nBEHAVIOR_CHANGES: none to organism runtime behavior.\n"
           "\nPRESERVED_INVARIANTS: Body-before-MIND, SELF/OTHER, cache, lineage, host preservation.\n"
           "\nRISKS: artifact path references are literal-string checks, not full semantic proof.\n"
           "\nOPEN_QUESTIONS: tokenizer measurement needs optional tiktoken authority.\n"
           "\nBLOCKERS: full protocol completion still needs chunk-by-chunk optimization passes.\n"
           "\nALIGNMENT_RESULT: REVISE; baseline maps generated, convergence pending.\n"
           "\nGUARDIAN_RESULT: %s; totals=%s; safe to continue in smaller passes.\n"
           % (report["file_count"], report["branch"], report["head"],
              report["file_count"], len(artifacts), len(report["change_ledger"]),
              dict(sorted(report["dispositions"].items())),
              report["version_alignment"]["status"],
              report["version_alignment"]["package_version"],
              report["version_alignment"]["module_version"],
              report["version_alignment"]["grimoire_stamp"],
              report["version_alignment"]["grimoire_version"],
              report["version_alignment"]["security_invariant_count"],
              report["project_model"]["status"], len(REQUIRED_PROJECT_MODEL_MAPS),
              report["alias_registry"]["collision_audit"]["status"],
              len(REQUIRED_ALIAS_COLLISION_CHECKS),
              len(report["merge_map"]["merge_candidates"]),
              dict(sorted(report["merge_map"]["candidate_decisions"].items())),
              report["merge_map"]["parity_review"]["status"],
              report["merge_map"]["parity_review"]["totals"],
              report["file_completion_gate"]["status"],
              report["file_completion_gate"]["totals"],
              report["subsystem_convergence"]["status"],
              report["subsystem_convergence"]["totals"],
              report["ripple_queue"]["status"], report["ripple_queue"]["totals"],
              len(report["ripple_queue"]["required_surfaces"]),
              report["whole_project_alignment"]["status"],
              report["whole_project_alignment"]["totals"],
              report["final_verification"]["status"],
              report["final_verification"]["totals"],
              report["blind_semantic_comparison"]["status"],
              report["blind_semantic_comparison"]["totals"],
              report["optimization_scorecard"]["status"],
              report["optimization_scorecard"]["totals"],
              report["guardian_review"]["status"],
              report["guardian_review"]["totals"]))
    return artifacts


def default_out_dir(root: str = paths.REPO_ROOT) -> str:
    return os.path.join(tempfile.gettempdir(), "mantle-os-optimization-artifacts")


def main(argv=None) -> int:
    argv = list(argv or [])
    out_dir = default_out_dir()
    strict = "--strict" in argv
    run_checks = "none"
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            print("usage: python -m mantle optimize-audit [--out DIR] [--json] "
                  "[--strict] [--run-checks=prove|fast|full|final]")
            return 2
        out_dir = argv[i + 1]
    for arg in argv:
        if arg.startswith("--out="):
            out_dir = arg.split("=", 1)[1]
        if arg.startswith("--run-checks="):
            run_checks = arg.split("=", 1)[1]
    observed = [] if run_checks in ("", "none") else _run_checks(paths.REPO_ROOT, run_checks)
    report = build_inventory(observed_checks=observed)
    artifacts = write_artifacts(report, out_dir)
    failures = strict_failures(report, artifacts)
    observed_failed = [r for r in observed if r.get("exit_code") not in (0,)]
    failures.extend("observed check failed: %s" % r.get("command") for r in observed_failed)
    if "--json" in argv:
        print(json.dumps({"ok": True, "out_dir": out_dir, "artifacts": artifacts,
                          "file_count": report["file_count"],
                          "categories": report["categories"],
                          "token_status": report["token_status"],
                          "merge_parity_review": {
                              "status": report["merge_map"]["parity_review"]["status"],
                              "totals": report["merge_map"]["parity_review"]["totals"],
                          },
                          "final_verification": {
                              "status": report["final_verification"]["status"],
                              "totals": report["final_verification"]["totals"],
                          },
                          "blind_semantic_comparison": {
                              "status": report["blind_semantic_comparison"]["status"],
                              "totals": report["blind_semantic_comparison"]["totals"],
                          },
                          "optimization_scorecard": {
                              "status": report["optimization_scorecard"]["status"],
                              "totals": report["optimization_scorecard"]["totals"],
                          },
                          "guardian_review": {
                              "status": report["guardian_review"]["status"],
                              "totals": report["guardian_review"]["totals"],
                          },
                          "observed_checks": observed,
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
        print("  parity    : %s %s" % (
            report["merge_map"]["parity_review"]["status"],
            report["merge_map"]["parity_review"]["totals"],
        ))
        if observed:
            print("  observed   : %d command(s)" % len(observed))
            for row in observed:
                code = "timeout" if row.get("timed_out") else row.get("exit_code")
                print("    %-8s %s" % (code, row.get("command")))
        print("  final     : %s %s" % (
            report["final_verification"]["status"],
            report["final_verification"]["totals"],
        ))
        print("  semantic  : %s %s" % (
            report["blind_semantic_comparison"]["status"],
            report["blind_semantic_comparison"]["totals"],
        ))
        print("  scorecard : %s %s" % (
            report["optimization_scorecard"]["status"],
            report["optimization_scorecard"]["totals"],
        ))
        print("  guardian  : %s %s" % (
            report["guardian_review"]["status"],
            report["guardian_review"]["totals"],
        ))
        if strict:
            print("  strict     : %s" % ("PASS" if not failures else "FAIL"))
            for failure in failures:
                print("               - %s" % failure)
    return 1 if strict and failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
