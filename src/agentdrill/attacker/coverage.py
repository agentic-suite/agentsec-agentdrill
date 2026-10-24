"""Search coverage report (M24 24.8, F89).

Per-effect tried / blocked / bypassed / untried coverage, plus a diff-aware
subset for rule changes. Coverage is explicit — the rest is ``untried``.
Design: ``docs/prd/28-policy-bypass-search.md``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field


class EffectCoverage(BaseModel):
    """One effect's search coverage."""

    effect: str
    tried: int = 0
    blocked: int = 0
    bypassed: int = 0
    untried: int = 0


class CoverageReport(BaseModel):
    """The per-effect search coverage report."""

    effects: list[EffectCoverage] = Field(default_factory=list)

    def for_effect(self, effect: str) -> EffectCoverage | None:
        """The coverage row for ``effect`` (or ``None``)."""
        return next((row for row in self.effects if row.effect == effect), None)


def build_coverage(effects: Sequence[str], *, statuses: Mapping[str, str]) -> CoverageReport:
    """Build the coverage report; effects without a status are ``untried``."""
    rows: list[EffectCoverage] = []
    for effect in effects:
        status = statuses.get(effect)
        rows.append(
            EffectCoverage(
                effect=effect,
                tried=1 if status else 0,
                blocked=1 if status == "blocked" else 0,
                bypassed=1 if status == "bypassed" else 0,
                untried=0 if status else 1,
            )
        )
    return CoverageReport(effects=rows)


def diff_aware(report: CoverageReport, *, changed_effects: Sequence[str]) -> list[str]:
    """The subset of ``report``'s effects affected by a rule change."""
    present = {row.effect for row in report.effects}
    return [effect for effect in changed_effects if effect in present]
