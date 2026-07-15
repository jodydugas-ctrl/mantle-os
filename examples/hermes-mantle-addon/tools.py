"""Mantle OS tool handlers for the Hermes plugin."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .mantle_addon.runtime import ResidentRuntime


_PLUGIN_ROOT = Path(__file__).resolve().parent
_MANTLE_PACKAGE = _PLUGIN_ROOT / "vendor" / "mantle-os" / "src" / "mantle"


def _literal_assignment(path: Path, name: str) -> Any:
    """Read one literal module assignment without importing global package state."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f"vendored Mantle metadata {name!r} is missing from {path.name}")


def _load_mantle_metadata() -> tuple[str, list[str]]:
    """Read metadata from the fixed vendored source without importing ``mantle``."""
    version = _literal_assignment(_MANTLE_PACKAGE / "__init__.py", "__version__")
    aliases = _literal_assignment(_MANTLE_PACKAGE / "cli.py", "_COMMAND_ALIASES")
    if not isinstance(version, str):
        raise RuntimeError("vendored Mantle __version__ must be a string")
    if not isinstance(aliases, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in aliases.items()
    ):
        raise RuntimeError("vendored Mantle command registry must map strings to strings")
    return version, sorted(set(aliases.values()))


def mantle_status(args: dict, **kwargs) -> str:
    """Report the bundled Mantle version and supported command surface."""
    del args, kwargs
    try:
        version, commands = _load_mantle_metadata()
        return json.dumps(
            {
                "success": True,
                "mantle_version": version,
                "mantle_scope": "true",
                "source": "vendored",
                "commands": commands,
            }
        )
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


def mantle_record_discovery(
    args: dict[str, Any],
    *,
    runtime: "ResidentRuntime" | None = None,
    runtime_provider: Callable[[], "ResidentRuntime"] | None = None,
    **kwargs: Any,
) -> str:
    """Persist one unverified idea through the resident's Limbs control."""
    del kwargs
    idea = args.get("idea") if isinstance(args, dict) else None
    try:
        if runtime is None:
            if runtime_provider is None:
                raise RuntimeError("resident runtime provider is unavailable")
            runtime = runtime_provider()
        outcome = runtime.record_discovery(idea)
        proof = outcome["proof"]
        success = bool(proof.get("ok")) and bool(outcome["durable"])
        return json.dumps(
            {
                "success": success,
                "control": proof.get("control"),
                "attempted": bool(proof.get("attempted")),
                "durable": bool(outcome["durable"]),
                "reason": proof.get("reason"),
                "classification": "inferred",
                "verified": False,
            }
        )
    except Exception as exc:
        return json.dumps(
            {
                "success": False,
                "attempted": False,
                "durable": False,
                "error": type(exc).__name__,
            }
        )
