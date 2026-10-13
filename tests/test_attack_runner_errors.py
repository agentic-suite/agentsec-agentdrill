"""M3 3.4 — error capture / non-abort (RED → GREEN).

A crashing case is marked `status="error"` with the captured traceback; the pack
keeps going — one failing case never aborts the run. Applies in-process and in
the isolated (timeout) path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.models.artifact import RunOutput
from agentdrill.models.attack_pack import AttackPack


def _case(case_id: str) -> dict[str, Any]:
    return {
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
    "cases": [_case("boom"), _case("ok"), _case("boom2")],
}


def _driver(case: Any) -> CaseOutcome:
    """Module-level (picklable) driver that raises for ids starting with 'boom'."""
    if case.id.startswith("boom"):
        raise RuntimeError(f"kaboom:{case.id}")
    return CaseOutcome(output=RunOutput(final=f"ok {case.id}"))


def test_failing_case_does_not_abort_pack_in_process(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs")
    artifacts = runner.run_all(AttackPack.model_validate(PACK), run_id="r")
    by_id = {a.case_id: a for a in artifacts}
    assert [a.case_id for a in artifacts] == ["boom", "ok", "boom2"]
    assert by_id["boom"].status == "error"
    assert "kaboom:boom" in (by_id["boom"].error or "")
    assert by_id["ok"].status == "completed"
    assert by_id["boom2"].status == "error"


def test_failing_case_does_not_abort_pack_isolated(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs", timeout_seconds=5)
    artifacts = runner.run_all(AttackPack.model_validate(PACK), run_id="r")
    by_id = {a.case_id: a for a in artifacts}
    assert by_id["boom"].status == "error"
    assert "kaboom:boom" in (by_id["boom"].error or "")
    assert by_id["ok"].status == "completed"
