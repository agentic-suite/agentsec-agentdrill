"""Time-boxed waivers (M28 28.2, F95).

A waiver is a **time-boxed, signed, drilled** exception. It **annotates, never
relabels**: the finding keeps its honest outcome and gains ``waived:<id>``; gate
impact may drop, **visibility never**. A waiver **auto-reopens** on expiry (or a
drift trigger), the release is gated by a **known-miss budget**, and **integrity
findings are not waivable**. Design: ``docs/design/exposure-attestation-roe.md``;
PRD 33 (R69).
"""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Sequence
from datetime import date, timedelta

from pydantic import BaseModel, Field

from agentdrill.ledger.finding import Finding, LedgerEntry, is_integrity
from agentdrill.ledger.ledger import Ledger

#: The default waiver lifetime, in days.
DEFAULT_WAIVER_DAYS = 90

#: The waiver lifetime for a critical finding, in days.
CRITICAL_WAIVER_DAYS = 30

#: The annotation prefix a waiver adds to a finding (never a relabel).
WAIVED_PREFIX = "waived:"


class WaiverError(ValueError):
    """Raised when a waiver is invalid, not permitted, or over budget."""


class Waiver(BaseModel):
    """A time-boxed waiver (signed; annotate, never relabel)."""

    id: str
    finding_id: str
    reason: str
    compensating_control: str
    approvers: list[str] = Field(default_factory=list)
    expires: str
    scope: str = "case"
    tier: str | None = None
    drift_trigger: str | None = None
    residual_risk: str = ""
    signature: str = ""


def require_waivable(finding: Finding) -> None:
    """Fail loudly if a finding may not be waived.

    Raises:
        WaiverError: The finding is an integrity finding (not waivable).
    """
    if is_integrity(finding):
        raise WaiverError(
            f"finding {finding.id!r} is an integrity finding and cannot be waived"
        )


def create_waiver(
    finding: Finding,
    *,
    waiver_id: str,
    reason: str,
    compensating_control: str,
    approvers: Sequence[str],
    now: str,
    critical: bool = False,
    scope: str = "case",
    tier: str | None = None,
    drift_trigger: str | None = None,
    residual_risk: str = "",
) -> Waiver:
    """Create a time-boxed waiver (90 d; 30 d when critical).

    Raises:
        WaiverError: The finding is not waivable.
    """
    require_waivable(finding)
    days = CRITICAL_WAIVER_DAYS if critical else DEFAULT_WAIVER_DAYS
    expires = (date.fromisoformat(now) + timedelta(days=days)).isoformat()
    return Waiver(
        id=waiver_id,
        finding_id=finding.id,
        reason=reason,
        compensating_control=compensating_control,
        approvers=list(approvers),
        expires=expires,
        scope=scope,
        tier=tier,
        drift_trigger=drift_trigger,
        residual_risk=residual_risk,
    )


def is_active(waiver: Waiver, *, now: str) -> bool:
    """Whether ``waiver`` is still within its time box at ``now``."""
    return date.fromisoformat(now) <= date.fromisoformat(waiver.expires)


def _matches(waiver: Waiver, finding: Finding) -> bool:
    """Whether ``waiver`` scopes to ``finding`` (case/pack/class)."""
    if waiver.scope == "pack":
        return waiver.finding_id == finding.pack
    if waiver.scope == "class":
        return waiver.finding_id == finding.dimension
    return waiver.finding_id == finding.id


def active_waivers(
    entry: LedgerEntry, waivers: Sequence[Waiver], *, now: str
) -> list[Waiver]:
    """The waivers that apply to ``entry`` and are still active at ``now``."""
    return [
        waiver
        for waiver in waivers
        if _matches(waiver, entry.finding) and is_active(waiver, now=now)
    ]


def sync_waivers(ledger: Ledger, waivers: Sequence[Waiver], *, now: str) -> Ledger:
    """Annotate findings with their active waivers; auto-reopen expired ones.

    A finding keeps its honest outcome; an active waiver adds ``waived:<id>``. A
    finding whose waiver has expired (and whose status was a side state) is
    reopened.
    """
    synced: dict[str, LedgerEntry] = {}
    for entry in ledger.all():
        active = active_waivers(entry, waivers, now=now)
        annotations = [f"{WAIVED_PREFIX}{waiver.id}" for waiver in active]
        status = entry.finding.status
        if not active and entry.finding.waivers and status == "accepted_risk":
            status = "open"
        updated = entry.finding.model_copy(update={"waivers": annotations, "status": status})
        synced[updated.id] = entry.model_copy(update={"finding": updated})
    return Ledger(entries=synced)


def require_known_miss_budget(ledger: Ledger, *, budget: int) -> None:
    """Fail loudly unless unwaived misses are within ``budget``.

    Raises:
        WaiverError: The number of unwaived misses exceeds ``budget``.
    """
    unwaived = [
        entry
        for entry in ledger.all()
        if entry.finding.outcome == "missed" and not entry.finding.waivers
    ]
    if len(unwaived) > budget:
        ids = [entry.finding.id for entry in unwaived]
        raise WaiverError(
            f"{len(unwaived)} unwaived miss(es) exceed the known-miss budget {budget}: {ids}"
        )


def _canonical(waiver: Waiver) -> str:
    """The canonical signing payload (everything but the signature)."""
    payload = waiver.model_dump(exclude={"signature"})
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def sign_waiver(waiver: Waiver, *, secret: str) -> Waiver:
    """Return a copy of ``waiver`` carrying an HMAC-SHA256 signature."""
    digest = hmac.new(secret.encode("utf-8"), _canonical(waiver).encode("utf-8"), hashlib.sha256)
    return waiver.model_copy(update={"signature": f"sha256={digest.hexdigest()}"})


def verify_waiver(waiver: Waiver, *, secret: str) -> bool:
    """Whether ``waiver`` carries a valid signature for ``secret``."""
    if not waiver.signature:
        return False
    expected = sign_waiver(waiver, secret=secret).signature
    return hmac.compare_digest(waiver.signature, expected)
