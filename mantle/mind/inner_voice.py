#!/usr/bin/env python3
"""
mantle.mind.inner_voice  --  the Inner Voice / Self-Inquiry skill (Mantle v3)

The first skill most AppAIs learn: to speak to themselves. A framed, bounded sub-query to
the MIND, separate from heartbeat cognition. Three modes:

    neutral   a plain question (self-exploration)
    search    a question needing fresh/external data (if the model has search)
    oppose    devil's advocate -- argue AGAINST an idea, to reflect against resistance

PROVENANCE (the thing to get right): an answer the agent gets by asking ITSELF is
INFERRED, not observed. It is never laundered into a remembered "fact":
  - factual/search answers land in `discoveries`, tagged verified=False, confidence="inferred"
  - dialectic self-debate lands in `thoughts` (private)
  - NOTHING here ever writes the `facts` band; promotion requires external, cited
    evidence through `Memory.promote_to_fact` -- deliberately, elsewhere.

A WASTE BUDGET caps self-conversation (failure is not the end; waste is).
"""
from __future__ import annotations

import hashlib
from typing import Any, Callable, Optional, Tuple

from ..vcw.entry import make_entry
from .containment import guarded_write

_STANCE = {
    "neutral": "",
    "search":  "Use up-to-date, external information to answer. ",
    "oppose":  "Argue the strongest possible case AGAINST the following idea, so I can "
               "stress-test my own thinking. ",
}


class InnerVoice:
    def __init__(self, organism, model: Callable[[str], str], max_calls: int = 8) -> None:
        self.org = organism
        self.model = model
        self.max_calls = max_calls
        self.calls = 0

    def _frame(self, question: str, mode: str) -> str:
        name = self.org.body.identity_name()
        return ("This is a Mantle Agent named %s. %sI have the following question for "
                "you: %s" % (name, _STANCE.get(mode, ""), question))

    def ask(self, question: str, mode: str = "neutral") -> Optional[Tuple[str, str]]:
        """Ask the inner voice. Returns (answer, band-it-landed-in) or None on the waste
        guard. The answer's provenance is always inferred; `facts` is never written."""
        if self.calls >= self.max_calls:
            self.org.immune_event("waste_guard",
                                  {"skill": "inner_voice", "limit": self.max_calls})
            return None
        self.calls += 1

        prompt = self._frame(question, mode)
        answer = self.model(prompt)

        # trace the model call (hashes only; secrets would be redacted by the boundary)
        guarded_write(self.org, "brain", make_entry(
            {"MODEL.REQUEST": {"skill": "inner_voice", "mode": mode,
                               "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                               "answer_hash": hashlib.sha256(answer.encode()).hexdigest()[:16]}},
            opcode="MODEL.REQUEST", author="BODY", authorship="BODY"))

        record = make_entry(
            {"question": question, "answer": answer, "mode": mode},
            opcode="INNER_VOICE", author="MIND", source="inner-voice",
            verified=False, confidence="inferred")

        if mode == "oppose":
            guarded_write(self.org, "thoughts", record)       # private reflection
            band = "thoughts"
        else:
            # inferred knowledge belongs in discoveries, NOT facts. discoveries is outside
            # the MIND write surface, so the BODY's Memory organ performs the write -- the
            # MIND requested, the Body acted, the provenance stays inferred.
            self.org.memory.append("discoveries", record)
            band = "discoveries"
        return answer, band
