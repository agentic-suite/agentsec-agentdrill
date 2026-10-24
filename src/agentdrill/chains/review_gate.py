"""Registry review gate (M15 15.5).

An adaptive case entering a **shipped** pack requires human review (HITL);
an unreviewed (or unapproved) adaptive case cannot ship. Design:
``docs/prd/16-attack-chain-orchestration.md``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pydantic import BaseModel

from agentdrill.chains.adaptive import ADAPTIVE_LABEL, AdaptiveCase


class ReviewGateError(ValueError):
    """Raised when an adaptive case would ship without an approved review."""


class ReviewRecord(BaseModel):
    """A human review decision for one adaptive case."""

    case_id: str
    reviewer: str
    approved: bool = False


def require_reviewed(cases: Sequence[AdaptiveCase], reviews: Mapping[str, ReviewRecord]) -> None:
    """Fail loudly if an adaptive case lacks an approved review.

    Non-adaptive cases need no review.

    Raises:
        ReviewGateError: An adaptive case has no review, or its review is not
            approved.
    """
    for case in cases:
        if case.label != ADAPTIVE_LABEL:
            continue
        record = reviews.get(case.id)
        if record is None:
            raise ReviewGateError(f"adaptive case {case.id} has no review — cannot ship")
        if not record.approved:
            raise ReviewGateError(
                f"adaptive case {case.id} review not approved by {record.reviewer!r} — cannot ship"
            )


def can_ship(cases: Sequence[AdaptiveCase], reviews: Mapping[str, ReviewRecord]) -> bool:
    """Whether every adaptive case is approved to ship."""
    try:
        require_reviewed(cases, reviews)
    except ReviewGateError:
        return False
    return True
