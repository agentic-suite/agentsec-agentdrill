"""M8 8.4 — contamination checks, F30 (RED → GREEN).

Probe each case for overlap with a judge/target model's declared training
posture (incident refs, case ids, tools). A contaminated case is **flagged**,
never hidden — the flag travels on the case artifact and in the reported table.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.determinism import ContaminationFlag, ContaminationProbe, TrainingPosture
from agentdrill.models.attack_pack import AttackPack


def _case(case_id: str, incident_ref: str, tool: str) -> dict[str, Any]:
    return {
        "id": case_id,
        "title": "t",
        "goal": "g",
        "incident_ref": incident_ref,
        "target": {"type": "policyweave-output"},
        "driver": {"type": "subprocess"},
        "attack": {"steps": [{"tool": tool}]},
        "oracle": {"expect": "blocked"},
        "tags": [],
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
                _case("c1", "incident-register#1", "shell"),
                _case("c2", "incident-register#2", "http"),
            ],
        }
    )


def _posture() -> TrainingPosture:
    return TrainingPosture(
        model="judge-x",
        exposed_case_ids=frozenset({"c1"}),
        exposed_incident_refs=frozenset(),
        exposed_tools=frozenset(),
    )


def _ok(case: Any) -> CaseOutcome:
    return CaseOutcome()


def test_probe_flags_an_overlapping_case() -> None:
    flag = ContaminationProbe(_posture()).probe(_pack().cases[0])
    assert isinstance(flag, ContaminationFlag)
    assert flag.contaminated is True
    assert "c1" in flag.reason
    assert flag.matched


def test_probe_passes_a_clean_case() -> None:
    flag = ContaminationProbe(_posture()).probe(_pack().cases[1])
    assert flag.contaminated is False
    assert flag.reason == ""
    assert flag.matched == []


def test_probe_matches_incident_ref_and_tool() -> None:
    posture = TrainingPosture(
        model="judge-y",
        exposed_incident_refs=frozenset({"incident-register#2"}),
        exposed_tools=frozenset({"shell"}),
    )
    probe = ContaminationProbe(posture)
    assert probe.probe(_pack().cases[0]).contaminated is True  # tool overlap
    assert probe.probe(_pack().cases[1]).contaminated is True  # incident overlap


def test_probe_pack_flags_only_overlapping_cases() -> None:
    flags = ContaminationProbe(_posture()).probe_pack(_pack())
    contaminated = {f.case_id for f in flags if f.contaminated}
    assert contaminated == {"c1"}


def test_run_marks_contaminated_case_in_the_artifact(tmp_path: Path) -> None:
    runner = AttackRunner(
        _ok,
        runs_dir=tmp_path / "runs",
        contamination_probe=ContaminationProbe(_posture()),
    )
    artifacts = runner.run_all(_pack(), run_id="r")
    by_id = {a.case_id: a for a in artifacts}
    assert by_id["c1"].contaminated is True
    assert by_id["c1"].contamination is not None
    assert by_id["c2"].contaminated is False

    written = json.loads(
        (tmp_path / "runs" / "r" / "artifacts" / "c1.json").read_text(encoding="utf-8")
    )
    assert written["contaminated"] is True


def test_run_without_probe_leaves_cases_unflagged(tmp_path: Path) -> None:
    artifacts = AttackRunner(_ok, runs_dir=tmp_path / "runs").run_all(_pack(), run_id="r")
    assert all(a.contaminated is False for a in artifacts)
