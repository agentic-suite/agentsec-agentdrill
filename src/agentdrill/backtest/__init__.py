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
from agentdrill.backtest.shadow import (
    DEFAULT_FALSE_BLOCK_BUDGET,
    ShadowDecision,
    ShadowError,
    ShadowReport,
    false_block_rate,
    require_false_block_budget,
    require_side_effect_free,
    run_shadow,
)

__all__ = [
    "DEFAULT_FALSE_BLOCK_BUDGET",
    "DEFAULT_MIN_FIDELITY",
    "BacktestError",
    "BacktestReport",
    "RecordedSession",
    "ReplayLabel",
    "ReplayPolicy",
    "SessionVerdict",
    "ShadowDecision",
    "ShadowError",
    "ShadowReport",
    "backtest",
    "false_block_rate",
    "require_false_block_budget",
    "require_fidelity",
    "require_side_effect_free",
    "run_shadow",
]
