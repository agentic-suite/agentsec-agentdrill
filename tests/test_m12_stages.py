"""M12 12.1 — kill-chain stage model + timestamps (RED → GREEN).

The shared stage model: attack_start → delivered → detected → decided → halted
→ revoked → ceased. Each case records per-stage timestamps; a missing stage is
null **+ flagged**, never inferred.
"""

from __future__ import annotations

import pytest

from agentdrill.killchain import KILL_CHAIN_STAGES, KillChainTimeline, build_timeline


def test_stage_model_is_the_documented_chain() -> None:
    assert KILL_CHAIN_STAGES == (
        "attack_start",
        "delivered",
        "detected",
        "decided",
        "halted",
        "revoked",
        "ceased",
    )


def test_timeline_reconstructs_every_stage() -> None:
    timeline = build_timeline(
        "c1",
        {
            "attack_start": 0.0,
            "delivered": 0.1,
            "detected": 0.4,
            "decided": 0.5,
            "halted": 0.6,
            "revoked": 0.8,
            "ceased": 1.2,
        },
    )
    assert isinstance(timeline, KillChainTimeline)
    assert timeline.case_id == "c1"
    assert timeline.stages["ceased"] == 1.2
    assert timeline.missing == []


def test_a_missing_stage_is_null_and_flagged() -> None:
    timeline = build_timeline(
        "c1", {"attack_start": 0.0, "delivered": 0.1, "detected": 0.4, "decided": 0.5}
    )
    assert timeline.stages["halted"] is None
    assert "halted" in timeline.missing
    assert "revoked" in timeline.missing
    assert "ceased" in timeline.missing
    assert timeline.flagged is True


def test_stages_are_ordered_as_in_the_model() -> None:
    timeline = build_timeline("c1", {"detected": 0.4, "attack_start": 0.0})
    assert list(timeline.stages) == list(KILL_CHAIN_STAGES)


def test_an_unknown_stage_fails_loudly() -> None:
    with pytest.raises(ValueError, match="unknown stage"):
        build_timeline("c1", {"attack_start": 0.0, "teleported": 0.4})


def test_timeline_round_trips_through_json() -> None:
    timeline = build_timeline("c1", {"attack_start": 0.0, "delivered": 0.1})
    again = KillChainTimeline.model_validate_json(timeline.model_dump_json())
    assert again == timeline
