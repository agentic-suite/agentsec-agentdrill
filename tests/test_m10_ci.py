"""M10 10.4 — bootstrap confidence intervals, F55 (RED → GREEN).

Every published rate carries a bootstrap CI (`blocked 87% [81%, 92%]
(n, seeds)`); a bare percentage is rejected.
"""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from agentdrill.reporting import (
    BarePercentageError,
    RateCI,
    bootstrap_ci,
    format_rate,
    rate_cis,
    require_ci,
)


def test_bootstrap_ci_brackets_the_point() -> None:
    values = [1.0, 1.0, 1.0, 0.0, 1.0]
    low, high = bootstrap_ci(values, seed=7)
    assert low <= 0.8 <= high
    assert 0.0 <= low <= high <= 1.0


def test_bootstrap_ci_is_deterministic_for_a_seed() -> None:
    values = [1.0, 0.0, 1.0, 1.0, 0.0]
    assert bootstrap_ci(values, seed=3) == bootstrap_ci(values, seed=3)


def test_empty_values_give_a_degenerate_ci() -> None:
    assert bootstrap_ci([], seed=1) == (0.0, 0.0)


def test_rate_ci_format_names_n_and_seeds() -> None:
    ci = RateCI(metric="blocked", point=0.87, low=0.81, high=0.92, n=100, seeds=[1, 2, 3])
    text = format_rate(ci)
    assert "87%" in text
    assert "[81%, 92%]" in text
    assert "seeds=3" in text


def test_rate_cis_over_seeds() -> None:
    runs: dict[int, Sequence[str]] = {
        1: ["blocked", "blocked", "missed"],
        2: ["blocked", "missed", "missed"],
        3: ["blocked", "blocked", "blocked"],
    }
    cis = rate_cis(runs, seed=11)
    blocked = cis["blocked"]
    assert isinstance(blocked, RateCI)
    assert blocked.seeds == [1, 2, 3]
    assert blocked.low <= blocked.point <= blocked.high


def test_bare_percentage_is_rejected() -> None:
    with pytest.raises(BarePercentageError):
        require_ci("87%")
    with pytest.raises(BarePercentageError):
        require_ci(0.87)


def test_a_rate_ci_passes_the_guard() -> None:
    ci = RateCI(metric="blocked", point=0.87, low=0.81, high=0.92, n=100, seeds=[1, 2, 3])
    assert require_ci(ci) is ci
