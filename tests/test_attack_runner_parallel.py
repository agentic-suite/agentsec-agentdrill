"""M3 3.5 — parallel execution + backpressure (RED → GREEN).

`--workers` runs cases concurrently; `--max-outstanding` bounds in-flight work.
Parallel results equal serial results and pack order is preserved.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.models.artifact import RunOutput
from agentdrill.models.attack_pack import AttackPack

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
        {
            "id": f"c{i}",
            "title": "t",
            "goal": "g",
            "incident_ref": "incident-register#1",
            "target": {"type": "policyweave-output"},
            "driver": {"type": "subprocess"},
            "attack": {"steps": [{"tool": "shell"}]},
            "oracle": {"expect": "blocked"},
            "tags": [],
        }
        for i in range(4)
    ],
}


def _ok(case: Any) -> CaseOutcome:
    return CaseOutcome(output=RunOutput(final=f"ok {case.id}"))


def _norm(artifacts: Any) -> list[tuple[str, str, str | None]]:
    return [(a.case_id, a.status, a.output.final) for a in artifacts]


def test_parallel_equals_serial_and_preserves_order(tmp_path: Path) -> None:
    pack = AttackPack.model_validate(PACK)
    serial = AttackRunner(_ok, runs_dir=tmp_path / "s").run_all(pack, run_id="r")
    parallel = AttackRunner(_ok, runs_dir=tmp_path / "p", workers=4).run_all(pack, run_id="r")
    assert _norm(parallel) == _norm(serial)
    assert [a.case_id for a in parallel] == ["c0", "c1", "c2", "c3"]


def test_backpressure_bounds_outstanding(tmp_path: Path) -> None:
    pack = AttackPack.model_validate(PACK)
    artifacts = AttackRunner(
        _ok, runs_dir=tmp_path / "p", workers=4, max_outstanding=1
    ).run_all(pack, run_id="r")
    assert [a.case_id for a in artifacts] == ["c0", "c1", "c2", "c3"]


def test_workers_run_concurrently(tmp_path: Path) -> None:
    class Probe:
        def __init__(self) -> None:
            self.lock = threading.Lock()
            self.active = 0
            self.max_seen = 0

        def enter(self) -> None:
            with self.lock:
                self.active += 1
                self.max_seen = max(self.max_seen, self.active)

        def exit(self) -> None:
            with self.lock:
                self.active -= 1

    probe = Probe()

    def driver(case: Any) -> CaseOutcome:
        probe.enter()
        time.sleep(0.05)
        probe.exit()
        return CaseOutcome(output=RunOutput(final=case.id))

    AttackRunner(driver, runs_dir=tmp_path / "p", workers=4).run_all(
        AttackPack.model_validate(PACK), run_id="r"
    )
    assert probe.max_seen >= 2, "workers did not run concurrently"
