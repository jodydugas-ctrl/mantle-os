"""v0.10 registry slot, intentionally unavailable until G-03."""
from __future__ import annotations

from typing import Any

from .common import GrimoireEditionError

PROFILE = "grimoire-v0.10"
DOCUMENT_PATH = "documents/grimoire/editions/grimoire-v0.10.md"
SELFTEST_VECTORS: tuple[str, ...] = ()
COMPOSITION_COUNT = 0
STATEMENT_COUNT = 0


def decode_statement(raw: Any, **context: Any) -> dict[str, Any]:
    raise GrimoireEditionError("Grimoire v0.10 decoder is not implemented until G-03")
