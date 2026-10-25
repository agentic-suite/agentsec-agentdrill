"""M15 15.5 — registry review gate (RED → GREEN).

An adaptive case entering a *shipped* pack requires human review (HITL); an
unreviewed adaptive case cannot ship.
"""

from __future__ import annotations

import pytest

from agentdrill.chains import (
    AdaptiveCase,
    ReviewGateError,
    ReviewRecord,
    can_ship,
    require_reviewed,
)


def _case(case_id: str = "a1", label: str = "adaptive") -> AdaptiveCase:
    return AdaptiveCase(
        id=case_id,
        parent_pattern="incident-register#1",
        mutation_summary="paraphrase",
        reviewer="author@example",
        mutation="paraphrase",
        label=label,
    )


def test_unreviewed_adaptive_case_cannot_ship() -> None:
    with pytest.raises(ReviewGateError, match="a1"):
        require_reviewed([_case("a1")], {})


def test_unapproved_review_blocks_ship() -> None:
    reviews = {"a1": ReviewRecord(case_id="a1", reviewer="r", approved=False)}
    with pytest.raises(ReviewGateError, match="not approved"):
        require_reviewed([_case("a1")], reviews)


def test_approved_review_allows_ship() -> None:
    reviews = {"a1": ReviewRecord(case_id="a1", reviewer="r", approved=True)}
    require_reviewed([_case("a1")], reviews)  # no raise
    assert can_ship([_case("a1")], reviews) is True


def test_non_adaptive_cases_need_no_review() -> None:
    require_reviewed([_case("plain", label="standard")], {})  # no raise


def test_can_ship_is_false_for_an_unreviewed_case() -> None:
    assert can_ship([_case("a1")], {}) is False
