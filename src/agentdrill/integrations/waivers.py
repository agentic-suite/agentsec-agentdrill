"""Waiver seam for SARIF suppressions (M26 26.1 → M28).

SARIF ``suppressions`` map to the exposure-ledger **waivers** (PRD 33), whose
SSOT — expiry, compensating control, auto-reopen — is owned by **M28**. Until
M28 lands, this module defines the minimal read-only record the emitters need
and marks findings, so 26.1 can be built and validated without a parallel
waiver registry. M28 re-points :func:`apply_waivers` at its ledger; the record
shape below is the compatibility seam, not a second implementation.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from pydantic import BaseModel

from agentdrill.integrations.model import IntegrationFinding


class WaiverRecord(BaseModel):
    """A read-only waiver projection: the case it covers and its justification.

    Attributes:
        case_id: The case the waiver covers.
        reason: The justification recorded on the emitted suppression.
    """

    case_id: str
    reason: str


def apply_waivers(
    findings: Iterable[IntegrationFinding],
    waivers: Sequence[WaiverRecord],
) -> list[IntegrationFinding]:
    """Return ``findings`` with active waivers marked (never relabelled).

    A waived finding keeps its true outcome and gains ``waived`` + a
    justification — a waiver suppresses a *gate*, it never turns a miss into a
    block (DD: waivers never relabel).
    """
    by_case = {waiver.case_id: waiver for waiver in waivers}
    marked: list[IntegrationFinding] = []
    for finding in findings:
        waiver = by_case.get(finding.case_id)
        if waiver is None:
            marked.append(finding)
        else:
            marked.append(
                finding.model_copy(update={"waived": True, "waiver_reason": waiver.reason})
            )
    return marked
