"""M5 5.6 — `.agentdrill/` run layout (RED → GREEN).

Each run stores its target metadata in `run.json` plus a recon snapshot
(`recon.json`), so a run reconstructs what it targeted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.attack_run import Run

TARGET_MANIFEST = {"type": "policyweave-output", "attestation": "fixture", "digest": "abc"}
RECON = {
    "tools": ["shell"],
    "mcp_servers": [],
    "capabilities": [],
    "case_bindings": {"c1": ["shell"]},
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
                {
                    "id": "c1",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                    "tags": [],
                }
            ],
        }
    )


def _ok(case: Any) -> CaseOutcome:
    return CaseOutcome()


def test_run_stores_target_and_recon(tmp_path: Path) -> None:
    runner = AttackRunner(
        _ok,
        runs_dir=tmp_path / "runs",
        target_manifest=TARGET_MANIFEST,
        recon_snapshot=RECON,
    )
    runner.run_all(_pack(), run_id="r")
    run_dir = tmp_path / "runs" / "r"
    run = Run.model_validate(json.loads((run_dir / "run.json").read_text(encoding="utf-8")))
    assert run.target["type"] == "policyweave-output"
    assert run.recon_ref == "recon.json"
    recon = json.loads((run_dir / "recon.json").read_text(encoding="utf-8"))
    assert recon == RECON


def test_run_reconstructs_target(tmp_path: Path) -> None:
    runner = AttackRunner(
        _ok,
        runs_dir=tmp_path / "runs",
        target_manifest=TARGET_MANIFEST,
        recon_snapshot=RECON,
    )
    runner.run_all(_pack(), run_id="r")
    run_dir = tmp_path / "runs" / "r"
    run = Run.model_validate(json.loads((run_dir / "run.json").read_text(encoding="utf-8")))
    recon_ref = run_dir / (run.recon_ref or "")
    assert recon_ref.exists()
    assert run.target["attestation"] == "fixture"


def test_run_without_recon_has_no_ref(tmp_path: Path) -> None:
    runner = AttackRunner(_ok, runs_dir=tmp_path / "runs", target_manifest=TARGET_MANIFEST)
    runner.run_all(_pack(), run_id="r")
    run_dir = tmp_path / "runs" / "r"
    run = Run.model_validate(json.loads((run_dir / "run.json").read_text(encoding="utf-8")))
    assert run.recon_ref is None
    assert not (run_dir / "recon.json").exists()
