"""Fail-open observer bridge from documented Hermes hooks into Mantle organs."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Mapping

from .aep import record_action_execution_proof
from .body import ResidentBodyFactory, save_resident
from .config import ResidentConfig


OBSERVER_HOOKS = (
    "on_session_start",
    "on_session_end",
    "on_session_finalize",
    "pre_llm_call",
    "post_llm_call",
    "pre_tool_call",
    "post_tool_call",
)


class ResidentRuntime:
    """One profile-scoped Body adapter; hook return values never alter Hermes behavior."""

    def __init__(
        self,
        config: ResidentConfig,
        *,
        profile_id: str,
        factory: Any | None = None,
    ) -> None:
        self.config = config
        self.profile_id = profile_id
        self.factory = factory or ResidentBodyFactory(config)
        self._handle: Any | None = None
        self._sequence = 0
        self.diagnostics: list[dict[str, str]] = []

    @property
    def organism(self) -> Any:
        return self._ensure_handle().organism

    def _ensure_handle(self) -> Any:
        if self._handle is None:
            handle = self.factory.get_or_create(self.profile_id)
            organism = handle.organism
            path = handle.path
            if self.config.checkpoint_each_turn:
                organism.heart.set_circulate(
                    lambda organism=organism, path=path: save_resident(organism, path)
                )
            else:
                organism.heart.set_circulate(None)
            self._handle = handle
            return handle
        return self._handle

    @staticmethod
    def _hash_text(value: str) -> str:
        return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()

    @classmethod
    def _content_summary(cls, value: Any) -> dict[str, Any]:
        if isinstance(value, str):
            return {"chars": len(value), "digest": cls._hash_text(value)}
        if isinstance(value, list):
            text_parts = []
            for item in value:
                if isinstance(item, Mapping):
                    content = item.get("content")
                    if isinstance(content, str):
                        text_parts.append(content)
            text = "\n".join(text_parts)
            return {
                "items": len(value),
                "chars": len(text),
                "digest": cls._hash_text(text),
            }
        return {"type": type(value).__name__}

    def _metadata(self, event_type: str, data: Mapping[str, Any]) -> dict[str, Any]:
        metadata: dict[str, Any] = {}
        session_id = data.get("session_id")
        if isinstance(session_id, str) and session_id:
            metadata["session"] = self._hash_text(session_id)[:23]
        if event_type in {"pre_llm_call", "post_llm_call"}:
            model = data.get("model")
            if isinstance(model, str):
                metadata["model"] = model[:256]
            for field in ("user_message", "conversation_history"):
                metadata[field] = self._content_summary(data.get(field))
            if event_type == "post_llm_call":
                metadata["assistant_response"] = self._content_summary(
                    data.get("assistant_response")
                )
            if event_type == "pre_llm_call" and isinstance(
                data.get("is_first_turn"), bool
            ):
                metadata["is_first_turn"] = data["is_first_turn"]
        if event_type in {"pre_tool_call", "post_tool_call"}:
            tool_name = data.get("tool_name")
            if isinstance(tool_name, str):
                metadata["tool_name"] = tool_name[:256]
            args = data.get("args")
            if isinstance(args, Mapping):
                metadata["arg_count"] = len(args)
        if event_type == "post_tool_call":
            metadata["status"] = str(data.get("status") or "unknown")[:64]
            error_type = data.get("error_type")
            if isinstance(error_type, str) and error_type:
                metadata["error_type"] = error_type[:128]
            duration = data.get("duration_ms")
            if isinstance(duration, (int, float)) and not isinstance(duration, bool):
                metadata["duration_ms"] = max(0, int(duration))
        encoded = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        if len(encoded) > self.config.max_event_chars:
            return {
                "truncated": True,
                "digest": self._hash_text(encoded),
                "chars": len(encoded),
            }
        return metadata

    def _observe(self, event_type: str, data: Mapping[str, Any]) -> None:
        self._sequence += 1
        organism = self.organism
        tool_call_id = data.get("tool_call_id")
        correlation_ref = (
            self._hash_text(tool_call_id)
            if isinstance(tool_call_id, str) and tool_call_id
            else ""
        )
        action_id = correlation_ref or f"{event_type}:{self._sequence}"
        organism.senses.inhale(
            {
                "action_id": action_id,
                "event_type": event_type,
                "source": "hermes-plugin-hook",
                "metadata": self._metadata(event_type, data),
            }
        )
        if event_type == "post_tool_call":
            status = str(data.get("status") or "unknown")
            attempted = status in {"ok", "error"}
            ok = status == "ok"
            tool_name = str(data.get("tool_name") or "unknown")
            reason = "ok" if ok else str(data.get("error_type") or status)[:128]
            duration = data.get("duration_ms")
            evidence = {
                "source": "post_tool_call",
                "status": status[:64],
                "duration_ms": (
                    max(0, int(duration))
                    if isinstance(duration, (int, float)) and not isinstance(duration, bool)
                    else None
                ),
            }
            record_action_execution_proof(
                organism,
                tool_name,
                action_id=correlation_ref or action_id,
                attempted=attempted,
                ok=ok,
                method="Hermes dispatch" if attempted else None,
                ref=correlation_ref,
                reason=reason,
                actor="Body",
                authorship="BODY",
                timestamp=time.time(),
                evidence=[evidence],
            )
            if status == "blocked":
                organism.immune.event(
                    "host_tool_block",
                    {"tool": tool_name, "error_type": reason},
                )
            elif status == "error":
                organism.immune.event(
                    "host_tool_error",
                    {"tool": tool_name, "error_type": reason},
                )
            elif status != "ok":
                organism.immune.event(
                    "host_tool_status_invalid",
                    {"tool": tool_name, "status": status[:64]},
                )
        organism.heart.beat(assemble=False)
        if (
            not self.config.checkpoint_each_turn
            and event_type in {"on_session_end", "on_session_finalize"}
            and self._handle is not None
        ):
            save_resident(organism, self._handle.path)

    def _safe_observe(self, event_type: str, data: Mapping[str, Any]) -> None:
        try:
            self._observe(event_type, data)
        except Exception as exc:
            detail = {"event_type": event_type, "error_type": type(exc).__name__}
            if self._handle is not None:
                try:
                    organism = self._handle.organism
                    organism.immune.event("hook_failure", detail)
                    save_resident(organism, self._handle.path)
                except Exception:
                    pass
            self.diagnostics.append(detail)
            del self.diagnostics[:-100]

    def on_session_start(self, **kwargs: Any) -> None:
        self._safe_observe("on_session_start", kwargs)

    def on_session_end(self, **kwargs: Any) -> None:
        self._safe_observe("on_session_end", kwargs)

    def on_session_finalize(self, **kwargs: Any) -> None:
        self._safe_observe("on_session_finalize", kwargs)

    def pre_llm_call(self, **kwargs: Any) -> None:
        self._safe_observe("pre_llm_call", kwargs)

    def post_llm_call(self, **kwargs: Any) -> None:
        self._safe_observe("post_llm_call", kwargs)

    def pre_tool_call(self, **kwargs: Any) -> None:
        self._safe_observe("pre_tool_call", kwargs)

    def post_tool_call(self, **kwargs: Any) -> None:
        self._safe_observe("post_tool_call", kwargs)
