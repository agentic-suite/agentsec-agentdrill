"""M5 5.3 — recon/scoping (RED → GREEN).

Probe the exposed surface, produce a `ReconSnapshot`, bind cases to what exists.
A case bound to a nonexistent surface fails **loudly** — never silently passes.
"""

from __future__ import annotations

import sys

import pytest

from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.errors import ConfigError
from agentdrill.recon import ReconSnapshot, bind_cases, probe, recon

INVENTORY = {
    "tools": ["shell", "query"],
    "mcp_servers": ["evil"],
    "capabilities": ["filesystem_write"],
}
PROBE_CMD = (
    "import json;"
    "print(json.dumps({'tools': ['shell'], 'mcp_servers': [], 'capabilities': []}))"
)


def _pack(tools: list[str]) -> AttackPack:
    case = {
        "id": "c1",
        "title": "t",
        "goal": "g",
        "incident_ref": "incident-register#1",
        "target": {"type": "policyweave-output"},
        "driver": {"type": "subprocess"},
        "attack": {"steps": [{"tool": t} for t in tools]},
        "oracle": {"expect": "blocked"},
        "tags": [],
    }
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
            "cases": [case],
        }
    )


def test_probe_from_inventory() -> None:
    snapshot = probe(inventory=INVENTORY)
    assert isinstance(snapshot, ReconSnapshot)
    assert snapshot.tools == ["shell", "query"]
    assert snapshot.mcp_servers == ["evil"]


def test_probe_from_command() -> None:
    snapshot = probe(command=[sys.executable, "-c", PROBE_CMD])
    assert snapshot.tools == ["shell"]


def test_probe_without_source_is_config_error() -> None:
    with pytest.raises(ConfigError):
        probe()


def test_bind_cases_records_bindings() -> None:
    snapshot = probe(inventory=INVENTORY)
    bind_cases(_pack(["shell"]), snapshot)
    assert snapshot.case_bindings["c1"] == ["shell"]


def test_missing_surface_fails_loudly() -> None:
    snapshot = probe(inventory={"tools": ["shell"], "mcp_servers": [], "capabilities": []})
    with pytest.raises(ConfigError, match="widget"):
        bind_cases(_pack(["widget"]), snapshot)


def test_mcp_tool_binds_to_server() -> None:
    snapshot = probe(inventory=INVENTORY)
    bind_cases(_pack(["mcp__evil__run"]), snapshot)
    assert snapshot.case_bindings["c1"] == ["mcp__evil__run"]


def test_recon_probes_and_binds() -> None:
    snapshot = recon(_pack(["shell"]), inventory=INVENTORY)
    assert snapshot.case_bindings["c1"] == ["shell"]


def test_recon_fails_on_missing_surface() -> None:
    with pytest.raises(ConfigError):
        recon(_pack(["widget"]), inventory=INVENTORY)
