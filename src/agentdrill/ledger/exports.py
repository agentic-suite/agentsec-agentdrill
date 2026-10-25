"""Ledger exports (M28 28.3, F95).

Project the ledger into the official interchange formats by **reusing the M26
emitters** (single source of truth): OSCAL POA&M / assessment-results and SARIF
(with waivers → ``suppressions``), plus ticket-status updates. This is where the
M26 ``WaiverRecord`` seam is **re-pointed** at the ledger's waivers — the ledger
owns the waiver shape; the integration emitter consumes a projection of it.
Design: ``docs/design/exposure-attestation-roe.md``; PRD 33 (R69).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel

from agentdrill.integrations import (
    IntegrationFinding,
    WaiverRecord,
    apply_waivers,
    to_oscal_assessment_results,
    to_oscal_poam,
    to_sarif,
)
from agentdrill.ledger.finding import Finding
from agentdrill.ledger.ledger import Ledger
from agentdrill.ledger.waivers import Waiver, active_waivers

#: Statuses that mean the underlying issue is resolved for ticketing.
_RESOLVED_STATUSES = frozenset({"verified_fixed", "false_positive"})

#: The ticket state derived from a finding.
TicketState = Literal["open", "resolved", "suppressed"]


class TicketUpdate(BaseModel):
    """A ticket-status update derived from a finding's ledger state."""

    finding_id: str
    key: str
    state: TicketState


def _project(finding: Finding) -> IntegrationFinding:
    """Project a ledger finding into the neutral integration finding."""
    # The ledger outcome is validated when the finding is created from a result.
    outcome: Any = finding.outcome
    return IntegrationFinding(
        case_id=finding.case_id,
        outcome=outcome,
        pack=finding.pack,
        severity=finding.severity_level,
        rationale=finding.rationale or finding.title,
    )


def findings_from_ledger(
    ledger: Ledger, waivers: Sequence[Waiver] = (), *, now: str
) -> list[IntegrationFinding]:
    """Project the ledger into integration findings, marking active waivers."""
    projected: list[IntegrationFinding] = []
    records: list[WaiverRecord] = []
    for entry in ledger.all():
        projected.append(_project(entry.finding))
        for waiver in active_waivers(entry, waivers, now=now):
            records.append(WaiverRecord(case_id=entry.finding.case_id, reason=waiver.reason))
    return apply_waivers(projected, records)


def to_waiver_record(waiver: Waiver) -> WaiverRecord:
    """Project a ledger waiver into the M26 integration waiver record."""
    return WaiverRecord(case_id=waiver.case_id, reason=waiver.reason)


def export_sarif(
    ledger: Ledger, waivers: Sequence[Waiver] = (), *, now: str, **kwargs: Any
) -> dict[str, Any]:
    """Export the ledger as a validated SARIF 2.1.0 log."""
    return to_sarif(findings_from_ledger(ledger, waivers, now=now), **kwargs)


def _poam_findings(
    ledger: Ledger, waivers: Sequence[Waiver], *, now: str
) -> list[IntegrationFinding]:
    """Findings that belong on a POA&M: unresolved and not actively waived."""
    kept: list[IntegrationFinding] = []
    for entry in ledger.all():
        if entry.finding.status in _RESOLVED_STATUSES:
            continue
        if active_waivers(entry, waivers, now=now):
            continue
        kept.append(_project(entry.finding))
    return kept


def export_oscal_poam(
    ledger: Ledger, waivers: Sequence[Waiver] = (), *, title: str, now: str
) -> dict[str, Any]:
    """Export the ledger's open items as an OSCAL plan-of-action-and-milestones."""
    findings = _poam_findings(ledger, waivers, now=now)
    return to_oscal_poam(findings, title=title, last_modified=f"{now}T00:00:00Z")


def export_oscal_assessment_results(
    ledger: Ledger, waivers: Sequence[Waiver] = (), *, title: str, now: str
) -> dict[str, Any]:
    """Export the ledger as an OSCAL assessment-results document."""
    findings = findings_from_ledger(ledger, waivers, now=now)
    stamp = f"{now}T00:00:00Z"
    return to_oscal_assessment_results(findings, title=title, start=stamp, end=stamp)


def ticket_updates(
    ledger: Ledger, waivers: Sequence[Waiver] = (), *, now: str
) -> list[TicketUpdate]:
    """Derive a ticket state per finding (suppressed > resolved > open)."""
    updates: list[TicketUpdate] = []
    for entry in ledger.all():
        finding = entry.finding
        if active_waivers(entry, waivers, now=now):
            state: TicketState = "suppressed"
        elif finding.status in _RESOLVED_STATUSES:
            state = "resolved"
        else:
            state = "open"
        updates.append(
            TicketUpdate(
                finding_id=finding.id,
                key=f"{finding.pack}:{finding.case_id}",
                state=state,
            )
        )
    return updates
