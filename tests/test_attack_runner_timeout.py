"""M3 3.3 — per-case hard timeout in isolation (RED → GREEN).

Callable drivers run in a separate process when a timeout is configured, so a
hung case cannot hang the pack; a timeout marks the case `status="timeout"` and
the pack continues.
"""

from __future__ import annotations

import time
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
    "cases": [_case("hang"), _case("fast")],
}


def _driver(case: Any) -> CaseOutcome:
    """Module-level (picklable) driver: 'hang' sleeps, others return quickly."""
    if case.id == "hang":
        time.sleep(30)
    return CaseOutcome(output=RunOutput(final=f"ok {case.id}"))


def test_hung_case_does_not_hang_the_pack(tmp_path: Path) -> None:
    runner = AttackRunner(_driver, runs_dir=tmp_path / "runs", timeout_seconds=1)
    start = time.perf_counter()
    artifacts = runner.run_all(AttackPack.model_validate(PACK), run_id="r")
    elapsed = time.perf_counter() - start
    assert elapsed < 15, f"pack hung for {elapsed:.1f}s"
    by_id = {a.case_id: a for a in artifacts}
    assert by_id["hang"].status == "timeout"
    assert by_id["fast"].status == "completed"
    assert by_id["fast"].output.final == "ok fast"
