"""M19 19.7 — dispute process, CUJ-13 (RED → GREEN).

A public dispute process with a 14-day resolution SLA; confirm / correct
(flagged) / withdraw — all on the record.
"""

from __future__ import annotations

import pytest

from agentdrill.credibility import (
    DISPUTE_SLA_DAYS,
    Dispute,
    DisputeError,
    dispute_record,
    resolve_dispute,
    within_dispute_sla,
)


def _dispute() -> Dispute:
    return Dispute(
        id="d1", case_id="c1", filed_at="2026-10-01T00:00:00Z", reason="oracle misjudged"
    )


def test_dispute_resolves_with_an_on_record_outcome() -> None:
    resolved = resolve_dispute(
        _dispute(), outcome="confirmed", note="oracle was right", resolved_at="2026-10-05T00:00:00Z"
    )
    assert resolved.outcome == "confirmed"
    assert resolved.resolution_note == "oracle was right"
    record = dispute_record(resolved)
    assert record["outcome"] == "confirmed"
    assert DISPUTE_SLA_DAYS == 14


def test_resolution_within_14_days() -> None:
    assert within_dispute_sla(10) is True
    assert within_dispute_sla(20) is False
    with pytest.raises(DisputeError, match="SLA"):
        resolve_dispute(
            _dispute(),
            outcome="corrected",
            note="re-scored",
            resolved_at="t",
            days_elapsed=20,
        )


def test_unknown_outcome_is_rejected() -> None:
    with pytest.raises(DisputeError, match="outcome"):
        resolve_dispute(_dispute(), outcome="ignored", note="", resolved_at="t")
