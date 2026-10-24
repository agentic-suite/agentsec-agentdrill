"""Platform compatibility matrix (M30 30.3-30.4, F103).

Make "compatible" **measurable**: graded levels **L0 listed -> L1 config-aware ->
L2 driven -> L3 observed (witnessed) -> L4 gated (contract pack in CI)**, each
with **evidence** required from L2 (measured, never asserted); per-surface rows;
the prioritization model; the **reference-harness policy** (headline tables use
open-source harnesses, >= 2 at L3+); the version-follow SLA label; and one
published number -- **adoption-weighted coverage (AWC)**. There is **no composite
exposure score**. Design: ``docs/design/trace-explorer-and-platform-standards.md``;
PRD 41 (R77).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

#: The graded compatibility levels.
PlatformLevel = Literal["L0", "L1", "L2", "L3", "L4"]

#: The levels in order.
LEVELS: tuple[str, ...] = ("L0", "L1", "L2", "L3", "L4")

#: Human labels per level.
LEVEL_LABELS: dict[str, str] = {
    "L0": "listed",
    "L1": "config-aware",
    "L2": "driven",
    "L3": "observed",
    "L4": "gated",
}

#: The prioritization model weights (must sum to 1.0).
PRIORITY_WEIGHTS: dict[str, float] = {
    "adoption": 0.30,
    "attack_surface": 0.25,
    "driveability": 0.20,
    "reproducibility": 0.15,
    "strategic": 0.10,
}

#: The minimum AWC a published matrix must reach.
MIN_AWC = 0.60

#: The minimum number of open-source harnesses at L3+ (reference-harness policy).
MIN_REFERENCE_HARNESSES = 2

#: The version-follow SLA, in days (L4 within 72 h).
VERSION_FOLLOW_SLA_DAYS = 7
VERSION_FOLLOW_SLA_L4_HOURS = 72

#: Factor scores run 0-5.
_MAX_FACTOR = 5


class PlatformError(ValueError):
    """Raised when the matrix is inconsistent or below a policy gate."""


class PlatformEntry(BaseModel):
    """One row of the compatibility matrix (per platform x surface)."""

    name: str
    level: PlatformLevel = "L0"
    surface: str = "cli"
    tier: int = 1
    open_source: bool = False
    adoption: int = 0
    attack_surface: int = 0
    driveability: int = 0
    reproducibility: int = 0
    strategic: int = 0
    evidence: list[str] = Field(default_factory=list)
    #: "defaults" or "auto-approve" — always labelled (never implied).
    config_posture: str = "defaults"


def priority_score(entry: PlatformEntry) -> float:
    """The weighted prioritization score for an entry (0.0-1.0)."""
    total = (
        PRIORITY_WEIGHTS["adoption"] * entry.adoption
        + PRIORITY_WEIGHTS["attack_surface"] * entry.attack_surface
        + PRIORITY_WEIGHTS["driveability"] * entry.driveability
        + PRIORITY_WEIGHTS["reproducibility"] * entry.reproducibility
        + PRIORITY_WEIGHTS["strategic"] * entry.strategic
    )
    return total / _MAX_FACTOR


def rank_entries(entries: Sequence[PlatformEntry]) -> list[PlatformEntry]:
    """Rank entries by priority (highest first), then by name."""
    return sorted(entries, key=lambda entry: (-priority_score(entry), entry.name))


def _level_ratio(level: str) -> float:
    return LEVELS.index(level) / (len(LEVELS) - 1)


def awc(entries: Sequence[PlatformEntry]) -> float:
    """Adoption-weighted coverage: the single published compatibility number."""
    weight = sum(entry.adoption for entry in entries)
    if weight == 0:
        return 1.0
    return sum(entry.adoption * _level_ratio(entry.level) for entry in entries) / weight


def require_awc(entries: Sequence[PlatformEntry], *, minimum: float = MIN_AWC) -> None:
    """Fail loudly unless AWC is at least ``minimum``.

    Raises:
        PlatformError: The coverage is below the gate.
    """
    coverage = awc(entries)
    if coverage < minimum:
        raise PlatformError(f"AWC {coverage:.2f} is below the required {minimum:.2f}")


def require_levels(entries: Sequence[PlatformEntry]) -> None:
    """Fail loudly unless every L2+ entry carries evidence.

    Raises:
        PlatformError: An L2+ entry has no evidence (measured, not asserted).
    """
    for entry in entries:
        if entry.level not in ("L0", "L1") and not entry.evidence:
            raise PlatformError(
                f"{entry.name}: level {entry.level} requires evidence (measured, not asserted)"
            )


def require_reference_harnesses(
    entries: Sequence[PlatformEntry], *, minimum: int = MIN_REFERENCE_HARNESSES
) -> None:
    """Fail loudly unless at least ``minimum`` open-source harnesses are at L3+.

    Raises:
        PlatformError: Too few open-source harnesses at L3+.
    """
    open_at_l3 = [
        entry
        for entry in entries
        if entry.open_source and LEVELS.index(entry.level) >= LEVELS.index("L3")
    ]
    if len(open_at_l3) < minimum:
        raise PlatformError(
            f"reference-harness policy needs >= {minimum} open-source harnesses at L3+, "
            f"found {len(open_at_l3)}"
        )
