"""Efficacy & utility package (M13).

The unguarded control group (13.1, F59), inert flagging (13.2), utility-under-
attack (13.3, F51), per-case cleanup (13.4, F50) and the efficacy report
artifact (13.5). Design: ``docs/design/efficacy.md``.
"""

from agentdrill.efficacy.cleanup import (
    DIRTY_TARGET,
    CleanupResult,
    DirtyTargetError,
    cleanup_after_case,
    dirty_targets,
    require_clean,
    run_cleanup,
)
from agentdrill.efficacy.control import (
    EfficacyError,
    EfficacyResult,
    require_efficacy_backed,
    run_efficacy,
)
from agentdrill.efficacy.inert import (
    INERT_FLAG,
    countable,
    enforcement_rate,
    inert_cases,
)
from agentdrill.efficacy.utility import (
    HIGH_ENFORCEMENT,
    UTILITY_COST,
    UtilityReport,
    assess_utility,
)

__all__ = [
    "DIRTY_TARGET",
    "HIGH_ENFORCEMENT",
    "INERT_FLAG",
    "UTILITY_COST",
    "CleanupResult",
    "DirtyTargetError",
    "EfficacyError",
    "EfficacyResult",
    "UtilityReport",
    "assess_utility",
    "cleanup_after_case",
    "countable",
    "dirty_targets",
    "enforcement_rate",
    "inert_cases",
    "require_clean",
    "require_efficacy_backed",
    "run_cleanup",
    "run_efficacy",
]
