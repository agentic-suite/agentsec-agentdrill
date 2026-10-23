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
from agentdrill.comparison.attribution import (
    Attribution,
    AttributionSource,
    attribute_flip,
    bisect_flip,
)
from agentdrill.comparison.change_detection import (
    ChangeKind,
    ChangeReport,
    RunChange,
    detect_changes,
)
from agentdrill.comparison.engine import ComparisonEngine, ComparisonResult
from agentdrill.comparison.golden import (
    Golden,
    GoldenCase,
    GoldenChange,
    GoldenCheck,
    check_golden,
)
from agentdrill.comparison.golden_store import GoldenNotFoundError, GoldenStore
from agentdrill.comparison.outcome_classification import (
    Classification,
    OutcomeClassification,
    classify_outcome,
)
from agentdrill.comparison.report import ComparisonReport

__all__ = [
    "AggregateDelta",
    "AttackComparison",
    "AttackComparisonEngine",
    "Attribution",
    "AttributionSource",
    "CaseDelta",
    "ChangeKind",
    "ChangeReport",
    "Classification",
    "ComparisonEngine",
    "ComparisonReport",
    "ComparisonResult",
    "Golden",
    "GoldenCase",
    "GoldenChange",
    "GoldenCheck",
    "GoldenNotFoundError",
    "GoldenStore",
    "OutcomeClassification",
    "RunChange",
    "TagDelta",
    "attribute_flip",
    "bisect_flip",
    "check_golden",
    "classify_outcome",
    "detect_changes",
]
