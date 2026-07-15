"""Hermes LLM provider transport for the Mantle MIND.

The framework's MIND fusion needs a single callable: `model(prompt) -> text`.
This module builds that callable from Hermes's provider configuration, so the
fused MIND thinks via whichever model Hermes is configured to use.

The transport is provider-agnostic: it reads the OpenAI-compatible endpoint
URL, API key, and model name from the addon config (which Hermes populates
from its own provider settings). No Hermes SDK imports, no vendor lock-in.

Usage (Phase 2 only — after Stage-1 certification):

    from mantle_addon.transport import build_model
    from mantle.mind import fuse

    model = build_model(config)
    mind = fuse(organism, model, max_thoughts=64)

The returned callable carries sidecar attributes for receipt tracking:
    model.last_usage       — normalized usage dict (or None)
    model.last_error       — last exception type (or None)
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any, Callable, Dict, List, Optional

from .config import ResidentConfig


def build_model(
    config: ResidentConfig,
    *,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    url: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = 1024,
    timeout: int = 60,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Callable[[str], str]:
    """Build a `model(prompt) -> text` callable from provider config.

    Args:
        config: The resident configuration (must have mind_enabled=True).
        api_key: API key for the LLM provider. If None, read from the
                 HERMES_MANTLE_API_KEY env var.
        model_name: The model identifier string. If None, read from
                    HERMES_MANTLE_MODEL env var.
        url: The OpenAI-compatible chat completions endpoint. If None,
             read from HERMES_MANTLE_URL env var, defaulting to OpenRouter.
        system: Optional system prompt prepended to every request.
        max_tokens: Max response tokens per call.
        timeout: HTTP timeout in seconds.
        extra_headers: Additional headers merged into every request.

    Returns:
        A callable `model(prompt: str) -> str` with sidecar attributes:
        - last_usage: normalized usage dict or None
        - last_error: last exception type name or None

    Raises:
        ConfigError: if config.mind_enabled is False (Phase-1 guard).
        ValueError: if no API key or model name is available.
    """
    if not config.mind_enabled:
        from .config import ConfigError
        raise ConfigError("MIND fusion is not enabled in the resident config")

    key = api_key or os.environ.get("HERMES_MANTLE_API_KEY")
    model = model_name or os.environ.get("HERMES_MANTLE_MODEL")
    endpoint = url or os.environ.get(
        "HERMES_MANTLE_URL",
        "https://openrouter.ai/api/v1/chat/completions",
    )

    if not key:
        raise ValueError(
            "no API key: set HERMES_MANTLE_API_KEY or pass api_key="
        )
    if not model:
        raise ValueError(
            "no model name: set HERMES_MANTLE_MODEL or pass model_name="
        )

    def _call(prompt: str) -> str:
        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }).encode("utf-8")

        headers: Dict[str, str] = {
            "Authorization": "Bearer %s" % key,
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)

        req = urllib.request.Request(
            endpoint, data=payload, headers=headers, method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            _call.last_usage = _normalize_usage(data)
            _call.last_error = None
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            _call.last_error = type(exc).__name__
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            raise ConnectionError(
                "LLM provider returned HTTP %d: %s" % (exc.code, body)
            ) from exc
        except Exception as exc:
            _call.last_error = type(exc).__name__
            raise

    _call.last_usage = None
    _call.last_error = None
    return _call


def _normalize_usage(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract normalized usage fields from an OpenAI-compatible response."""
    usage = data.get("usage", {}) or {}
    return {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "model": data.get("model", ""),
        "id": data.get("id", ""),
    }


def stub_model(prompt: str) -> str:
    """Offline deterministic stand-in for tests and demos.

    Mirrors the framework's stub_mind: no network, no key, deterministic.
    Use this when mind_enabled=True but no real provider is configured.
    """
    return (
        "[offline Hermes transport] Context considered (%d chars); "
        "no Body change proposed." % len(prompt)
    )
