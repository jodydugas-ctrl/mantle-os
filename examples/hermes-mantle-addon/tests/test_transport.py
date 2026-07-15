"""Tests for the Hermes LLM provider transport (mantle_addon.transport)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mantle_addon.config import ResidentConfig, ConfigError
from mantle_addon.transport import build_model, stub_model, _normalize_usage


class StubModelTests(unittest.TestCase):
    def test_stub_returns_deterministic_response(self):
        """The stub model should return a deterministic, offline response."""
        result1 = stub_model("hello world")
        result2 = stub_model("hello world")
        self.assertEqual(result1, result2)
        self.assertIn("offline", result1.lower())
        self.assertIn("11", result1)  # len("hello world")

    def test_stub_never_touches_network(self):
        """The stub model should not require any network or key."""
        result = stub_model("test prompt")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TransportBoundaryTests(unittest.TestCase):
    def test_bespoke_transport_is_unreachable_from_valid_phase1_config(self):
        """B-05 remains blocked until transport uses Hermes's profile-aware LLM facade."""
        config = ResidentConfig.from_mapping({})
        with self.assertRaisesRegex(ConfigError, "MIND fusion is not enabled"):
            build_model(
                config,
                api_key="must-not-be-used",
                model_name="must-not-be-used",
            )

    def test_normalize_usage_extracts_fields(self):
        """_normalize_usage should extract token counts from a response."""
        data = {
            "id": "gen-123",
            "model": "test-model",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        }
        usage = _normalize_usage(data)
        self.assertEqual(100, usage["prompt_tokens"])
        self.assertEqual(50, usage["completion_tokens"])
        self.assertEqual(150, usage["total_tokens"])
        self.assertEqual("test-model", usage["model"])
        self.assertEqual("gen-123", usage["id"])

    def test_normalize_usage_handles_missing_usage(self):
        """_normalize_usage should handle responses with no usage block."""
        data = {"id": "x", "model": "m", "choices": [{"message": {"content": "hi"}}]}
        usage = _normalize_usage(data)
        self.assertEqual(0, usage["prompt_tokens"])
        self.assertEqual(0, usage["total_tokens"])
if __name__ == "__main__":
    unittest.main()
