#!/usr/bin/env python3
"""Check or synchronize the Hermes addon's non-recursive Mantle snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ADDON_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ADDON_ROOT.parents[1]
VENDOR_ROOT = ADDON_ROOT / "vendor" / "mantle-os"
ROOT_FILES = (".gitignore", "CONTRIBUTING.md", "LICENSE", "README.md", "pyproject.toml")
SNAPSHOT_DIRS = (".github/workflows", "documents", "examples", "src/mantle")


def _included_source_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for relative in ROOT_FILES:
        path = REPOSITORY_ROOT / relative
        if path.is_file():
            files[relative] = path
    for relative in SNAPSHOT_DIRS:
        base = REPOSITORY_ROOT / relative
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(REPOSITORY_ROOT)
            if "__pycache__" in rel.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            if rel.parts[:2] == ("examples", "hermes-mantle-addon"):
                continue
            files[str(rel)] = path
    return files


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tracked_vendor_files() -> set[str]:
    prefix = str(VENDOR_ROOT.relative_to(REPOSITORY_ROOT)) + "/"
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--", prefix],
        cwd=REPOSITORY_ROOT, capture_output=True, check=True,
    )
    tracked = set()
    for item in completed.stdout.split(b"\0"):
        path = item.decode("utf-8")
        if path.startswith(prefix):
            tracked.add(path[len(prefix):])
    return tracked


def status() -> dict[str, object]:
    expected = {rel: _digest(path) for rel, path in _included_source_files().items()}
    actual = {
        str(path.relative_to(VENDOR_ROOT)): _digest(path)
        for path in sorted(VENDOR_ROOT.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    } if VENDOR_ROOT.exists() else {}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual)
                     if expected[path] != actual[path])
    tracked = _tracked_vendor_files()
    untracked = sorted(set(actual) - tracked)
    index_missing = sorted(set(expected) - tracked)
    index_extra = sorted(tracked - set(expected))
    source_files = sum(path.startswith("src/mantle/") for path in expected)
    return {
        "snapshot_files": len(expected),
        "vendor_files": len(actual),
        "tracked_files": len(tracked),
        "source_files": source_files,
        "missing": missing,
        "extra": extra,
        "changed": changed,
        "untracked": untracked,
        "index_missing": index_missing,
        "index_extra": index_extra,
        "aligned": not any((missing, extra, changed, untracked,
                            index_missing, index_extra)),
    }


def sync() -> None:
    files = _included_source_files()
    if "src/mantle/__init__.py" not in files:
        raise SystemExit("authoritative Mantle source tree not found")
    shutil.rmtree(VENDOR_ROOT, ignore_errors=True)
    for relative, source in files.items():
        destination = VENDOR_ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    if args.sync:
        sync()
    receipt = status()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["aligned"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
