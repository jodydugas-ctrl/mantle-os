"""Target-bound lifecycle authorization and journal primitives.

The primitives are intentionally independent of hatch/graft storage so callers can
validate an authorization before creating a target directory.  SELF-vault recovery
can bypass this external activation gate; external artifacts cannot.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import json
import os
import secrets
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional


class LifecycleAction(str, Enum):
    HATCH = "hatch"
    GRAFT = "graft"


class LifecycleResult(str, Enum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    REFUSED = "refused"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class LifecycleAuthorization:
    schema_version: str
    action: LifecycleAction
    artifact_sha256: str
    target_id: str
    operator_approved: bool
    issued_at: str
    expires_at: str
    nonce: str

    @classmethod
    def issue(cls, action: LifecycleAction, artifact: str, target_id: str,
              *, expires_at: Optional[str] = None) -> "LifecycleAuthorization":
        digest = hashlib.sha256(open(artifact, "rb").read()).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        default_expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        return cls("mantle-lifecycle-authorization-v1", action, digest, str(target_id),
                   True, now, expires_at or default_expiry, secrets.token_hex(16))

    def redacted(self) -> Dict[str, Any]:
        data = asdict(self)
        data["action"] = self.action.value
        data["target_id"] = hashlib.sha256(self.target_id.encode("utf-8")).hexdigest()[:16]
        return data


class LifecycleAuthorizationError(PermissionError):
    pass


def validate_authorization(auth: LifecycleAuthorization, action: LifecycleAction,
                           artifact: str, target_id: str,
                           *, used_nonces: Optional[set] = None) -> None:
    """Fail closed before target creation for missing, stale, replayed or mismatched auth."""
    if auth.schema_version != "mantle-lifecycle-authorization-v1":
        raise LifecycleAuthorizationError("unsupported lifecycle authorization schema")
    if auth.action != action or not auth.operator_approved:
        raise LifecycleAuthorizationError("operator authorization does not approve this action")
    digest = hashlib.sha256(open(artifact, "rb").read()).hexdigest()
    if digest != auth.artifact_sha256:
        raise LifecycleAuthorizationError("artifact fingerprint does not match authorization")
    if str(target_id) != auth.target_id:
        raise LifecycleAuthorizationError("resolved target does not match authorization")
    if used_nonces is not None and auth.nonce in used_nonces:
        raise LifecycleAuthorizationError("authorization nonce has already been used")
    try:
        expires = datetime.fromisoformat(auth.expires_at.replace("Z", "+00:00"))
        if expires < datetime.now(timezone.utc):
            raise LifecycleAuthorizationError("lifecycle authorization has expired")
    except ValueError:
        raise LifecycleAuthorizationError("authorization expiry is invalid")


def authorization_from_dict(data: Dict[str, Any]) -> LifecycleAuthorization:
    try:
        return LifecycleAuthorization(
            schema_version=str(data["schema_version"]),
            action=LifecycleAction(str(data["action"])),
            artifact_sha256=str(data["artifact_sha256"]),
            target_id=str(data["target_id"]),
            operator_approved=bool(data["operator_approved"]),
            issued_at=str(data["issued_at"]),
            expires_at=str(data["expires_at"]),
            nonce=str(data["nonce"]),
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise LifecycleAuthorizationError("malformed lifecycle authorization") from exc


@dataclass
class LifecycleJournal:
    path: str
    action: LifecycleAction
    target_id: str
    result: LifecycleResult = LifecycleResult.INTERRUPTED
    phase: str = "created"

    def write(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        payload = {"schema": "mantle-lifecycle-journal-v1", **asdict(self)}
        payload["action"] = self.action.value
        payload["result"] = self.result.value
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
