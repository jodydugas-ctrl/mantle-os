from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mantle_addon.config import ConfigError, ResidentConfig
from mantle_addon.primer import build_primer


class ResidentConfigTests(unittest.TestCase):
    def test_defaults_are_body_first_and_observer_only(self):
        config = ResidentConfig.from_mapping({})

        self.assertTrue(config.body_enabled)
        self.assertFalse(config.mind_enabled)
        self.assertIsNone(config.storage_root)
        self.assertEqual("none", config.dnr)
        self.assertFalse(config.record_raw_prompts)
        self.assertFalse(config.record_raw_tool_args)
        self.assertEqual(4096, config.max_event_chars)
        self.assertTrue(config.checkpoint_each_turn)

    def test_config_is_immutable_and_rejects_unknown_fields(self):
        config = ResidentConfig.from_mapping({})

        with self.assertRaises(FrozenInstanceError):
            setattr(config, "body_enabled", False)
        with self.assertRaisesRegex(ConfigError, "unknown configuration field"):
            ResidentConfig.from_mapping({"surprise": True})

    def test_direct_constructor_cannot_bypass_phase1_gates(self):
        with self.assertRaisesRegex(ConfigError, "MIND fusion"):
            ResidentConfig(mind_enabled=True)
        with self.assertRaisesRegex(ConfigError, "raw payload retention"):
            ResidentConfig(record_raw_prompts=True)

    def test_config_validates_types_ranges_and_dnr(self):
        invalid = [
            {"body_enabled": "yes"},
            {"max_event_chars": 0},
            {"max_event_chars": 1_000_001},
            {"dnr": "rebuild_anyway"},
            {"storage_root": 123},
        ]

        for mapping in invalid:
            with self.subTest(mapping=mapping):
                with self.assertRaises(ConfigError):
                    ResidentConfig.from_mapping(mapping)

    def test_mind_requires_fresh_stage1_and_separate_fusion_authority(self):
        with self.assertRaisesRegex(ConfigError, "Stage-1 PASS"):
            ResidentConfig.from_mapping({"mind_enabled": True})
        with self.assertRaisesRegex(ConfigError, "fusion authorization"):
            ResidentConfig.from_mapping(
                {"mind_enabled": True}, stage1_passed=True
            )

        with self.assertRaisesRegex(ConfigError, "fusion is not implemented"):
            ResidentConfig.from_mapping(
                {"mind_enabled": True},
                stage1_passed=True,
                fusion_authorized=True,
            )

    def test_raw_payload_retention_flags_are_present_but_not_authorized(self):
        for field in ("record_raw_prompts", "record_raw_tool_args"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ConfigError, "raw payload retention"):
                    ResidentConfig.from_mapping({field: True})

    def test_defaults_file_matches_runtime_defaults(self):
        defaults = json.loads(
            (PROJECT_ROOT / "config" / "defaults.json").read_text(encoding="utf-8")
        )
        self.assertEqual(defaults, ResidentConfig.from_mapping({}).to_dict())


class PrimerTests(unittest.TestCase):
    def test_primer_declares_residency_and_all_nine_organs_with_brain_dormant(self):
        primer = build_primer(ResidentConfig.from_mapping({}))

        self.assertEqual("Hermes.Mantle.AppAI", primer.identity["name"])
        self.assertEqual("hospitari", primer.identity["residency_mode"])
        self.assertEqual("dormant", primer.identity["mind_state"])
        self.assertEqual(
            {
                "heart",
                "genome",
                "nervous",
                "senses",
                "immune",
                "limbs",
                "memory",
                "brain",
                "reproduction",
            },
            set(primer.identity["organs"]),
        )
        self.assertIn("Body before MIND", primer.commandments)
        self.assertTrue(any("Action Execution Proof" in item for item in primer.commandments))
        self.assertTrue(any("Hermes approvals" in item for item in primer.truths))

    def test_primer_output_is_deterministic_and_contains_no_runtime_secret(self):
        config = ResidentConfig.from_mapping({"dnr": "no_reconstruction"})

        first = build_primer(config).to_dict()
        second = build_primer(config).to_dict()

        self.assertEqual(first, second)
        serialized = json.dumps(first, sort_keys=True).lower()
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("genesis_key", serialized)
        self.assertEqual("no_reconstruction", first["identity"]["dnr"])


if __name__ == "__main__":
    unittest.main()
