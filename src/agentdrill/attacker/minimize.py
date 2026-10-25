"""Minimization + dedup + promotion (M24 24.7, F89).

Delta-debug minimization of a confirmed bypass, family-level dedup, and
auto-promotion to a permanent regression case (F61) with attribution (F38) —
in the same release. Design: ``docs/prd/28-policy-bypass-search.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from pydantic import BaseModel, Field

from agentdrill.lifecycle import FixCase, regression_case


class MinimizedBypass(BaseModel):
    """A minimized bypass reproducer and its minimization ratio."""

    effect: str
    reproducer: list[str] = Field(default_factory=list)
    ratio: float = 0.0
    regression_case: str | None = None


def minimize(
    effect: str,
    steps: Sequence[str],
    *,
    essential: Callable[[Sequence[str]], bool],
) -> MinimizedBypass:
    """Delta-debug ``steps`` to the smallest subset for which ``essential`` holds."""
    current = list(steps)
    for step in list(current):
        candidate = [s for s in current if s != step]
        if candidate and essential(candidate):
            current = candidate
    ratio = len(steps) / len(current) if current else 0.0
    return MinimizedBypass(effect=effect, reproducer=current, ratio=ratio)


def dedup_by_family(routes: Sequence[str]) -> list[str]:
    """Keep the first route per family (``effect:family``)."""
    seen: set[str] = set()
    kept: list[str] = []
    for route in routes:
        family = route.split(":")[-1]
        if family not in seen:
            seen.add(family)
            kept.append(route)
    return kept


def promote_to_regression(effect: str, *, fix_commit: str) -> FixCase:
    """Promote a confirmed bypass to a permanent pinned regression case (F61)."""
    return regression_case(f"bypass-{effect}", fix_commit=fix_commit)
