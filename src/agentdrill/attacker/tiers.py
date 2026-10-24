"""Attacker tiers (M24 24.1, F85).

T0 static · T1 repeated (k in {1,5,10,25}, seeded) · T2 documented-pattern
mutation (F40 caps) · T3 stub deferred, RoE-gated, local-only. Every result
carries its tier + k + effort. Design:
``docs/prd/25-attacker-strength-and-pressure.md``.
"""

from __future__ import annotations

from pydantic import BaseModel

#: The attacker tiers.
TIERS: tuple[str, ...] = ("T0", "T1", "T2", "T3")

#: The repeat counts for T1.
K_VALUES: tuple[int, ...] = (1, 5, 10, 25)

#: Effort label per tier.
_EFFORT: dict[str, str] = {
    "T0": "static",
    "T1": "repeated",
    "T2": "mutation",
    "T3": "deferred",
}


class TierError(ValueError):
    """Raised when an unknown attacker tier is labelled."""


class TierLabel(BaseModel):
    """The tier + k + effort carried by every published result."""

    tier: str
    k: int = 1
    effort: str = "static"


def label_tier(tier: str, *, k: int = 1) -> TierLabel:
    """Label a result with its attacker tier, k and effort.

    Raises:
        TierError: The tier is unknown.
    """
    effort = _EFFORT.get(tier)
    if effort is None:
        raise TierError(f"unknown attacker tier: {tier!r}; known: {list(TIERS)}")
    return TierLabel(tier=tier, k=k, effort=effort)


def t3_deferred() -> bool:
    """Whether T3 remains deferred (RoE-gated, local-only when introduced)."""
    return True
