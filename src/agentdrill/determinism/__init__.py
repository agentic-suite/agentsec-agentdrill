"""Determinism module — tools for reproducible evaluation runs.

Provides :class:`EnvironmentFreezer` to freeze time, random state, and hash
seeds, :class:`SeedManager` for deterministic PRNG, and
:class:`ReproducibilityChecker` to measure score/trajectory variance across runs.
"""

from agentdrill.determinism.freeze import EnvironmentFreezer
from agentdrill.determinism.pins import PIN_FIELDS, PinChange, PinSet, compare_pins, repin_note
from agentdrill.determinism.reproducibility import ReproducibilityChecker, ReproducibilityReport
from agentdrill.determinism.seed import DeterminismConfig, SeedManager

__all__ = [
    "PIN_FIELDS",
    "DeterminismConfig",
    "EnvironmentFreezer",
    "PinChange",
    "PinSet",
    "ReproducibilityChecker",
    "ReproducibilityReport",
    "SeedManager",
    "compare_pins",
    "repin_note",
]
