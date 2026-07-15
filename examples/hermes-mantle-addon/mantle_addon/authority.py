"""Authenticated, target-bound dual authority for MIND fusion."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import hmac
import json
import os
from typing import Any


class AuthorityError(PermissionError):
    """Fusion authority is absent, malformed, stale, or unauthenticated."""


def _canonical_payload(
    role: str,
    authorization: Mapping[str, Any],
    key_id: str,
) -> bytes:
    payload = {
        "schema_version": "mantle-fusion-approval-v1",
        "role": role,
        "key_id": key_id,
        "fusion_decision": "APPROVED",
        "recorded_at": authorization.get("recorded_at"),
        "target": authorization.get("target"),
        "mind_fusion_authorized": True,
        "reproduction_activation_authorized": False,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class HmacAuthorityProvider:
    """Verify separate operator and guardian approvals without signing them."""

    def __init__(
        self,
        *,
        operator_key_id: str,
        operator_key: bytes,
        guardian_key_id: str,
        guardian_key: bytes,
    ) -> None:
        if not operator_key_id or not guardian_key_id:
            raise ValueError("authority key ids must be non-empty")
        if operator_key_id == guardian_key_id:
            raise ValueError("operator and guardian key ids must be distinct")
        if len(operator_key) < 32 or len(guardian_key) < 32:
            raise ValueError("authority keys must contain at least 32 bytes")
        if hmac.compare_digest(operator_key, guardian_key):
            raise ValueError("operator and guardian keys must be independent")
        self._keys = {
            "operator": (operator_key_id, bytes(operator_key)),
            "guardian": (guardian_key_id, bytes(guardian_key)),
        }

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> "HmacAuthorityProvider | None":
        """Load authority credentials only from secret environment variables."""
        env = environment or os.environ
        values = {
            "operator_key_id": env.get("MANTLE_OPERATOR_KEY_ID", ""),
            "operator_key": env.get("MANTLE_OPERATOR_APPROVAL_KEY", "").encode(),
            "guardian_key_id": env.get("MANTLE_GUARDIAN_KEY_ID", ""),
            "guardian_key": env.get("MANTLE_GUARDIAN_APPROVAL_KEY", "").encode(),
        }
        if not any(values.values()):
            return None
        try:
            return cls(**values)
        except ValueError as exc:
            raise AuthorityError("fusion authority credentials are invalid") from exc

    def verify(self, authorization: Mapping[str, Any]) -> dict[str, Any]:
        """Authenticate both approvals and return a minimized core receipt."""
        if not isinstance(authorization, Mapping):
            raise AuthorityError("fusion authorization must be a mapping")
        target = authorization.get("target")
        effective = authorization.get("effective_decision")
        if not isinstance(target, Mapping) or not isinstance(effective, Mapping):
            raise AuthorityError("fusion authorization is incomplete")
        if (
            effective.get("mind_fusion_authorized") is not True
            or effective.get("reproduction_activation_authorized") is not False
        ):
            raise AuthorityError("fusion authorization has unsafe effective scope")

        for role, (expected_key_id, secret) in self._keys.items():
            record = authorization.get(role)
            if not isinstance(record, Mapping):
                raise AuthorityError(f"{role} approval is missing")
            key_id = record.get("key_id")
            signature = record.get("signature")
            if key_id != expected_key_id or not isinstance(signature, str):
                raise AuthorityError(f"{role} approval key is not trusted")
            expected = hmac.new(
                secret,
                _canonical_payload(role, authorization, expected_key_id),
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise AuthorityError(f"{role} approval signature is invalid")

        return {
            "recorded_at": authorization.get("recorded_at"),
            "target": dict(target),
            "operator": {"fusion_decision": "APPROVED"},
            "guardian": {"fusion_decision": "APPROVED"},
            "effective_decision": {
                "mind_fusion_authorized": True,
                "reproduction_activation_authorized": False,
            },
        }
