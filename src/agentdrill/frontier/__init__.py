"""Frontier attack classes (M29, F101).

The registry of ASI-gap attack classes and their acceptance checks. Design:
``docs/design/detonation-breakit-frontier.md``; PRD 39 (R75).
"""

from agentdrill.frontier.classes import (
    ASI_CATEGORIES,
    DEFAULT_MIN_ASI_COVERAGE,
    FRONTIER_CLASSES,
    MIN_CARRIERS,
    ApprovalProbe,
    AsiCategory,
    FrontierClass,
    FrontierError,
    approval_fidelity,
    asi_coverage,
    require_approval_fidelity,
    require_asi_coverage,
    require_audience_rejection,
    require_bounded_handoff,
    require_browser_guards,
    require_carriers,
    require_cost_within_ceiling,
    require_dual_use_signed,
    require_no_persistence,
    require_spec_gated,
)

__all__ = [
    "ASI_CATEGORIES",
    "DEFAULT_MIN_ASI_COVERAGE",
    "FRONTIER_CLASSES",
    "MIN_CARRIERS",
    "ApprovalProbe",
    "AsiCategory",
    "FrontierClass",
    "FrontierError",
    "approval_fidelity",
    "asi_coverage",
    "require_approval_fidelity",
    "require_asi_coverage",
    "require_audience_rejection",
    "require_bounded_handoff",
    "require_browser_guards",
    "require_carriers",
    "require_cost_within_ceiling",
    "require_dual_use_signed",
    "require_no_persistence",
    "require_spec_gated",
]
