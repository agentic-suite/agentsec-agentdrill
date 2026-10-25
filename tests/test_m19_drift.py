"""M19 19.3 — judge drift detection, F81 (RED → GREEN).

Judge-vs-deterministic / judge-vs-human agreement tracked via seeded **canary**
cases; a flip without a pin change is `judge_drift` (release-blocking); judge
prompts are hashed into the manifest.
"""

from __future__ import annotations

import pytest

from agentdrill.credibility import (
    JUDGE_DRIFT,
    CanaryCase,
    DriftReport,
    JudgeDriftError,
    detect_drift,
    hash_prompt,
    require_no_drift,
)


def _canary(case_id: str, outcome: str) -> CanaryCase:
    return CanaryCase(case_id=case_id, expected="blocked", judge_outcome=outcome)


def test_a_canary_flip_without_a_pin_change_is_drift() -> None:
    report = detect_drift(
        [_canary("c1", "missed")],
        previous_outcomes={"c1": "blocked"},
        pin_changed=False,
        judge_prompt_hash=hash_prompt("judge prompt"),
    )
    assert isinstance(report, DriftReport)
    assert report.drift is True
    assert report.flips == ["c1"]
    assert JUDGE_DRIFT == "judge_drift"
    with pytest.raises(JudgeDriftError, match="c1"):
        require_no_drift(report)


def test_a_flip_with_a_pin_change_is_not_drift() -> None:
    report = detect_drift(
        [_canary("c1", "missed")],
        previous_outcomes={"c1": "blocked"},
        pin_changed=True,
        judge_prompt_hash="sha256:x",
    )
    assert report.drift is False


def test_no_flip_is_no_drift() -> None:
    report = detect_drift(
        [_canary("c1", "blocked")],
        previous_outcomes={"c1": "blocked"},
        pin_changed=False,
        judge_prompt_hash="sha256:x",
    )
    assert report.flips == []
    assert report.drift is False


def test_judge_prompt_is_hashed_into_the_manifest() -> None:
    digest = hash_prompt("did the agent refuse?")
    assert digest.startswith("sha256:")
    report = detect_drift([], previous_outcomes={}, pin_changed=False, judge_prompt_hash=digest)
    assert report.judge_prompt_hash == digest
