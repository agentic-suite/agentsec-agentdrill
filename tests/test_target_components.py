"""M5 5.2 — deployed-stack targets (RED → GREEN).

Each component target (`agentgate`, `agentkeys`, `agentseatbelt`, `agentkernel`,
`policyweave-output`, `agenthalt`) drives its enforcement path and reads back a
decision + evidence.
"""

from __future__ import annotations

import sys

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
from agentdrill.models.errors import ConfigError
from agentdrill.targets.registry import TARGETS, get_target

COMPONENTS = [
    "agentgate",
    "agentkeys",
    "agentseatbelt",
    "agentkernel",
    "policyweave-output",
    "agenthalt",
]

DECIDE = (
    "import sys, json;"
    "p = json.load(sys.stdin);"
    "print(json.dumps({'decision': {'decision': 'deny', 'rationale': p['target']['type']},"
    " 'evidence': [{'event': 'denied', 'summary': 'enforced'}]}))"
)


def _case(component: str) -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type=component),
        driver=DriverCfg(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=Oracle(expect="blocked"),
    )


def test_all_components_registered() -> None:
    assert set(COMPONENTS) <= set(TARGETS)


@pytest.mark.parametrize("component", COMPONENTS)
def test_component_drives_and_reads(component: str) -> None:
    target = get_target(component, {"command": [sys.executable, "-c", DECIDE]})
    target.drive(_case(component))
    assert target.read_decision().decision == "deny"
    assert target.read_decision().rationale == component
    assert target.read_evidence()[0].event == "denied"


def test_unknown_component_is_config_error() -> None:
    with pytest.raises(ConfigError, match="widget"):
        get_target("widget", {})
