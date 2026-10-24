"""Version-follow SLA + drivers (M30 30.4, F103).

Keep the matrix honest over time: a **nightly driver canary** that catches a
breakage before a user hits it (>= 90 %); a **freshness SLA** on every matrix row
(<= 7 days, L4 <= 72 h); the **"defaults vs auto-approve"** posture is always
labelled; and the runtime matrix includes a **local-first, judge-free** subset.
Design: ``docs/design/trace-explorer-and-platform-standards.md``; PRD 41 (R77).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel

from agentdrill.platform.matrix import LEVELS, VERSION_FOLLOW_SLA_DAYS, PlatformError

#: The minimum share of known breakages the canary must catch pre-user.
MIN_CANARY_DETECTION = 0.9

#: The L4 freshness bound, in days (72 h).
L4_FRESHNESS_DAYS = 3.0

#: The config posture a matrix row must declare.
ConfigPosture = Literal["defaults", "auto-approve"]


class DriverCanary(BaseModel):
    """One driver's nightly canary result."""

    driver: str
    passing: bool
    at: str


class MatrixFreshness(BaseModel):
    """How recently one matrix row was updated."""

    level: str
    updated_days_ago: float


class RuntimeSubset(BaseModel):
    """One host/CI/model-runtime cell of the compatibility matrix."""

    name: str
    local_first: bool = False
    judge_free: bool = False


def canary_detection_rate(*, detected: int, known: int) -> float:
    """The share of known breakages the canary caught before a user."""
    if known <= 0:
        return 1.0
    return detected / known


def require_canary_detection(
    *, detected: int, known: int, minimum: float = MIN_CANARY_DETECTION
) -> None:
    """Fail loudly unless the canary catches at least ``minimum`` of known breakages.

    Raises:
        PlatformError: The detection rate is below the gate.
    """
    rate = canary_detection_rate(detected=detected, known=known)
    if rate < minimum:
        raise PlatformError(f"canary detection {rate:.0%} is below the required {minimum:.0%}")


def require_canary_green(canary: Sequence[DriverCanary]) -> None:
    """Fail loudly if any driver's canary is failing.

    Raises:
        PlatformError: A driver canary is red.
    """
    broken = [result.driver for result in canary if not result.passing]
    if broken:
        raise PlatformError(f"driver canary is red for: {broken}")


def require_freshness(freshness: Sequence[MatrixFreshness]) -> None:
    """Fail loudly unless every row is within its freshness SLA.

    Raises:
        PlatformError: A row is stale (<= 7 d; L4 <= 72 h).
    """
    for row in freshness:
        if row.level not in LEVELS:
            raise PlatformError(f"unknown matrix level {row.level!r}")
        bound = L4_FRESHNESS_DAYS if row.level == "L4" else float(VERSION_FOLLOW_SLA_DAYS)
        if row.updated_days_ago > bound:
            raise PlatformError(
                f"{row.level} row is {row.updated_days_ago:.1f} days old "
                f"(SLA {bound:.1f} days)"
            )


def require_config_posture(posture: str) -> None:
    """Fail loudly unless the posture is explicitly "defaults" or "auto-approve".

    Raises:
        PlatformError: The posture is unlabelled or unknown.
    """
    if posture not in ("defaults", "auto-approve"):
        raise PlatformError(
            f"config posture {posture!r} must be 'defaults' or 'auto-approve' (always labelled)"
        )


def require_judge_free_subset(subsets: Sequence[RuntimeSubset]) -> None:
    """Fail loudly unless a local-first, judge-free runtime subset is published.

    Raises:
        PlatformError: No local-first judge-free subset exists.
    """
    local = [s for s in subsets if s.local_first and s.judge_free]
    if not local:
        raise PlatformError(
            "the runtime matrix must include a local-first, judge-free subset "
            "(no model/judge required)"
        )
