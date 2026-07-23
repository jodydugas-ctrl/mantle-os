#!/usr/bin/env python3
"""
mantle.assimilator.substrate  --  Phase-0 host substrate discovery

Code-agnostic assimilation starts by identifying what the host is made of. The
scanner may then use a parser, generate a local adapter, or explicitly report
that coverage is incomplete. Silent undercounting is not a valid Phase-0 result.
"""
from __future__ import annotations

import os
from typing import Any, Dict


NATIVE_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".m", ".mm"}
QT_EXTS = {".ui", ".qrc"}
PY_EXTS = {".py"}
TREE_SITTER_EXTS = {".js", ".mjs", ".go", ".rs"}
BUILD_FILES = {"cmakelists.txt", "makefile", "meson.build", "build.gradle",
               "package.json", "pyproject.toml", "cargo.toml", "go.mod"}


def discover(root: str) -> Dict[str, Any]:
    """Return a read-only substrate census for a host tree."""
    counts: Dict[str, int] = {}
    build_files = []
    first_party_files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "node_modules", ".venv",
                                    "venv", "dist", "build", ".pytest_cache")]
        for filename in filenames:
            first_party_files += 1
            lower = filename.lower()
            ext = os.path.splitext(filename)[1].lower()
            if lower in BUILD_FILES:
                rel = os.path.relpath(os.path.join(dirpath, filename), root)
                build_files.append(rel.replace(os.sep, "/"))
            counts[ext or "<none>"] = counts.get(ext or "<none>", 0) + 1

    native_count = sum(counts.get(ext, 0) for ext in NATIVE_EXTS)
    qt_count = sum(counts.get(ext, 0) for ext in QT_EXTS)
    tree_sitter_count = sum(counts.get(ext, 0) for ext in TREE_SITTER_EXTS)
    python_count = sum(counts.get(ext, 0) for ext in PY_EXTS)
    cmake = any(os.path.basename(path).lower() == "cmakelists.txt" for path in build_files)

    languages = []
    if python_count:
        languages.append("python")
    if tree_sitter_count:
        languages.append("tree-sitter-optional")
    if native_count:
        languages.append("native-c-family")
    if qt_count:
        languages.append("qt-resource-ui")
    if cmake:
        languages.append("cmake")

    unsupported = []
    if native_count:
        unsupported.append({
            "substrate": "native-c-family",
            "files": native_count,
            "reason": "requires native parser/adapter before signed organ insertion",
        })
    if qt_count:
        unsupported.append({
            "substrate": "qt-resource-ui",
            "files": qt_count,
            "reason": "requires Qt UI/resource graph extraction before signed organ insertion",
        })

    return {
        "root": os.path.abspath(root),
        "files": first_party_files,
        "extension_counts": dict(sorted(counts.items())),
        "build_files": sorted(build_files),
        "languages": languages or ["unknown"],
        "python_files": python_count,
        "tree_sitter_candidate_files": tree_sitter_count,
        "native_candidate_files": native_count,
        "qt_candidate_files": qt_count,
        "coverage": {
            "python_ast": python_count,
            "tree_sitter_optional": tree_sitter_count,
            "requires_adaptive_native_tools": native_count + qt_count,
        },
        "unsupported": unsupported,
        "read_only": True,
    }
