"""Fail-open observer bridge from documented Hermes hooks into Mantle organs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from threading import RLock
import time
from typing import Any, Callable, Mapping

from .aep import record_action_execution_proof
from .body import ResidentBodyFactory, save_resident
from .config import ResidentConfig


def _safe_save(organism: Any, path: Any) -> None:
    """Fail-open save for the atexit handler — never raises on the way down."""
    try:
        save_resident(organism, path)
    except Exception:
        pass


OBSERVER_HOOKS = (
    "on_session_start",
    "on_session_end",
    "on_session_finalize",
    "pre_llm_call",
    "post_llm_call",
    "pre_tool_call",
    "post_tool_call",
    "pre_approval_request",
    "post_approval_response",
    "subagent_start",
    "subagent_stop",
    "pre_gateway_dispatch",
)

DISCOVERY_CONTROL_ID = "hermes.mantle.record_discovery"
MAX_DISCOVERY_CHARS = 2_000


def _validated_discovery(value: Any) -> str:
    """Validate the only model-facing mutation before it reaches Memory."""
    if not isinstance(value, str):
        raise TypeError("discovery must be a string")
    text = value.strip()
    if not text:
        raise ValueError("discovery must not be empty")
    if len(text) > MAX_DISCOVERY_CHARS:
        raise ValueError(
            f"discovery must be at most {MAX_DISCOVERY_CHARS} characters"
        )
    if any(ord(char) < 32 and char not in "\n\t" for char in text):
        raise ValueError("discovery contains unsupported control characters")
    return text


class ResidentRuntime:
    """One profile-scoped Body adapter; hook return values never alter Hermes behavior."""

    def __init__(
        self,
        config: ResidentConfig,
        *,
        profile_id: str,
        hermes_home: str | Path | None = None,
        factory: Any | None = None,
    ) -> None:
        self.config = config
        self.profile_id = profile_id
        self.factory = factory or ResidentBodyFactory(config, hermes_home=hermes_home)
        self._handle: Any | None = None
        self._sequence = 0
        self._lock = RLock()
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
            # Dual-flush: persist on BOTH explicit checkpoint AND atexit, so a
            # cube is never lost to an ungraceful shutdown. The atexit handler
            # calls circulate(), which is a no-op when the circulate callback is
            # None (deferred mode) — but in deferred mode we install our own
            # atexit handler below that performs the full save.
            organism.heart.install_dual_flush()
            if not self.config.checkpoint_each_turn:
                import atexit as _atexit
                _atexit.register(
                    lambda organism=organism, path=path: _safe_save(organism, path)
                )
            self._wire_controls(organism)
            self._handle = handle
            return handle
        return self._handle

    @staticmethod
    def _wire_controls(organism: Any) -> None:
        """Expose the bounded model-facing mutation through Senses + Limbs."""
        def record_discovery(value: Any) -> None:
            text = _validated_discovery(value)
            organism.memory.remember(
                "discoveries",
                {"idea": text},
                opcode="INGESTED",
                source="Hermes mantle_record_discovery",
                verified=False,
                confidence="inferred",
            )

        organism.limbs.register_control(
            DISCOVERY_CONTROL_ID,
            {
                "label": "Record inferred discovery",
                "kind": "bounded_text",
                "band": "discoveries",
                "max_chars": MAX_DISCOVERY_CHARS,
                "verified": False,
            },
            record_discovery,
        )

    def record_discovery(self, text: Any) -> dict[str, Any]:
        """Record one inferred discovery through Limbs and persist its proof."""
        with self._lock:
            handle = self._ensure_handle()
            organism = handle.organism
            proof = organism.limbs.operate(DISCOVERY_CONTROL_ID, text)
            try:
                save_resident(organism, handle.path)
                durable = True
            except Exception as exc:
                durable = False
                organism.immune_event(
                    "checkpoint_failed",
                    {"event_type": "mantle_record_discovery", "error": type(exc).__name__},
                )
            return {"proof": proof, "durable": durable}

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
        if event_type in {"pre_approval_request", "post_approval_response"}:
            metadata["command"] = self._content_summary(data.get("command"))
            metadata["description"] = self._content_summary(data.get("description"))
            for field in ("surface", "choice", "decided_by"):
                value = data.get(field)
                if isinstance(value, str) and value:
                    metadata[field] = value[:64]
        if event_type in {"subagent_start", "subagent_stop"}:
            if event_type == "subagent_start":
                metadata["goal"] = self._content_summary(data.get("child_goal"))
            else:
                metadata["summary"] = self._content_summary(data.get("child_summary"))
                child_status = data.get("child_status")
                if isinstance(child_status, str) and child_status:
                    metadata["child_status"] = child_status[:64]
                duration = data.get("duration_ms")
                if isinstance(duration, (int, float)) and not isinstance(duration, bool):
                    metadata["duration_ms"] = max(0, int(duration))
            child_role = data.get("child_role")
            if isinstance(child_role, str) and child_role:
                metadata["child_role"] = child_role[:64]
            for field in ("parent_session_id", "child_session_id"):
                value = data.get(field)
                if isinstance(value, str) and value:
                    metadata[field] = self._hash_text(value)[:23]
        if event_type == "pre_gateway_dispatch":
            event = data.get("event")
            metadata["text"] = self._content_summary(getattr(event, "text", None))
            message_type = getattr(event, "message_type", None)
            if message_type is not None:
                metadata["message_type"] = str(
                    getattr(message_type, "value", message_type)
                )[:64]
            media_urls = getattr(event, "media_urls", None)
            if isinstance(media_urls, list):
                metadata["media_count"] = len(media_urls)
            source = getattr(event, "source", None)
            platform = getattr(source, "platform", None)
            if platform is not None:
                metadata["platform"] = str(
                    getattr(platform, "value", platform)
                )[:64]
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
        with self._lock:
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

    def pre_approval_request(self, **kwargs: Any) -> None:
        self._safe_observe("pre_approval_request", kwargs)

    def post_approval_response(self, **kwargs: Any) -> None:
        self._safe_observe("post_approval_response", kwargs)

    def subagent_start(self, **kwargs: Any) -> None:
        self._safe_observe("subagent_start", kwargs)

    def subagent_stop(self, **kwargs: Any) -> None:
        self._safe_observe("subagent_stop", kwargs)

    def pre_gateway_dispatch(self, **kwargs: Any) -> None:
        """Observe gateway ingress without rewriting, skipping, or authorizing it."""
        self._safe_observe("pre_gateway_dispatch", kwargs)


class RuntimeRegistry:
    """Resolve one locked resident per active Hermes home/profile at invocation time."""

    def __init__(
        self,
        config: ResidentConfig | None = None,
        *,
        profile_resolver: Callable[[], str],
        home_resolver: Callable[[], str | Path] | None = None,
        config_resolver: Callable[[], ResidentConfig] | None = None,
    ) -> None:
        if config is None and config_resolver is None:
            raise ValueError("config or config_resolver is required")
        self.config = config
        self._config_resolver = config_resolver or (lambda: config)  # type: ignore[return-value]
        self._profile_resolver = profile_resolver
        self._home_resolver = home_resolver or self._active_hermes_home
        self._lock = RLock()
        self._runtimes: dict[
            tuple[str, str, tuple[tuple[str, Any], ...]], ResidentRuntime
        ] = {}

    @staticmethod
    def _active_hermes_home() -> Path:
        from hermes_constants import get_hermes_home

        return get_hermes_home()

    def current(self) -> ResidentRuntime:
        home = Path(self._home_resolver()).expanduser().resolve()
        profile = self._profile_resolver()
        config = self._config_resolver()
        if not isinstance(config, ResidentConfig):
            raise TypeError("config_resolver must return ResidentConfig")
        config_key = tuple(sorted(config.to_dict().items()))
        key = (str(home), profile, config_key)
        with self._lock:
            runtime = self._runtimes.get(key)
            if runtime is None:
                runtime = ResidentRuntime(
                    config,
                    profile_id=profile,
                    hermes_home=home,
                )
                self._runtimes[key] = runtime
            return runtime

    def invoke(self, hook_name: str, **kwargs: Any) -> None:
        getattr(self.current(), hook_name)(**kwargs)
