"""M24 24.2 — Hold@k / ASR@k metrics, F86 (RED → GREEN).

All-of-k and any-of-k per case/class; bootstrap CIs; first-break distribution
(p50/p95); attacker cost-to-break. A bare percentage is not renderable.
"""

from __future__ import annotations

import pytest

from agentdrill.attacker import HoldAtK, hold_at_k
from agentdrill.reporting import BarePercentageError, require_ci


def test_hold_at_k_computes_blocks() -> None:
    metric = hold_at_k([True, True, True, True, True], k=5, seed=1)
    assert isinstance(metric, HoldAtK)
    assert metric.k == 5
    assert metric.hold_rate.point == 1.0
    assert metric.asr_at_k.point == 0.0


def test_asr_at_k_is_the_complement() -> None:
    metric = hold_at_k([True, False, True, True, True], k=5, seed=1)
    assert metric.hold_rate.point == 0.0
    assert metric.asr_at_k.point == 1.0


def test_first_break_distribution_is_reported() -> None:
    metric = hold_at_k([True, True, False, True, True, False], k=3, seed=1)
    assert metric.first_break_p50 >= 0
    assert metric.first_break_p95 >= metric.first_break_p50


def test_bare_percentage_is_not_renderable() -> None:
    metric = hold_at_k([True, False], k=2, seed=1)
    assert require_ci(metric.hold_rate) is metric.hold_rate
    with pytest.raises(BarePercentageError):
        require_ci(metric.hold_rate.point)  # a bare float is rejected


def test_cost_to_break_is_carried() -> None:
    metric = hold_at_k([True, False], k=2, seed=1, cost_to_break=1.25)
    assert metric.cost_to_break == 1.25
