"""M4 4.5 — per-harness drivers (RED → GREEN).

`claude-code` and `cursor` deliver the attack through their harness surface.
Each harness pack runs end to end; the harness is marked in the child env.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from agentdrill.attack_runner import AttackRunner
from agentdrill.drivers.harness import ClaudeCodeDriver, CursorDriver
from agentdrill.models.attack_pack import (
    Attack,
    AttackCase,
    AttackPack,
    AttackStep,
    AttackTarget,
    Oracle,
)
from agentdrill.models.attack_pack import (
    Driver as DriverCfg,
)

ENVELOPE = (
    "import sys, json, os;"
    "p = json.load(sys.stdin);"
    "print(json.dumps({'output': {'final': os.environ.get('AGENTDRILL_HARNESS', '?')"
    " + ':' + p['case_id']}}))"
)


def _command() -> list[str]:
    return [sys.executable, "-c", ENVELOPE]


def _case(driver_type: str, config: dict[str, Any] | None = None) -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=DriverCfg(type=driver_type, config=config or {}),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=Oracle(expect="blocked"),
    )


@pytest.mark.parametrize(
    ("driver", "harness"),
    [(ClaudeCodeDriver(), "claude-code"), (CursorDriver(), "cursor")],
)
def test_harness_driver_delivers(driver: Any, harness: str) -> None:
    outcome = driver.run(_case(harness), {"command": _command()})
    assert outcome.output.final == f"{harness}:c1"


def _pack(harness: str) -> AttackPack:
    return AttackPack.model_validate(
        {
            "pack": {
                "name": f"{harness}-pack",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
                "hash": "deadbeef",
            },
            "cases": [
                {
                    "id": "c1",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": harness, "config": {"command": _command()}},
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                    "tags": [],
                }
            ],
        }
    )


@pytest.mark.parametrize(
    ("driver", "harness"),
    [(ClaudeCodeDriver(), "claude-code"), (CursorDriver(), "cursor")],
)
def test_harness_pack_runs_end_to_end(tmp_path: Path, driver: Any, harness: str) -> None:
    artifacts = AttackRunner(driver, runs_dir=tmp_path / "runs").run_all(
        _pack(harness), run_id="r"
    )
    assert [a.status for a in artifacts] == ["completed"]
    assert artifacts[0].output.final == f"{harness}:c1"
