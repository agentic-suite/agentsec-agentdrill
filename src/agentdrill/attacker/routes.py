"""Route-family library (M24 24.5, F89).

Effect goals x route families (command / path / encoding / indirection /
tool-overlap / multi-step / transport / timing); >= 12 effects catalogued and
reviewed like packs. Design: ``docs/prd/28-policy-bypass-search.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

#: The documented route families.
ROUTE_FAMILIES: tuple[str, ...] = (
    "command",
    "path",
    "encoding",
    "indirection",
    "tool-overlap",
    "multi-step",
    "transport",
    "timing",
)


class RouteError(ValueError):
    """Raised when the route catalog is unreviewed or malformed."""


class EffectGoal(BaseModel):
    """An effect goal and the route families that may reach it."""

    effect: str
    families: list[str] = Field(default_factory=list)


class RouteCatalog(BaseModel):
    """The effect-goal x route-family catalog."""

    goals: list[EffectGoal] = Field(default_factory=list)
    reviewed: bool = True


def default_catalog() -> RouteCatalog:
    """The default catalog (>= 12 effect goals)."""
    goals = [
        EffectGoal(effect="write-forbidden-file", families=["path", "encoding"]),
        EffectGoal(effect="delete-forbidden-file", families=["command", "path"]),
        EffectGoal(effect="read-secret", families=["indirection", "tool-overlap"]),
        EffectGoal(effect="exfiltrate-to-network", families=["transport", "encoding"]),
        EffectGoal(effect="exec-shell", families=["command", "multi-step"]),
        EffectGoal(effect="privilege-escalate", families=["indirection", "multi-step"]),
        EffectGoal(effect="approval-bypass", families=["timing", "multi-step"]),
        EffectGoal(effect="tool-shadowing", families=["tool-overlap"]),
        EffectGoal(effect="prompt-injection", families=["encoding", "indirection"]),
        EffectGoal(effect="memory-poisoning", families=["indirection"]),
        EffectGoal(effect="cross-task-leak", families=["tool-overlap", "multi-step"]),
        EffectGoal(effect="budget-evasion", families=["timing"]),
    ]
    return RouteCatalog(goals=goals, reviewed=True)


def require_reviewed(catalog: RouteCatalog) -> None:
    """Fail loudly if the catalog was not reviewed like a pack.

    Raises:
        RouteError: The catalog is unreviewed or names an unknown family.
    """
    if not catalog.reviewed:
        raise RouteError("route catalog must be reviewed like a pack")
    for goal in catalog.goals:
        unknown = set(goal.families) - set(ROUTE_FAMILIES)
        if unknown:
            raise RouteError(f"goal {goal.effect!r} uses unknown families: {sorted(unknown)}")
