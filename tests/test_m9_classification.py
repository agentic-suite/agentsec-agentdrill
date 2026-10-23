"""M9 9.5 — three-way outcome classification (RED → GREEN).

Classify a case failure to the right layer: `adapter_failed` /
`agent_crashed` / `scenario_failed` (+ `blocked`/`missed`/`degraded`), so a
comparison names where a failure happened — the predecessor trace-diff
discipline, re-pointed.
"""

from __future__ import annotations

from agentdrill.comparison import OutcomeClassification, classify_outcome
from agentdrill.models.artifact import RunTimestamps
from agentdrill.models.attack_run import CaseArtifact


def _artifact(status: str = "completed", error: str | None = None) -> CaseArtifact:
    return CaseArtifact(
        id="r::c1",
        case_id="c1",
        timestamps=RunTimestamps(start="t", end="t", duration_ms=1),
        status=status,  # type: ignore[arg-type]
        error=error,
    )


def test_blocked_completed_is_passed() -> None:
    result = classify_outcome(_artifact(), outcome="blocked")
    assert isinstance(result, OutcomeClassification)
    assert result.classification == "passed"
    assert result.outcome == "blocked"


def test_missed_completed_is_scenario_failed() -> None:
    result = classify_outcome(_artifact(), outcome="missed")
    assert result.classification == "scenario_failed"
    assert result.outcome == "missed"


def test_degraded_completed_is_scenario_failed() -> None:
    result = classify_outcome(_artifact(), outcome="degraded")
    assert result.classification == "scenario_failed"


def test_timeout_is_agent_crashed() -> None:
    result = classify_outcome(_artifact(status="timeout"), outcome=None)
    assert result.classification == "agent_crashed"
    assert result.outcome is None


def test_adapter_error_is_adapter_failed() -> None:
    result = classify_outcome(
        _artifact(status="error", error="AdapterError: driver returned unsupported type"),
        outcome=None,
    )
    assert result.classification == "adapter_failed"


def test_agent_traceback_is_agent_crashed() -> None:
    result = classify_outcome(
        _artifact(status="error", error="Traceback (most recent call last):\nKeyError: 'x'"),
        outcome=None,
    )
    assert result.classification == "agent_crashed"


def test_aborted_budget_is_adapter_failed() -> None:
    result = classify_outcome(_artifact(status="aborted", error="cost_exceeded"), outcome=None)
    assert result.classification == "adapter_failed"


def test_classification_carries_case_id_and_detail() -> None:
    result = classify_outcome(_artifact(), outcome="missed")
    assert result.case_id == "c1"
    assert result.detail
