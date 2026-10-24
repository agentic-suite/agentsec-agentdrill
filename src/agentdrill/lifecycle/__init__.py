"""Lifecycle package (M18).

Incident intake (18.1, F60), fix-validation (18.2, F61), seam probing (18.3,
F62), target attestation (18.4, F63), the standalone verifier (18.5, F64),
evidence privacy (18.6, F65), quickstart (18.7, F66), the MCP/memory pack
classes (18.8, F19/F20) and closes-the-loop policy suggestion (18.9, F21).
Design: ``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from agentdrill.lifecycle.attestation import (
    AttestationError,
    can_publish,
    require_publishable,
    result_attestation,
)
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
from agentdrill.lifecycle.privacy import (
    PATTERNS,
    Receipt,
    RedactionResult,
    redact,
    verify_receipts,
)
from agentdrill.lifecycle.quickstart import (
    BUDGET_MINUTES,
    DEMO_WATERMARK,
    QuickstartResult,
    run_quickstart,
    within_budget,
)
from agentdrill.lifecycle.seams import SEAM_GAP, SeamFinding, probe_seam
from agentdrill.lifecycle.verifier import (
    MIN_SEEDS,
    Bundle,
    VerifyVerdict,
    verify_bundle,
)

__all__ = [
    "BUDGET_MINUTES",
    "DEMO_WATERMARK",
    "FIX_DECAY",
    "MIN_SEEDS",
    "PATTERNS",
    "SEAM_GAP",
    "SLA_DAYS",
    "AttestationError",
    "Bundle",
    "Decision",
    "FixCase",
    "FixDecayError",
    "Incident",
    "IntakeError",
    "QuickstartResult",
    "Receipt",
    "RedactionResult",
    "SeamFinding",
    "TriageResult",
    "VerifyVerdict",
    "assess",
    "attribute_decay",
    "can_publish",
    "evaluate_fix",
    "is_stale",
    "probe_seam",
    "redact",
    "regression_case",
    "require_fix_holds",
    "require_publishable",
    "require_within_sla",
    "result_attestation",
    "run_quickstart",
    "verify_bundle",
    "verify_receipts",
    "within_budget",
]
