import json
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DECISION_JSON = PROJECT_ROOT / "docs" / "FUSION_DECISIONS.json"
DECISION_MD = PROJECT_ROOT / "docs" / "FUSION_DECISIONS.md"
README = PROJECT_ROOT / "README.md"


class FusionDecisionTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(DECISION_JSON.read_text(encoding="utf-8"))

    def test_machine_record_defers_both_fusion_decisions(self):
        self.assertEqual("1.0", self.record["schema_version"])
        self.assertEqual("0.4.0", self.record["target"]["version"])
        self.assertEqual(
            list(range(1, 11)),
            self.record["evidence_basis"]["completed_roadmap_steps"],
        )
        for role in ("operator", "guardian"):
            with self.subTest(role=role):
                self.assertEqual(
                    "APPROVED", self.record[role]["runtime_decision"]
                )
                self.assertEqual(
                    "DEFERRED", self.record[role]["fusion_decision"]
                )

    def test_effective_gate_fails_closed(self):
        effective = self.record["effective_decision"]
        self.assertTrue(effective["current_runtime_authorized"])
        self.assertFalse(effective["mind_fusion_authorized"])
        self.assertFalse(effective["reproduction_activation_authorized"])
        self.assertIsNone(effective["next_permitted_roadmap_step"])
        self.assertIn("separate explicit", effective["fusion_rule"])
        self.assertIn("Silence", effective["fusion_rule"])

    def test_open_evidence_prevents_premature_approval(self):
        evidence = self.record["evidence_basis"]
        self.assertEqual(96, evidence["addon_unit_tests"])
        self.assertEqual(18, evidence["fast_addon_stage1_tests"])
        self.assertEqual(11, evidence["containment_rows"])
        self.assertFalse(
            any(
                self.record[role]["fusion_decision"] == "APPROVED"
                for role in ("operator", "guardian")
            )
        )
        open_gates = " ".join(evidence["known_open_gates"]).lower()
        self.assertIn("not_ready", open_gates)
        self.assertIn("111 of 111", open_gates)
        self.assertIn("fail-closed phase-2 configuration transition exists", open_gates)
        self.assertIn("no addon fusion lifecycle", open_gates)

    def test_human_and_readme_surfaces_match_machine_authority(self):
        decision_text = DECISION_MD.read_text(encoding="utf-8")
        readme_text = README.read_text(encoding="utf-8")

        self.assertIn("MIND fusion | **DEFERRED — NOT AUTHORIZED**", decision_text)
        self.assertIn("readiness PASS", decision_text)
        self.assertIn(
            "both fusion decisions DEFERRED",
            readme_text,
        )
        self.assertIn("MIND fusion DEFERRED", readme_text)
        self.assertNotIn("MIND fusion APPROVED", decision_text)
        self.assertNotIn("MIND fusion APPROVED", readme_text)


if __name__ == "__main__":
    unittest.main()
