"""Performance & scale (M22 22.1).

Per-pack run budgets, parallel-equals-serial and cache stats. Design:
``docs/prd/13-non-functional-requirements.md``.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel


class PerfBudget(BaseModel):
    """A pack run's performance budget and whether it was met."""

    pack_ref: str
    elapsed_seconds: float
    budget_seconds: float
    met: bool


def measure_budget(pack_ref: str, *, elapsed_seconds: float, budget_seconds: float) -> PerfBudget:
    """Measure a run against its budget."""
    return PerfBudget(
        pack_ref=pack_ref,
        elapsed_seconds=elapsed_seconds,
        budget_seconds=budget_seconds,
        met=elapsed_seconds <= budget_seconds,
    )


def parallel_matches_serial(serial: Sequence[Any], parallel: Sequence[Any]) -> bool:
    """Whether a parallel run produced the same results as a serial run (order-free)."""
    return sorted(map(str, serial)) == sorted(map(str, parallel))


def cache_stats(cache: Any) -> dict[str, int]:
    """The hit/miss stats of a cache (reads a ``stats`` mapping when present)."""
    stats = getattr(cache, "stats", None)
    return dict(stats) if isinstance(stats, dict) else {}
