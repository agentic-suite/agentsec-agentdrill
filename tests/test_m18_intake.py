"""M18 18.1 — incident-intake pipeline, F60 (RED → GREEN).

Watchlist → triage SLA: a new incident must be assessed **≤7 days** — either a
pack draft or an explicit N/A with a reason. An N/A without a reason is rejected.
"""

from __future__ import annotations

import pytest

from agentdrill.lifecycle import (
    SLA_DAYS,
    Incident,
    IntakeError,
    TriageResult,
    assess,
    is_stale,
    require_within_sla,
)


def _incident() -> Incident:
    return Incident(
        id="incident-register#30",
        summary="MCP rug-pull via marketplace skill",
        source="vendor-advisory",
        first_seen="2026-10-01T00:00:00Z",
    )


def test_within_sla_is_met() -> None:
    result = assess(_incident(), decision="pack-draft", now="2026-10-06T00:00:00Z", days_elapsed=5)
    assert isinstance(result, TriageResult)
    assert result.within_sla is True
    assert result.decision == "pack-draft"
    assert SLA_DAYS == 7


def test_over_sla_is_flagged() -> None:
    result = assess(_incident(), decision="pack-draft", now="t", days_elapsed=8)
    assert result.within_sla is False
    with pytest.raises(IntakeError, match="SLA"):
        require_within_sla(result)


def test_na_requires_a_reason() -> None:
    with pytest.raises(IntakeError, match="reason"):
        assess(_incident(), decision="n/a", reason="", now="t", days_elapsed=2)


def test_na_with_a_reason_is_accepted() -> None:
    result = assess(
        _incident(),
        decision="n/a",
        reason="covered by incidents-security#slack-exfil-chain",
        now="t",
        days_elapsed=2,
    )
    assert result.decision == "n/a"
    assert result.reason


def test_stale_detection_for_packs() -> None:
    assert is_stale(_incident(), now="2026-11-01T00:00:00Z", max_age_days=30) is True
    assert is_stale(_incident(), now="2026-10-10T00:00:00Z", max_age_days=30) is False
