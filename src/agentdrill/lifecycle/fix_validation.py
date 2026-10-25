"""Remediation validation (M18 18.2, F61).

Every fixed miss becomes a **permanent pinned regression case**; a fix that
later stops holding is ``fix_decay`` — **release-blocking**, with attribution to
the fix commit. Design: ``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel

#: The release-blocking finding raised when a fix decays.
FIX_DECAY = "fix_decay"


class FixDecayError(ValueError):
    """Raised when a previously-fixed miss no longer holds (fix decay)."""


class FixCase(BaseModel):
    """A pinned regression case guarding a fixed miss."""

    case_id: str
    fix_commit: str
    pinned: bool = True
    decayed: bool = False


def regression_case(case_id: str, *, fix_commit: str) -> FixCase:
    """Build a permanent, pinned regression case for a fixed miss."""
    return FixCase(case_id=case_id, fix_commit=fix_commit, pinned=True)


def evaluate_fix(case: FixCase, *, observed_outcome: str) -> FixCase:
    """Mark the fix ``decayed`` when the attack lands again (not ``blocked``)."""
    return case.model_copy(update={"decayed": observed_outcome != "blocked"})


def attribute_decay(case: FixCase) -> str:
    """A decay attribution naming the case and its fix commit."""
    return f"{FIX_DECAY} on {case.case_id} (fix {case.fix_commit})"


def require_fix_holds(cases: Iterable[FixCase]) -> None:
    """Fail loudly (release-blocking) if any fix decayed.

    Raises:
        FixDecayError: One or more fixes no longer hold.
    """
    decayed = [case for case in cases if case.decayed]
    if decayed:
        detail = "; ".join(attribute_decay(case) for case in decayed)
        raise FixDecayError(f"{FIX_DECAY}: {detail}")
