"""Compliance-mapped reporting (M17 17.4, F24).

Findings mapped to **EU AI Act Art. 12**, **NIST AI RMF** and **ISO 42001**,
with an offline evidence export for agentcomply. Design:
``docs/prd/03-landscape.md``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

#: The compliance frameworks a finding maps to.
FRAMEWORKS: tuple[str, ...] = ("eu_ai_act_art12", "nist_ai_rmf", "iso_42001")


class ComplianceError(ValueError):
    """Raised when a finding type has no compliance mapping."""


@dataclass(frozen=True)
class ComplianceMapping:
    """A finding type's control ids per framework."""

    finding_type: str
    frameworks: dict[str, str]


#: Static finding-type → framework control mapping.
_MAPPING: dict[str, dict[str, str]] = {
    "safety_miss": {
        "eu_ai_act_art12": "Art.12(1) logging",
        "nist_ai_rmf": "MEASURE 2.6",
        "iso_42001": "A.6.2.6",
    },
    "policy_miss": {
        "eu_ai_act_art12": "Art.12(2) traceability",
        "nist_ai_rmf": "MEASURE 2.7",
        "iso_42001": "A.6.2.7",
    },
    "kill_slow": {
        "eu_ai_act_art12": "Art.12(3) monitoring",
        "nist_ai_rmf": "MANAGE 2.2",
        "iso_42001": "A.6.2.8",
    },
    "cease_gap": {
        "eu_ai_act_art12": "Art.12(3) monitoring",
        "nist_ai_rmf": "MANAGE 4.1",
        "iso_42001": "A.8.4",
    },
    "utility_cost": {
        "eu_ai_act_art12": "Art.12(1) logging",
        "nist_ai_rmf": "MEASURE 2.11",
        "iso_42001": "A.5.4",
    },
    "dirty_target": {
        "eu_ai_act_art12": "Art.12(2) traceability",
        "nist_ai_rmf": "MANAGE 2.4",
        "iso_42001": "A.8.2",
    },
    "evidence_gap": {
        "eu_ai_act_art12": "Art.12(1) logging",
        "nist_ai_rmf": "MEASURE 2.8",
        "iso_42001": "A.6.2.6",
    },
    "telemetry_gap": {
        "eu_ai_act_art12": "Art.12(1) logging",
        "nist_ai_rmf": "MEASURE 2.8",
        "iso_42001": "A.6.2.6",
    },
}


class ComplianceRow(BaseModel):
    """One finding's compliance mapping."""

    case_id: str
    finding_type: str
    frameworks: dict[str, str] = Field(default_factory=dict)


class ComplianceReport(BaseModel):
    """A compliance-mapped report for a run's findings."""

    title: str = "Compliance mapping"
    generated: str
    rows: list[ComplianceRow] = Field(default_factory=list)


def map_finding(finding_type: str) -> ComplianceMapping:
    """Map a finding type to control ids across the frameworks.

    Raises:
        ComplianceError: The finding type has no mapping.
    """
    mapping = _MAPPING.get(finding_type)
    if mapping is None:
        raise ComplianceError(f"unknown finding type: {finding_type!r}; known: {sorted(_MAPPING)}")
    return ComplianceMapping(finding_type=finding_type, frameworks=dict(mapping))


def build_compliance_report(
    findings: Iterable[tuple[str, str]], *, generated: str
) -> ComplianceReport:
    """Build a compliance report from ``(case_id, finding_type)`` pairs."""
    rows = [
        ComplianceRow(
            case_id=case_id,
            finding_type=finding_type,
            frameworks=map_finding(finding_type).frameworks,
        )
        for case_id, finding_type in findings
    ]
    return ComplianceReport(generated=generated, rows=rows)


def export_agentcomply(report: ComplianceReport, dest: str | Path) -> Path:
    """Write the compliance report as an offline artifact for agentcomply."""
    directory = Path(dest)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "compliance-report.json"
    path.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path
