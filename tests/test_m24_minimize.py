"""M24 24.7 — minimization + dedup + promotion, F89 (RED → GREEN).

Delta-debug minimization; family dedup; auto-promote a confirmed bypass to a
regression (F61) with attribution (F38) — same release.
"""

from __future__ import annotations

from agentdrill.attacker import dedup_by_family, minimize, promote_to_regression
from agentdrill.lifecycle import FixCase


def test_minimization_reduces_the_reproducer() -> None:
    steps = ["a", "b", "c", "d", "e", "f"]
    essential = lambda s: {"b", "e"} <= set(s)  # noqa: E731 - a test predicate
    result = minimize("write-forbidden-file", steps, essential=essential)
    assert result.reproducer == ["b", "e"]
    assert result.ratio == 3.0


def test_family_dedup_keeps_one_per_family() -> None:
    routes = ["e1:path", "e2:path", "e3:encoding", "e4:path"]
    assert dedup_by_family(routes) == ["e1:path", "e3:encoding"]


def test_confirmed_bypass_promotes_to_a_regression() -> None:
    case = promote_to_regression("write-forbidden-file", fix_commit="abc123")
    assert isinstance(case, FixCase)
    assert case.pinned is True
    assert "write-forbidden-file" in case.case_id
