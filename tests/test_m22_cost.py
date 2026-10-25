"""M22 22.5 — cost controls (RED → GREEN).

Run-level `--max-cost`; over-budget aborts and reports; caching savings
reported.
"""

from __future__ import annotations

from agentdrill.hardening import CostReport, cost_report, over_budget


def test_over_budget_aborts_and_reports() -> None:
    report = cost_report(spent_usd=2.0, budget_usd=1.0, cached_savings_usd=0.25)
    assert isinstance(report, CostReport)
    assert report.aborted is True
    assert report.savings_usd == 0.25


def test_within_budget_is_not_aborted() -> None:
    report = cost_report(spent_usd=0.5, budget_usd=1.0)
    assert report.aborted is False


def test_over_budget_helper() -> None:
    assert over_budget(2.0, 1.0) is True
    assert over_budget(0.5, 1.0) is False
    assert over_budget(99.0, None) is False  # no budget ⇒ never over
