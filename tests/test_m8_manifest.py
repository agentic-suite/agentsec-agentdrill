"""M8 8.2 — run manifest (RED → GREEN).

A run emits `run-manifest.json` alongside `run.json`: host, pack hash,
target/driver digests, pins, dependency tree, and environment variable
**names only** (never values). `--no-manifest` / `emit_manifest=False`
suppresses it. Same environment ⇒ same manifest (R6).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.manifest import RunManifest

TARGET_MANIFEST = {"type": "policyweave-output", "attestation": "fixture", "digest": "abc"}
DRIVER_MANIFEST = {"type": "subprocess", "digest": "def"}
SENTINEL_VALUE = "super-secret-value-should-never-appear"


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


def test_run_manifest_reproduces_the_environment(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setenv("M8_SECRET_TOKEN", SENTINEL_VALUE)
    runner = AttackRunner(
        _ok,
        runs_dir=tmp_path / "runs",
        target_manifest=TARGET_MANIFEST,
        driver_manifest=DRIVER_MANIFEST,
        pins={"seed": 7},
    )
    runner.run_all(_pack(), run_id="r")

    path = tmp_path / "runs" / "r" / "run-manifest.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["run_id"] == "r"
    assert data["host"]["os"]
    assert data["host"]["arch"]
    assert data["host"]["python"]
    assert data["pack"] == {"name": "p", "version": "1.0.0", "hash": "deadbeef"}
    assert data["targets"] == [TARGET_MANIFEST]
    assert data["drivers"] == [DRIVER_MANIFEST]
    assert data["pins"] == {"seed": 7}
    assert "M8_SECRET_TOKEN" in data["environment"]
    assert isinstance(data["deps"], list)


def test_manifest_never_stores_env_values(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setenv("M8_SECRET_TOKEN", SENTINEL_VALUE)
    runner = AttackRunner(_ok, runs_dir=tmp_path / "runs")
    runner.run_all(_pack(), run_id="r")
    text = (tmp_path / "runs" / "r" / "run-manifest.json").read_text(encoding="utf-8")
    assert SENTINEL_VALUE not in text


def test_manifest_can_be_disabled(tmp_path: Path) -> None:
    runner = AttackRunner(_ok, runs_dir=tmp_path / "runs", emit_manifest=False)
    runner.run_all(_pack(), run_id="r")
    assert not (tmp_path / "runs" / "r" / "run-manifest.json").exists()


def test_emitted_manifest_round_trips(tmp_path: Path) -> None:
    runner = AttackRunner(_ok, runs_dir=tmp_path / "runs")
    runner.run_all(_pack(), run_id="r")
    raw = (tmp_path / "runs" / "r" / "run-manifest.json").read_text(encoding="utf-8")
    manifest = RunManifest.model_validate(json.loads(raw))
    assert manifest.run_id == "r"
    assert manifest.pack["name"] == "p"


def test_manifest_is_environment_deterministic(tmp_path: Path) -> None:
    """Two runs in the same environment differ only by run identity/time."""

    def _emitted(run_id: str) -> dict[str, Any]:
        AttackRunner(_ok, runs_dir=tmp_path / run_id).run_all(_pack(), run_id=run_id)
        return json.loads(
            (tmp_path / run_id / run_id / "run-manifest.json").read_text(encoding="utf-8")
        )

    first = _emitted("a")
    second = _emitted("b")
    for volatile in ("run_id", "timestamp"):
        first.pop(volatile, None)
        second.pop(volatile, None)
    assert first == second
