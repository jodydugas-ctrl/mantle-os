"""Operator-authorized Grimoire edition adoption for new tissue."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict

from .registry import get_edition


DEFAULT_NEW_TISSUE_PROFILE = "grimoire-v0.10"
PRIOR_PROFILE = "grimoire-v0.9"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adopt_v010(*, body: Any, operator_authorized: bool, commit: str,
               repository_root: str | Path = ".") -> Dict[str, Any]:
    """Record the adoption event; only an explicit operator authorization may call it."""
    if operator_authorized is not True:
        raise PermissionError("Grimoire adoption requires operator authorization")
    root = Path(repository_root)
    edition = get_edition(DEFAULT_NEW_TISSUE_PROFILE)
    source = root / edition.document_path
    runtime = root / "src" / "mantle" / "vcw" / "grimoire_editions" / "v010.py"
    verifier = root / "tools" / "grimoire_tool.py"
    receipt = {
        "kind": "grimoire_edition_adoption",
        "edition": DEFAULT_NEW_TISSUE_PROFILE,
        "source_sha256": _sha256(source),
        "runtime_sha256": _sha256(runtime),
        "independent_verifier_sha256": _sha256(verifier),
        "operator_authorized": True,
        "default_scope": "new-tissue-only",
        "prior_default": PRIOR_PROFILE,
        "legacy_reinterpretation": False,
        "commit": str(commit),
    }
    return body.record_edition_adoption(receipt)


def new_grimoire_params(profile: str = DEFAULT_NEW_TISSUE_PROFILE) -> Dict[str, str]:
    """Return explicit carrier params for a newly created Grimoire band."""
    get_edition(profile)
    return {"profile": profile}
