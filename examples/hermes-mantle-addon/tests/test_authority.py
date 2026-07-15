"""Authentication boundary for operator and guardian fusion approval."""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mantle_addon.authority import (
    AuthorityError,
    HmacAuthorityProvider,
    _canonical_payload,
)


class AuthorityProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.operator_key = b"o" * 32
        self.guardian_key = b"g" * 32
        self.provider = HmacAuthorityProvider(
            operator_key_id="operator-2026",
            operator_key=self.operator_key,
            guardian_key_id="guardian-2026",
            guardian_key=self.guardian_key,
        )
        self.authorization = {
            "recorded_at": "2026-07-15T12:00:00+00:00",
            "target": {
                "resident_identity": "resident",
                "body_fingerprint": "fingerprint",
            },
            "operator": {
                "fusion_decision": "APPROVED",
                "key_id": "operator-2026",
            },
            "guardian": {
                "fusion_decision": "APPROVED",
                "key_id": "guardian-2026",
            },
            "effective_decision": {
                "mind_fusion_authorized": True,
                "reproduction_activation_authorized": False,
            },
        }
        for role, key in (
            ("operator", self.operator_key),
            ("guardian", self.guardian_key),
        ):
            key_id = self.authorization[role]["key_id"]
            self.authorization[role]["signature"] = hmac.new(
                key,
                _canonical_payload(role, self.authorization, key_id),
                hashlib.sha256,
            ).hexdigest()

    def test_valid_independent_approvals_reduce_to_core_receipt(self):
        receipt = self.provider.verify(self.authorization)
        self.assertEqual("APPROVED", receipt["operator"]["fusion_decision"])
        self.assertEqual("APPROVED", receipt["guardian"]["fusion_decision"])
        self.assertNotIn("signature", str(receipt))

    def test_caller_authored_or_tampered_mapping_is_refused(self):
        self.authorization["target"]["resident_identity"] = "other"
        with self.assertRaisesRegex(AuthorityError, "signature is invalid"):
            self.provider.verify(self.authorization)

    def test_roles_must_use_distinct_credentials(self):
        with self.assertRaisesRegex(ValueError, "independent"):
            HmacAuthorityProvider(
                operator_key_id="operator",
                operator_key=b"x" * 32,
                guardian_key_id="guardian",
                guardian_key=b"x" * 32,
            )

    def test_missing_environment_is_dormant_not_authorized(self):
        self.assertIsNone(HmacAuthorityProvider.from_environment({}))


if __name__ == "__main__":
    unittest.main()
