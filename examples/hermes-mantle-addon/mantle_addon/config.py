"""Validated immutable configuration for a Hermes Mantle resident."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


class ConfigError(ValueError):
    """Resident configuration is unknown, unsafe, or internally inconsistent."""


_DNR_VALUES = {"none", "retire_only", "no_reconstruction", "operator_defined"}


@dataclass(frozen=True)
class ResidentConfig:
    body_enabled: bool = True
    mind_enabled: bool = False
    storage_root: str | None = None
    dnr: str = "none"
    record_raw_prompts: bool = False
    record_raw_tool_args: bool = False
    max_event_chars: int = 4096
    checkpoint_each_turn: bool = True

    def __post_init__(self) -> None:
        for name in (
            "body_enabled",
            "mind_enabled",
            "record_raw_prompts",
            "record_raw_tool_args",
            "checkpoint_each_turn",
        ):
            if not isinstance(getattr(self, name), bool):
                raise ConfigError(f"{name} must be a boolean")
        if self.record_raw_prompts or self.record_raw_tool_args:
            raise ConfigError("raw payload retention is not authorized in Phase 1")
        if self.storage_root is not None and (
            not isinstance(self.storage_root, str) or not self.storage_root.strip()
        ):
            raise ConfigError("storage_root must be null or a non-empty string")
        if self.dnr not in _DNR_VALUES:
            raise ConfigError(
                "dnr must be one of: " + ", ".join(sorted(_DNR_VALUES))
            )
        if (
            isinstance(self.max_event_chars, bool)
            or not isinstance(self.max_event_chars, int)
            or not 1 <= self.max_event_chars <= 1_000_000
        ):
            raise ConfigError("max_event_chars must be an integer from 1 to 1000000")
        if self.mind_enabled:
            raise ConfigError("MIND fusion is not implemented in the Phase-1 addon")

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, Any],
        *,
        stage1_passed: bool = False,
        fusion_authorized: bool = False,
    ) -> "ResidentConfig":
        if not isinstance(values, Mapping):
            raise ConfigError("resident configuration must be a mapping")
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise ConfigError(f"unknown configuration field: {unknown[0]}")

        merged = cls().to_dict()
        merged.update(values)
        for name in (
            "body_enabled",
            "mind_enabled",
            "record_raw_prompts",
            "record_raw_tool_args",
            "checkpoint_each_turn",
        ):
            if not isinstance(merged[name], bool):
                raise ConfigError(f"{name} must be a boolean")
        if merged["record_raw_prompts"] or merged["record_raw_tool_args"]:
            raise ConfigError("raw payload retention is not authorized in Phase 1")
        storage_root = merged["storage_root"]
        if storage_root is not None and (
            not isinstance(storage_root, str) or not storage_root.strip()
        ):
            raise ConfigError("storage_root must be null or a non-empty string")
        if merged["dnr"] not in _DNR_VALUES:
            raise ConfigError(
                "dnr must be one of: " + ", ".join(sorted(_DNR_VALUES))
            )
        max_event_chars = merged["max_event_chars"]
        if (
            isinstance(max_event_chars, bool)
            or not isinstance(max_event_chars, int)
            or not 1 <= max_event_chars <= 1_000_000
        ):
            raise ConfigError("max_event_chars must be an integer from 1 to 1000000")
        if merged["mind_enabled"] and not stage1_passed:
            raise ConfigError("MIND requires a fresh Stage-1 PASS receipt")
        if merged["mind_enabled"] and not fusion_authorized:
            raise ConfigError("MIND requires separate operator fusion authorization")
        if merged["mind_enabled"]:
            raise ConfigError("MIND fusion is not implemented in the Phase-1 addon")
        return cls(**merged)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
