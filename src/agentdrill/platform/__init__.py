"""Platform compatibility matrix (M30, F103).

Graded L0-L4 levels with evidence, per-surface rows, the prioritization model,
the reference-harness policy, the version-follow SLA label and the AWC metric.
Design: ``docs/design/trace-explorer-and-platform-standards.md``; PRD 41 (R77).
"""

from agentdrill.platform.matrix import (
    LEVEL_LABELS,
    LEVELS,
    MIN_AWC,
    MIN_REFERENCE_HARNESSES,
    PRIORITY_WEIGHTS,
    VERSION_FOLLOW_SLA_DAYS,
    VERSION_FOLLOW_SLA_L4_HOURS,
    PlatformEntry,
    PlatformError,
    PlatformLevel,
    awc,
    priority_score,
    rank_entries,
    require_awc,
    require_levels,
    require_reference_harnesses,
)

__all__ = [
    "LEVELS",
    "LEVEL_LABELS",
    "MIN_AWC",
    "MIN_REFERENCE_HARNESSES",
    "PRIORITY_WEIGHTS",
    "VERSION_FOLLOW_SLA_DAYS",
    "VERSION_FOLLOW_SLA_L4_HOURS",
    "PlatformEntry",
    "PlatformError",
    "PlatformLevel",
    "awc",
    "priority_score",
    "rank_entries",
    "require_awc",
    "require_levels",
    "require_reference_harnesses",
]
