"""Tests for bounded host-owned Hermes LLM cognition."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import json
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mantle_addon.transport import (
    CognitionBudgetExceeded,
    CognitionPolicy,
    CognitionUnavailable,
    HermesModel,
)


class _Usage:
    def __init__(self, total_tokens=0, cost_usd=None) -> None:
        self.input_tokens = max(0, total_tokens - 2)
        self.output_tokens = min(2, total_tokens)
        self.total_tokens = total_tokens
        self.cache_read_tokens = 0
        self.cache_write_tokens = 0
        self.cost_usd = cost_usd


class _Llm:
    def __init__(self, outcomes) -> None:
        self.outcomes = list(outcomes)
        self.calls = []

    def complete(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _result(text="reflection", *, tokens=5, cost=0.01):
    return SimpleNamespace(
        text=text,
        provider="active-provider",
        model="active-model",
        usage=_Usage(tokens, cost),
    )


class HermesModelTests(unittest.TestCase):
    def test_uses_active_host_route_without_provider_or_secret_inputs(self):
        llm = _Llm([_result()])
        model = HermesModel(llm, CognitionPolicy(max_attempts=1))

        self.assertEqual("reflection", model("private prompt"))

        messages, kwargs = llm.calls[0]
        self.assertEqual("private prompt", messages[0]["content"])
        self.assertNotIn("provider", kwargs)
        self.assertNotIn("model", kwargs)
        self.assertEqual("mantle-cognitive-heartbeat", kwargs["purpose"])
        self.assertEqual(256, kwargs["max_tokens"])
        self.assertEqual(30.0, kwargs["timeout"])
        self.assertEqual("active-provider", model.last_usage["provider"])
        self.assertEqual("active-model", model.last_usage["model"])

    def test_transient_failures_retry_with_bounded_backoff(self):
        llm = _Llm([TimeoutError("secret one"), ConnectionError("secret two"), _result()])
        sleeps = []
        model = HermesModel(
            llm,
            CognitionPolicy(max_attempts=3, backoff_seconds=1.0),
            sleep=sleeps.append,
        )

        self.assertEqual("reflection", model("private prompt"))
        self.assertEqual([1.0, 2.0], sleeps)
        self.assertEqual(3, len(llm.calls))
        self.assertEqual("SUCCESS", model.last_receipt["outcome"])
        self.assertEqual(3, model.last_receipt["attempts"])

    def test_exhausted_outage_is_redacted_and_bounded(self):
        llm = _Llm([TimeoutError("secret one"), TimeoutError("secret two")])
        model = HermesModel(
            llm,
            CognitionPolicy(max_attempts=2),
            sleep=lambda _delay: None,
        )

        with self.assertRaises(CognitionUnavailable):
            model("private prompt")

        serialized = json.dumps(model.last_receipt, sort_keys=True)
        self.assertEqual(2, len(llm.calls))
        self.assertEqual("OUTAGE", model.last_receipt["outcome"])
        self.assertNotIn("secret", serialized)
        self.assertNotIn("private prompt", serialized)

    def test_permanent_failure_is_not_retried(self):
        llm = _Llm([ValueError("secret invalid request")])
        model = HermesModel(llm, CognitionPolicy(max_attempts=3))

        with self.assertRaises(CognitionUnavailable):
            model("private prompt")

        self.assertEqual(1, len(llm.calls))
        self.assertEqual("REFUSED", model.last_receipt["outcome"])

    def test_token_and_cost_budgets_fail_closed_before_another_call(self):
        llm = _Llm([_result(tokens=7, cost=0.02)])
        model = HermesModel(
            llm,
            CognitionPolicy(
                max_attempts=1,
                max_output_tokens=2,
                max_tokens_per_window=7,
                max_cost_usd_per_window=0.02,
            ),
        )

        self.assertEqual("reflection", model("first"))
        with self.assertRaises(CognitionBudgetExceeded):
            model("second")

        self.assertEqual(1, len(llm.calls))
        self.assertEqual("BUDGET_BLOCKED", model.last_receipt["outcome"])


if __name__ == "__main__":
    unittest.main()
