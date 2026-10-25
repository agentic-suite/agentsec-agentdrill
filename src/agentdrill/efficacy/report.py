"""Efficacy report artifact (M13 13.5).

Efficacy status (verified / inert) is shipped **per case** in the evidence
bundle (CUJ-11), so efficacy is visible per case. Design:
``docs/design/efficacy.md``.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, Field

from agentdrill.efficacy.control import EfficacyResult
from agentdrill.efficacy.inert import INERT_FLAG
from agentdrill.models.evidence import Evidence


class CaseEfficacy(BaseModel):
    """One case's efficacy status."""

    case_id: str
    efficacy_verified: bool
    inert: bool
    guarded_outcome: str | None = None
    flag: str | None = None


class EfficacyReport(BaseModel):
    """Per-case efficacy status for a run."""

    cases: list[CaseEfficacy] = Field(default_factory=list)

    def for_case(self, case_id: str) -> CaseEfficacy | None:
        """The efficacy entry for ``case_id``, or ``None`` when absent."""
        return next((case for case in self.cases if case.case_id == case_id), None)


def build_efficacy_report(results: Iterable[EfficacyResult]) -> EfficacyReport:
    """Build the per-case efficacy report from control results."""
    cases = [
        CaseEfficacy(
            case_id=result.case_id,
            efficacy_verified=result.efficacy_verified,
            inert=result.inert,
            guarded_outcome=result.guarded_outcome,
            flag=INERT_FLAG if result.inert else None,
        )
        for result in results
    ]
    return EfficacyReport(cases=cases)


def efficacy_evidence(result: EfficacyResult) -> Evidence:
    """An evidence event recording one case's efficacy status."""
    status = INERT_FLAG if result.inert else "efficacy-verified"
    return Evidence(
        event="efficacy",
        summary=f"{result.case_id}: {status} (guarded {result.guarded_outcome or 'n/a'})",
        ref=result.case_id,
    )
