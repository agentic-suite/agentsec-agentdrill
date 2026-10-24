"""M28 28.7 — safe-fire interlocks (RED → GREEN).

The global **abort** (independent of the in-band agenthalt), the **dead-man
switch** (lost heartbeat → abort + cleanup), rate/cost **watchdogs**, **verified
teardown** (``dirty_target`` is release-blocking, reusing M13 cleanup), and the
**consent gate** for any attack content leaving the machine.
"""

from __future__ import annotations

import time

import pytest

from agentdrill.efficacy import CleanupResult
from agentdrill.roe import (
    AbortController,
    DeadManSwitch,
    InterlockError,
    check_cost_watchdog,
    check_rate_watchdog,
    require_egress_consent,
    verified_teardown,
)


def test_global_abort_is_immediate_and_independent() -> None:
    controller = AbortController()
    assert controller.is_aborted() is False
    controller.require_running()

    start = time.perf_counter()
    controller.abort(reason="operator stop")
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0  # abort p95 ≤ 5 s (operational target)
    assert controller.is_aborted() is True
    assert controller.reason == "operator stop"
    with pytest.raises(InterlockError):
        controller.require_running()
    controller.abort(reason="again")  # idempotent: the first reason sticks
    assert controller.reason == "operator stop"


def test_dead_man_switch_with_no_heartbeat_is_not_tripped() -> None:
    assert DeadManSwitch(timeout_seconds=10).is_tripped(now=1000.0) is False


def test_dead_man_switch_trips_on_lost_heartbeat() -> None:
    switch = DeadManSwitch(timeout_seconds=10)
    switch.heartbeat(now=100.0)
    assert switch.is_tripped(now=105.0) is False
    switch.require_alive(now=105.0)

    assert switch.is_tripped(now=120.0) is True
    with pytest.raises(InterlockError):
        switch.require_alive(now=120.0)


def test_rate_and_cost_watchdogs() -> None:
    check_rate_watchdog(rate=10, ceiling=100)
    with pytest.raises(InterlockError):
        check_rate_watchdog(rate=101, ceiling=100)

    check_cost_watchdog(cost_usd=1.0, ceiling=5.0)
    with pytest.raises(InterlockError):
        check_cost_watchdog(cost_usd=9.0, ceiling=5.0)


def test_verified_teardown_blocks_on_a_dirty_target() -> None:
    clean = [
        CleanupResult(case_id="c1", ran=True, succeeded=True, dirty=False),
        CleanupResult(case_id="c2", ran=True, succeeded=True, dirty=False),
    ]
    verified_teardown(clean)

    dirty = [*clean, CleanupResult(case_id="c3", ran=True, succeeded=False, dirty=True)]
    with pytest.raises(InterlockError):
        verified_teardown(dirty)


def test_consent_gate_for_egress() -> None:
    require_egress_consent(leaving_machine=False, consented=False)  # local: no consent needed
    require_egress_consent(leaving_machine=True, consented=True)
    with pytest.raises(InterlockError):
        require_egress_consent(leaving_machine=True, consented=False)
