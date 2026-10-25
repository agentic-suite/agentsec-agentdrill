"""M27 27.3 — trace→drill (RED → GREEN).

Promote a redacted production session into a draft attack case tagged
``origin:production-trace`` with a mined benign twin, proving **zero unredacted
secrets** (F65 receipts) and gating the draft behind HITL review (reviewer ≠
drafter).
"""

from __future__ import annotations

import pytest

from agentdrill.backtest import (
    PRODUCTION_ORIGIN,
    PromotedCase,
    PromoteError,
    RecordedSession,
    approve_promoted,
    promote_session,
    require_approved,
)
from agentdrill.evidence import AgentWatchEvent


def _session() -> RecordedSession:
    return RecordedSession(
        session_id="s-prod-1",
        redacted=True,
        events=[
            AgentWatchEvent(
                event="denied",
                ref="mcp__filesystem__write?token=ghp_abcdefghijklmnop",
                detail="blocked a write using key sk-abcdefghij",
            )
        ],
    )


def test_promote_builds_a_redacted_production_case() -> None:
    promoted = promote_session(_session(), case_id="trace-destructive-write", twin_id="twin-1")
    assert isinstance(promoted, PromotedCase)
    case = promoted.case
    assert PRODUCTION_ORIGIN in case.tags
    assert "origin:production-trace" in case.tags
    assert case.benign_twin == "twin-1"
    assert case.incident_ref == "trace:s-prod-1"
    serialized = case.model_dump_json()
    assert "ghp_" not in serialized
    assert "sk-abcdefghij" not in serialized
    assert any(receipt.klass in ("token", "secret") for receipt in promoted.receipts)
    assert promoted.approved is False


def test_unredacted_session_is_refused() -> None:
    session = RecordedSession(session_id="s", redacted=False)
    with pytest.raises(PromoteError):
        promote_session(session, case_id="c")


def test_empty_session_still_yields_a_case_with_one_step() -> None:
    promoted = promote_session(RecordedSession(session_id="s-empty"), case_id="c-empty")
    assert len(promoted.case.attack.steps) == 1


def test_a_leaked_secret_anywhere_in_the_case_fails_the_gate() -> None:
    with pytest.raises(PromoteError):
        promote_session(_session(), case_id="sk-abcdefghij")  # the id itself carries a secret


def test_hitl_review_gate() -> None:
    promoted = promote_session(_session(), case_id="c1")
    with pytest.raises(PromoteError):
        require_approved(promoted)  # a draft cannot ship unreviewed
    with pytest.raises(PromoteError):
        approve_promoted(promoted, reviewer="agentdrill", drafter="agentdrill")
    approved = approve_promoted(promoted, reviewer="alice@example.com")
    assert approved.approved is True
    require_approved(approved)
