#!/usr/bin/env python3
"""
redact.py  --  The secret boundary (Mantle v2.3)

A deterministic, LLM-free redactor applied at the sense/immune logging boundary so that
secrets NEVER land in the VCW (Audit B-20 / HF-B20: "Secrets never appear in senses/immune
logs"). The cube is append-only and inspectable as images -- a leaked secret there is
permanent and visible. So redaction happens once, at the boundary, before any append.

It is intentionally conservative (mask on suspicion): a false positive only obscures a log
line, while a false negative permanently burns a secret into memory. Patterns cover the
common shapes -- bearer/API tokens, key=value secrets, AWS keys, JWTs, private-key blocks,
and long high-entropy hex/base64 runs.
"""
from __future__ import annotations

import re
from typing import Any

MASK = "[REDACTED]"

# Ordered (pattern, replacement) rules applied to every string crossing the boundary.
_RULES = [
    # PEM private-key blocks
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
                re.DOTALL), MASK),
    # Bearer tokens
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{8,}"), "Bearer " + MASK),
    # secret-ish key = "value" / key: value  (api_key, apikey, token, password, secret, auth)
    (re.compile(r"(?i)\b([\w-]*(?:api[_-]?key|secret|token|password|passwd|auth|access[_-]?key)"
                r"[\w-]*)\b\s*[:=]\s*[\"']?([^\s\"',;}]{4,})[\"']?"), r"\1=" + MASK),
    # OpenAI-style keys (sk-...) and AWS access key ids (AKIA...)
    (re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"), MASK),
    (re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{12,}\b"), MASK),
    # JWTs: three base64url segments
    (re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b"), MASK),
    # long high-entropy hex / base64 runs (e.g. raw key material)
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), MASK),
    (re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b"), MASK),
]


def redact_str(s: str) -> str:
    for pat, repl in _RULES:
        s = pat.sub(repl, s)
    return s


def redact(obj: Any) -> Any:
    """Return a redacted deep copy of obj. Strings are scrubbed; dict/list are walked.
    Dict keys whose NAME looks secret have their whole value masked, regardless of shape."""
    if isinstance(obj, str):
        return redact_str(obj)
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if re.search(r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key|"
                         r"access[_-]?key|auth)", str(k)):
                out[k] = MASK
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, (list, tuple)):
        return type(obj)(redact(v) for v in obj)
    return obj


def contains_secret(obj: Any) -> bool:
    """True if redact(obj) would change anything -- i.e. obj still carries a recognizable
    secret. Used by the audit harness and tests to prove the boundary holds."""
    return redact(obj) != obj
