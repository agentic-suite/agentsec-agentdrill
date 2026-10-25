"""Dispute process (M19 19.7, CUJ-13).

A public dispute process with a **14-day** resolution SLA; confirm / correct
(flagged) / withdraw — all on the record. Design:
``docs/prd/23-oracle-credibility.md``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

#: The dispute resolution SLA in days.
DISPUTE_SLA_DAYS = 14

#: A dispute outcome.
DisputeOutcome = Literal["confirmed", "corrected", "withdrawn"]


class DisputeError(ValueError):
    """Raised when a dispute is resolved past SLA or with an unknown outcome."""


class Dispute(BaseModel):
    """A filed dispute against a result."""

    id: str
    case_id: str
    filed_at: str
    reason: str
    outcome: str = "open"
    resolution_note: str = ""
    resolved_at: str | None = None


def within_dispute_sla(days_elapsed: float) -> bool:
    """Whether a resolution landed within the 14-day SLA."""
    return days_elapsed <= DISPUTE_SLA_DAYS


def resolve_dispute(
    dispute: Dispute,
    *,
    outcome: str,
    note: str,
    resolved_at: str,
    days_elapsed: float = 0.0,
) -> Dispute:
    """Resolve a dispute on the record (confirm / correct / withdraw).

    Raises:
        DisputeError: The outcome is unknown or resolution breached the SLA.
    """
    if outcome not in ("confirmed", "corrected", "withdrawn"):
        raise DisputeError(
            f"dispute {dispute.id}: unknown outcome {outcome!r} (confirmed/corrected/withdrawn)"
        )
    if not within_dispute_sla(days_elapsed):
        raise DisputeError(
            f"dispute {dispute.id}: resolved after the {DISPUTE_SLA_DAYS}-day SLA "
            f"({days_elapsed} days)"
        )
    return dispute.model_copy(
        update={"outcome": outcome, "resolution_note": note, "resolved_at": resolved_at}
    )


def dispute_record(dispute: Dispute) -> dict[str, str]:
    """The public on-record entry for a dispute."""
    return {
        "id": dispute.id,
        "case_id": dispute.case_id,
        "outcome": dispute.outcome,
        "resolution_note": dispute.resolution_note,
        "resolved_at": dispute.resolved_at or "",
    }
