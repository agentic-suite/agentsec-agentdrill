"""Exposure ledger: finding lifecycle + models (M28 28.1, F95).

A finding's honest ``outcome`` is **immutable** — a miss stays a miss through
every lifecycle transition; only its ``status`` moves. The lifecycle is
``open → triaged → fix_in_progress → fixed → verified_fixed → decayed`` with the
side states ``accepted_risk`` / ``false_positive`` / ``wont_fix``; ``fixed →
verified_fixed`` requires verification (verified, not believed). Severity is a
**per-finding** CVSS v4.0 + AIVSS vector, **never aggregated** — a composite score
is refused. Design: ``docs/design/exposure-attestation-roe.md``; PRD 33 (R69).
"""

from __future__ import annotations

from typing import Literal, NoReturn

from pydantic import BaseModel, Field

#: A finding's lifecycle status.
FindingStatus = Literal[
    "open",
    "triaged",
    "fix_in_progress",
    "fixed",
    "verified_fixed",
    "decayed",
    "accepted_risk",
    "false_positive",
    "wont_fix",
]

#: The primary forward flow.
PRIMARY_FLOW: tuple[FindingStatus, ...] = (
    "open",
    "triaged",
    "fix_in_progress",
    "fixed",
    "verified_fixed",
    "decayed",
)

#: The terminal side states.
SIDE_STATES: tuple[FindingStatus, ...] = ("accepted_risk", "false_positive", "wont_fix")

#: The allowed transitions.
_ALLOWED: dict[str, set[str]] = {
    "open": {"triaged", "accepted_risk", "false_positive", "wont_fix"},
    "triaged": {"fix_in_progress", "accepted_risk", "false_positive", "wont_fix"},
    "fix_in_progress": {"fixed", "accepted_risk", "wont_fix"},
    "fixed": {"verified_fixed", "fix_in_progress", "decayed"},
    "verified_fixed": {"decayed", "open"},
    "decayed": {"open"},
    "accepted_risk": {"open"},
    "false_positive": {"open"},
    "wont_fix": {"open"},
}


class LedgerError(ValueError):
    """Raised for an illegal lifecycle transition or a refused aggregation."""


class SeverityVector(BaseModel):
    """A per-finding CVSS v4.0 + AIVSS vector (never aggregated)."""

    cvss: str | None = None
    aivss: str | None = None


class Finding(BaseModel):
    """A finding in the exposure ledger.

    ``outcome`` is the honest result (blocked/missed/degraded/untested) and is
    never rewritten; ``status`` is the lifecycle position.
    """

    id: str
    case_id: str
    pack: str | None = None
    outcome: str
    dimension: str = "enforcement"
    title: str = ""
    severity: SeverityVector = Field(default_factory=SeverityVector)
    #: The rated severity level (M10 rubric), used for waiver expiry defaults.
    severity_level: str | None = None
    status: FindingStatus = "open"
    waivers: list[str] = Field(default_factory=list)
    rationale: str = ""


class Transition(BaseModel):
    """One lifecycle transition, recorded for the audit trail."""

    from_status: str
    to_status: str
    actor: str
    reason: str = ""


class LedgerEntry(BaseModel):
    """A finding plus its transition history."""

    finding: Finding
    history: list[Transition] = Field(default_factory=list)


def is_integrity(finding: Finding) -> bool:
    """Whether a finding is an integrity finding (not waivable; see 28.2)."""
    return finding.dimension == "integrity"


def open_finding(finding: Finding) -> LedgerEntry:
    """Open a finding at status ``open``."""
    opened = finding.model_copy(update={"status": "open"})
    return LedgerEntry(
        finding=opened,
        history=[Transition(from_status="open", to_status="open", actor="system", reason="opened")],
    )


def transition(
    entry: LedgerEntry,
    to_status: str,
    *,
    actor: str,
    reason: str = "",
    fix_verified: bool = False,
) -> LedgerEntry:
    """Move a finding to ``to_status``, validating the transition.

    Raises:
        LedgerError: The transition is not allowed, or ``verified_fixed`` is
            requested without verification.
    """
    current = entry.finding.status
    if to_status not in _ALLOWED:
        raise LedgerError(f"unknown status: {to_status!r}")
    if to_status not in _ALLOWED[current]:
        raise LedgerError(f"illegal transition: {current} → {to_status}")
    if to_status == "verified_fixed" and not fix_verified:
        raise LedgerError("verified_fixed requires a verification (verified, not believed)")
    moved = entry.finding.model_copy(update={"status": to_status})
    record = Transition(from_status=current, to_status=to_status, actor=actor, reason=reason)
    return LedgerEntry(finding=moved, history=[*entry.history, record])


def composite_score(*_args: object, **_kwargs: object) -> NoReturn:
    """Refuse to aggregate findings into a composite score.

    Raises:
        LedgerError: Always — severity is per-finding by design (never aggregated).
    """
    raise LedgerError(
        "the exposure ledger never aggregates findings into a composite score; "
        "read per-finding CVSS v4.0 / AIVSS vectors"
    )
