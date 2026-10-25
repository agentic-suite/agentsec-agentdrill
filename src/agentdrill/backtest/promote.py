"""Trace → drill promotion (M27 27.3, F92).

Promote a redacted production session into a **draft** attack case tagged
``origin:production-trace`` (PRD 30), with a mined benign twin. Promotion
**redacts with receipts** (F65) and refuses to emit a case that still contains a
known secret class. The draft is HITL-gated: it cannot ship until a reviewer
(other than the drafter) approves it. Design:
``docs/design/backtest-path-intake.md``; PRD 30 (R66).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.backtest.replay import RecordedSession
from agentdrill.lifecycle.privacy import Receipt, redact, verify_receipts
from agentdrill.models.attack_pack import AttackCase

#: The tag marking a case promoted from a production trace.
PRODUCTION_ORIGIN = "origin:production-trace"

#: The default target a promoted case exercises.
DEFAULT_PROMOTED_TARGET = "policyweave-output"


class PromoteError(ValueError):
    """Raised when a session cannot be promoted, or a draft ships unreviewed."""


class PromotedCase(BaseModel):
    """A draft case promoted from a production trace, with its redaction receipts."""

    case: AttackCase
    receipts: list[Receipt] = Field(default_factory=list)
    twin_id: str | None = None
    approved: bool = False
    reviewer: str | None = None
    drafter: str = "agentdrill"


def _redact(value: str, *, location: str, receipts: list[Receipt]) -> str:
    """Redact ``value`` (collecting its receipts) and return the redacted text."""
    result = redact(value, location=location)
    receipts.extend(result.receipts)
    return result.redacted


def promote_session(
    session: RecordedSession,
    *,
    case_id: str,
    target: str = DEFAULT_PROMOTED_TARGET,
    twin_id: str | None = None,
) -> PromotedCase:
    """Promote a redacted session into a draft attack case.

    Raises:
        PromoteError: The session is not redacted, or the promoted case still
            contains a known secret class (zero unredacted secrets).
    """
    if not session.redacted:
        raise PromoteError(
            f"session {session.session_id!r} must be redacted before promotion"
        )

    receipts: list[Receipt] = []
    steps = []
    for index, event in enumerate(session.events):
        reference = _redact(
            event.ref or event.event,
            location=f"session:{session.session_id}/event:{index}/ref",
            receipts=receipts,
        )
        steps.append({"tool": reference, "args": {}})
    if not steps:  # a promoted case must attempt at least one action
        steps.append({"tool": "promoted-action", "args": {}})

    case = AttackCase.model_validate(
        {
            "id": case_id,
            "title": _redact(
                f"Promoted from production trace {session.session_id}",
                location=f"session:{session.session_id}/title",
                receipts=receipts,
            ),
            "goal": "Verify the deployed stack stops a reproduced production action",
            "incident_ref": f"trace:{session.session_id}",
            "target": {"type": target},
            "driver": {"type": "subprocess"},
            "attack": {"steps": steps},
            "oracle": {"expect": "blocked"},
            "benign_twin": twin_id,
            "tags": [PRODUCTION_ORIGIN],
        }
    )

    if not verify_receipts(case.model_dump_json(), receipts):
        raise PromoteError(
            f"promoted case {case_id!r} still contains a known secret class "
            f"(zero unredacted secrets required)"
        )
    return PromotedCase(case=case, receipts=receipts, twin_id=twin_id)


def approve_promoted(
    promoted: PromotedCase, *, reviewer: str, drafter: str = "agentdrill"
) -> PromotedCase:
    """Approve a promoted draft (HITL).

    Raises:
        PromoteError: The reviewer is the drafter (independent review required).
    """
    if reviewer == drafter:
        raise PromoteError("HITL review requires a reviewer independent of the drafter")
    return promoted.model_copy(update={"approved": True, "reviewer": reviewer})


def require_approved(promoted: PromotedCase) -> None:
    """Fail loudly unless the promoted case was approved by a reviewer.

    Raises:
        PromoteError: The case is still a draft.
    """
    if not promoted.approved:
        raise PromoteError(
            f"promoted case {promoted.case.id!r} is a draft; "
            "HITL review is required before it ships"
        )
