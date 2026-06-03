#!/usr/bin/env python3
"""
skills.py  --  The Inner Voice / Self-Inquiry skill (Mantle v2.1)

The first skill most AppAIs learn: to speak to themselves. The agent issues a framed,
bounded sub-query to its own MIND -- separate from heartbeat cognition -- and remembers the
answer. Three modes:

    neutral   a plain question (self-exploration)
    search    a question needing fresh/external data (if the model has search)
    oppose    devil's advocate -- ask the MIND to argue AGAINST an idea so it can reflect
              against resistance instead of in an echo chamber

PROVENANCE (the thing to get right): an answer the agent gets by asking ITSELF is INFERRED,
not observed. It must never be laundered into a remembered "fact". So:
  - factual / search answers land in `discoveries`, tagged verified=False, confidence="inferred";
  - dialectic self-debate lands in `thoughts` (private);
  - nothing here ever writes the `facts` band. Promotion to a verified fact requires external,
    cited evidence -- handled elsewhere, deliberately.

A WASTE BUDGET caps self-conversation so the agent cannot spiral (Failure is not the end;
waste is). This is a MIND-mediated reflex: the orchestration is Body code; the answer needs
the model.
"""
from __future__ import annotations

import hashlib
from typing import Any, Callable, Optional

from drivers import make_entry

_STANCE = {
    "neutral": "",
    "search":  "Use up-to-date, external information to answer. ",
    "oppose":  "Argue the strongest possible case AGAINST the following idea, so I can "
               "stress-test my own thinking. ",
}


class InnerVoice:
    def __init__(self, organism, model: Callable[[str], str], max_calls: int = 8) -> None:
        self.org = organism
        self.model = model                 # any callable: prompt -> answer text
        self.max_calls = max_calls
        self.calls = 0

    def _frame(self, question: str, mode: str) -> str:
        name = self.org.body.identity_name()
        return ("This is a Mantle Agent named %s. %sI have the following question for you: %s"
                % (name, _STANCE.get(mode, ""), question))

    def ask(self, question: str, mode: str = "neutral") -> Optional[str]:
        # waste guard
        if self.calls >= self.max_calls:
            self.org.immune_event("waste_guard",
                                  {"skill": "inner_voice", "limit": self.max_calls})
            return None
        self.calls += 1

        prompt = self._frame(question, mode)
        answer = self.model(prompt)         # the side-channel MODEL.REQUEST

        # trace the model call (secrets would be redacted by the immune system)
        self.org.prime.append("brain", make_entry(
            {"MODEL.REQUEST": {"skill": "inner_voice", "mode": mode,
                               "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                               "answer_hash": hashlib.sha256(answer.encode()).hexdigest()[:16]}},
            opcode="MODEL.REQUEST", author="BODY"))

        # store with honest provenance -- inferred, never a verified fact
        record = make_entry(
            {"question": question, "answer": answer, "mode": mode},
            opcode="INNER_VOICE", author="MIND", source="inner-voice",
            verified=False, confidence="inferred")

        if mode == "oppose":
            self.org.prime.append("thoughts", record)      # private reflection
            band = "thoughts"
        else:
            self.org.prime.append("discoveries", record)   # inferred knowledge, NOT facts
            band = "discoveries"
        return answer, band  # type: ignore[return-value]


def stub_model(prompt: str) -> str:
    """A deterministic offline stand-in for a real MIND, so the demo needs no network/key."""
    if "AGAINST" in prompt:
        return ("Counterpoint: the assumption may not hold in edge cases; consider the "
                "opposite and what evidence would change your mind.")
    if "up-to-date" in prompt:
        return "[search result] As of the latest data, the answer is X (source: example.org)."
    return "A considered answer to: %s" % prompt.split("question for you:")[-1].strip()
