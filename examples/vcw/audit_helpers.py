#!/usr/bin/env python3
"""
audit_helpers.py  --  shared scaffolding for the audit/test harnesses (Mantle v2.3)

audit.py, audit_mind.py and test_invariants.py independently re-implemented the same four
helpers (a row record, a fail-open check wrapper, a row printer, and an exception-expectation
guard). They live here once so the three harnesses stay in lock-step and read clearly. This
module contains NO assertions of its own -- it only standardizes how checks are recorded and
shown; every correctness check still lives in its harness.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

PASS, FAIL, NA = "PASS", "FAIL", "N/A"


def make_row(code: str, requirement: str, result: Any, hf: str = None, note: str = "") -> Dict[str, Any]:
    """One audit-table row. `result` may be a bool (True->PASS, False->FAIL) or an explicit
    status string (PASS/FAIL/NA), so both calling styles in the harnesses are supported."""
    if isinstance(result, bool):
        result = PASS if result else FAIL
    return {"code": code, "requirement": requirement, "hf": hf, "result": result, "note": note}


def safe(rows: List[Dict[str, Any]], code: str, requirement: str, hf: str,
         fn: Callable[[], Tuple[bool, str]]) -> None:
    """Run a check `fn` that returns (ok, note) and append its row. Fail-open: an exception in a
    check becomes a FAIL with evidence, never a crash of the harness."""
    try:
        ok, note = fn()
    except Exception as e:  # noqa: BLE001 -- a check bug is a FAIL with evidence, not a crash
        ok, note = False, "check crashed: %s: %s" % (type(e).__name__, e)
    rows.append(make_row(code, requirement, ok, hf, note))


def print_row(r: Dict[str, Any], width: int, result_width: int = 9) -> None:
    hf = (" [%s]" % r["hf"]) if r["hf"] else ""
    print("  %-4s %-*s %-*s %s%s" % (r["code"], result_width, r["result"], width,
                                     r["requirement"], r["note"], hf))


def expect_raise(fn: Callable[[], Any], exc) -> Tuple[bool, str]:
    """Return (True, ...) iff calling fn() raises `exc`. The standard shape for guard tests."""
    try:
        fn()
        return False, "expected %s, nothing raised" % getattr(exc, "__name__", exc)
    except exc:
        return True, "raised %s as required" % getattr(exc, "__name__", exc)
    except Exception as e:  # noqa: BLE001 -- a different exception is still a failure, with evidence
        return False, "expected %s, got %s: %s" % (getattr(exc, "__name__", exc),
                                                   type(e).__name__, e)
