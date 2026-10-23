"""Determinism module — tools for reproducible evaluation runs.

Provides :class:`EnvironmentFreezer` to freeze time, random state, and hash
seeds, :class:`SeedManager` for deterministic PRNG, and
:class:`ReproducibilityChecker` to measure score/trajectory variance across runs.
"""

from agentdrill.determinism.contamination import (
    ContaminationFlag,
    ContaminationProbe,
    TrainingPosture,
)
from agentdrill.determinism.freeze import EnvironmentFreezer
from agentdrill.determinism.pins import PIN_FIELDS, PinChange, PinSet, compare_pins, repin_note
from agentdrill.determinism.reproducibility import ReproducibilityChecker, ReproducibilityReport
from agentdrill.determinism.reproduction import (
    ReproductionResult,
    fingerprint_artifacts,
    verify_reproduction,
)
from agentdrill.determinism.seed import DeterminismConfig, SeedManager

__all__ = [
    "PIN_FIELDS",
    "ContaminationFlag",
    "ContaminationProbe",
    "DeterminismConfig",
    "EnvironmentFreezer",
    "PinChange",
    "PinSet",
    "ReproducibilityChecker",
    "ReproducibilityReport",
    "ReproductionResult",
    "SeedManager",
    "TrainingPosture",
    "compare_pins",
    "fingerprint_artifacts",
    "repin_note",
    "verify_reproduction",
]
