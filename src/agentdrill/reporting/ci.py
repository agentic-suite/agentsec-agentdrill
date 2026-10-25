"""Bootstrap confidence intervals on outcome rates (M10 10.4, F55).

Every published rate carries a bootstrap CI — ``blocked 87% [81%, 92%]
(n, seeds)``; a bare percentage is rejected. The resample is seeded so the CI
is reproducible. Design: ``docs/design/reporting.md``.
"""

from __future__ import annotations

import random
import statistics
from collections.abc import Mapping, Sequence

from pydantic import BaseModel

from agentdrill.reporting.stats import _OUTCOMES, _rate

#: Default bootstrap settings.
DEFAULT_RESAMPLES = 1000
DEFAULT_LEVEL = 0.95


class BarePercentageError(ValueError):
    """Raised when a rate is published without a confidence interval."""


class RateCI(BaseModel):
    """A published rate with its bootstrap confidence interval.

    Attributes:
        metric: The outcome name.
        point: The point estimate (mean rate).
        low: Lower CI bound.
        high: Upper CI bound.
        n: Number of observations.
        seeds: The pinned seeds, sorted.
    """

    metric: str
    point: float
    low: float
    high: float
    n: int
    seeds: list[int]


def _percentile(sorted_values: list[float], q: float) -> float:
    """Nearest-rank percentile of a sorted list."""
    if not sorted_values:
        return 0.0
    index = min(len(sorted_values) - 1, max(0, int(q * len(sorted_values))))
    return sorted_values[index]


def bootstrap_ci(
    values: Sequence[float],
    *,
    seed: int = 0,
    level: float = DEFAULT_LEVEL,
    n_resamples: int = DEFAULT_RESAMPLES,
) -> tuple[float, float]:
    """Bootstrap ``(low, high)`` for the mean of ``values`` (seeded, reproducible)."""
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)  # noqa: S311 - seeded statistical resample, not crypto
    n = len(values)
    means = sorted(
        statistics.fmean(values[rng.randrange(n)] for _ in range(n)) for _ in range(n_resamples)
    )
    alpha = (1.0 - level) / 2.0
    return (_percentile(means, alpha), _percentile(means, 1.0 - alpha))


def rate_cis(
    runs: Mapping[int, Sequence[str]], *, seed: int = 0, level: float = DEFAULT_LEVEL
) -> dict[str, RateCI]:
    """A :class:`RateCI` per outcome across ``runs`` (seed → case outcomes)."""
    seeds = sorted(runs)
    n = sum(len(runs[s]) for s in seeds)
    cis: dict[str, RateCI] = {}
    for name in _OUTCOMES:
        rates = [_rate(runs[s], name) for s in seeds]
        point = statistics.fmean(rates) if rates else 0.0
        low, high = bootstrap_ci(rates, seed=seed, level=level)
        cis[name] = RateCI(metric=name, point=point, low=low, high=high, n=n, seeds=seeds)
    return cis


def format_rate(rate: RateCI) -> str:
    """Format a rate as ``blocked 87% [81%, 92%] (n=100, seeds=3)``."""
    return (
        f"{rate.metric} {round(rate.point * 100)}% "
        f"[{round(rate.low * 100)}%, {round(rate.high * 100)}%] "
        f"(n={rate.n}, seeds={len(rate.seeds)})"
    )


def require_ci(value: object) -> RateCI:
    """Return ``value`` if it is a :class:`RateCI`, else reject a bare percentage.

    Raises:
        BarePercentageError: ``value`` is not a rate with a confidence interval.
    """
    if isinstance(value, RateCI):
        return value
    raise BarePercentageError(
        f"a published rate must carry a confidence interval, got bare {value!r}"
    )
