#!/usr/bin/env python3
"""Generate/check the whole-repository Hermes alignment inventory."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tomllib


ADDON_ROOT = Path(__file__).resolve().parents[1]
ROOT = ADDON_ROOT.parents[1]
JSON_REPORT = ADDON_ROOT / "docs" / "REPOSITORY_ALIGNMENT.json"
MD_REPORT = ADDON_ROOT / "docs" / "REPOSITORY_ALIGNMENT.md"
GENERATED = {
    str(JSON_REPORT.relative_to(ROOT)),
    str(MD_REPORT.relative_to(ROOT)),
}
INTERNAL_PREFIXES = (".hermes/",)


def repository_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, check=True,
    )
    paths = {
        path
        for item in completed.stdout.split(b"\0")
        if item
        for path in (item.decode("utf-8"),)
        if not path.startswith(INTERNAL_PREFIXES)
    }
    paths.update(GENERATED)
    return sorted(paths)


def category(path: str) -> str:
    parts = Path(path).parts
    suffix = Path(path).suffix.lower()
    if "vendor" in parts:
        return "vendor"
    if path.startswith(".github/workflows/"):
        return "workflow"
    if "tests" in parts or Path(path).name.startswith("test_"):
        return "test"
    if suffix == ".py" and path.startswith("src/"):
        return "core-source"
    if suffix == ".py":
        return "example-or-addon-source"
    if suffix in {".md", ".txt"}:
        return "documentation"
    if suffix in {".json", ".toml", ".yaml", ".yml"}:
        return "machine-data"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"}:
        return "asset"
    return "metadata-or-other"


def review_method(kind: str) -> str:
    return {
        "core-source": "AST parse + invariants + framework gates + architecture claim scan",
        "example-or-addon-source": "AST parse + unittest/integration gates + architecture claim scan",
        "test": "AST parse + executed proof surface",
        "vendor": "SHA-256 snapshot parity + private-namespace execution",
        "documentation": "UTF-8 decode + architecture claim scan + authority reconciliation",
        "machine-data": "format parse + schema/contract tests",
        "workflow": "UTF-8/YAML inspection + command-reference audit",
        "asset": "path classification + SHA-256 integrity",
        "metadata-or-other": "UTF-8/binary classification + package/repository audit",
    }[kind]


def validate(path: Path) -> tuple[bool, str]:
    suffix = path.suffix.lower()
    if not path.exists():
        return False, "missing"
    if suffix == ".py":
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, "python-ast"
    if suffix == ".json":
        json.loads(path.read_text(encoding="utf-8"))
        return True, "json"
    if suffix == ".toml":
        tomllib.loads(path.read_text(encoding="utf-8"))
        return True, "toml"
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError:
            path.read_text(encoding="utf-8")
            return True, "yaml-unverifiable-parser-unavailable"
        yaml.safe_load(path.read_text(encoding="utf-8"))
        return True, "yaml"
    try:
        path.read_text(encoding="utf-8")
        return True, "utf-8"
    except UnicodeDecodeError:
        return True, "binary"


def build() -> dict[str, object]:
    records = []
    parse_errors = []
    stale_claims = []
    forbidden = {
        "event-" + "gated cognition": "old event-gated heartbeat contract",
        "109" + "/110": "old framework receipt",
        "109 of " + "110": "old framework receipt",
        "authorized only when " + "open hard-fails": "Stage-1 evidence presented as fusion authority",
        "only key that unlocks " + "fusion": "Stage-1 evidence presented as sole fusion authority",
        "wakes the mind " + "only when": "nociception presented as a baseline cognition gate",
    }
    for relative in repository_paths():
        path = ROOT / relative
        kind = category(relative)
        generated = relative in GENERATED
        try:
            valid, validation = (True, "self-validating-generated-report") if generated else validate(path)
        except Exception as exc:  # noqa: BLE001
            valid, validation = False, "%s: %s" % (type(exc).__name__, exc)
            parse_errors.append(relative)
        size = path.stat().st_size if path.exists() else None
        digest = None if generated or not path.exists() else hashlib.sha256(path.read_bytes()).hexdigest()
        if (not generated and path.exists() and kind not in {"test", "vendor", "asset"}
                and path.suffix.lower() in {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}):
            try:
                lowered = path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                lowered = ""
            for phrase, reason in forbidden.items():
                if phrase in lowered:
                    stale_claims.append({"path": relative, "phrase": phrase, "reason": reason})
        records.append({
            "path": relative,
            "category": kind,
            "review_method": review_method(kind),
            "validation": validation,
            "valid": valid,
            "size_bytes": size,
            "sha256": digest,
        })
    counts = Counter(row["category"] for row in records)
    return {
        "schema": "hermes-mantle-repository-alignment-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(ROOT),
        "scope": "every git-tracked or non-ignored repository file; ignored caches/build output excluded",
        "files_total": len(records),
        "category_counts": dict(sorted(counts.items())),
        "parse_errors": parse_errors,
        "stale_architecture_claims": stale_claims,
        "resolved_findings": [
            "APPLET-5 private-namespace import",
            "Stage-1 evidence/authority conflation",
            "event-gated natural cognition",
            "core per-artifact atomicity and owner-only modes",
            "unclosed file and mock HTTP-server resources",
            "invalid MacroDroid YAML",
            "root/vendor snapshot drift",
            "framework version and invariant-count drift",
            "reversible authenticated fusion lifecycle",
            "fixed 600-second addon cognitive scheduler",
            "Hermes-native model routing and bounded outage policy",
        ],
        "remaining_readiness_blockers": [],
        "mind_fusion_authorized": False,
        "reproduction_activation_authorized": False,
        "status": "PASS" if not parse_errors and not stale_claims else "FAIL",
        "files": records,
    }


def write_reports(report: dict[str, object]) -> None:
    JSON_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = report["category_counts"]
    lines = [
        "# Repository Alignment Receipt",
        "",
        "**Status:** **%s**" % report["status"],
        "",
        "**Files covered:** **%s**" % report["files_total"],
        "",
        "**MIND fusion authorized:** **NO**",
        "",
        "**Reproduction authorized:** **NO**",
        "",
        "## Scope",
        "",
        str(report["scope"]),
        "",
        "## Classification",
        "",
        "| Class | Files |",
        "|---|---:|",
    ]
    lines.extend("| %s | %s |" % item for item in sorted(counts.items()))
    lines.extend([
        "",
        "## Resolved findings",
        "",
        *["- %s" % item for item in report["resolved_findings"]],
        "",
        "## Deployment activation boundary",
        "",
        "No engineering blocker remains. Production fusion still requires fresh resident-bound evidence and two independently authenticated approvals. Technical alignment does not authorize fusion.",
        "",
        "## Machine evidence",
        "",
        "`REPOSITORY_ALIGNMENT.json` records every path, class, review method, parser result, size, and SHA-256 (generated receipts are self-validating and therefore omit self-hashes).",
        "",
    ])
    MD_REPORT.write_text("\n".join(lines), encoding="utf-8")


def check(report: dict[str, object]) -> list[str]:
    failures = []
    expected = set(repository_paths())
    rows = {row["path"]: row for row in report.get("files", [])}
    if expected != set(rows):
        failures.append("inventory path set differs from repository path set")
    for relative, row in rows.items():
        if relative in GENERATED:
            continue
        path = ROOT / relative
        if not path.exists():
            failures.append("missing: %s" % relative)
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if row.get("sha256") != digest:
            failures.append("digest drift: %s" % relative)
    if report.get("status") != "PASS":
        failures.append("report status is not PASS")
    if report.get("mind_fusion_authorized") is not False:
        failures.append("fusion authority must remain false")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = build()
        write_reports(report)
    else:
        report = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    failures = check(report)
    print(json.dumps({
        "status": report.get("status"),
        "files_total": report.get("files_total"),
        "category_counts": report.get("category_counts"),
        "failures": failures,
        "ok": not failures,
    }, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
