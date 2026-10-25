"""M4 4.3 — python driver (RED → GREEN).

Import a module and call `run(payload)`; a hard timeout runs the callable in a
separate process so a hung callable cannot hang the pack.
"""

from __future__ import annotations

import time
from typing import Any

import pytest

from agentdrill.drivers.python_driver import PythonDriver
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
from agentdrill.models.errors import AdapterError, AgentTimeoutError, ConfigError


def _case() -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=DriverCfg(type="python"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=Oracle(expect="blocked"),
    )


def _config(function: str = "run", **extra: Any) -> dict[str, Any]:
    config: dict[str, Any] = {"module": "fixtures.attack_harness", "function": function}
    config.update(extra)
    return config


def test_callable_invoked_in_process() -> None:
    outcome = PythonDriver().run(_case(), _config())
    assert outcome.output.final == "handled c1"
    assert outcome.trajectory[0].content == "ok"


def test_callable_invoked_isolated() -> None:
    outcome = PythonDriver().run(_case(), _config(timeout_seconds=5))
    assert outcome.output.final == "handled c1"


def test_hard_timeout_isolated() -> None:
    start = time.perf_counter()
    with pytest.raises(AgentTimeoutError):
        PythonDriver().run(_case(), _config(function="run_hang", timeout_seconds=1))
    assert time.perf_counter() - start < 10


def test_missing_module_raises_adapter_error() -> None:
    with pytest.raises(AdapterError):
        PythonDriver().run(_case(), {"module": "does.not.exist"})


def test_missing_module_config_error() -> None:
    with pytest.raises(ConfigError):
        PythonDriver().run(_case(), {})
