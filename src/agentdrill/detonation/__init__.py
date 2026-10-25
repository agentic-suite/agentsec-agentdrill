"""Extension detonation (M29, F98).

Detonate unknown extensions in the hermetic lab and report observed behaviour as
bounded evidence. Design: ``docs/design/detonation-breakit-frontier.md``; PRD 36
(R72).
"""

from agentdrill.detonation.behavior import (
    DEFAULT_MIN_RECALL,
    OBSERVATION_KINDS,
    BehaviorReport,
    DetonationError,
    ExtensionSpec,
    LabEvent,
    Observation,
    ObservationKind,
    detect_observations,
    prior_version_diff,
    require_no_escapes,
    require_recall,
    run_detonation,
    seeded_recall,
)

__all__ = [
    "DEFAULT_MIN_RECALL",
    "OBSERVATION_KINDS",
    "BehaviorReport",
    "DetonationError",
    "ExtensionSpec",
    "LabEvent",
    "Observation",
    "ObservationKind",
    "detect_observations",
    "prior_version_diff",
    "require_no_escapes",
    "require_recall",
    "run_detonation",
    "seeded_recall",
]
