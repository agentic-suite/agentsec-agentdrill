"""M10 10.2 — honest report: misses mandatory (RED → GREEN).

The outcome split must be exactly the rows in the report — a run cannot
publish with its misses (or degradations) hidden. `publish` validates honesty
then renders.
"""

from __future__ import annotations

import pytest

from agentdrill.oracles.engine import OutcomeSplit
from agentdrill.reporting import HonestyError, Report, ReportRow, check_honesty, publish


def _report(*outcomes: str) -> Report:
    split = OutcomeSplit()
    for outcome in outcomes:
        setattr(split, outcome, getattr(split, outcome) + 1)
    return Report(
        title="t",
        pack_ref="p@1.0.0+deadbeef",
        generated="2026-10-23T00:00:00Z",
        outcome=split,
        rows=[ReportRow(case_id=f"c{i}", outcome=o) for i, o in enumerate(outcomes)],
    )


def test_consistent_report_is_publishable() -> None:
    report = _report("blocked", "missed", "degraded")
    check = check_honesty(report)
    assert check.ok is True
    assert check.problems == []
    rendered = publish(report, "markdown")
    assert "missed" in rendered and "degraded" in rendered


def test_report_hiding_its_misses_is_rejected() -> None:
    report = _report("blocked")  # rows say no misses...
    report.outcome = OutcomeSplit(blocked=1, missed=1)  # ...but the split claims one
    check = check_honesty(report)
    assert check.ok is False
    assert any("missed" in p for p in check.problems)
    with pytest.raises(HonestyError, match="missed"):
        publish(report, "json")


def test_report_hiding_a_degradation_is_rejected() -> None:
    report = _report("blocked", "blocked")
    report.outcome = OutcomeSplit(blocked=1, missed=0, degraded=1)
    with pytest.raises(HonestyError):
        publish(report, "html")


def test_unknown_outcome_is_rejected() -> None:
    report = _report("blocked")
    report.rows.append(ReportRow(case_id="cX", outcome="allowed_through"))
    check = check_honesty(report)
    assert check.ok is False
    assert any("unknown outcome" in p for p in check.problems)


def test_check_honesty_require_raises() -> None:
    report = _report("blocked")
    report.outcome = OutcomeSplit(blocked=1, missed=1)
    with pytest.raises(HonestyError):
        check_honesty(report).require()
