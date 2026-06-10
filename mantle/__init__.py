"""Mantle OS v3 -- the Homeostatic AppAI Framework.

Grow software like a living organism: a deterministic, auditable BODY first (eight organs
meshed on one signal bus around the durable VCW substrate), a bounded MIND second.

    from mantle import Organism, standard_genome
    org = Organism.birth(identity={"name": "My.AppAI"},
                         truths=["if it is not in the VCW it did not happen"],
                         commandments=["protect your VCW", "you are a tool USER"])
    org.senses.inhale({"action_id": "boot", "event_type": "start"})
    org.heart.run(3)        # the Body lives -- no LLM anywhere in this path

Phase 2 (only after the Stage-1 gate): `from mantle.mind import Mind, fuse, stub_mind`.
Phase-1 packages (mantle.core / mantle.vcw / mantle.organs) never import mantle.mind.
"""
from .core import Organism, Body, SignalBus
from .vcw import (Cube, standard_genome, make_band_boot, make_entry, entry_hash,
                  code_hash, trial, CapacityError,
                  OVERFLOW_THRESHOLD, EMERGENCY_THRESHOLD)

__version__ = "3.0.0"

__all__ = ["Organism", "Body", "SignalBus", "Cube", "standard_genome", "make_band_boot",
           "make_entry", "entry_hash", "code_hash", "trial", "CapacityError",
           "OVERFLOW_THRESHOLD", "EMERGENCY_THRESHOLD", "__version__"]
