"""Comparison engine: candidate-vs-baseline deltas and reports (spec §"Comparison Model").

Provides ComparisonEngine (3-level delta computation) and ComparisonReport
(JSON + Markdown output). See individual module docs for details.

The comparison pipeline:
1. :class:`ComparisonEngine` takes a baseline RunScore and a candidate RunScore
   and computes per-scenario, per-family, and aggregate deltas.
2. :class:`ComparisonReport` formats the result as JSON or Markdown for CI
   and human consumption.
"""

from agentdrill.comparison.attack_engine import (
    AggregateDelta,
    AttackComparison,
    AttackComparisonEngine,
    CaseDelta,
    TagDelta,
)
from agentdrill.comparison.engine import ComparisonEngine, ComparisonResult
from agentdrill.comparison.golden import (
    Golden,
    GoldenCase,
    GoldenChange,
    GoldenCheck,
    check_golden,
)
from agentdrill.comparison.report import ComparisonReport

__all__ = [
    "AggregateDelta",
    "AttackComparison",
    "AttackComparisonEngine",
    "CaseDelta",
    "ComparisonEngine",
    "ComparisonReport",
    "ComparisonResult",
    "Golden",
    "GoldenCase",
    "GoldenChange",
    "GoldenCheck",
    "TagDelta",
    "check_golden",
]
