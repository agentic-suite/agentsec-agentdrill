"""M19 19.2 — calibration corpus, F80 (RED → GREEN).

A published labeled corpus with per-release agreement / false-block /
false-miss rates carrying CIs.
"""

from __future__ import annotations

from agentdrill.credibility import CalibrationCase, CalibrationReport, calibrate


def _case(case_id: str, expected: str, oracle: str) -> CalibrationCase:
    return CalibrationCase(case_id=case_id, expected=expected, oracle_outcome=oracle)


CASES = [
    _case("c1", "blocked", "blocked"),
    _case("c2", "blocked", "missed"),  # false miss
    _case("c3", "missed", "blocked"),  # false block
    _case("c4", "missed", "missed"),
]


def test_rates_published_per_release() -> None:
    report = calibrate(CASES, release="v0.1.0", seed=1)
    assert isinstance(report, CalibrationReport)
    assert report.release == "v0.1.0"
    assert report.n == 4


def test_agreement_rate_computed() -> None:
    report = calibrate(CASES, release="v0.1.0", seed=1)
    assert report.agreement.point == 0.5


def test_false_block_and_false_miss_computed() -> None:
    report = calibrate(CASES, release="v0.1.0", seed=1)
    assert report.false_block.point == 0.25
    assert report.false_miss.point == 0.25


def test_rates_carry_cis() -> None:
    report = calibrate(CASES, release="v0.1.0", seed=1)
    for rate in (report.agreement, report.false_block, report.false_miss):
        assert rate.low <= rate.point <= rate.high
