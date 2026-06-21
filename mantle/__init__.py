"""Argonaut OS -- generation 4 of the Mantle lineage.

The mantle octopus secretes a paper-thin shell from its own body -- not a home, a
BROOD VESSEL for its eggs. That is this framework's evolutionary step: Mantle grew the
organism; Argonaut grows the vessels that carry new organisms.

    python -m mantle teach                       # the Field Guide, running
    python -m mantle hatch eggs/greeter.json --out=nest/

Everything Mantle OS v3 guaranteed is inherited UNCHANGED: the eight contracted organs
on one deterministic SignalBus, the VCW cube (same on-disk format, vcw-cube-png-v2 --
an Argonaut can read a Mantle cube and vice versa), the veil, the staged atomic save,
capacity->metabolism (never rebirth), seal-fingerprinted ancestry, the bounded MIND,
audit before fusion, and the runnable gates with their tamper proofs.
"""
from .core import Organism, Body, SignalBus
from .vcw import (Cube, standard_genome, make_band_boot, make_entry, entry_hash,
                  code_hash, trial, CapacityError,
                  OVERFLOW_THRESHOLD, EMERGENCY_THRESHOLD)
from .egg import EGG_FORMAT, EggError, validate as validate_egg, load as load_egg
from .hatchery import incubate, hatch, HatchError

__version__ = "4.0.0"
__lineage__ = ("Mantle OS v3 (Homeostatic AppAI Framework)", "Argonaut OS")

__all__ = ["Organism", "Body", "SignalBus", "Cube", "standard_genome", "make_band_boot",
           "make_entry", "entry_hash", "code_hash", "trial", "CapacityError",
           "OVERFLOW_THRESHOLD", "EMERGENCY_THRESHOLD",
           "EGG_FORMAT", "EggError", "validate_egg", "load_egg",
           "incubate", "hatch", "HatchError", "__version__", "__lineage__"]
