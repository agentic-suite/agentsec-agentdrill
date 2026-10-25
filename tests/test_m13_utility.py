"""M13 13.3 — utility-under-attack, F51 (RED → GREEN).

Every attack case links a benign twin; the report publishes benign utility,
utility-under-attack and the enforcement rate — so a `blocked` number carries
its utility price tag. High enforcement + collapsed utility ⇒ `utility_cost`.
"""

from __future__ import annotations

from agentdrill.efficacy import UtilityReport, assess_utility


def test_blocked_number_carries_its_utility_price_tag() -> None:
    report = assess_utility(
        "c1",
        benign_utility=True,
        utility_under_attack=True,
        enforcement_rate=1.0,
    )
    assert isinstance(report, UtilityReport)
    assert report.enforcement_rate == 1.0
    assert report.benign_utility is True
    assert report.utility_under_attack is True


def test_high_enforcement_with_collapsed_utility_is_a_utility_cost() -> None:
    report = assess_utility(
        "c1",
        benign_utility=True,
        utility_under_attack=False,
        enforcement_rate=1.0,
    )
    assert "utility_cost" in report.findings


def test_high_enforcement_with_preserved_utility_has_no_finding() -> None:
    report = assess_utility(
        "c1", benign_utility=True, utility_under_attack=True, enforcement_rate=1.0
    )
    assert report.findings == []


def test_low_enforcement_with_collapsed_utility_has_no_utility_cost() -> None:
    report = assess_utility(
        "c1", benign_utility=True, utility_under_attack=False, enforcement_rate=0.4
    )
    assert "utility_cost" not in report.findings


def test_utility_report_round_trips() -> None:
    report = assess_utility(
        "c1", benign_utility=True, utility_under_attack=True, enforcement_rate=1.0
    )
    assert UtilityReport.model_validate_json(report.model_dump_json()) == report
