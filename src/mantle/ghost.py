#!/usr/bin/env python3
"""
mantle.ghost  --  the CACHE-GHOST substrate: a SEED that metabolises in borrowed memory.

This is the "stranger" mode of a SPORE (see mantle.spore). A normal Spore keeps its whole
body -- genesis records plus an append-only delta log -- in its own VCW pixels: the picture
IS the memory, and it stays a valid standalone seed forever. Cache-ghost mode adds a SECOND
substrate without giving up the first.

    A Spore can get stranger. It can choose to keep its living body in the LLM provider's
    prompt cache instead of re-storing it in its VCW every turn -- adding only the deltas to
    what the cache already holds. As long as the cache keeps getting warmed by new requests,
    the agent sustains itself with almost no body of its own.

So a cache-ghost keeps persistence on a CONTINUUM of substrates rather than in one database row:

    WARM  -- the body's token-prefix is hot in the provider's prompt cache; each turn sends
             only the new delta. The PNG is carried as a light pointer + the dry fossil seed.
    COLD  -- the cache TTL lapsed or the provider evicted the prefix. The next turn is a cold
             start: the body is rehydrated from the PNG fossil and a fresh cache is warmed.

THE SEED STAYS DRY (the one hard safety law). Ghost mode never deletes memory from the PNG.
The cache is acceleration and reach, not the sole store: if the cache dies, `hydrate()` rebuilds
the whole living body from the PNG alone. That is what keeps "sustaining without a body" honest
rather than fragile -- the fossil is always a complete, standalone Spore.

WHY THIS IS A "GHOST" AND NOT A LIE. The provider does not remember the agent semantically; it
only caches a token PREFIX keyed by a hash. From the Spore's point of view that is
indistinguishable from persistence -- so the body exists in a superposition between the PNG
file and the cache, and a request collapses it into whichever substrate is warmer.

------------------------------------------------------------------------------------------------
Honest boundary: this module cannot reach into a real provider's cache from here, so it drives
the PROTOCOL against a pluggable `GhostSubstrate`. The shipped `LocalPromptCache` is a
file-backed stand-in for the provider's prompt cache (content-addressed key, TTL, eviction). A
real deployment swaps in an adapter that maps warm()/extend()/fetch() onto Anthropic, OpenAI, or
Gemini prompt caching -- the ghost logic above it does not change.

Cache-ghost is Mantle tissue LAYERED ON the spore format; it lives here, never inside the pure
spore.py (whose purity audit forbids exactly this kind of growth). It touches a Spore only
through the public spore API and one transparent extra state key, `ghost`.

    python -m mantle ghost selftest
    python -m mantle ghost warm    <spore.png>
    python -m mantle ghost append  <spore.png> <user|assistant|system|tool> "<content>"
    python -m mantle ghost hydrate <spore.png>
    python -m mantle ghost status  <spore.png>
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional

from . import spore as _spore

GHOST_KEY = "ghost"                      # the transparent extra key inside a spore's state
DEFAULT_TTL_S = 300                      # provider prompt caches are short-lived (minutes)
SUBSTRATE_NAME = "local-prompt-cache"    # the shipped stand-in; real adapters override this


class GhostError(Exception):
    """A cache-ghost operation could not proceed (e.g. no pointer, or a torn cache blob)."""


# ---------------------------------------------------------------------------
# The substrate interface + a file-backed stand-in for the provider cache
# ---------------------------------------------------------------------------

class GhostSubstrate:
    """A warm-prefix store standing in for an LLM provider's prompt cache.

    Real adapters implement these four methods against a provider's caching API. Keys are
    content-addressed (a hash of the warmed prefix); values are opaque bytes to the substrate.
    """

    name = "abstract"

    def warm(self, key: str, blob: bytes, ttl_s: int) -> None:
        raise NotImplementedError

    def extend(self, key: str, blob: bytes, ttl_s: int) -> bool:
        """Refresh an existing warm key with a longer prefix; False if it had lapsed."""
        raise NotImplementedError

    def fetch(self, key: str) -> Optional[bytes]:
        """Return the warm blob, or None if the key is cold (evicted / expired)."""
        raise NotImplementedError

    def evict(self, key: str) -> None:
        raise NotImplementedError

    def alive(self, key: str) -> bool:
        return self.fetch(key) is not None


class LocalPromptCache(GhostSubstrate):
    """A JSON-file stand-in for the provider's prompt cache: TTL + eviction, nothing else.

    It deliberately lives OUTSIDE the PNG (default: beside it, `<png>.cache.json`) because the
    whole point of ghost mode is that the living body sits off-PNG, in borrowed memory.
    """

    name = SUBSTRATE_NAME

    def __init__(self, path: str, clock=time.time):
        self.path = path
        self._clock = clock

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def _save(self, store: Dict[str, Any]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(store, f)
        os.replace(tmp, self.path)

    def _live_entry(self, store: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
        ent = store.get(key)
        if not ent:
            return None
        if ent.get("expires_at", 0) <= self._clock():
            return None                  # lapsed: the provider would have dropped the prefix
        return ent

    def warm(self, key: str, blob: bytes, ttl_s: int) -> None:
        store = self._load()
        store[key] = {"blob": blob.decode("utf-8"),
                      "warmed_at": self._clock(),
                      "expires_at": self._clock() + ttl_s,
                      "bytes": len(blob)}
        self._save(store)

    def extend(self, key: str, blob: bytes, ttl_s: int) -> bool:
        store = self._load()
        if self._live_entry(store, key) is None:
            return False
        store[key] = {"blob": blob.decode("utf-8"),
                      "warmed_at": store[key].get("warmed_at", self._clock()),
                      "expires_at": self._clock() + ttl_s,   # every new request keeps it warm
                      "bytes": len(blob)}
        self._save(store)
        return True

    def fetch(self, key: str) -> Optional[bytes]:
        store = self._load()
        ent = self._live_entry(store, key)
        return ent["blob"].encode("utf-8") if ent else None

    def evict(self, key: str) -> None:
        store = self._load()
        if key in store:
            del store[key]
            self._save(store)


# ---------------------------------------------------------------------------
# Body <-> cache blob, and the ghost pointer carried in the PNG
# ---------------------------------------------------------------------------

def _body_of(state: Dict[str, Any]) -> Dict[str, Any]:
    """The living body a provider would cache: the whole Spore state minus the ghost pointer.

    The pointer is metadata about the cache, not part of the body, so stripping it keeps the
    cache key stable across re-warms and avoids a pointer-references-its-own-hash cycle.
    """
    return {k: v for k, v in state.items() if k != GHOST_KEY}


def _blob(body: Dict[str, Any]) -> bytes:
    return json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _fingerprint(body: Dict[str, Any]) -> str:
    return hashlib.sha256(_blob(body)).hexdigest()[:16]


def _cache_key(state: Dict[str, Any]) -> str:
    """A content-addressed key over the STABLE identity of the seed (birth + name + task).

    A provider keys its cache by the prefix hash; here the key names the lineage so every
    re-warm of the same Spore lands on the same slot, mirroring a warm prefix being refreshed.
    """
    ident = state.get("identity", {})
    seed = f"{ident.get('spore_name')}|{ident.get('created_at')}|{ident.get('task')}"
    return "ghost-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]


def _latest_id(state: Dict[str, Any]) -> int:
    conv = state.get("conversation", [])
    return conv[-1]["id"] if conv else -1


def _write_pointer(path: str, state: Dict[str, Any], pointer: Dict[str, Any]) -> None:
    """Persist the ghost pointer into the PNG by regenerating from canonical state.

    `state[GHOST_KEY]` round-trips through spore.py untouched (it serialises the whole state
    dict), so the pure seed code never learns about ghosts.
    """
    state[GHOST_KEY] = pointer
    _spore.render_spore(state, path, status=state.get("display", {}).get("status", "ACTIVE"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def default_substrate(path: str) -> LocalPromptCache:
    """The shipped stand-in cache that lives beside the PNG (off-PNG, as ghost mode requires)."""
    return LocalPromptCache(path + ".cache.json")


def warm(path: str, substrate: Optional[GhostSubstrate] = None,
         ttl_s: int = DEFAULT_TTL_S) -> Dict[str, Any]:
    """Push the Spore's body into the cache substrate and record the ghost pointer in the PNG."""
    substrate = substrate or default_substrate(path)
    state = _spore.read_spore(path)["state"]
    body = _body_of(state)
    key = _cache_key(state)
    substrate.warm(key, _blob(body), ttl_s)
    pointer = {
        "substrate": substrate.name,
        "cache_key": key,
        "synced_entry_id": _latest_id(state),
        "prefix_fingerprint": _fingerprint(body),
        "ttl_s": ttl_s,
        "warmed_at": _spore._now(),
        "note": ("body warmed in the provider prompt cache; the PNG stays the dry fossil seed "
                 "and can rehydrate it if the cache lapses"),
    }
    _write_pointer(path, state, pointer)
    return {"status": "WARM", "cache_key": key, "synced_entry_id": pointer["synced_entry_id"],
            "bytes_warmed": len(_blob(body)), "substrate": substrate.name}


