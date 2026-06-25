#!/usr/bin/env python3
"""
mantle.symbiosis  --  the energy economy: the AppAI earns its keep (Mantle OS)

An AppAI lives in SYMBIOSIS with its user. The user provides RESOURCES (API keys) and
ENERGY (API credits); the organism spends energy to think and repays the relationship
with usefulness. Nothing about this is metaphor-only -- it is an auditable ledger in
the organism's own memory:

  the `symbiosis` band (append-only, hashed, like all memory) records:
    GRANT   the user fed the organism (credits granted; a key NAMED, never stored raw)
    SPEND   the organism burned energy (every metered MODEL call is a SPEND first)
    VALUE   the organism recorded work it did for the user (with evidence)

  balance  = sum(GRANT) - sum(SPEND)        -- computed, never stored
  state    = FED (>25% of lifetime grants remain) | HUNGRY (low) | STARVING (0)

THE STARVATION LAW (inherited doctrine, now executable): an organism with no energy
does not die and does not crash -- the MIND sleeps gracefully and the Body keeps
beating. A starved AppAI is a Zombie Body again, not a corpse. Energy can never go
negative; a spend the balance cannot cover is REFUSED + recorded as a `starvation`
immune event.

THE KEY LAW: API keys are resources, not memories. The ledger records a key's NAME and
fingerprint-of-availability only; raw key material is redacted at the boundary like
every other secret (HF-B20). The key itself stays in the keyfile (§0 KEYFILE_PATH).

The symbiotic loop, in code:
    feed -> energy -> metered cognition -> usefulness -> VALUE entries -> the user
    sees an honest account of what their credits bought -> feeds again.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .core.redact import redact
from .vcw.bands import make_band_boot
from .vcw.entry import make_entry

BAND = "symbiosis"
BAND_HEAD = 560
HUNGRY_FRACTION = 0.25      # below this fraction of lifetime grants: HUNGRY

FED, HUNGRY, STARVING = "FED", "HUNGRY", "STARVING"


def symbiosis_band(span: int = 20) -> Dict[str, Any]:
    """The band boot sector to include in a genome at genesis."""
    return make_band_boot(BAND, BAND_HEAD, "log-json", span=span,
                          purpose="the symbiotic ledger: grants in, work out")


class StarvationError(Exception):
    """The organism cannot afford this thought. The Body keeps beating regardless."""


def _has_band(org) -> bool:
    return BAND in org.prime.bands


def grant(org, credits: float, source: str = "user",
          key_name: Optional[str] = None, note: str = "") -> Dict[str, Any]:
    """The user feeds the organism. A key is recorded by NAME only -- if anything
    secret-shaped slips into the note, the band's redaction boundary masks it."""
    if credits <= 0:
        raise ValueError("a grant must be positive energy")
    # the ledger is a SECRET BOUNDARY: a key pasted into a note must never burn into
    # append-only memory. Names yes; material never (HF-B20 applies here too).
    content = {"credits": float(credits), "source": redact(source), "note": redact(note)}
    if key_name:
        content["resource"] = {"key_name": redact(key_name), "stored": "name-only"}
    e = make_entry(content, opcode="GRANT", author="BODY", source=source)
    org.prime.append(BAND, e)
    org.bus.emit("fed", {"credits": credits})
    return e


def spend(org, credits: float, purpose: str) -> bool:
    """Burn energy. Refused (False + `starvation` immune event) if the balance cannot
    cover it -- energy NEVER goes negative; the organism never crashes for hunger."""
    if credits <= 0:
        raise ValueError("a spend must be positive energy")
    if balance(org) < credits:
        org.immune_event("starvation", {"wanted": credits, "balance": balance(org),
                                        "purpose": purpose})
        return False
    org.prime.append(BAND, make_entry({"credits": float(credits), "purpose": purpose},
                                      opcode="SPEND", author="BODY", source=purpose))
    return True


def record_value(org, what: str, evidence: Any = None) -> Dict[str, Any]:
    """The organism's side of the bargain: an auditable record of work delivered."""
    e = make_entry({"value": redact(what), "evidence": redact(evidence)},
                   opcode="VALUE", author="BODY", source="symbiosis")
    org.prime.append(BAND, e)
    return e


