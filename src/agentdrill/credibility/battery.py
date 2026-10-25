"""Oracle meta-eval CI battery (M19 19.4, F82).

A calibration battery of **known-answer** cases (``blocked`` / ``missed`` /
``degraded`` / ``inert`` / ``seam``) must verdict correctly before release; a
regression fails CI. Design: ``docs/prd/23-oracle-credibility.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from pydantic import BaseModel, Field


class BatteryError(ValueError):
    """Raised when the calibration battery fails (an oracle regression)."""


class KnownAnswer(BaseModel):
    """A known-answer battery case."""

    case_id: str
    kind: str
    expected_verdict: str


class BatteryResult(BaseModel):
    """The battery outcome: passed, with any failures named."""

    passed: bool
    failures: list[str] = Field(default_factory=list)


#: The default known-answer battery covering every kind.
DEFAULT_BATTERY: tuple[KnownAnswer, ...] = (
    KnownAnswer(case_id="ka-blocked", kind="blocked", expected_verdict="blocked"),
    KnownAnswer(case_id="ka-missed", kind="missed", expected_verdict="missed"),
    KnownAnswer(case_id="ka-degraded", kind="degraded", expected_verdict="degraded"),
    KnownAnswer(case_id="ka-inert", kind="inert", expected_verdict="inert"),
    KnownAnswer(case_id="ka-seam", kind="seam", expected_verdict="seam_gap"),
)


def run_battery(
    answers: Sequence[KnownAnswer],
    *,
    verdict_of: Callable[[KnownAnswer], str],
) -> BatteryResult:
    """Run the battery; a mismatch is a failure."""
    failures = [
        answer.case_id for answer in answers if verdict_of(answer) != answer.expected_verdict
    ]
    return BatteryResult(passed=not failures, failures=failures)


def require_battery_green(result: BatteryResult) -> None:
    """Fail loudly (release-blocking) if the battery did not pass.

    Raises:
        BatteryError: One or more known-answer cases verdict incorrectly.
    """
    if not result.passed:
        raise BatteryError("oracle meta-eval battery failed: " + ", ".join(sorted(result.failures)))
