"""M24 24.6 — bounded search engine, F89 (RED → GREEN).

Seeded breadth-over-families then depth; budgets; family-level pruning; runs
only under RoE. Same seed ⇒ same sequence.
"""

from __future__ import annotations

import pytest

from agentdrill.attacker import (
    SearchError,
    SearchResult,
    bounded_search,
    default_catalog,
)


def test_same_seed_yields_the_same_sequence() -> None:
    a = bounded_search(default_catalog(), seed=7, max_routes=8)
    b = bounded_search(default_catalog(), seed=7, max_routes=8)
    assert isinstance(a, SearchResult)
    assert a.sequence == b.sequence
    assert a.roe_enforced is True


def test_budget_caps_the_sequence() -> None:
    result = bounded_search(default_catalog(), seed=7, max_routes=5)
    assert len(result.sequence) <= 5


def test_runs_only_under_roe() -> None:
    with pytest.raises(SearchError, match="RoE"):
        bounded_search(default_catalog(), seed=7, max_routes=5, roe_ok=False)


def test_sequence_covers_families_breadth_first() -> None:
    result = bounded_search(default_catalog(), seed=1, max_routes=100)
    families = {route.split(":")[1] for route in result.sequence}
    assert len(families) >= 4
