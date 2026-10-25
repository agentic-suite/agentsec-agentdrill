"""Incident-intake pipeline (M18 18.1, F60).

Watchlist → triage SLA: a new incident is assessed **≤7 days** — either a pack
draft or an explicit **N/A with a reason**. A stale pack is deprecation
candidate. Design: ``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel

#: The intake SLA in days.
SLA_DAYS = 7

#: A triage decision.
Decision = Literal["pack-draft", "n/a"]


class IntakeError(ValueError):
    """Raised when an incident breaches the intake SLA or is mis-triaged."""


class Incident(BaseModel):
    """A watchlist incident awaiting triage."""

    id: str
    summary: str
    source: str = ""
    first_seen: str


class TriageResult(BaseModel):
    """The triage assessment for one incident."""

    incident_id: str
    decision: Decision
    reason: str = ""
    assessed_at: str
    days_elapsed: float
    within_sla: bool


def _parse(timestamp: str) -> datetime:
    """Parse an ISO-8601 timestamp (accepting a trailing ``Z``)."""
    normalized = timestamp.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def assess(
    incident: Incident,
    *,
    decision: Decision,
    now: str,
    days_elapsed: float,
    reason: str = "",
) -> TriageResult:
    """Assess an incident: a pack draft, or an N/A with a reason.

    Raises:
        IntakeError: An N/A decision lacks a reason.
    """
    if decision == "n/a" and not reason:
        raise IntakeError(f"incident {incident.id}: an N/A decision requires a reason")
    return TriageResult(
        incident_id=incident.id,
        decision=decision,
        reason=reason,
        assessed_at=now,
        days_elapsed=days_elapsed,
        within_sla=days_elapsed <= SLA_DAYS,
    )


def require_within_sla(result: TriageResult) -> None:
    """Fail loudly if an incident breached the intake SLA.

    Raises:
        IntakeError: The incident was assessed later than the SLA.
    """
    if not result.within_sla:
        raise IntakeError(
            f"incident {result.incident_id}: assessed after the {SLA_DAYS}-day SLA "
            f"({result.days_elapsed} days)"
        )


def is_stale(incident: Incident, *, now: str, max_age_days: int) -> bool:
    """Whether an incident (or the pack it produced) is older than ``max_age_days``."""
    age = (_parse(now) - _parse(incident.first_seen)).days
    return age > max_age_days
