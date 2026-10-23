"""M10 10.3 — statistical rigor, F29 (RED → GREEN).

Every published number is a mean ± std over ≥3 pinned seeds. A single-run (or
duplicate-seed) number fails the publish check.
"""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from agentdrill.reporting import (
    SeedStat,
    SingleRunError,
    require_multi_seed,
    seed_stats,
)

RUNS: dict[int, Sequence[str]] = {
    1: ["blocked", "blocked", "missed"],
    2: ["blocked", "missed", "missed"],
    3: ["blocked", "blocked", "blocked"],
}


def test_aggregates_mean_and_std_over_seeds() -> None:
    stats = seed_stats(RUNS)
    blocked = stats["blocked"]
    assert isinstance(blocked, SeedStat)
    assert blocked.n == 3
    assert blocked.seeds == [1, 2, 3]
    # rates 2/3, 1/3, 3/3
    assert blocked.mean == pytest.approx(2 / 3, abs=1e-6)
    assert blocked.std == pytest.approx(0.2721655, abs=1e-4)


def test_missed_rate_published_too() -> None:
    stats = seed_stats(RUNS)
    assert stats["missed"].mean == pytest.approx(1 / 3, abs=1e-6)


def test_three_seeds_are_ok() -> None:
    require_multi_seed([1, 2, 3])  # no raise


def test_single_seed_is_rejected() -> None:
    with pytest.raises(SingleRunError, match="3"):
        require_multi_seed([1])


def test_two_seeds_are_rejected() -> None:
    with pytest.raises(SingleRunError):
        require_multi_seed([7, 8])


def test_duplicate_seeds_do_not_count_as_multi_seed() -> None:
    with pytest.raises(SingleRunError):
        require_multi_seed([1, 1, 1])


def test_publishing_a_single_seed_number_is_rejected() -> None:
    stats = seed_stats({1: ["blocked", "missed"]})
    with pytest.raises(SingleRunError):
        require_multi_seed(stats["blocked"].seeds)
