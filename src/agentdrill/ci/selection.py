"""Diff-aware re-run selection (M11 11.6, F76).

Compute the affected cases from the changed surface so CI time scales with diff
size: the selected set is exactly the cases bound to the changed surfaces.
Design: ``docs/design/ci-gate.md`` §Change-driven execution.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from pydantic import BaseModel

from agentdrill.models.attack_pack import AttackCase


class Selection(BaseModel):
    """The cases a diff selects, and the fraction of the pack that implies."""

    selected: list[str]
    total: int
    fraction: float


def case_surfaces(case: AttackCase) -> set[str]:
    """The surfaces a case binds: its target type, attack tools and tags."""
    surfaces = {case.target.type}
    surfaces.update(step.tool for step in case.attack.steps)
    surfaces.update(case.tags)
    return surfaces


def affected_cases(cases: Sequence[AttackCase], changed_surfaces: Iterable[str]) -> list[str]:
    """Case ids bound to at least one changed surface, in pack order."""
    changed = set(changed_surfaces)
    return [case.id for case in cases if case_surfaces(case) & changed]


def selection(cases: Sequence[AttackCase], changed_surfaces: Iterable[str]) -> Selection:
    """The :class:`Selection` for a diff (its fraction scales CI time)."""
    selected = affected_cases(cases, changed_surfaces)
    total = len(cases)
    fraction = len(selected) / total if total else 0.0
    return Selection(selected=selected, total=total, fraction=fraction)
