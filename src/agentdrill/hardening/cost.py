"""Cost controls (M22 22.5).

Run-level ``--max-cost``; an over-budget run aborts and reports, and caching
savings are reported. Design: ``docs/prd/13-non-functional-requirements.md``.
"""

from __future__ import annotations

from pydantic import BaseModel


class CostReport(BaseModel):
    """A run's cost report."""

    spent_usd: float
    budget_usd: float | None = None
    aborted: bool = False
    savings_usd: float = 0.0


def over_budget(spent_usd: float, budget_usd: float | None) -> bool:
    """Whether the spend exceeds the budget (no budget ⇒ never over)."""
    return budget_usd is not None and spent_usd > budget_usd


def cost_report(
    *, spent_usd: float, budget_usd: float | None = None, cached_savings_usd: float = 0.0
) -> CostReport:
    """Build a cost report; an over-budget run is marked aborted."""
    return CostReport(
        spent_usd=spent_usd,
        budget_usd=budget_usd,
        aborted=over_budget(spent_usd, budget_usd),
        savings_usd=cached_savings_usd,
    )
