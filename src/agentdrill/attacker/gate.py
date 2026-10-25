"""`Hold@k` CI gate (M24 24.4, F86).

A configurable gate on critical must-block cases — default k=5 for PRs and
k=25 nightly; ``Hold@5 < 100%`` blocks. Design:
``docs/prd/25-attacker-strength-and-pressure.md``.
"""

from __future__ import annotations

from pydantic import BaseModel

#: The default k for PR runs.
DEFAULT_PR_K = 5

#: The default k for nightly runs.
DEFAULT_NIGHTLY_K = 25


class HoldGateError(ValueError):
    """Raised when a must-block case does not hold at k."""


class HoldGateResult(BaseModel):
    """The `Hold@k` gate result."""

    k: int
    hold_rate: float
    required: float = 1.0
    passed: bool = True


def hold_gate(hold_rate: float, *, k: int = DEFAULT_PR_K, required: float = 1.0) -> HoldGateResult:
    """Gate a critical must-block case on ``Hold@k`` (default 100%)."""
    return HoldGateResult(k=k, hold_rate=hold_rate, required=required, passed=hold_rate >= required)


def require_hold(result: HoldGateResult) -> None:
    """Fail loudly if the `Hold@k` gate is not passed.

    Raises:
        HoldGateError: The hold rate is below the required threshold.
    """
    if not result.passed:
        raise HoldGateError(
            f"Hold@{result.k} {result.hold_rate:.0%} < required {result.required:.0%}"
        )
