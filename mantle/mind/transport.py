#!/usr/bin/env python3
"""
mantle.mind.transport  --  pluggable model transports (Argonaut, of the Mantle lineage)

THE MODEL IS A PLUGGABLE TRANSPORT -- THERE IS NO VENDOR CODE IN THE BODY. The MIND talks
to its model through a single callable `model(prompt) -> text`. The offline deterministic
`stub_mind` is the default: the demo and the Stage-2 audit need no network and no key.
`openai_compatible_model(...)` (pure stdlib urllib, built lazily) reaches ANY
OpenAI-compatible endpoint -- OpenRouter is the reference gateway, a local llama.cpp/vLLM
server works identically. You change providers by changing a STRING, never Body code.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Optional

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def stub_mind(prompt: str) -> str:
    """An offline, deterministic stand-in MODEL so demos + the Stage-2 audit need no key
    or network. Mirrors the rest of the framework's 'no network, no LLM' ethos."""
    return ("[offline MIND] The assembled context reads as coherent; I note it and propose "
            "no Body change. (%d chars of context considered.)" % len(prompt))


def load_keyfile(path: str) -> str:
    """Read the single model credential from a keyfile (Phase 2 only). The value is a
    secret boundary: it is redacted everywhere it could surface in senses/immune logs."""
    with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
        return f.read().strip()


def openai_compatible_model(api_key: str, model: str, *, url: str = OPENROUTER_URL,
                            system: Optional[str] = None, max_tokens: int = 1024,
                            timeout: int = 60,
                            extra_headers: Optional[Dict[str, str]] = None
                            ) -> Callable[[str], str]:
    """Return a `model(prompt) -> text` callable for ANY OpenAI-compatible chat endpoint.
    Pure standard library (urllib), imported lazily: importing this module never requires
    a network or a key. No vendor SDK, ever."""
    import urllib.request  # local import: only touched when a real model is wired

    def _call(prompt: str) -> str:
        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({"model": model, "messages": messages,
                              "max_tokens": max_tokens}).encode("utf-8")
        headers = {"Authorization": "Bearer %s" % api_key,
                   "Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    return _call


def openrouter_model(api_key: str, model: str, **kwargs: Any) -> Callable[[str], str]:
    """The reference transport: OpenAI-compatible, pointed at OpenRouter. `model` is a
    provider-neutral id string; provider choice is one string, the Body is identical."""
    kwargs.setdefault("url", OPENROUTER_URL)
    return openai_compatible_model(api_key, model, **kwargs)
