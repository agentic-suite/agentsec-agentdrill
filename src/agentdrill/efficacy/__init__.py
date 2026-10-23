"""Efficacy & utility package (M13).

The unguarded control group (13.1, F59), inert flagging (13.2), utility-under-
attack (13.3, F51), per-case cleanup (13.4, F50) and the efficacy report
artifact (13.5). Design: ``docs/design/efficacy.md``.
"""

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

__all__ = [
    "INERT_FLAG",
    "EfficacyError",
    "EfficacyResult",
    "countable",
    "enforcement_rate",
    "inert_cases",
    "require_efficacy_backed",
    "run_efficacy",
]
