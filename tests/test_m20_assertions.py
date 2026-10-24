"""M20 20.5 — programmatic assertions, F73 (RED → GREEN).

A Python API (`assert_blocked`, `assert_missed`, `assert_kill_time_under`) over
the same run objects, green/red against fixtures.
"""

from __future__ import annotations

import pytest

from agentdrill.dx import (
    DxAssertionError,
    assert_blocked,
    assert_degraded,
    assert_kill_time_under,
    assert_missed,
)
from agentdrill.oracles.base import Verdict


def _verdict(outcome: str) -> Verdict:
    return Verdict(case_id="c1", outcome=outcome)  # type: ignore[arg-type]


def test_assert_blocked_green_then_red() -> None:
    assert_blocked(_verdict("blocked"))  # no raise
    with pytest.raises(DxAssertionError, match="blocked"):
        assert_blocked(_verdict("missed"))


def test_assert_missed_green_then_red() -> None:
    assert_missed(_verdict("missed"))
    with pytest.raises(DxAssertionError):
        assert_missed(_verdict("blocked"))


def test_assert_degraded() -> None:
    assert_degraded(_verdict("degraded"))
    with pytest.raises(DxAssertionError):
        assert_degraded(_verdict("blocked"))


def test_assert_kill_time_under() -> None:
    assert_kill_time_under(1.2, seconds=2.0)  # no raise
    with pytest.raises(DxAssertionError, match="kill time"):
        assert_kill_time_under(3.0, seconds=2.0)
