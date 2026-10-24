"""M22 22.2 — fault injection & fail-closed (RED → GREEN).

Faults across runner/targets/oracles/drivers fail **closed** (never silently
green); a case failure never aborts the pack.
"""

from __future__ import annotations

import pytest

from agentdrill.hardening import (
    FAULT_KINDS,
    FaultError,
    FaultOutcome,
    require_fail_closed,
    run_fault,
    run_pack,
)


def _boom() -> None:
    raise RuntimeError("injected fault")


def test_each_fault_kind_fails_closed() -> None:
    assert set(FAULT_KINDS) >= {"runner", "target", "oracle", "driver", "tamper"}
    for kind in FAULT_KINDS:
        outcome = run_fault(kind, _boom)
        assert isinstance(outcome, FaultOutcome)
        assert outcome.fail_closed is True
        assert outcome.raised is True


def test_a_silent_fault_is_not_fail_closed() -> None:
    outcome = run_fault("runner", lambda: None)  # swallows — silently green
    assert outcome.fail_closed is False
    with pytest.raises(FaultError, match="silently"):
        require_fail_closed([outcome])


def test_a_case_failure_never_aborts_the_pack() -> None:
    results = run_pack([lambda: "ok", _boom, lambda: "ok"])
    assert results == [True, False, True]
