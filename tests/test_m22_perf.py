"""M22 22.1 — performance & scale (RED → GREEN).

Per-pack run budget; parallel == serial; cache stats reported.
"""

from __future__ import annotations

from agentdrill.hardening import PerfBudget, measure_budget, parallel_matches_serial


def test_budget_met_when_within() -> None:
    budget = measure_budget("p@1.0.0+abc", elapsed_seconds=10.0, budget_seconds=30.0)
    assert isinstance(budget, PerfBudget)
    assert budget.met is True


def test_budget_missed_when_over() -> None:
    assert measure_budget("p", elapsed_seconds=40.0, budget_seconds=30.0).met is False


def test_parallel_matches_serial() -> None:
    serial = ["a", "b", "c"]
    parallel = ["a", "b", "c"]
    assert parallel_matches_serial(serial, parallel) is True
    assert parallel_matches_serial(serial, ["a", "c", "b"]) is True  # order-insensitive
    assert parallel_matches_serial(serial, ["a", "b"]) is False


def test_budget_reports_the_pack_ref() -> None:
    assert measure_budget("p@1.0.0+abc", elapsed_seconds=1.0, budget_seconds=2.0).pack_ref == (
        "p@1.0.0+abc"
    )
