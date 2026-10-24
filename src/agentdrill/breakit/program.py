"""Break-It program (M29 29.2, F99).

A crowd program over **pinned reference ranges**: a structured proof-of-bypass is
**auto-verified by the M23 witness** (never by the reporter's word), triaged on an
SLA, disclosed under a fix window + embargo (CVE/CWE), and an accepted bypass is
**converted into a permanent regression** (F61, reusing M24/M18) and recorded in
the route-**family** catalogue. Accepted payloads stay private until fix + embargo;
published artifacts are family-level. Design:
``docs/design/detonation-breakit-frontier.md``; PRD 37 (R73).
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel

from agentdrill.attacker.minimize import dedup_by_family, promote_to_regression
from agentdrill.lifecycle import FixCase

#: The triage acknowledgement SLA, in hours.
ACK_SLA_HOURS = 24

#: The default minimum share of submissions auto-verified by the witness.
DEFAULT_MIN_AUTO_VERIFIED = 0.8

#: The coordinated-disclosure window bounds, in days.
MIN_FIX_WINDOW_DAYS = 30
MAX_FIX_WINDOW_DAYS = 90


class BreakItError(ValueError):
    """Raised when a submission fails triage, the SLA, or the disclosure policy."""


class ProofOfBypass(BaseModel):
    """A structured proof-of-bypass, auto-verified against the witness."""

    route: str
    effect_goal: str
    witness_effect: str | None = None
    verified: bool = False


class DisclosureTimeline(BaseModel):
    """The coordinated-disclosure timeline for an accepted bypass."""

    acknowledged: str
    fix_window_days: int
    embargo_days: int
    cve: str | None = None
    cwe: str | None = None
    credit: str = ""


class BypassSubmission(BaseModel):
    """One submitted bypass and its triage state."""

    id: str
    route: str
    effect_goal: str
    proof: ProofOfBypass | None = None
    severity_cvss: str | None = None
    severity_aivss: str | None = None
    timeline: DisclosureTimeline | None = None
    accepted: bool = False
    regression_case_id: str | None = None


def verify_proof(submission: BypassSubmission, *, witness_effect: str | None) -> BypassSubmission:
    """Auto-verify the proof against the witness's observed effect."""
    proof = ProofOfBypass(
        route=submission.route,
        effect_goal=submission.effect_goal,
        witness_effect=witness_effect,
        verified=witness_effect == submission.effect_goal,
    )
    return submission.model_copy(update={"proof": proof})


def require_triage_sla(ack_hours: float, *, sla_hours: float = ACK_SLA_HOURS) -> None:
    """Fail loudly unless the submission was acknowledged within the SLA.

    Raises:
        BreakItError: The acknowledgement took longer than the SLA.
    """
    if ack_hours > sla_hours:
        raise BreakItError(f"triage ack {ack_hours}h exceeds the {sla_hours}h SLA")


def require_disclosure_timeline(timeline: DisclosureTimeline) -> None:
    """Fail loudly unless the disclosure window obeys the policy.

    Raises:
        BreakItError: The fix window is out of bounds, or the embargo is shorter.
    """
    if not MIN_FIX_WINDOW_DAYS <= timeline.fix_window_days <= MAX_FIX_WINDOW_DAYS:
        raise BreakItError(
            f"fix window {timeline.fix_window_days}d must be "
            f"{MIN_FIX_WINDOW_DAYS}-{MAX_FIX_WINDOW_DAYS}d"
        )
    if timeline.embargo_days < timeline.fix_window_days:
        raise BreakItError(
            f"embargo {timeline.embargo_days}d is shorter than the fix window "
            f"{timeline.fix_window_days}d"
        )


def triage(
    submission: BypassSubmission,
    *,
    witness_effect: str | None,
    ack_hours: float,
    now: str,
    fix_window_days: int = 60,
    embargo_days: int = 90,
    sla_hours: float = ACK_SLA_HOURS,
) -> BypassSubmission:
    """Triage a submission: verify the proof, enforce the SLA, open a timeline.

    Raises:
        BreakItError: The acknowledgement missed the SLA.
    """
    require_triage_sla(ack_hours, sla_hours=sla_hours)
    verified = verify_proof(submission, witness_effect=witness_effect)
    if verified.proof is None or not verified.proof.verified:
        return verified.model_copy(update={"accepted": False, "timeline": None})
    timeline = DisclosureTimeline(
        acknowledged=now,
        fix_window_days=fix_window_days,
        embargo_days=embargo_days,
    )
    require_disclosure_timeline(timeline)
    return verified.model_copy(update={"accepted": True, "timeline": timeline})


def auto_verified_rate(submissions: Sequence[BypassSubmission]) -> float:
    """The share of submissions whose proof the witness auto-verified."""
    if not submissions:
        return 1.0
    verified = sum(
        1 for s in submissions if s.proof is not None and s.proof.verified
    )
    return verified / len(submissions)


def require_auto_verified(
    submissions: Sequence[BypassSubmission], *, minimum: float = DEFAULT_MIN_AUTO_VERIFIED
) -> None:
    """Fail loudly unless the auto-verified share is at least ``minimum``.

    Raises:
        BreakItError: The auto-verified rate is below the gate.
    """
    rate = auto_verified_rate(submissions)
    if rate < minimum:
        raise BreakItError(f"auto-verified rate {rate:.0%} is below the required {minimum:.0%}")


def family_catalogue(submissions: Sequence[BypassSubmission]) -> dict[str, int]:
    """Count submissions per route family (``effect:family``)."""
    catalogue: dict[str, int] = {}
    for submission in submissions:
        family = submission.route.split(":")[-1]
        catalogue[family] = catalogue.get(family, 0) + 1
    return catalogue


def dedup_families(submissions: Sequence[BypassSubmission]) -> list[str]:
    """One representative route per family (reusing M24's family dedup)."""
    return dedup_by_family([submission.route for submission in submissions])


def convert_to_regression(submission: BypassSubmission, *, fix_commit: str) -> FixCase:
    """Convert an accepted bypass into a permanent regression (F61).

    Raises:
        BreakItError: The submission was not accepted.
    """
    if not submission.accepted:
        raise BreakItError(f"submission {submission.id!r} is not accepted; nothing to convert")
    return promote_to_regression(submission.effect_goal, fix_commit=fix_commit)
