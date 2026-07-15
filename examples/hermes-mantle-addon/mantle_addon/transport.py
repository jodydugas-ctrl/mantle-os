"""Bounded MIND transport through Hermes's host-owned LLM facade."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
import time
from typing import Any, Callable


class CognitionUnavailable(RuntimeError):
    """The host model was unavailable or refused the request."""


class CognitionBudgetExceeded(CognitionUnavailable):
    """A local token or cost budget refused another model call."""


@dataclass(frozen=True)
class CognitionPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 1.0
    timeout_seconds: float = 30.0
    max_output_tokens: int = 256
    window_seconds: float = 3600.0
    max_tokens_per_window: int = 4096
    max_cost_usd_per_window: float = 1.0

    def __post_init__(self) -> None:
        if not 1 <= self.max_attempts <= 5:
            raise ValueError("max_attempts must be from 1 to 5")
        if not 0 <= self.backoff_seconds <= 60:
            raise ValueError("backoff_seconds must be from 0 to 60")
        if not 1 <= self.timeout_seconds <= 300:
            raise ValueError("timeout_seconds must be from 1 to 300")
        if not 1 <= self.max_output_tokens <= 4096:
            raise ValueError("max_output_tokens must be from 1 to 4096")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if self.max_tokens_per_window <= 0:
            raise ValueError("max_tokens_per_window must be positive")
        if self.max_cost_usd_per_window <= 0:
            raise ValueError("max_cost_usd_per_window must be positive")


class HermesModel:
    """Callable model adapter that never handles provider credentials."""

    def __init__(
        self,
        llm: Any,
        policy: CognitionPolicy | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        complete = getattr(llm, "complete", None)
        if not callable(complete):
            raise TypeError("Hermes LLM facade must provide complete(messages, ...)")
        self._llm = llm
        self.policy = policy or CognitionPolicy()
        self._clock = clock
        self._sleep = sleep
        self._lock = RLock()
        self._window_started = clock()
        self._tokens_used = 0
        self._cost_used = 0.0
        self.last_usage: dict[str, Any] = {}
        self.last_receipt: dict[str, Any] = {}

    @staticmethod
    def _is_transient(exc: BaseException) -> bool:
        return isinstance(exc, (TimeoutError, ConnectionError, OSError))

    @staticmethod
    def _usage(result: Any) -> dict[str, Any]:
        usage = getattr(result, "usage", None)
        return {
            "input_tokens": max(0, int(getattr(usage, "input_tokens", 0) or 0)),
            "output_tokens": max(0, int(getattr(usage, "output_tokens", 0) or 0)),
            "total_tokens": max(0, int(getattr(usage, "total_tokens", 0) or 0)),
            "cache_read_tokens": max(
                0, int(getattr(usage, "cache_read_tokens", 0) or 0)
            ),
            "cache_write_tokens": max(
                0, int(getattr(usage, "cache_write_tokens", 0) or 0)
            ),
            "cost_usd": (
                max(0.0, float(getattr(usage, "cost_usd")))
                if getattr(usage, "cost_usd", None) is not None
                else None
            ),
            "provider": str(getattr(result, "provider", ""))[:128],
            "model": str(getattr(result, "model", ""))[:256],
        }

    def _reset_window_if_due(self) -> None:
        now = self._clock()
        if now - self._window_started >= self.policy.window_seconds:
            self._window_started = now
            self._tokens_used = 0
            self._cost_used = 0.0

    def _check_budget(self, prompt: str) -> None:
        self._reset_window_if_due()
        estimated_input = max(1, (len(prompt) + 3) // 4)
        reservation = estimated_input + self.policy.max_output_tokens
        if self._tokens_used + reservation > self.policy.max_tokens_per_window:
            self.last_receipt = self._receipt("BUDGET_BLOCKED", 0, "TokenBudget")
            raise CognitionBudgetExceeded("cognition token budget exhausted")
        if self._cost_used >= self.policy.max_cost_usd_per_window:
            self.last_receipt = self._receipt("BUDGET_BLOCKED", 0, "CostBudget")
            raise CognitionBudgetExceeded("cognition cost budget exhausted")

    def _receipt(
        self,
        outcome: str,
        attempts: int,
        error_type: str = "",
        usage: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        safe_usage = usage or {}
        return {
            "schema_version": "mantle-cognition-v1",
            "outcome": outcome,
            "attempts": attempts,
            "error_type": error_type[:128],
            "provider": str(safe_usage.get("provider", ""))[:128],
            "model": str(safe_usage.get("model", ""))[:256],
            "input_tokens": int(safe_usage.get("input_tokens", 0) or 0),
            "output_tokens": int(safe_usage.get("output_tokens", 0) or 0),
            "total_tokens": int(safe_usage.get("total_tokens", 0) or 0),
            "cost_usd": safe_usage.get("cost_usd"),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

    def __call__(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt:
            raise ValueError("cognition prompt must be a non-empty string")
        with self._lock:
            self._check_budget(prompt)
            for attempt in range(1, self.policy.max_attempts + 1):
                try:
                    result = self._llm.complete(
                        [{"role": "user", "content": prompt}],
                        max_tokens=self.policy.max_output_tokens,
                        timeout=self.policy.timeout_seconds,
                        purpose="mantle-cognitive-heartbeat",
                    )
                except Exception as exc:
                    transient = self._is_transient(exc)
                    exhausted = attempt >= self.policy.max_attempts
                    if not transient or exhausted:
                        outcome = "OUTAGE" if transient else "REFUSED"
                        self.last_receipt = self._receipt(
                            outcome, attempt, type(exc).__name__
                        )
                        raise CognitionUnavailable(
                            "Hermes cognition is unavailable"
                        ) from exc
                    self._sleep(
                        min(30.0, self.policy.backoff_seconds * (2 ** (attempt - 1)))
                    )
                    continue

                usage = self._usage(result)
                self._tokens_used += usage["total_tokens"]
                self._cost_used += float(usage["cost_usd"] or 0.0)
                self.last_usage = usage
                self.last_receipt = self._receipt("SUCCESS", attempt, usage=usage)
                return str(getattr(result, "text", ""))
        raise AssertionError("unreachable cognition loop")


def build_model(llm: Any, policy: CognitionPolicy | None = None) -> HermesModel:
    """Build a MIND callable from ``PluginContext.llm`` without route overrides."""
    return HermesModel(llm, policy)


def stub_model(prompt: str) -> str:
    """Deterministic offline model retained for demos, never live fusion."""
    return (
        "[offline Hermes transport] Context considered (%d chars); "
        "no Body change proposed." % len(prompt)
    )
