#!/usr/bin/env python3
"""
mantle.doctor  --  a deployment checkup (Mantle OS · §3)

Most real-world breakage in a living organism is not a logic bug -- it is a STALE VIEW: a
truncated write, a split copy on two drives, docs that drifted from the code. The doctor is
a deterministic health check that catches those before they bite:

  cube-verify           the Prime cube hashes/coheres (no silent corruption)
  ancestor-seals        every sealed ancestor still matches its fingerprint
  genesis-key           the SELF key still matches its recorded fingerprint (M2)
  ledger-nonnegative    the symbiosis ledger never went negative (the starvation law)
  docs-vs-code          no doc hardcodes an invariant count (the count is derived from the
                        code -- `mantle prove` prints it -- so prose can never drift stale);
                        docs-vs-code-organs ties the README's organ count to ORGAN_ORDER

`checkup(org, repo_root=...)` returns {ok, checks:[...]}; `ok` is False if any check fails.
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional


_NUMBER_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                 "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def _docs_vs_code(repo_root: str) -> Dict[str, Any]:
    """The coherence gate, inverted: NO doc may hardcode an invariant count. The live
    count comes from the code (`python -m mantle prove` prints it); a number written
    into prose goes stale the moment an invariant is added, so its presence IS the
    failure. Scans README.md and every markdown file under documents/."""
    pattern = re.compile(r"\b\d+(?:/\d+)?\s+(?:security\s+|executable\s+)?invariants\b",
                         re.IGNORECASE)
    offenders: List[str] = []
    targets = [os.path.join(repo_root, "README.md")]
    docs_dir = os.path.join(repo_root, "documents")
    for base, _dirs, files in os.walk(docs_dir):
        targets.extend(os.path.join(base, f) for f in files if f.endswith(".md"))
    if not os.path.isfile(targets[0]):
        return {"check": "docs-vs-code", "ok": False, "detail": "README.md not found"}
    for path in targets:
        try:
            with open(path, encoding="utf-8") as f:
                if pattern.search(f.read()):
                    offenders.append(os.path.relpath(path, repo_root))
        except OSError:
            continue
    return {"check": "docs-vs-code", "ok": not offenders,
            "detail": ("no hardcoded invariant counts (the count is derived: mantle prove)"
                       if not offenders else
                       "hardcoded invariant count in: %s" % ", ".join(offenders[:5]))}


def _docs_vs_code_organs(repo_root: str) -> Dict[str, Any]:
    """The same coherence gate for the organ count: the README's "<N> deterministic
    organs" claim must equal len(ORGAN_ORDER). Added after the ninth-organ molt left
    stale "eight organs" prose behind -- this class of drift is now caught mechanically."""
    from .core.organism import ORGAN_ORDER
    actual = len(ORGAN_ORDER)
    try:
        with open(os.path.join(repo_root, "README.md"), encoding="utf-8") as f:
            m = re.search(r"(\w+)\s+deterministic organs", f.read(), re.IGNORECASE)
    except OSError:
        return {"check": "docs-vs-code-organs", "ok": False, "detail": "README.md not found"}
    word = m.group(1).lower() if m else None
    claimed = _NUMBER_WORDS.get(word, int(word) if word and word.isdigit() else None)
    return {"check": "docs-vs-code-organs", "ok": claimed == actual,
            "detail": "README claims %s organs; ORGAN_ORDER has %d" % (claimed, actual)}


def checkup(org: Any, repo_root: Optional[str] = None) -> Dict[str, Any]:
    """Run the deployment checkup. Pass `repo_root` to include the docs-vs-code gate."""
    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    problems = org.prime.verify()
    add("cube-verify", problems == [], "" if not problems else "; ".join(problems[:2]))
    seal_issues = [p for c in org.ancestral for p in c.verify_seal()]
    add("ancestor-seals", not seal_issues, "; ".join(seal_issues[:2]))
    if org.body.has_key:
        add("genesis-key", org.body.key_fingerprint_consistent(),
            "" if org.body.key_fingerprint_consistent() else "key fingerprint mismatch")
    from .symbiosis import BAND, balance
    if BAND in org.prime.bands:
        add("ledger-nonnegative", balance(org) >= 0, "balance=%.2f" % balance(org))
    if repo_root:
        checks.append(_docs_vs_code(repo_root))
        checks.append(_docs_vs_code_organs(repo_root))

    return {"ok": all(c["ok"] for c in checks), "checks": checks}
