"""Hermes Mantle Addon plugin registration."""

from .mantle_addon.config import ResidentConfig
from .mantle_addon.runtime import OBSERVER_HOOKS, ResidentRuntime
from .schemas import MANTLE_STATUS
from .tools import mantle_status


def register(ctx):
    """Register one read-only tool and fail-open resident observer hooks."""
    ctx.register_tool(
        name="mantle_status",
        toolset="mantle",
        schema=MANTLE_STATUS,
        handler=mantle_status,
        description="Report the bundled Mantle OS version and command surface.",
    )
    runtime = ResidentRuntime(
        ResidentConfig.from_mapping({}),
        profile_id=ctx.profile_name,
    )
    for hook_name in OBSERVER_HOOKS:
        ctx.register_hook(hook_name, getattr(runtime, hook_name))
