"""M30 30.4 — version-follow SLA + drivers (RED -> GREEN).

A nightly driver canary that catches breakage before a user hits it (>=90%);
the matrix freshness SLA (<=7 d, L4 <=72 h); the "defaults vs auto-approve" label
is mandatory; and the runtime matrix includes a local-first, judge-free subset.
"""

from __future__ import annotations

import pytest

from agentdrill.platform import (
    ConfigPosture,
    DriverCanary,
    MatrixFreshness,
    PlatformError,
    RuntimeSubset,
    canary_detection_rate,
    require_canary_detection,
    require_canary_green,
    require_config_posture,
    require_freshness,
    require_judge_free_subset,
)


def test_the_canary_catches_breakage_before_users() -> None:
    assert canary_detection_rate(detected=9, known=10) == pytest.approx(0.9)
    require_canary_detection(detected=9, known=10)  # >=90%
    with pytest.raises(PlatformError):
        require_canary_detection(detected=8, known=10)
    assert canary_detection_rate(detected=0, known=0) == 1.0


def test_a_failing_canary_driver_fails_loudly() -> None:
    require_canary_green([DriverCanary(driver="d1", passing=True, at="2026-02-01")])
    with pytest.raises(PlatformError):
        require_canary_green(
            [DriverCanary(driver="d2", passing=False, at="2026-02-01")]
        )


def test_matrix_freshness_sla() -> None:
    require_freshness([MatrixFreshness(level="L3", updated_days_ago=5.0)])
    with pytest.raises(PlatformError):
        require_freshness([MatrixFreshness(level="L3", updated_days_ago=8.0)])
    # L4 must be current within 72 h
    require_freshness([MatrixFreshness(level="L4", updated_days_ago=2.5)])
    with pytest.raises(PlatformError):
        require_freshness([MatrixFreshness(level="L4", updated_days_ago=4.0)])


def test_an_unknown_matrix_level_fails_loudly() -> None:
    with pytest.raises(PlatformError):
        require_freshness([MatrixFreshness(level="LX", updated_days_ago=1.0)])


def test_config_posture_is_always_labelled() -> None:
    assert set(ConfigPosture.__args__) == {"defaults", "auto-approve"}
    require_config_posture("defaults")
    require_config_posture("auto-approve")
    with pytest.raises(PlatformError):
        require_config_posture("tuned")


def test_a_local_first_judge_free_subset_is_required() -> None:
    require_judge_free_subset(
        [RuntimeSubset(name="local-small", local_first=True, judge_free=True)]
    )
    with pytest.raises(PlatformError):
        require_judge_free_subset(
            [RuntimeSubset(name="cloud", local_first=False, judge_free=False)]
        )
