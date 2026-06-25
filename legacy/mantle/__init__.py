"""Mantle OS -- the Homeostatic AppAI Framework (generation 4).

Mantle v3 grew the organism: eight contracted organs on one deterministic SignalBus, a
heartbeat, durable picture-memory, an immune system, a bounded MIND -- all certified before
cognition. Generation 4 adds the reproductive, symbiotic, and self-evolving tissue: an AppAI
can now be declared as an egg, take residence in a host codebase, share knowledge, redesign
its own VCW, and reconstruct itself.

    python -m mantle teach                       # the Field Guide, running
    python -m mantle hatch eggs/greeter.json --out=nest/

Everything Mantle OS v3 guaranteed is inherited UNCHANGED: the VCW cube (same on-disk
format, vcw-cube-png-v2), the veil, the staged atomic save, capacity->metabolism (never
rebirth), seal-fingerprinted ancestry, the bounded MIND, audit before fusion, and the
runnable gates with their tamper proofs.
"""
from .core import Organism, Body, SignalBus
from .vcw import (Cube, standard_genome, make_band_boot, make_entry, entry_hash,
                  code_hash, trial, CapacityError,
                  OVERFLOW_THRESHOLD, EMERGENCY_THRESHOLD)
from .egg import EGG_FORMAT, EggError, validate as validate_egg, load as load_egg
from .hatchery import incubate, hatch, HatchError

__version__ = "4.5.0"
__lineage__ = ("Mantle OS v3 (Homeostatic AppAI Framework)", "Mantle OS")

__all__ = ["Organism", "Body", "SignalBus", "Cube", "standard_genome", "make_band_boot",
           "make_entry", "entry_hash", "code_hash", "trial", "CapacityError",
           "OVERFLOW_THRESHOLD", "EMERGENCY_THRESHOLD",
           "EGG_FORMAT", "EggError", "validate_egg", "load_egg",
           "incubate", "hatch", "HatchError", "__version__", "__lineage__"]