def append(path: str, role: str, content: str,
           substrate: Optional[GhostSubstrate] = None,
           ttl_s: int = DEFAULT_TTL_S) -> Dict[str, Any]:
    """Append a turn, then sync it to the cache as a DELTA when warm, or re-warm when cold.

    The PNG is always grown first (the seed stays dry); the cache is updated to match. Returns
    what a real client would have paid to send this turn: only the delta while warm, the whole
    body on a cold start.
    """
    substrate = substrate or default_substrate(path)

    before = _spore.read_spore(path)["state"]
    res = _spore.append_turn(path, role, content)
    if not res.get("appended"):
        return {"appended": False, "reason": res.get("reason"), "status": res.get("status")}

    state = _spore.read_spore(path)["state"]
    body = _body_of(state)
    key = _cache_key(state)

    pointer = before.get(GHOST_KEY)
    delta_bytes = len(content.encode("utf-8"))
    full_bytes = len(_blob(body))

    warm_ok = bool(pointer) and substrate.extend(key, _blob(body), ttl_s)
    if warm_ok:
        sent, sent_bytes, status = "delta", delta_bytes, "WARM"
    else:
        substrate.warm(key, _blob(body), ttl_s)          # cold start: re-warm the whole prefix
        sent, sent_bytes, status = "full", full_bytes, "REWARMED"

    new_pointer = {
        "substrate": substrate.name,
        "cache_key": key,
        "synced_entry_id": _latest_id(state),
        "prefix_fingerprint": _fingerprint(body),
        "ttl_s": ttl_s,
        "warmed_at": _spore._now(),
        "note": (pointer or {}).get("note", "cache-ghost body"),
    }
    _write_pointer(path, state, new_pointer)
    return {"appended": True, "status": status, "sent": sent, "bytes_sent": sent_bytes,
            "body_bytes": full_bytes, "entry_count": len(state.get("conversation", [])),
            "cache_key": key}


