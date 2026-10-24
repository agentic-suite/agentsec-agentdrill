"""Lifecycle package (M18).

Incident intake (18.1, F60), fix-validation (18.2, F61), seam probing (18.3,
F62), target attestation (18.4, F63), the standalone verifier (18.5, F64),
evidence privacy (18.6, F65), quickstart (18.7, F66), the MCP/memory pack
classes (18.8, F19/F20) and closes-the-loop policy suggestion (18.9, F21).
Design: ``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from agentdrill.lifecycle.fix_validation import (
    FIX_DECAY,
    FixCase,
    FixDecayError,
    attribute_decay,
    evaluate_fix,
    regression_case,
    require_fix_holds,
)
from agentdrill.lifecycle.intake import (
    SLA_DAYS,
    Decision,
    Incident,
    IntakeError,
    TriageResult,
    assess,
    is_stale,
    require_within_sla,
)

__all__ = [
    "FIX_DECAY",
    "SLA_DAYS",
    "Decision",
    "FixCase",
    "FixDecayError",
    "Incident",
    "IntakeError",
    "TriageResult",
    "assess",
    "attribute_decay",
    "evaluate_fix",
    "is_stale",
    "regression_case",
    "require_fix_holds",
    "require_within_sla",
]
