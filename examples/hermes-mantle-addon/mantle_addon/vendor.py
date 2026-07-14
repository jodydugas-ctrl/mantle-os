"""Origin-checked loader for the bundled Mantle runtime."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
from threading import RLock
from types import ModuleType
from typing import Any


_ALIAS = "_hermes_mantle_vendor"
_PACKAGE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "vendor"
    / "mantle-os"
    / "src"
    / "mantle"
).resolve()
_LOCK = RLock()
_TRUSTED_PACKAGE: ModuleType | None = None
_TRUSTED_MODULES: dict[str, ModuleType] = {}
_TRUSTED_SYMBOLS: dict[tuple[str, str], Any] = {}


class VendorRuntimeError(ImportError):
    """The fixed vendored Mantle runtime cannot be loaded safely."""


def _expected_origin(qualified_name: str) -> Path:
    relative = qualified_name.removeprefix(_ALIAS).lstrip(".")
    base = _PACKAGE_ROOT.joinpath(*relative.split(".")) if relative else _PACKAGE_ROOT
    module_file = base.with_suffix(".py")
    return module_file if module_file.is_file() else base / "__init__.py"


def _has_expected_origin(name: str, module: ModuleType) -> bool:
    origin = getattr(module, "__file__", None)
    spec = getattr(module, "__spec__", None)
    spec_origin = getattr(spec, "origin", None)
    expected = _expected_origin(name).resolve()
    try:
        return (
            isinstance(origin, str)
            and Path(origin).resolve() == expected
            and isinstance(spec_origin, str)
            and Path(spec_origin).resolve() == expected
        )
    except OSError:
        return False


def _purge_untrusted_aliases() -> None:
    prefix = _ALIAS + "."
    for name in list(sys.modules):
        if name == _ALIAS or name.startswith(prefix):
            trusted = _TRUSTED_MODULES.get(name)
            if trusted is None or sys.modules.get(name) is not trusted:
                sys.modules.pop(name, None)
    for name, module in _TRUSTED_MODULES.items():
        sys.modules[name] = module


def _capture_trusted_modules() -> None:
    prefix = _ALIAS + "."
    for name, module in list(sys.modules.items()):
        if name == _ALIAS or name.startswith(prefix):
            if not isinstance(module, ModuleType) or not _has_expected_origin(name, module):
                raise VendorRuntimeError(f"untrusted vendored module origin: {name}")
            _TRUSTED_MODULES[name] = module


def _load_package() -> ModuleType:
    global _TRUSTED_PACKAGE
    with _LOCK:
        _purge_untrusted_aliases()
        if _TRUSTED_PACKAGE is not None:
            sys.modules[_ALIAS] = _TRUSTED_PACKAGE
            return _TRUSTED_PACKAGE
        init_path = _PACKAGE_ROOT / "__init__.py"
        spec = importlib.util.spec_from_file_location(
            _ALIAS,
            init_path,
            submodule_search_locations=[str(_PACKAGE_ROOT)],
        )
        if spec is None or spec.loader is None:
            raise VendorRuntimeError(f"cannot load vendored Mantle package at {init_path}")
        package = importlib.util.module_from_spec(spec)
        sys.modules[_ALIAS] = package
        try:
            spec.loader.exec_module(package)
            if not _has_expected_origin(_ALIAS, package):
                raise VendorRuntimeError("vendored Mantle package origin mismatch")
            _TRUSTED_PACKAGE = package
            _capture_trusted_modules()
        except Exception:
            sys.modules.pop(_ALIAS, None)
            _TRUSTED_PACKAGE = None
            _TRUSTED_MODULES.clear()
            raise
        return package


def vendored_symbol(module: str, symbol: str) -> Any:
    """Resolve a symbol only from origin-checked private vendored modules."""
    if not module or module.startswith(".") or ".." in module.split("."):
        raise VendorRuntimeError("invalid vendored module name")
    key = (module, symbol)
    with _LOCK:
        _load_package()
        cached = _TRUSTED_SYMBOLS.get(key)
        if cached is not None:
            return cached
        _purge_untrusted_aliases()
        qualified = f"{_ALIAS}.{module}"
        loaded = importlib.import_module(qualified)
        if not _has_expected_origin(qualified, loaded):
            sys.modules.pop(qualified, None)
            raise VendorRuntimeError(f"vendored Mantle module origin mismatch: {module}")
        _capture_trusted_modules()
        try:
            value = getattr(loaded, symbol)
        except AttributeError as exc:
            raise VendorRuntimeError(
                f"vendored Mantle symbol {module}.{symbol} is unavailable"
            ) from exc
        _TRUSTED_SYMBOLS[key] = value
        return value
