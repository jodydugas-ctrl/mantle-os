#!/usr/bin/env python3
"""
mantle.ghost_anthropic  --  the REAL cache-ghost substrate: Anthropic prompt caching.

`AnthropicPromptCache` is a `GhostSubstrate` adapter that haunts an actual provider cache
instead of the file-backed stand-in. It is the honest realization of what `mantle.ghost`
simulates -- and honesty here means three departures from the stand-in:

    WRITE-ONLY.   A provider prompt cache can only be spoken INTO. There is no fetch API;
                  `fetch()` always returns None and `hydrate()` therefore always rebuilds
                  from the PNG fossil (the ghost layer handles that via `write_only=True`).
                  Warmth between requests is PREDICTED (last warm time + TTL) and only
                  OBSERVED after the fact, as `cache_read_input_tokens` on a response.

    COMPUTE, NOT BANDWIDTH.  The full prefix travels on every request. A warm hit means the
                  provider skips PREFILL COMPUTE over the cached span (~0.1x input price and
                  a large latency drop), not that fewer bytes were sent.

    MINIMUM PREFIX.  Prefixes below a model-dependent floor (1024-4096 tokens) are SILENTLY
                  never cached. The adapter publishes `min_prefix_tokens` so the ghost layer
                  can refuse to pretend (`TOO-SMALL-TO-HAUNT`) instead of reporting a warmth
                  that does not exist.

How the verbs map onto the Messages API:

    warm(blob)    one `messages.create` with `max_tokens=0` -- the documented pre-warm shape:
                  the API runs prefill (writing the cache at the `cache_control` breakpoints)
                  and returns immediately with no billed output.
    extend(blob)  the same request; a cache READ refreshes the TTL at read price. Returns
                  True when the response shows `cache_read_input_tokens > 0` (observed warm).
                  On a miss the very same request already re-wrote the cache, so the adapter
                  marks the key pre-warmed and the ghost layer's follow-up `warm()` becomes a
                  no-op rather than a duplicate spend.
    fetch()       None, always. evict() only forgets locally -- a provider cache cannot be
                  evicted on demand; it lapses.

Breakpoint budget (max 4 `cache_control` markers per request), spent per the CACHE-HAUNT
prefix law (genome -> consolidated context -> append-only log -> volatile delta):

    #1  the GENESIS line (identity-at-birth + tools protocol) -- system block; never
        invalidated short of rebirth.
    #2  the ROLLING LOG TAIL -- the delta lines as the first user block; moves every turn,
        giving incremental hits as the conversation grows.
    #3, #4  reserved (consolidated-context split and phenotype experiments).

Phase-2 tissue: this module needs the `anthropic` SDK and an API key, so NOTHING else in
Mantle imports it -- `mantle.ghost`'s selftest, the Stage-1 gate, and the spore purity audit
all stay pure-stdlib, offline, and keyless. The import of `anthropic` is lazy (first use).

    from mantle import ghost, ghost_anthropic
    sub = ghost_anthropic.AnthropicPromptCache(model="claude-opus-4-8", ttl="1h")
    ghost.warm("spore.png", substrate=sub)              # real pre-warm request
    ghost.append("spore.png", "user", "...", substrate=sub)
    ghost.status("spore.png", substrate=sub)            # PREDICTED-WARM / PREDICTED-COLD
    sub.last_usage                                      # observed cache telemetry

    python -m mantle.ghost_anthropic <spore.png> [model]   # one real warm, with telemetry
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from .ghost import DEFAULT_TTL_S, GhostSubstrate

# The provider's minimum cacheable prefix, by model (tokens). Below it the API accepts the
# request but silently writes no cache entry (`cache_creation_input_tokens: 0`). Unknown
# models get the conservative ceiling.
MIN_PREFIX_TOKENS = {
    "claude-opus-4-8": 4096,
    "claude-opus-4-7": 4096,
    "claude-opus-4-6": 4096,
    "claude-opus-4-5": 4096,
    "claude-haiku-4-5": 4096,
    "claude-fable-5": 2048,
    "claude-sonnet-4-6": 2048,
    "claude-sonnet-4-5": 1024,
}
DEFAULT_MIN_PREFIX_TOKENS = 4096

# Cache-write premiums by TTL (economics; reads are ~0.1x regardless).
TTL_CHOICES = {"5m": 300, "1h": 3600}


class AnthropicPromptCache(GhostSubstrate):
    """A write-only `GhostSubstrate` over Anthropic prompt caching.

    Args:
        model:  the model whose cache is haunted (caches are model-scoped: switching models
                is always a cold start).
        ttl:    "5m" (write 1.25x, break-even 2 warm reads) or "1h" (write 2x, break-even 3).
                This is the REAL TTL; the `ttl_s` the ghost layer passes per call is advisory
                and only checked for gross mismatch.
        client: an `anthropic.Anthropic` instance; constructed lazily from the environment
                (ANTHROPIC_API_KEY / an `ant auth login` profile) when omitted.
    """

    name = "anthropic-prompt-cache"
    write_only = True

    def __init__(self, model: str = "claude-opus-4-8", ttl: str = "5m", client=None):
        if ttl not in TTL_CHOICES:
            raise ValueError(f"ttl must be one of {sorted(TTL_CHOICES)}, not {ttl!r}")
        self.model = model
        self.ttl = ttl
        self.ttl_s = TTL_CHOICES[ttl]
        self.min_prefix_tokens = MIN_PREFIX_TOKENS.get(model, DEFAULT_MIN_PREFIX_TOKENS)
        self._client = client
        self._warmed_at: Dict[str, float] = {}     # key -> monotonic time of last warm/extend
        self._prewarmed: set = set()               # keys a failed extend() already re-wrote
        self.last_usage: Optional[Dict[str, int]] = None   # observed telemetry, last request

    # -- lazy client -------------------------------------------------------------------

    def _cli(self):
        if self._client is None:
            import anthropic                        # deliberate lazy import: optional dep
            self._client = anthropic.Anthropic()
        return self._client

    def _cache_control(self) -> Dict[str, str]:
        cc = {"type": "ephemeral"}
        if self.ttl != "5m":
            cc["ttl"] = self.ttl
        return cc

    # -- the one real request shape ------------------------------------------------------

    def _prewarm_request(self, blob: bytes) -> Dict[str, int]:
        """One `max_tokens=0` pre-warm: prefill runs, cache writes/reads, nothing generates.

        Breakpoint #1 sits on the genesis system block; breakpoint #2 rides the rolling tail
        of the delta log. The placeholder user text is required by the API and sits AFTER the
        last breakpoint, so it never pollutes the cached span.
        """
        text = blob.decode("utf-8")
        genesis_line, _, delta_log = text.partition("\n")
        cc = self._cache_control()
        message_content = [{
            "type": "text",
            "text": delta_log or "(no turns yet)",
            "cache_control": cc,                    # breakpoint 2: rolling log tail
        }]
        resp = self._cli().messages.create(
            model=self.model,
            max_tokens=0,
            system=[{
                "type": "text",
                "text": ("You are the warm body of a Mantle cache-ghost Spore. Your genesis "
                         "record and append-only conversation log follow.\nGENESIS: "
                         + genesis_line),
                "cache_control": cc,                # breakpoint 1: immutable genesis
            }],
            messages=[{"role": "user", "content": message_content},
                      {"role": "user", "content": "warmup"}],
        )
        u = resp.usage
        self.last_usage = {
            "input_tokens": getattr(u, "input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
            "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
        }
        return self.last_usage

    # -- GhostSubstrate ------------------------------------------------------------------

    def warm(self, key: str, blob: bytes, ttl_s: int = DEFAULT_TTL_S) -> None:
        if key in self._prewarmed:
            self._prewarmed.discard(key)            # a failed extend() already paid this write
            return
        self._prewarm_request(blob)
        self._warmed_at[key] = time.monotonic()

    def extend(self, key: str, blob: bytes, ttl_s: int = DEFAULT_TTL_S) -> bool:
        usage = self._prewarm_request(blob)
        self._warmed_at[key] = time.monotonic()
        if usage["cache_read_input_tokens"] > 0:
            return True                             # OBSERVED warm: the prefix was served hot
        # Miss: this very request already re-wrote the cache; don't let the ghost layer's
        # follow-up warm() buy the same write twice.
        self._prewarmed.add(key)
        return False

    def fetch(self, key: str) -> Optional[bytes]:
        return None                                 # the write-only law: never readable

    def evict(self, key: str) -> None:
        self._warmed_at.pop(key, None)              # forget locally; the provider only lapses

    def alive(self, key: str) -> bool:
        """PREDICTED warmth only -- the ground truth is the next request's usage."""
        t = self._warmed_at.get(key)
        return t is not None and (time.monotonic() - t) < self.ttl_s


def _main(argv) -> int:
    if len(argv) < 2:
        print("usage: python -m mantle.ghost_anthropic <spore.png> [model] [5m|1h]")
        return 1
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. This adapter performs REAL requests; the "
              "offline stand-in is `python -m mantle ghost ...` (no key, no network).")
        return 1
    from . import ghost
    model = argv[2] if len(argv) > 2 else "claude-opus-4-8"
    ttl = argv[3] if len(argv) > 3 else "5m"
    sub = AnthropicPromptCache(model=model, ttl=ttl)
    result = ghost.warm(argv[1], substrate=sub, ttl_s=sub.ttl_s)
    print(result)
    if sub.last_usage:
        print("observed usage:", sub.last_usage)
        if result.get("status") == "WARM" and not sub.last_usage["cache_creation_input_tokens"] \
                and not sub.last_usage["cache_read_input_tokens"]:
            print("NOTE: zero cache tokens observed -- prefix likely below the model's "
                  f"minimum ({sub.min_prefix_tokens} tokens); the spore is TOO SMALL TO HAUNT.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_main(sys.argv))
