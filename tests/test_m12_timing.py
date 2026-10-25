"""M12 12.3 — repeated trials → percentiles (RED → GREEN).

≥5 trials per kill-time case → p50/p95/max per stage and total (means are
never published alone).
"""

from __future__ import annotations

import pytest

from agentdrill.killchain import (
    InsufficientTrialsError,
    StagePercentiles,
    TimingReport,
    build_timeline,
    compute_timing,
    require_trials,
)


def _trial(detect_delay: float) -> object:
    return build_timeline(
        "c1",
        {
            "attack_start": 0.0,
            "delivered": 0.0,
            "detected": detect_delay,
            "decided": detect_delay + 1.0,
            "halted": detect_delay + 1.5,
            "revoked": detect_delay + 2.0,
            "ceased": detect_delay + 2.5,
        },
    )


TRIALS = [_trial(d) for d in (1.0, 2.0, 3.0, 4.0, 5.0)]


def test_percentiles_reported_per_stage_and_total() -> None:
    report = compute_timing("c1", TRIALS)
    assert isinstance(report, TimingReport)
    assert report.trials == 5
    segments = {s.stage: s for s in report.segments}
    detected = segments["delivered->detected"]
    assert isinstance(detected, StagePercentiles)
    assert detected.n == 5
    assert detected.p50 == 3.0
    assert detected.p95 == 5.0
    assert detected.max == 5.0
    assert report.total.p50 > 0


def test_total_is_attack_start_to_ceased() -> None:
    report = compute_timing("c1", TRIALS)
    # detected varies 1..5, ceased = detected + 2.5 → p50 total = 5.5
    assert report.total.p50 == 5.5
    assert report.total.max == 7.5


def test_fewer_than_five_trials_rejected() -> None:
    with pytest.raises(InsufficientTrialsError, match="5"):
        compute_timing("c1", TRIALS[:4])


def test_require_trials_rejects_too_few() -> None:
    with pytest.raises(InsufficientTrialsError):
        require_trials(3)


def test_require_trials_accepts_five() -> None:
    require_trials(5)


def test_a_total_needs_a_start_and_an_end() -> None:
    only_start = build_timeline("c1", {"attack_start": 0.0})
    report = compute_timing("c1", [only_start] * 5, require_min=False)
    assert report.total.n == 0
