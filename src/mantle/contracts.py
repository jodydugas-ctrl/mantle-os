"""Shared evidence-grounded contracts for Mantle 2 resident integrations.

These types deliberately contain no provider or host-specific behavior.  They are
the small, serialisable boundary between deterministic Body evidence and untrusted
interpretation supplied by a MIND/provider.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


class ClaimStatus(str, Enum):
    OBSERVED = "observed"
    VERIFIED = "verified"
    USER_REPORTED = "user_reported"
    INFERRED = "inferred"
    PROPOSED = "proposed"
    SPECULATIVE = "speculative"
    CONTRADICTED = "contradicted"
    REFUSED = "refused"


@dataclass(frozen=True)
class EvidenceRef:
    kind: str
    stable_id: str
    source: str
    location: Optional[str] = None
    sha256: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass(frozen=True)
class GroundedClaim:
    claim_id: str
    text: str
    status: ClaimStatus
    evidence: Tuple[EvidenceRef, ...] = ()
    limitations: Tuple[str, ...] = ()
    contradictions: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "status": self.status.value,
            "evidence": [e.__dict__ for e in self.evidence],
            "limitations": list(self.limitations),
            "contradictions": list(self.contradictions),
        }


@dataclass(frozen=True)
class GroundedAnswer:
    visible_answer: str
    claims: Tuple[GroundedClaim, ...] = ()
    uncertainty: Tuple[str, ...] = ()
    deterministic_fallback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "visible_answer": self.visible_answer,
            "claims": [c.to_dict() for c in self.claims],
            "uncertainty": list(self.uncertainty),
            "deterministic_fallback": self.deterministic_fallback,
        }


@dataclass(frozen=True)
class ResidentTurnResult:
    route: str
    visible_output: str
    body_requests: Tuple[Dict[str, Any], ...] = ()
    body_proofs: Tuple[Dict[str, Any], ...] = ()
    provider_receipt: Optional[Dict[str, Any]] = None
    vcw_event_ids: Tuple[str, ...] = ()
    answer: Optional[GroundedAnswer] = None


@dataclass(frozen=True)
class CertificationStatus:
    """Historical certification is evidence, never current runtime authority."""

    protocol_version: str
    historical_receipt: Optional[str]
    current_runtime_authority: bool
    stale: bool = False
    reason: Optional[str] = None


class HostAdapter:
    """Small host seam used by ResidentRuntime; safe no-op defaults are intentional."""

    def host_evidence(self) -> Sequence[EvidenceRef]:
        return ()

    def working_surfaces(self) -> Sequence[Dict[str, Any]]:
        return ()

    def body_operations(self) -> Sequence[str]:
        return ()

    def verify(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None


class ResidentRuntime:
    """Canonical command/conversation/heartbeat orchestration boundary.

    The runtime is deliberately provider-agnostic.  Commands are dispatched by the
    Body; conversation can be delegated by an integration, but never bypasses the
    evidence classification helpers below.
    """

    PROTOCOL_VERSION = "mantle-resident-v2"

    def __init__(self, dispatcher: Any = None, host: Optional[HostAdapter] = None):
        self.dispatcher = dispatcher
        self.host = host or HostAdapter()
        self.events: List[Dict[str, Any]] = []

    @staticmethod
    def classify_claim(text: str, status: ClaimStatus,
                       evidence: Sequence[EvidenceRef] = ()) -> GroundedClaim:
        """Enforce the evidence firewall for a single claim."""
        # Verified claims without a stable evidence reference are not acceptable.
        if status == ClaimStatus.VERIFIED and not evidence:
            status = ClaimStatus.REFUSED
            limitations = ("verification requires a stable evidence reference",)
        else:
            limitations = ()
        return GroundedClaim(
            claim_id="claim-" + __import__("hashlib").sha256(text.encode("utf-8")).hexdigest()[:16],
            text=text,
            status=status,
            evidence=tuple(evidence),
            limitations=limitations,
        )

    def deterministic_answer(self, text: str, evidence: Sequence[EvidenceRef] = ()) -> GroundedAnswer:
        claim = self.classify_claim(text, ClaimStatus.OBSERVED, evidence)
        return GroundedAnswer(text, (claim,), deterministic_fallback=text)

    def turn(self, text: str) -> ResidentTurnResult:
        """Route slash commands to Body; ordinary text remains conversation input."""
        if text.startswith("/") and self.dispatcher is not None:
            result = self.dispatcher.dispatch(text)
            output = getattr(result, "output", str(result))
            self.events.append({"stage": "body_command", "command": text.split()[0],
                                "output": output})
            return ResidentTurnResult("body", output, vcw_event_ids=())
        answer = self.deterministic_answer(
            "Conversation turn accepted by the resident Body; provider interpretation is untrusted.")
        self.events.append({"stage": "conversation", "text": text})
        return ResidentTurnResult("mind", answer.visible_answer, answer=answer)

