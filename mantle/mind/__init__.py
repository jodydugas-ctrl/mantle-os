"""mantle.mind -- the bounded MIND (Phase 2 only; Argonaut).

NOTHING in mantle.core / mantle.vcw / mantle.organs imports this package: the import
direction IS the Phase-1 guarantee. The model is a pluggable transport (a callable);
the offline deterministic stub is the default; there is no vendor SDK anywhere.
"""
from .transport import stub_mind, openai_compatible_model, openrouter_model, load_keyfile
from .containment import WRITE_SURFACE, guarded_write
from .mind import Mind, fuse
from .inner_voice import InnerVoice
from .runtime import AppAIRuntime

__all__ = ["stub_mind", "openai_compatible_model", "openrouter_model", "load_keyfile",
           "WRITE_SURFACE", "guarded_write", "Mind", "fuse", "InnerVoice", "AppAIRuntime"]
