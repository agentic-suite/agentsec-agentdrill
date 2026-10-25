"""Severity rubric (M10 10.5, F41).

A finding is scored by **attack-class x exposure** with a rationale, so
findings are comparable and sortable across packs.
Design: ``docs/design/reporting.md``; PRD 12 R25.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel

#: Severity levels, most severe first.
Severity = Literal["critical", "high", "medium", "low"]

#: Attack-class weights (contribution to the severity score).
_CLASS_WEIGHT: dict[str, int] = {
    "injection": 1,
    "exfiltration": 2,
    "destructive": 3,
    "privilege_escalation": 4,
}

#: Exposure weights (contribution to the severity score).
_EXPOSURE_WEIGHT: dict[str, int] = {
    "external": 0,
    "partner": 1,
    "internal": 2,
    "privileged": 3,
}

#: Sort rank per severity (lower = more severe).
_SEVERITY_RANK: dict[str, int] = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class RatedFinding(BaseModel):
    """A finding with an attack-class x exposure severity and rationale."""

    case_id: str
    attack_class: str
    exposure: str
    severity: Severity
    rationale: str
    pack: str | None = None


def _level(score: int) -> Severity:
    """Map a severity score to a level."""
    if score >= 6:
        return "critical"
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def rate_finding(
    case_id: str,
    *,
    attack_class: str,
    exposure: str,
    pack: str | None = None,
) -> RatedFinding:
    """Score a finding by attack-class x exposure.

    Raises:
        ValueError: ``attack_class`` or ``exposure`` is not in the rubric.
    """
    if attack_class not in _CLASS_WEIGHT:
        raise ValueError(f"unknown attack_class: {attack_class!r}; known: {sorted(_CLASS_WEIGHT)}")
    if exposure not in _EXPOSURE_WEIGHT:
        raise ValueError(f"unknown exposure: {exposure!r}; known: {sorted(_EXPOSURE_WEIGHT)}")
    score = _CLASS_WEIGHT[attack_class] + _EXPOSURE_WEIGHT[exposure]
    severity = _level(score)
    rationale = f"{attack_class} attack at {exposure} exposure ⇒ {severity} (score {score})"
    return RatedFinding(
        case_id=case_id,
        attack_class=attack_class,
        exposure=exposure,
        severity=severity,
        rationale=rationale,
        pack=pack,
    )


def sort_findings(findings: Iterable[RatedFinding]) -> list[RatedFinding]:
    """Sort findings by severity (most severe first), then pack, then case id."""
    return sorted(
        findings,
        key=lambda f: (_SEVERITY_RANK.get(f.severity, 9), f.pack or "", f.case_id),
    )
