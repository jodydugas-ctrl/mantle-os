#!/usr/bin/env python3
"""
mind.py  --  The reference MIND fusion (Phase 2), PROVIDER-AGNOSTIC (Mantle v2.3)

The MIND is a fused LLM. Mantle keeps it sharply bounded by the BODY -- this module makes that
boundary executable, not just prose:

  * the MIND receives only the deterministically-assembled, already-resolved, already-veiled
    context snapshot (the Nervous System) -- never a raw reference;
  * it may write ONLY the `thoughts` band (private) and the `brain` band (dispatch + model trace).
    Any other band is refused by the Body and logged as an immune event -- so the MIND can only
    ever EXTEND, never break, the Body;
  * it PROPOSES Special Instructions; the Body applies them (`body.mind_propose_special`);
  * it cannot touch the Genome and cannot self-promote a skill -- a cultivated skill must pass
    `trial` (and the static sandbox gate) before the BODY calcifies it.

THE MODEL IS A PLUGGABLE TRANSPORT -- THERE IS NO VENDOR CODE IN THE BODY.
The MIND talks to its model through a single callable `model(prompt) -> text`. Nothing here is
tied to a particular company. The reference transport is **OpenRouter** -- one OpenAI-compatible
endpoint, one keyfile, and a model-id STRING that selects ANY provider/model -- which is the
deliberate choice for this system. But the transport is fully customizable: any callable works,
including the offline deterministic `stub_mind` so the demo and the Stage-2 audit need no network
or key, or `openai_compatible_model(...)` pointed at a local server. You change providers by
changing a STRING, never the Body code. See the worked examples at the bottom of this file.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

from drivers import make_entry, trial
from redact import redact

# The ONLY bands a fused MIND may write. Everything else is the Body's, permanently.
WRITE_SURFACE = ("thoughts", "brain")


def _h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ============================================================================
# Pluggable model transports  (the one vendor seam -- a plain callable)
# ============================================================================
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_keyfile(path: str) -> str:
    """Read the single model credential from a keyfile (the Genome's KEYFILE_PATH; Phase 2 only).
    The value is a `secret_boundary`: it is redacted everywhere it could surface in senses/immune
    logs. One keyfile by default -- credential POOLS are an Extensions opt-in, never the default."""
    with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
        return f.read().strip()


def openai_compatible_model(api_key: str, model: str, *, url: str = OPENROUTER_URL,
                            system: Optional[str] = None, max_tokens: int = 1024,
                            timeout: int = 60,
                            extra_headers: Optional[Dict[str, str]] = None
                            ) -> Callable[[str], str]:
    """Return a `model(prompt) -> text` callable for ANY OpenAI-compatible chat endpoint -- the
    reference transport for OpenRouter, but equally a local llama.cpp/vLLM server or any compatible
    gateway. Pure standard library (urllib): NO vendor SDK. `model` is a provider-neutral id string
    -- swap the provider by changing that string, not this code.

    The HTTP call is built lazily so importing this module never requires a network or a key."""
    import urllib.request  # local import: stdlib only, and only touched when a real model is wired

    def _call(prompt: str) -> str:
        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({"model": model, "messages": messages,
                              "max_tokens": max_tokens}).encode("utf-8")
        headers = {"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    return _call


def openrouter_model(api_key: str, model: str, **kwargs: Any) -> Callable[[str], str]:
    """The system's reference transport: OpenAI-compatible, pointed at OpenRouter. `model` is a
    provider-neutral id string (e.g. 'anthropic/claude-...', 'openai/gpt-...',
    'google/gemini-...', 'meta-llama/llama-...'). Provider choice is one string; the Body is
    identical regardless."""
    kwargs.setdefault("url", OPENROUTER_URL)
    return openai_compatible_model(api_key, model, **kwargs)


def stub_mind(prompt: str) -> str:
    """An offline, deterministic stand-in MODEL so the demo + the Stage-2 audit need no key or
    network. Mirrors the rest of the repo's 'no network, no LLM' ethos."""
    return ("[offline MIND] The assembled context reads as coherent; I note it and propose no "
            "Body change. (%d chars of context considered.)" % len(prompt))


# ============================================================================
# The fused MIND -- bounded entirely by the Body
# ============================================================================
class Mind:
    def __init__(self, organism: Any, model: Callable[[str], str], *,
                 max_thoughts: int = 64) -> None:
        self.org = organism
        self.model = model                  # the pluggable transport: prompt -> text
        self.max_thoughts = max_thoughts    # a waste budget: the MIND cannot spiral
        self.thoughts_written = 0

    # ---- the bounded write surface (Body-enforced) -----------------------
    def _guarded_write(self, band: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """The single choke point for every MIND write. A write outside `thoughts`/`brain` is
        refused by the Body and recorded as an immune event -- the breach never executes."""
        if band not in WRITE_SURFACE:
            self.org.immune_event("mind_write_refused",
                                  {"band": band, "allowed": list(WRITE_SURFACE)})
            raise PermissionError("the MIND may write only %s, not %r"
                                  % (list(WRITE_SURFACE), band))
        return self.org.prime.append(band, entry)

    def _trace(self, kind: str, detail: Dict[str, Any]) -> None:
        """Record a model call to the brain band (the Body authors the trace; secrets redacted)."""
        self._guarded_write("brain", make_entry(
            {"MODEL." + kind: redact(detail)}, opcode="MODEL." + kind,
            author="BODY", authorship="BODY"))

    # ---- think: receive the assembled snapshot, reflect into thoughts ----
    def think(self, snapshot: Dict[str, Any], question: Optional[str] = None) -> Optional[str]:
        if self.thoughts_written >= self.max_thoughts:
            self.org.immune_event("waste_guard", {"organ": "mind", "limit": self.max_thoughts})
            return None
        prompt = question or self._frame(snapshot)
        self._trace("REQUEST", {"prompt_hash": _h(prompt)})
        answer = self.model(prompt)                         # the side-channel MODEL call
        self._trace("RESPONSE", {"answer_hash": _h(answer)})
        self.thoughts_written += 1
        # the MIND's reflection is private and INFERRED -- never laundered into a verified fact
        self._guarded_write("thoughts", make_entry(
            {"reflection": answer}, opcode="THINK", author="MIND",
            verified=False, confidence="inferred"))
        return answer

    def _frame(self, snapshot: Dict[str, Any]) -> str:
        return ("You are the fused MIND of a Mantle AppAI named %s. Your context has been "
                "assembled deterministically (every reference already resolved, the private "
                "`thoughts` band veiled). Reflect briefly; you may propose Body changes but you "
                "do not apply them.\n\nCONTEXT:\n%s"
                % (self.org.body.identity_name(),
                   json.dumps(snapshot, default=str)[:4000]))

    # ---- propose Special Instructions (the Body applies) -----------------
    def propose_special(self, text: str) -> Dict[str, Any]:
        """The MIND may only PROPOSE. The returned intent is NOT written; the Body applies it via
        `body.apply_special`, keeping steering a Body action."""
        return self.org.body.mind_propose_special(text)

    # ---- cultivate a skill (the Body calcifies, only after trial) --------
    def cultivate(self, band: str, code: str, entry: str,
                  cases: List[Tuple[Dict[str, Any], Any]],
                  signature: Dict[str, Any], capabilities: Dict[str, Any]
                  ) -> Optional[Dict[str, Any]]:
        """Learning -> instinct, under containment. The MIND cannot self-promote: the candidate
        must pass the static sandbox gate + `trial`, and then the BODY performs the calcify."""
        try:
            result = trial(code, entry, cases)              # static sandbox gate + proving cases
        except Exception as e:  # noqa: BLE001 -- a refused/failed candidate is not calcified
            self.org.immune_event("skill_refused", {"entry": entry, "reason": str(e)})
            return None
        if not result["ok"]:
            self.org.immune_event("skill_trial_failed", {"entry": entry, "detail": result})
            return None
        self.org.prime.calcify(
            band, code, entry=entry, signature=signature, capabilities=capabilities,
            provenance={"author": "MIND", "born_gen": self.org.prime.generation})
        return result

    # ---- cognition: the Phase-2 heartbeat extension ----------------------
    def cognize(self, org: Any = None) -> Optional[str]:
        """One cognition pulse: assemble a fully-resolved, veiled snapshot, then think. Pass this
        as the Heart's `cognition` callback so the SAME heartbeat that runs the Body now also
        thinks -- an extension of the reflex, never a replacement."""
        from organs import NervousSystem
        snapshot = NervousSystem(self.org).assemble()
        return self.think(snapshot)


# ============================================================================
# Worked examples -- the model is just a string; the Body code never changes
# ============================================================================
# Offline (no key, no network) -- exactly what the demo and Stage-2 audit use:
#
#     from mind import Mind, stub_mind
#     mind = Mind(org, stub_mind)
#     mind.cognize()                 # assemble context -> reflect into the private `thoughts` band
#
# A real model via OpenRouter (the system's reference transport). Provider/model is ONE STRING --
# the Body code below is identical no matter which you pick:
#
#     from mind import Mind, openrouter_model, load_keyfile
#     key = load_keyfile("~/.mantle/openrouter.key")        # the single model keyfile (Phase 2)
#
#     transport = openrouter_model(key, model="anthropic/claude-sonnet-4")        # one option ...
#     transport = openrouter_model(key, model="openai/gpt-4o")                    # ... or another ...
#     transport = openrouter_model(key, model="google/gemini-2.0-flash")          # ... or another ...
#     transport = openrouter_model(key, model="meta-llama/llama-3.1-70b-instruct")
#     # (model ids are operator-supplied and change over time -- use whatever you have access to)
#
#     mind = Mind(org, transport)    # <-- identical regardless of provider; no vendor SDK anywhere
#
# Any OpenAI-compatible endpoint (a local llama.cpp / vLLM server, a private gateway, ...):
#
#     from mind import openai_compatible_model
#     transport = openai_compatible_model("not-needed", model="local-model",
#                                         url="http://localhost:8080/v1/chat/completions")
#
# Or write your own transport -- a `model(prompt) -> text` callable is the entire contract.
