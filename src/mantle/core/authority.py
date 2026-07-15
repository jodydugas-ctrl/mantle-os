#!/usr/bin/env python3
"""Fusion authorization shared by the Phase-1 Brain socket and Phase-2 MIND.

Stage-1 certification is technical evidence. It never creates operator authority.
A fusion request must carry two explicit, target-bound approvals and an effective
fail-closed decision.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict


class FusionAuthorizationError(PermissionError):
    """A fusion request lacks valid independent operator and guardian approval."""


def validate_fusion_authorization(organism: Any, authorization: Any) -> Dict[str, Any]:
    """Validate and minimize a machine-readable dual-authority fusion decision."""
    if not isinstance(authorization, Mapping):
        raise FusionAuthorizationError(
            "MIND fusion requires explicit operator and guardian approval"
        )

    target = authorization.get("target")
    expected = organism.body.identity_name()
    if not isinstance(target, Mapping) or target.get("resident_identity") != expected:
        raise FusionAuthorizationError(
            "fusion authorization target does not match this resident identity"
        )

    decisions: Dict[str, str] = {}
    for role in ("operator", "guardian"):
        record = authorization.get(role)
        decision = record.get("fusion_decision") if isinstance(record, Mapping) else None
        if decision != "APPROVED":
            raise FusionAuthorizationError(
                "%s fusion decision must be explicitly APPROVED" % role
            )
        decisions[role] = decision

    effective = authorization.get("effective_decision")
    if not isinstance(effective, Mapping) or effective.get("mind_fusion_authorized") is not True:
        raise FusionAuthorizationError(
            "effective fusion decision must explicitly authorize the MIND"
        )

    return {
        "resident_identity": expected,
        "operator": decisions["operator"],
        "guardian": decisions["guardian"],
        "mind_fusion_authorized": True,
    }