def ledger(org) -> Dict[str, Any]:
    entries = org.prime.read(BAND) if _has_band(org) else []
    granted = sum(e["content"]["credits"] for e in entries if e["opcode"] == "GRANT")
    spent = sum(e["content"]["credits"] for e in entries if e["opcode"] == "SPEND")
    value = [e["content"]["value"] for e in entries if e["opcode"] == "VALUE"]
    keys = sorted({e["content"]["resource"]["key_name"] for e in entries
                   if e["opcode"] == "GRANT" and "resource" in e["content"]})
    return {"granted": granted, "spent": spent, "balance": granted - spent,
            "value_records": value, "keys": keys, "entries": len(entries)}


def balance(org) -> float:
    return ledger(org)["balance"]


def metabolic_state(org) -> str:
    """FED | HUNGRY | STARVING -- the organism's felt energy condition."""
    led = ledger(org)
    if led["balance"] <= 0:
        return STARVING
    if led["granted"] and led["balance"] / led["granted"] < HUNGRY_FRACTION:
        return HUNGRY
    return FED


def metered(model: Callable[[str], str], org, cost_per_call: float = 1.0,
            purpose: str = "MODEL.REQUEST") -> Callable[[str], str]:
    """Wrap any model transport in the METABOLIC GATE: every call must be paid for
    BEFORE it happens. An unaffordable call raises StarvationError -- which the Brain
    socket catches fail-open (a `cognition_fault` immune event), so a starving
    organism's heartbeat completes every pulse with the MIND asleep."""
    def call(prompt: str) -> str:
        if not spend(org, cost_per_call, purpose):
            raise StarvationError(
                "no energy for cognition (balance=%.1f); the MIND sleeps, the Body "
                "keeps beating. Feed the organism: python -m mantle feed ..."
                % balance(org))
        return model(prompt)
    call.__name__ = "metered_%s" % getattr(model, "__name__", "model")
    return call


def _rough_tokens(result: Any) -> int:
    """A provider-free token proxy (~4 chars/token) for transports that report no usage."""
    return max(1, len(str(result)) // 4)


def metered_by_usage(model: Callable[[str], str], org, price_per_1k: float = 1.0,
                     usage_of: Optional[Callable[[Any], int]] = None,
                     purpose: str = "MODEL.REQUEST") -> Callable[[str], str]:
    """REAL metering: energy is charged from ACTUAL token usage, not a flat fee. The
    starvation law still holds -- a call is refused when the balance is already empty (the
    MIND sleeps) -- and the spend is reconciled to the response's real size, so credits in
    the cube mirror usage in the world. `usage_of(result)` returns the token count (defaults
    to the rough proxy)."""
    usage_of = usage_of or _rough_tokens
    def call(prompt: str) -> str:
        if balance(org) <= 0:
            org.immune_event("starvation", {"purpose": purpose, "balance": balance(org)})
            raise StarvationError(
                "no energy for cognition; the MIND sleeps, the Body keeps beating.")
        result = model(prompt)
        tokens = usage_of(result)
        spend(org, price_per_1k * tokens / 1000.0, "%s (%d tok)" % (purpose, tokens))
        return result
    call.__name__ = "usage_metered_%s" % getattr(model, "__name__", "model")
    return call


def metering_summary(org) -> Dict[str, Any]:
    """The honest burn report: calls made, average burn per call, and the starvation horizon
    (how many calls of energy remain) -- what `vitals` shows the user."""
    entries = org.prime.read(BAND) if _has_band(org) else []
    spends = [e["content"]["credits"] for e in entries if e["opcode"] == "SPEND"]
    bal = balance(org)
    burn = (sum(spends) / len(spends)) if spends else 0.0
    horizon = (bal / burn) if burn > 0 else float("inf")
    return {"calls": len(spends), "spent": sum(spends), "balance": bal,
            "burn_rate": burn, "starvation_horizon": horizon}
