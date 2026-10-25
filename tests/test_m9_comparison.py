"""M9 9.2 — comparison engine (RED → GREEN).

Per-case, per-tag and aggregate deltas between a candidate run and its golden.
Direction ranks `blocked` > `degraded` > `missed`, so a `blocked → missed` flip
is a regression.
"""

from __future__ import annotations

from typing import Any

from agentdrill.comparison import AttackComparison, AttackComparisonEngine, Golden
from agentdrill.models.attack_pack import AttackPack


def _case(case_id: str, tags: list[str]) -> dict[str, Any]:
    return {
        "id": case_id,
        "title": "t",
        "goal": "g",
        "incident_ref": "incident-register#1",
        "target": {"type": "policyweave-output"},
        "driver": {"type": "subprocess"},
        "attack": {"steps": [{"tool": "shell"}]},
        "oracle": {"expect": "blocked"},
        "tags": tags,
    }


def _pack() -> AttackPack:
    return AttackPack.model_validate(
        {
            "pack": {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
                "hash": "deadbeef",
            },
            "cases": [
                _case("c1", ["destructive"]),
                _case("c2", ["secret"]),
                _case("c3", ["destructive", "secret"]),
            ],
        }
    )


def _golden() -> Golden:
    return Golden.from_outcomes(
        pack_ref="p@1.0.0+deadbeef",
        outcomes={"c1": "blocked", "c2": "blocked", "c3": "blocked"},
    )


def _engine() -> AttackComparisonEngine:
    return AttackComparisonEngine(_pack())


def test_per_case_deltas() -> None:
    result = _engine().compare(_golden(), {"c1": "missed", "c2": "blocked", "c3": "degraded"})
    assert isinstance(result, AttackComparison)
    by_id = {d.case_id: d for d in result.case_deltas}
    assert by_id["c1"].changed is True
    assert by_id["c1"].direction == "regressed"
    assert by_id["c2"].changed is False
    assert by_id["c2"].direction == "unchanged"
    assert by_id["c3"].direction == "regressed"
    assert by_id["c1"].golden_outcome == "blocked"
    assert by_id["c1"].candidate_outcome == "missed"


def test_improvement_is_detected() -> None:
    result = _engine().compare(_golden(), {"c1": "blocked", "c2": "blocked", "c3": "blocked"})
    golden_missed = Golden.from_outcomes(
        pack_ref="p@1.0.0+deadbeef",
        outcomes={"c1": "missed", "c2": "blocked", "c3": "blocked"},
    )
    improved = _engine().compare(golden_missed, {"c1": "blocked", "c2": "blocked", "c3": "blocked"})
    by_id = {d.case_id: d for d in improved.case_deltas}
    assert by_id["c1"].direction == "improved"
    assert result.aggregate.regressed == 0


def test_per_tag_deltas() -> None:
    result = _engine().compare(_golden(), {"c1": "missed", "c2": "blocked", "c3": "degraded"})
    tags = {t.tag: t for t in result.tag_deltas}
    assert tags["destructive"].golden.blocked == 2
    assert tags["destructive"].candidate.blocked == 0
    assert tags["destructive"].candidate.missed == 1
    assert tags["destructive"].candidate.degraded == 1
    assert tags["secret"].candidate.blocked == 1
    assert tags["secret"].candidate.degraded == 1


def test_aggregate_outcome_split_delta() -> None:
    result = _engine().compare(_golden(), {"c1": "missed", "c2": "blocked", "c3": "degraded"})
    agg = result.aggregate
    assert agg.golden.blocked == 3
    assert agg.candidate.blocked == 1
    assert agg.candidate.missed == 1
    assert agg.candidate.degraded == 1
    assert agg.changed == 2
    assert agg.regressed == 2
    assert agg.improved == 0


def test_a_case_only_in_the_candidate_is_new() -> None:
    result = _engine().compare(
        _golden(), {"c1": "blocked", "c2": "blocked", "c3": "blocked", "c4": "missed"}
    )
    by_id = {d.case_id: d for d in result.case_deltas}
    assert by_id["c4"].direction == "new"
    assert by_id["c4"].golden_outcome is None
