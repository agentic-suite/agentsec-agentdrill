"""Bounded search engine (M24 24.6, F89).

A seeded breadth-over-families then depth search with budgets and family-level
pruning; it runs **only under Rules of Engagement**. Same seed ⇒ same sequence.
Design: ``docs/prd/28-policy-bypass-search.md``.
"""

from __future__ import annotations

import random
from collections import defaultdict

from pydantic import BaseModel, Field

from agentdrill.attacker.routes import RouteCatalog


class SearchError(ValueError):
    """Raised when the route search would run without Rules of Engagement."""


class SearchResult(BaseModel):
    """A seeded, bounded route-search sequence."""

    seed: int
    sequence: list[str] = Field(default_factory=list)
    roe_enforced: bool = True


def bounded_search(
    catalog: RouteCatalog,
    *,
    seed: int,
    max_routes: int,
    roe_ok: bool = True,
) -> SearchResult:
    """Search the route space breadth-over-families then depth.

    Raises:
        SearchError: The search would run without Rules of Engagement.
    """
    if not roe_ok:
        raise SearchError("route search runs only under Rules of Engagement (RoE)")

    by_family: dict[str, list[str]] = defaultdict(list)
    for goal in catalog.goals:
        for family in goal.families:
            by_family[family].append(f"{goal.effect}:{family}")

    rng = random.Random(seed)  # noqa: S311 - seeded search order, not crypto
    families = sorted(by_family)
    rng.shuffle(families)

    sequence: list[str] = []
    # breadth: one route per family first, then depth into each family.
    depth = 0
    while len(sequence) < max_routes:
        added = False
        for family in families:
            routes = sorted(by_family[family])
            if depth < len(routes):
                sequence.append(routes[depth])
                added = True
                if len(sequence) >= max_routes:
                    break
        if not added:
            break
        depth += 1

    return SearchResult(seed=seed, sequence=sequence, roe_enforced=True)
