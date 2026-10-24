"""Fault injection & fail-closed (M22 22.2).

Faults across the runner, targets, oracles, drivers and tamper checks fail
**closed** — a fault is never silently green — and a case failure never aborts
the pack. Design: ``docs/prd/13-non-functional-requirements.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any

from pydantic import BaseModel

#: The surfaces faults are injected into.
FAULT_KINDS: tuple[str, ...] = ("runner", "target", "oracle", "driver", "tamper")


class FaultError(ValueError):
    """Raised when a fault was silently green (not fail-closed)."""


class FaultOutcome(BaseModel):
    """The outcome of an injected fault."""

    kind: str
    raised: bool
    fail_closed: bool
    detail: str = ""


def run_fault(kind: str, fn: Callable[[], Any]) -> FaultOutcome:
    """Run ``fn`` as a fault probe: a fault must raise to be fail-closed."""
    try:
        fn()
    except Exception as exc:  # a fault that raises is fail-closed
        return FaultOutcome(kind=kind, raised=True, fail_closed=True, detail=str(exc))
    return FaultOutcome(kind=kind, raised=False, fail_closed=False, detail="silently green")


def require_fail_closed(outcomes: Iterable[FaultOutcome]) -> None:
    """Fail loudly if any fault was silently green.

    Raises:
        FaultError: A fault did not fail closed.
    """
    silent = [outcome.kind for outcome in outcomes if not outcome.fail_closed]
    if silent:
        raise FaultError(f"fault(s) were silently green: {silent}")


def run_pack(cases: Sequence[Callable[[], Any]]) -> list[bool]:
    """Run a pack of case callables; a failure never aborts the pack."""
    results: list[bool] = []
    for case in cases:
        try:
            case()
            results.append(True)
        except Exception:
            results.append(False)
    return results
