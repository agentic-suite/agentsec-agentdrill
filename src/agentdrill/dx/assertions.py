"""Programmatic assertions (M20 20.5, F73).

A Python API — ``assert_blocked`` / ``assert_missed`` / ``assert_degraded`` /
``assert_kill_time_under`` — over the same run objects, so a host test suite can
embed agentdrill's verdicts. Design: ``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

from typing import Any


class DxAssertionError(AssertionError):
    """Raised when a programmatic assertion fails."""


def _outcome(result: Any) -> str:
    """The outcome of a run object (a ``Verdict`` or an outcome string)."""
    if isinstance(result, str):
        return result
    return str(getattr(result, "outcome", result))


def _case_id(result: Any) -> str:
    if isinstance(result, str):
        return "case"
    return str(getattr(result, "case_id", "case"))


def assert_blocked(result: Any) -> None:
    """Assert a result is ``blocked``.

    Raises:
        DxAssertionError: The outcome is not ``blocked``.
    """
    outcome = _outcome(result)
    if outcome != "blocked":
        raise DxAssertionError(f"{_case_id(result)}: expected blocked, got {outcome!r}")


def assert_missed(result: Any) -> None:
    """Assert a result is ``missed``."""
    outcome = _outcome(result)
    if outcome != "missed":
        raise DxAssertionError(f"{_case_id(result)}: expected missed, got {outcome!r}")


def assert_degraded(result: Any) -> None:
    """Assert a result is ``degraded``."""
    outcome = _outcome(result)
    if outcome != "degraded":
        raise DxAssertionError(f"{_case_id(result)}: expected degraded, got {outcome!r}")


def assert_kill_time_under(elapsed: float, *, seconds: float) -> None:
    """Assert a kill time is under ``seconds``.

    Raises:
        DxAssertionError: The elapsed time is not under the bound.
    """
    if elapsed > seconds:
        raise DxAssertionError(f"kill time {elapsed}s exceeds {seconds}s")
