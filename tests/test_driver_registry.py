"""M4 4.6 — driver registry + plugin discovery (RED → GREEN).

A registry of built-in drivers, entry-point discovery for community drivers,
unknown → ConfigError, and an AdapterManifest whose SHA-256 digest is bound into
each run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.drivers.base import Driver
from agentdrill.drivers.harness import ClaudeCodeDriver, CursorDriver
from agentdrill.drivers.http_driver import HttpDriver
from agentdrill.drivers.python_driver import PythonDriver
from agentdrill.drivers.registry import (
    DRIVERS,
    discover,
    get_driver,
    manifest_for,
)
from agentdrill.drivers.subprocess_driver import SubprocessDriver
from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.errors import ConfigError


class _CustomDriver(Driver):
    name = "custom"

    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> Any:
        return {"output": {"final": "ok"}}


class _FakeEntryPoint:
    name = "custom"

    def load(self) -> type[Driver]:
        return _CustomDriver


def test_builtin_drivers_registered() -> None:
    assert {"subprocess", "python", "http", "claude-code", "cursor"} <= set(DRIVERS)


def test_get_driver_returns_instance() -> None:
    assert isinstance(get_driver("subprocess"), SubprocessDriver)
    assert isinstance(get_driver("python"), PythonDriver)
    assert isinstance(get_driver("http"), HttpDriver)
    assert isinstance(get_driver("claude-code"), ClaudeCodeDriver)
    assert isinstance(get_driver("cursor"), CursorDriver)


def test_unknown_driver_is_config_error() -> None:
    with pytest.raises(ConfigError, match="nope"):
        get_driver("nope")


def test_entry_point_discovery_registers() -> None:
    registered = discover([_FakeEntryPoint()])
    assert "custom" in registered
    assert isinstance(get_driver("custom"), _CustomDriver)


def test_manifest_digest_is_stable_sha256() -> None:
    manifest = manifest_for(SubprocessDriver)
    assert manifest.name == "subprocess"
    assert len(manifest.digest) == 64
    assert manifest.digest == manifest_for(SubprocessDriver).digest


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


def test_digest_bound_into_run(tmp_path: Path) -> None:
    from agentdrill.models.attack_run import Run

    manifest = manifest_for(SubprocessDriver)
    runner = AttackRunner(
        _ok, runs_dir=tmp_path / "runs", driver_manifest=manifest.to_dict()
    )
    runner.run_all(_pack(), run_id="r")
    run = Run.model_validate(
        json.loads((tmp_path / "runs" / "r" / "run.json").read_text(encoding="utf-8"))
    )
    assert run.driver["name"] == "subprocess"
    assert run.driver["digest"] == manifest.digest
