import json
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
READINESS_JSON = PROJECT_ROOT / "docs" / "MIND_READINESS.json"
READINESS_MD = PROJECT_ROOT / "docs" / "MIND_READINESS.md"
DECISIONS_JSON = PROJECT_ROOT / "docs" / "FUSION_DECISIONS.json"
README = PROJECT_ROOT / "README.md"
STAGE1_GATE = PROJECT_ROOT / "mantle_addon" / "stage1_gate.py"


class MindReadinessTests(unittest.TestCase):
    def setUp(self):
        self.readiness = json.loads(READINESS_JSON.read_text(encoding="utf-8"))
        self.decisions = json.loads(DECISIONS_JSON.read_text(encoding="utf-8"))

    def test_verdict_fails_closed(self):
        self.assertEqual("NOT_READY", self.readiness["verdict"])
        self.assertFalse(self.readiness["mind_fusion_authorized"])
        self.assertFalse(self.readiness["reproduction_activation_authorized"])
        self.assertEqual("DEFERRED", self.readiness["evidence"]["operator_fusion_decision"])
        self.assertEqual("DEFERRED", self.readiness["evidence"]["guardian_fusion_decision"])

    def test_complete_gate_evidence_is_exact(self):
        evidence = self.readiness["evidence"]
        addon = evidence["addon_stage1"]
        framework = evidence["framework_stage1"]
        self.assertEqual((14, 14), (addon["passed_rows"], addon["total_rows"]))
        self.assertTrue(addon["passed"])
        self.assertEqual(20, framework["gate_rows"])
        self.assertEqual(111, framework["security_invariants_passed"])
        self.assertEqual(111, framework["security_invariants_total"])
        self.assertTrue(framework["passed"])
        self.assertIsNone(framework["failed_invariant"])
        self.assertEqual(96, evidence["addon_unit_tests"])
        self.assertIn("_hermes_mantle_vendor", framework["root_cause"])

    def test_five_remaining_blockers_and_three_resolutions_are_machine_readable(self):
        blockers = self.readiness["blocking_requirements"]
        self.assertEqual([f"B-{i:02d}" for i in range(3, 8)], [b["id"] for b in blockers])
        self.assertEqual(
            ["B-01", "B-02", "B-08"],
            [row["id"] for row in self.readiness["resolved_requirements"]],
        )
        self.assertTrue(all(blocker["required_resolution"] for blocker in blockers))
        hard = [blocker for blocker in blockers if blocker["severity"] == "HARD"]
        self.assertEqual(5, len(hard))

    def test_decision_authority_and_next_step_match_report(self):
        effective = self.decisions["effective_decision"]
        self.assertFalse(effective["mind_fusion_authorized"])
        self.assertIsNone(effective["next_permitted_roadmap_step"])
        self.assertIsNone(self.readiness["next_action"]["roadmap_step"])
        for role in ("operator", "guardian"):
            self.assertEqual("DEFERRED", self.decisions[role]["fusion_decision"])

    def test_human_surfaces_do_not_promote_readiness_into_authority(self):
        report = READINESS_MD.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        stage1 = STAGE1_GATE.read_text(encoding="utf-8")
        self.assertIn("**Verdict:** **NOT READY**", report)
        self.assertIn("five blockers remain", readme)
        self.assertIn("eligible for separate Phase-2 readiness and authorization", stage1)
        self.assertNotIn("STAGE-1 PASSED — Phase 2 authorized", stage1)
        self.assertNotIn("MIND fusion APPROVED", report)
        self.assertNotIn("MIND fusion APPROVED", readme)


if __name__ == "__main__":
    unittest.main()