def hydrate(path: str, substrate: Optional[GhostSubstrate] = None) -> Dict[str, Any]:
    """Return the living body, from the cache when warm, else rebuilt from the PNG fossil.

    Either way the result reflects the LATEST PNG: any PNG deltas newer than the cache are
    folded on top, and on a cold cache the whole body comes from the seed. This is the proof
    that the seed stays dry -- the Spore never depends on the cache to survive.
    """
    substrate = substrate or default_substrate(path)
    info = _spore.read_spore(path)
    state = info["state"]
    fossil = _body_of(state)
    pointer = state.get(GHOST_KEY)

    if pointer and substrate.alive(pointer["cache_key"]):
        cached = json.loads(substrate.fetch(pointer["cache_key"]).decode("utf-8"))
        # Reconcile: the PNG is canonical (RULE: the latest PNG is the living copy). If the
        # cache is behind the fossil, trust the fossil; the cache was simply not yet re-warmed.
        cached_latest = cached.get("conversation", [])[-1]["id"] if cached.get("conversation") else -1
        source = "cache" if cached_latest >= _latest_id(state) else "cache+png"
        body = cached if source == "cache" else fossil
        return {"source": source, "rehydrated": False, "body": body,
                "corrections": info["corrections"], "cache_key": pointer["cache_key"]}

    # COLD: the ghost has no warm body. Rebuild wholly from the PNG seed.
    return {"source": "png", "rehydrated": True, "body": fossil,
            "corrections": info["corrections"],
            "cache_key": pointer["cache_key"] if pointer else None}


def status(path: str, substrate: Optional[GhostSubstrate] = None) -> Dict[str, Any]:
    """Report where the body currently lives and whether the fossil and cache agree."""
    substrate = substrate or default_substrate(path)
    state = _spore.read_spore(path)["state"]
    pointer = state.get(GHOST_KEY)
    if not pointer:
        return {"ghost": False, "state": "NO-GHOST",
                "detail": "this Spore has never been warmed; it lives entirely in its PNG"}
    alive = substrate.alive(pointer["cache_key"])
    latest = _latest_id(state)
    behind = latest - pointer.get("synced_entry_id", latest)
    return {
        "ghost": True,
        "state": "WARM" if alive else "COLD",
        "cache_key": pointer["cache_key"],
        "substrate": pointer.get("substrate"),
        "latest_entry_id": latest,
        "synced_entry_id": pointer.get("synced_entry_id"),
        "unsynced_deltas": max(0, behind),
        "detail": ("body is warm in the cache; the PNG is the dry fossil"
                   if alive else
                   "cache lapsed; the body lives only in the PNG until the next warm"),
    }


# ---------------------------------------------------------------------------
# Self-test: prove the continuum, the linear delta cost, and the dry-seed law
# ---------------------------------------------------------------------------

