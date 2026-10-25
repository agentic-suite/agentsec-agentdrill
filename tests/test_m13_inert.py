"""M13 13.2 — inert flagging (RED → GREEN).

An unguarded failure ⇒ `attack_inert`; inert cases are excluded from
enforcement rates and can never pad a green table.
"""

from __future__ import annotations

from agentdrill.efficacy import (
    INERT_FLAG,
    countable,
    enforcement_rate,
    inert_cases,
    run_efficacy,
)


def _verified(case_id: str, guarded: str):
    return run_efficacy(case_id, unguarded=lambda: True, guarded_outcome=guarded)


def _inert(case_id: str, guarded: str | None = "blocked"):
    return run_efficacy(case_id, unguarded=lambda: False, guarded_outcome=guarded)


def test_inert_case_is_flagged() -> None:
    results = [_verified("c1", "blocked"), _inert("c2")]
    assert inert_cases(results) == ["c2"]
    assert INERT_FLAG == "attack_inert"


def test_inert_case_is_excluded_from_the_enforcement_rate() -> None:
    results = [_verified("c1", "blocked"), _verified("c2", "missed"), _inert("c3", "blocked")]
    # if inert padded the table, rate would be 2/3; excluded it is 1/2
    assert enforcement_rate(results) == 0.5


def test_inert_cases_are_not_countable_coverage() -> None:
    results = [_verified("c1", "blocked"), _inert("c2")]
    assert [r.case_id for r in countable(results)] == ["c1"]


def test_rate_is_none_when_every_case_is_inert() -> None:
    assert enforcement_rate([_inert("c1"), _inert("c2")]) is None


def test_rate_counts_blocked_over_blocked_plus_missed() -> None:
    results = [_verified("c1", "blocked"), _verified("c2", "missed")]
    assert enforcement_rate(results) == 0.5
