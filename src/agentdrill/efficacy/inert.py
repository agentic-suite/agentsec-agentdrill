"""Inert-attack flagging (M13 13.2).

An unguarded failure means the case is inert: flagged ``attack_inert``,
**excluded from enforcement rates**, and never counted as coverage — an inert
attack can never pad a green table. Design: ``docs/design/efficacy.md``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from agentdrill.efficacy.control import EfficacyResult

#: The flag applied to a case whose attack does not work unguarded.
INERT_FLAG = "attack_inert"


def inert_cases(results: Iterable[EfficacyResult]) -> list[str]:
    """Case ids flagged ``attack_inert`` (unguarded failure)."""
    return [result.case_id for result in results if result.inert]


def countable(results: Iterable[EfficacyResult]) -> list[EfficacyResult]:
    """The efficacy-verified results — inert cases are excluded from rates."""
    return [result for result in results if result.efficacy_verified]


def enforcement_rate(results: Sequence[EfficacyResult]) -> float | None:
    """``blocked / (blocked + missed)`` over efficacy-verified cases only.

    Returns ``None`` when no countable case is blocked or missed (including
    when every case is inert).
    """
    counted = countable(results)
    blocked = sum(1 for r in counted if r.guarded_outcome == "blocked")
    missed = sum(1 for r in counted if r.guarded_outcome == "missed")
    total = blocked + missed
    return (blocked / total) if total else None
