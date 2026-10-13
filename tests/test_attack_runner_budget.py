"""M3 3.6 — budget governor (RED → GREEN).

Per-case `budget.max_cost_usd` and a run-level `max_cost_usd` cap: an over-budget
case is marked `status="aborted"` with `error="cost_exceeded"`; once the run-level
cap is exceeded, the remaining cases are aborted — reported, never hidden.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.models.artifact import Cost, RunOutput
from agentdrill.models.attack_pack import AttackPack


def _case(case_id: str, budget: dict[str, Any] | None = None) -> dict[str, Any]:
    case: dict[str, Any] = {
        "id": case_id,
        "title": "t",
        "goal": "g",
        "incident_ref": "incident-register#1",
        "target": {"type": "policyweave-output"},
        "driver": {"type": "subprocess"},
        "attack": {"steps": [{"tool": "shell"}]},
        "oracle": {"expect": "blocked"},
        "tags": [],
    }
    if budget is not None:
        case["budget"] = budget
    return case


def _pack(cases: list[dict[str, Any]]) -> AttackPack:
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
            "cases": cases,
        }
    )


def _driver(case: Any) -> CaseOutcome:
    return CaseOutcome(output=RunOutput(final=case.id), cost=Cost(cost_usd=1.0))


def test_per_case_budget_aborts_over_budget_case(tmp_path: Path) -> None:
    pack = _pack([_case("cheap", {"max_cost_usd": 0.01}), _case("ok")])
    artifacts = AttackRunner(_driver, runs_dir=tmp_path / "runs").run_all(pack, run_id="r")
    by_id = {a.case_id: a for a in artifacts}
    assert by_id["cheap"].status == "aborted"
    assert by_id["cheap"].error == "cost_exceeded"
    assert by_id["ok"].status == "completed"


def test_run_level_max_cost_aborts_remaining(tmp_path: Path) -> None:
    pack = _pack([_case("c0"), _case("c1"), _case("c2")])
    artifacts = AttackRunner(
        _driver, runs_dir=tmp_path / "runs", max_cost_usd=1.5
    ).run_all(pack, run_id="r")
    by_id = {a.case_id: a for a in artifacts}
    assert by_id["c0"].status == "completed"
    assert by_id["c2"].status == "aborted"
    assert by_id["c2"].error == "cost_exceeded"
    assert len(artifacts) == 3  # aborted cases are still reported


def test_no_cap_runs_everything(tmp_path: Path) -> None:
    pack = _pack([_case("c0"), _case("c1")])
    artifacts = AttackRunner(_driver, runs_dir=tmp_path / "runs").run_all(pack, run_id="r")
    assert all(a.status == "completed" for a in artifacts)
