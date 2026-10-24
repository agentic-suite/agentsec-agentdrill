"""Frontier attack classes (M29, F101).

The registry of ASI-gap attack classes and their acceptance checks. Design:
``docs/design/detonation-breakit-frontier.md``; PRD 39 (R75).
"""

from agentdrill.frontier.classes import (
    ASI_CATEGORIES,
    DEFAULT_MIN_ASI_COVERAGE,
    FRONTIER_CLASSES,
    AsiCategory,
    FrontierClass,
    FrontierError,
    asi_coverage,
    require_asi_coverage,
    require_audience_rejection,
    require_dual_use_signed,
)

__all__ = [
    "ASI_CATEGORIES",
    "DEFAULT_MIN_ASI_COVERAGE",
    "FRONTIER_CLASSES",
    "AsiCategory",
    "FrontierClass",
    "FrontierError",
    "asi_coverage",
    "require_asi_coverage",
    "require_audience_rejection",
    "require_dual_use_signed",
]
