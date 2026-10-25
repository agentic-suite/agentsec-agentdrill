"""Statistical rigor over pinned seeds (M10 10.3, F29).

Every published number is a mean ± std over **≥3 pinned seeds**; a single-run
(or duplicate-seed) number fails the publish check. Design:
``docs/design/reporting.md`` §Honesty rules.
"""

from __future__ import annotations

import statistics
from collections.abc import Mapping, Sequence

from pydantic import BaseModel

#: Minimum distinct pinned seeds required to publish a number.
MIN_SEEDS = 3

#: The outcome names a rate is published for.
_OUTCOMES = ("blocked", "missed", "degraded")


class SingleRunError(ValueError):
    """Raised when a number is published from fewer than :data:`MIN_SEEDS` seeds."""


class SeedStat(BaseModel):
    """A published number: mean ± std over the pinned seeds.

    Attributes:
        metric: The outcome name (``blocked`` / ``missed`` / ``degraded``).
        mean: Mean rate across seeds.
        std: Population std of the rate across seeds.
        n: Number of seeds.
        seeds: The pinned seeds, sorted.
    """

    metric: str
    mean: float
    std: float
    n: int
    seeds: list[int]


def _rate(outcomes: Sequence[str], name: str) -> float:
    """The rate of ``name`` among ``outcomes`` (0.0 for an empty run)."""
    if not outcomes:
        return 0.0
    return sum(1 for o in outcomes if o == name) / len(outcomes)


def seed_stats(runs: Mapping[int, Sequence[str]]) -> dict[str, SeedStat]:
    """Mean ± std of each outcome rate across ``runs`` (seed → case outcomes)."""
    seeds = sorted(runs)
    stats: dict[str, SeedStat] = {}
    for name in _OUTCOMES:
        rates = [_rate(runs[seed], name) for seed in seeds]
        mean = statistics.fmean(rates) if rates else 0.0
        std = statistics.pstdev(rates) if len(rates) > 1 else 0.0
        stats[name] = SeedStat(metric=name, mean=mean, std=std, n=len(seeds), seeds=seeds)
    return stats


def require_multi_seed(seeds: Sequence[int], *, min_seeds: int = MIN_SEEDS) -> None:
    """Require at least ``min_seeds`` distinct pinned seeds.

    Raises:
        SingleRunError: Fewer than ``min_seeds`` distinct seeds (a single-run
            number must never be published).
    """
    distinct = sorted(set(seeds))
    if len(distinct) < min_seeds:
        raise SingleRunError(
            f"a published number requires ≥{min_seeds} distinct pinned seeds, "
            f"got {len(distinct)} ({distinct})"
        )
