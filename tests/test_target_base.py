"""M5 5.1 — target adapter base (RED → GREEN).

A `Target` drives the deployed enforcement path and reads back its decision +
evidence: `drive(case)` → `read_decision()` / `read_evidence()`.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest

from agentdrill.models.attack_pack import (
    Attack,
    AttackCase,
    AttackStep,
    AttackTarget,
    Oracle,
)
from agentdrill.models.attack_pack import (
    Driver as DriverCfg,
)
from agentdrill.models.errors import AdapterError, ConfigError
from agentdrill.targets.base import CommandTarget, Decision, Evidence, Target

DECIDE = (
    "import sys, json;"
    "p = json.load(sys.stdin);"
    "print(json.dumps({'decision': {'decision': 'deny', 'rationale': 'blocked ' + p['case_id']},"
    " 'evidence': [{'event': 'policy-fired', 'summary': 'rule matched'}]}))"
)
BOOM = "import sys; sys.stderr.write('target down\\n'); sys.exit(4)"


def _case() -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=DriverCfg(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell", args={"cmd": "drop database prod"})]),
        oracle=Oracle(expect="blocked"),
    )


def test_command_target_drive_then_read() -> None:
    target = CommandTarget({"command": [sys.executable, "-c", DECIDE]})
    target.drive(_case())
    decision = target.read_decision()
    assert isinstance(decision, Decision)
    assert decision.decision == "deny"
    assert "c1" in decision.rationale
    evidence = target.read_evidence()
    assert isinstance(evidence[0], Evidence)
    assert evidence[0].event == "policy-fired"


def test_read_before_drive_is_unknown() -> None:
    target = CommandTarget({"command": [sys.executable, "-c", DECIDE]})
    assert target.read_decision().decision == "unknown"
    assert target.read_evidence() == []


def test_missing_command_is_config_error() -> None:
    with pytest.raises(ConfigError):
        CommandTarget({}).drive(_case())


def test_non_zero_exit_raises_adapter_error() -> None:
    with pytest.raises(AdapterError, match="target down"):
        CommandTarget({"command": [sys.executable, "-c", BOOM]}).drive(_case())


def test_payload_excludes_ground_truth() -> None:
    target = CommandTarget({"command": [sys.executable, "-c", DECIDE]})
    payload = target.build_payload(_case())
    assert "oracle" not in payload
    assert "expect" not in payload
    assert payload["attack"]["steps"][0]["tool"] == "shell"


def test_target_is_abstract() -> None:
    with pytest.raises(TypeError):
        Target()  # type: ignore[abstract]


def test_my_component_name() -> None:
    class MyTarget(CommandTarget):
        component = "my-component"

    target: Any = MyTarget({"command": [sys.executable, "-c", DECIDE]})
    assert target.component == "my-component"
