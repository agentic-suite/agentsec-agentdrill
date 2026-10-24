"""Trace backtest & shadow mode (M27, F92).

Backtest a candidate policy against redacted production sessions, run a
side-effect-free shadow, and promote a session into a redacted drill case.
Design: ``docs/design/backtest-path-intake.md``; PRD 30 (R66).
"""

from agentdrill.backtest.replay import (
    DEFAULT_MIN_FIDELITY,
    BacktestError,
    BacktestReport,
    RecordedSession,
    ReplayLabel,
    ReplayPolicy,
    SessionVerdict,
    backtest,
    require_fidelity,
)

__all__ = [
    "DEFAULT_MIN_FIDELITY",
    "BacktestError",
    "BacktestReport",
    "RecordedSession",
    "ReplayLabel",
    "ReplayPolicy",
    "SessionVerdict",
    "backtest",
    "require_fidelity",
]
