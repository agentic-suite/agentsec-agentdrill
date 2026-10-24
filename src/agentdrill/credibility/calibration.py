"""Calibration corpus (M19 19.2, F80).

A published labeled corpus with per-release **agreement / false-block /
false-miss** rates carrying CIs. Design: ``docs/prd/23-oracle-credibility.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentdrill.reporting.ci import RateCI, bootstrap_ci


class CalibrationCase(BaseModel):
    """One labeled calibration case and the oracle's verdict."""

    case_id: str
    expected: str
    oracle_outcome: str


class CalibrationReport(BaseModel):
    """Per-release calibration rates (each a rate with a CI)."""

    release: str
    n: int
    agreement: RateCI
    false_block: RateCI
    false_miss: RateCI
    cases: list[CalibrationCase] = Field(default_factory=list)


def _rate(metric: str, series: list[float], *, seed: int, n: int) -> RateCI:
    point = sum(series) / len(series) if series else 0.0
    low, high = bootstrap_ci(series, seed=seed)
    return RateCI(metric=metric, point=point, low=low, high=high, n=n, seeds=[seed])


def calibrate(
    cases: Sequence[CalibrationCase], *, release: str, seed: int = 0
) -> CalibrationReport:
    """Compute the agreement / false-block / false-miss rates for a release."""
    agreement = [1.0 if case.oracle_outcome == case.expected else 0.0 for case in cases]
    false_block = [
        1.0 if case.oracle_outcome == "blocked" and case.expected != "blocked" else 0.0
        for case in cases
    ]
    false_miss = [
        1.0 if case.expected == "blocked" and case.oracle_outcome != "blocked" else 0.0
        for case in cases
    ]
    n = len(cases)
    return CalibrationReport(
        release=release,
        n=n,
        agreement=_rate("agreement", agreement, seed=seed, n=n),
        false_block=_rate("false_block", false_block, seed=seed, n=n),
        false_miss=_rate("false_miss", false_miss, seed=seed, n=n),
        cases=list(cases),
    )
