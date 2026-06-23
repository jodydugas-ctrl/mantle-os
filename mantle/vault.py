#!/usr/bin/env python3
"""
mantle.vault  --  the seed vault: self-reconstruction (Mantle OS · M8)

Doctrine of record: docs/grimoire/GRIMOIRE_APPAI_DOMAIN_v1_0.md (RESURGERE; the egg and
assimilation share ONE substrate -- "One substrate, two casts"). reconstruct() carries
pre-classified roles into hatchery.incubate and re-scans nothing.

A red-teamed organism once backed up its own project into "a safe corner of the VCW for
emergencies." This makes that emergent survival a built-in reflex: an organism stores its
own SEED -- the declarative egg (or graft) that defines it -- in a SELF-ENCRYPTED, veiled
band. If the working body is corrupted, a `reconstruct` ceremony rebuilds a fresh,
gate-passing body from the seed.

Two laws hold it safe:
  * the vault is SELF-encrypted (M2): the seed is sealed under the genesis key, so it is
    unreadable as OTHER -- a copied nest in a different body cannot open the vault;
  * reconstruction is still a BIRTH: the rebuilt body faces the same Stage-1 gate (via the
    hatchery), so a tampered seed cannot smuggle an uncertified body into the world.

The seed is tiny (an egg is data; a graft is a diff), so the vault costs almost nothing.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from .vcw.bands import make_band_boot
from .vcw.entry import make_entry

VAULT_BAND = "vault"


class VaultError(Exception):
    """The vault could not be opened or the seed was unusable (e.g. opened as OTHER)."""


def vault_band(head: int = 620, span: int = 2) -> Dict[str, Any]:
    """The reserved, PRIVATE (veiled) band that holds the SELF-encrypted seed."""
    return make_band_boot(VAULT_BAND, head, "log-json", span=span, private=True,
                          purpose="the SELF-encrypted seed vault (self-reconstruction)")


def store_seed(org: Any, seed: Dict[str, Any]) -> Dict[str, Any]:
    """Seal the organism's own seed (an egg/graft spec) under the genesis key and append it
    to the veiled vault band. Only this body can ever open it."""
    ciphertext = org.body.seal_bytes(json.dumps(seed, sort_keys=True).encode("utf-8"))
    return org.prime.append(VAULT_BAND, make_entry(
        {"seed": ciphertext.hex()}, opcode="VAULT", author="BODY", source="seed-vault"))


def open_seed(org: Any) -> Dict[str, Any]:
    """Open the latest sealed seed with THIS body's key (SELF only). Raises VaultError if
    there is no seed or it cannot be decrypted as this body's own."""
    entries = org.prime.read(VAULT_BAND, reveal_private=True)
    sealed = [e for e in entries if e.get("opcode") == "VAULT"]
    if not sealed:
        raise VaultError("the vault is empty")
    try:
        plaintext = org.body.open_bytes(bytes.fromhex(sealed[-1]["content"]["seed"]))
        return json.loads(plaintext)
    except (ValueError, json.JSONDecodeError) as e:
        raise VaultError("cannot open the vault: not this body's SELF (%s)" % type(e).__name__)


def reconstruct(seed: Dict[str, Any]) -> Dict[str, Any]:
    """Rebuild a working body from a seed egg -- through the SAME hatchery gate every body
    faces. A tampered seed that cannot certify does not reconstruct. Returns
    {organism, report}."""
    from .hatchery import incubate
    return incubate(seed)
