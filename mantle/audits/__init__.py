"""mantle.audits -- the gates (Mantle v3).

Stage 1 certifies the Zombie Body (deterministic, LLM-free). Stage 2 re-runs every
Stage-1 row after fusion and adds containment rows. The invariants prove every guard
red/green. Any hard-fail blocks progression. No invariant is ever weakened to pass.
"""
from . import invariants
from . import stage1
from . import stage2

__all__ = ["invariants", "stage1", "stage2"]