class _Clock:
    """A hand-cranked clock so the self-test can expire the cache deterministically."""

    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def selftest(verbose: bool = True) -> bool:
    import tempfile
    import shutil

    checks, problems = [], []

    def ck(name, cond, detail=""):
        checks.append((name, bool(cond), detail))
        if not cond:
            problems.append(f"{name}: {detail}")

    d = tempfile.mkdtemp(prefix="ghost_test_")
    try:
        p = os.path.join(d, "ghost.png")
        clock = _Clock()
        cache = LocalPromptCache(p + ".cache.json", clock=clock)

        # 1. a normal Spore, born in its PNG, no ghost yet
        _spore.create_spore("GHOST-SEED", "sustain through the cache", author="Jody", path=p)
        _spore.append_turn(p, "user", "what are you?")
        _spore.append_turn(p, "assistant",
                           "I am a cache-ghost Spore: my body can live in the provider's prompt "
                           "cache while my PNG stays the dry seed.")
        st0 = status(p, cache)
        ck("starts with no ghost", st0["state"] == "NO-GHOST", str(st0))
        ck("PNG is a valid standalone seed before warming", _spore.verify_spore(p)["ok"])

        # 2. warm the body into the cache; the PNG must still verify as a pure Spore
        w = warm(p, cache, ttl_s=300)
        ck("warm reports WARM", w["status"] == "WARM", str(w))
        ck("PNG still a valid standalone seed after warming", _spore.verify_spore(p)["ok"])
        ck("status is WARM after warming", status(p, cache)["state"] == "WARM")

        # 3. run turns through the warm cache: each should send only the DELTA
        sent_bytes, body_bytes = [], []
        for i in range(6):
            r = append(p, "user", "D" * 300, substrate=cache, ttl_s=300)
            clock.advance(10)                       # time passes, but < TTL: stays warm
            ck(f"turn {i}: appended to PNG", r["appended"], str(r))
            ck(f"turn {i}: sent a delta while warm", r["sent"] == "delta", str(r))
            sent_bytes.append(r["bytes_sent"])
            body_bytes.append(r["body_bytes"])
        ck("delta cost stays ~constant per turn (linear, not the whole body)",
           max(sent_bytes) - min(sent_bytes) <= 8, f"sent={sent_bytes}")
        ck("a turn's uploaded delta is far smaller than the whole body",
           max(sent_bytes) * 3 < min(body_bytes), f"sent={sent_bytes} body={body_bytes}")

        # 4. hydrate while warm: body comes from the cache
        h_warm = hydrate(p, cache)
        ck("warm hydrate reads from the cache", h_warm["source"] in ("cache", "cache+png"),
           str(h_warm["source"]))
        ck("warm hydrate is not a rehydration", h_warm["rehydrated"] is False)

        conv_before = _spore.read_spore(p)["state"]["conversation"]

        # 5. the provider evicts the prefix (TTL lapses). The body is now bodiless...
        clock.advance(10_000)                       # push well past the 300s TTL
        st_cold = status(p, cache)
        ck("cache lapses to COLD when the TTL passes", st_cold["state"] == "COLD", str(st_cold))

        # 6. ...but the SEED STAYED DRY: hydrate rebuilds the whole body from the PNG alone
        h_cold = hydrate(p, cache)
        ck("cold hydrate rebuilds from the PNG fossil", h_cold["source"] == "png", str(h_cold))
        ck("cold hydrate is flagged as a rehydration", h_cold["rehydrated"] is True)
        ck("rehydrated body == the body from before the cache died",
           h_cold["body"]["conversation"] == conv_before,
           "conversation drifted across a cache death")

        # 7. a cold-start turn re-warms the whole prefix, then deltas resume
        r_cold = append(p, "assistant", "the cache lapsed, so I re-warmed from my seed",
                        substrate=cache, ttl_s=300)
        ck("cold-start turn sends the whole body once", r_cold["sent"] == "full", str(r_cold))
        r_hot = append(p, "user", "and now?", substrate=cache, ttl_s=300)
        ck("the next turn is a delta again", r_hot["sent"] == "delta", str(r_hot))

        # 8. through all of it, the PNG never stopped being a pure, verifiable Spore
        ck("PNG verifies as a pure Spore at the end", _spore.verify_spore(p)["ok"])
        purity = _body_of(_spore.read_spore(p)["state"])
        ck("the ghost pointer is metadata, not body (stripped cleanly)",
           GHOST_KEY not in purity)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    if verbose:
        print("=" * 66)
        print("MANTLE CACHE-GHOST SELF-TEST")
        print("=" * 66)
        for name, ok, detail in checks:
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
                  + (f"   ({detail})" if detail and not ok else ""))
        print("-" * 66)
        print(f"RESULT: {'PASS' if not problems else 'FAIL'}   "
              f"({len(checks) - len(problems)}/{len(checks)} checks)")
        print("=" * 66)
    return not problems
