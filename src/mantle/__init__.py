"""Mantle OS -- the Homeostatic AppAI Framework.

Grow software like a living organism, then give it a mind. An AppAI is built Body first:
eight contracted organs mesh on one deterministic SignalBus around a durable picture-memory
(the VCW cube), with an immune system and a heartbeat -- all certified with no LLM attached.
Only then may a bounded MIND be fused, and it may only ever extend what already lives.

An AppAI can be declared as a single egg, take residence in a host codebase, share knowledge,
redesign its own VCW, and reconstruct itself -- every capability gated by the runnable audits
and their tamper proofs.

    python -m mantle teach                       # the Field Guide, running
    python -m mantle hatch examples/eggs/greeter.json --out=nest/
"""
__version__ = "1.0.0"

# The public API is exposed lazily (PEP 562): importing `mantle` is near-free; each name pulls
# in its submodule only on first access. `from mantle import Organism` and `mantle.Organism`
# both still work -- they just defer the core/vcw/hatchery import chains (and the heavy audit
# suite those drag in) until something is actually used.
_LAZY = {
    "Organism": ("mantle.core", "Organism"),
    "Body": ("mantle.core", "Body"),
    "SignalBus": ("mantle.core", "SignalBus"),
    "Cube": ("mantle.vcw", "Cube"),
    "standard_genome": ("mantle.vcw", "standard_genome"),
    "make_band_boot": ("mantle.vcw", "make_band_boot"),
    "make_entry": ("mantle.vcw", "make_entry"),
    "entry_hash": ("mantle.vcw", "entry_hash"),
    "code_hash": ("mantle.vcw", "code_hash"),
    "trial": ("mantle.vcw", "trial"),
    "CapacityError": ("mantle.vcw", "CapacityError"),
    "OVERFLOW_THRESHOLD": ("mantle.vcw", "OVERFLOW_THRESHOLD"),
    "EMERGENCY_THRESHOLD": ("mantle.vcw", "EMERGENCY_THRESHOLD"),
    "EGG_FORMAT": ("mantle.egg", "EGG_FORMAT"),
    "EggError": ("mantle.egg", "EggError"),
    "validate_egg": ("mantle.egg", "validate"),
    "load_egg": ("mantle.egg", "load"),
    "incubate": ("mantle.hatchery", "incubate"),
    "hatch": ("mantle.hatchery", "hatch"),
    "HatchError": ("mantle.hatchery", "HatchError"),
}

__all__ = list(_LAZY) + ["__version__"]


def __getattr__(name):
    spec = _LAZY.get(name)
    if spec is None:
        raise AttributeError("module %r has no attribute %r" % (__name__, name))
    import importlib
    value = getattr(importlib.import_module(spec[0]), spec[1])
    globals()[name] = value  # cache so the lazy lookup happens at most once
    return value


def __dir__():
    return sorted(list(globals()) + list(_LAZY))
