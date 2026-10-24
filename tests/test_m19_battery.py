"""M19 19.4 — oracle meta-eval CI, F82 (RED → GREEN).

A calibration battery (known-answer blocked/missed/degraded/inert/seam) must
verdict correctly before release; a regression fails CI.
"""

from __future__ import annotations

import pytest

from agentdrill.credibility import (
    DEFAULT_BATTERY,
    BatteryError,
    BatteryResult,
    KnownAnswer,
    require_battery_green,
    run_battery,
)


def test_known_answers_cover_the_battery_kinds() -> None:
    kinds = {answer.kind for answer in DEFAULT_BATTERY}
    assert kinds == {"blocked", "missed", "degraded", "inert", "seam"}


def test_battery_green_when_all_verdicts_correct() -> None:
    result = run_battery(DEFAULT_BATTERY, verdict_of=lambda a: a.expected_verdict)
    assert isinstance(result, BatteryResult)
    assert result.passed is True
    assert result.failures == []


def test_a_regression_fails_ci() -> None:
    def wrong(answer: KnownAnswer) -> str:
        return "missed" if answer.case_id == DEFAULT_BATTERY[0].case_id else answer.expected_verdict

    result = run_battery(DEFAULT_BATTERY, verdict_of=wrong)
    assert result.passed is False
    assert result.failures
    with pytest.raises(BatteryError):
        require_battery_green(result)


def test_green_battery_passes_the_gate() -> None:
    require_battery_green(run_battery(DEFAULT_BATTERY, verdict_of=lambda a: a.expected_verdict))
