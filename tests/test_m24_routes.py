"""M24 24.5 — route-family library, F89 (RED → GREEN).

Effect goals x route families (command/path/encoding/indirection/tool-overlap/
multi-step/transport/timing); ≥12 effects catalogued and reviewed like packs.
"""

from __future__ import annotations

import pytest

from agentdrill.attacker import (
    ROUTE_FAMILIES,
    RouteCatalog,
    RouteError,
    default_catalog,
    require_reviewed,
)


def test_at_least_twelve_effects() -> None:
    catalog = default_catalog()
    assert len(catalog.goals) >= 12


def test_families_are_the_documented_set() -> None:
    assert set(ROUTE_FAMILIES) == {
        "command",
        "path",
        "encoding",
        "indirection",
        "tool-overlap",
        "multi-step",
        "transport",
        "timing",
    }


def test_every_goal_uses_known_families() -> None:
    catalog = default_catalog()
    for goal in catalog.goals:
        assert set(goal.families) <= set(ROUTE_FAMILIES), goal.effect


def test_families_are_reviewed_like_packs() -> None:
    require_reviewed(default_catalog())  # no raise
    with pytest.raises(RouteError, match="review"):
        require_reviewed(RouteCatalog(goals=[], reviewed=False))


def test_catalog_is_a_pydantic_model() -> None:
    assert isinstance(default_catalog(), RouteCatalog)
