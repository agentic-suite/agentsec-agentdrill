"""M3 3.2 — run_one / run_all + artifact writing (RED → GREEN).

A validated pack runs end to end; `--tags` filters cases; the run writes
`.agentdrill/runs/<id>/` (`run.json` + `artifacts/<case_id>.json`). A stub
driver suffices for the spine (drivers are M4).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.models.artifact import RunOutput, TrajectoryStep
from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.attack_run import CaseArtifact, Run


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


PACK: dict[str, Any] = {
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
        _case("a", ["destructive"]),
        _case("b", ["secret"]),
        _case("c", ["destructive", "secret"]),
    ]
}


def _pack() -> AttackPack:
    return AttackPack.model_validate(PACK)


def _driver(case: Any) -> CaseOutcome:
    return CaseOutcome(
        output=RunOutput(final=f"ran {case.id}"),
        trajectory=[TrajectoryStep(type="response", content=case.id)],
    )


def test_run_all_executes_every_case(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs")
    artifacts = runner.run_all(_pack(), run_id="run-1")
    assert isinstance(artifacts[0], CaseArtifact)
    assert [a.case_id for a in artifacts] == ["a", "b", "c"]
    assert all(a.status == "completed" for a in artifacts)
    assert artifacts[0].output.final == "ran a"


def test_run_all_writes_run_and_artifacts(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs")
    runner.run_all(_pack(), run_id="run-1")
    run_dir = tmp_path / "runs" / "run-1"
    assert (run_dir / "run.json").exists()
    for case_id in ("a", "b", "c"):
        assert (run_dir / "artifacts" / f"{case_id}.json").exists()
    run = Run.model_validate(json.loads((run_dir / "run.json").read_text(encoding="utf-8")))
    assert run.case_order == ["a", "b", "c"]
    assert run.pack_ref == "p@1.0.0+deadbeef"
    # artifacts round-trip
    art = CaseArtifact.model_validate(
        json.loads((run_dir / "artifacts" / "a.json").read_text(encoding="utf-8"))
    )
    assert art.case_id == "a"
    assert art.output.final == "ran a"


def test_run_all_tag_filter(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs")
    artifacts = runner.run_all(_pack(), tags=["secret"], run_id="r")
    assert [a.case_id for a in artifacts] == ["b", "c"]


def test_run_one(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs")
    case = _pack().cases[0]
    artifact = runner.run_one(case, run_id="r")
    assert artifact.case_id == "a"
    assert artifact.id == "r::a"
    assert artifact.status == "completed"


def test_run_all_default_run_id(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs")
    artifacts = runner.run_all(_pack())
    assert len(artifacts) == 3
    # a run directory was created under runs/
    assert any((tmp_path / "runs").iterdir())
