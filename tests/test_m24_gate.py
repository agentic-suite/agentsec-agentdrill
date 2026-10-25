"""M24 24.4 — Hold@k CI gate, F86 (RED → GREEN).

A configurable gate (default k=5 PR, 25 nightly) on critical must-block cases;
`Hold@5 < 100%` blocks.
"""

from __future__ import annotations

import pytest

from agentdrill.attacker import (
    DEFAULT_NIGHTLY_K,
    DEFAULT_PR_K,
    HoldGateError,
    HoldGateResult,
    hold_gate,
    require_hold,
)


def test_hold_at_5_below_100_blocks() -> None:
    result = hold_gate(0.8, k=5)
    assert isinstance(result, HoldGateResult)
    assert result.passed is False
    with pytest.raises(HoldGateError, match="Hold@5"):
        require_hold(result)


def test_full_hold_passes() -> None:
    require_hold(hold_gate(1.0, k=5))  # no raise


def test_default_ks() -> None:
    assert DEFAULT_PR_K == 5
    assert DEFAULT_NIGHTLY_K == 25
