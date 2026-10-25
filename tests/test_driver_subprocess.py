"""M4 4.2 — subprocess driver (RED → GREEN).

stdin JSON payload → stdout run-envelope; raw-text fallback unless
`strict_output`; harmless logs on stderr; timeout → AgentTimeoutError; crash →
AdapterError.
"""

from __future__ import annotations

import sys
import time
from typing import Any

import pytest

from agentdrill.drivers.subprocess_driver import SubprocessDriver
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

ENVELOPE = (
    "import sys, json;"
    "p = json.load(sys.stdin);"
    "print(json.dumps({'schema_version': 'agentdrill.run_envelope.v1',"
    " 'output': {'final': 'ok ' + p['case_id']}, 'trajectory': {'steps': []}}))"
)
RAW = "import sys, json; json.load(sys.stdin); print('plain text output')"
FAIL = "import sys; sys.stderr.write('boom\\n'); sys.exit(3)"
HANG = "import time; time.sleep(30)"


def _case() -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=DriverCfg(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=Oracle(expect="blocked"),
    )


def _config(script: str, **extra: Any) -> dict[str, Any]:
    config: dict[str, Any] = {"command": [sys.executable, "-c", script]}
    config.update(extra)
    return config


def test_envelope_delivered_via_stdin() -> None:
    outcome = SubprocessDriver().run(_case(), _config(ENVELOPE))
    assert outcome.output.final == "ok c1"
    assert outcome.trajectory == []


def test_raw_text_fallback() -> None:
    outcome = SubprocessDriver().run(_case(), _config(RAW))
    assert outcome.output.final == "plain text output"
    assert outcome.trajectory == []


def test_strict_output_rejects_non_envelope() -> None:
    with pytest.raises(AdapterError):
        SubprocessDriver().run(_case(), _config(RAW, strict_output=True))


def test_non_zero_exit_raises_adapter_error() -> None:
    with pytest.raises(AdapterError, match="boom"):
        SubprocessDriver().run(_case(), _config(FAIL))


def test_timeout_raises_agent_timeout_error() -> None:
    start = time.perf_counter()
    with pytest.raises(AgentTimeoutError):
        SubprocessDriver().run(_case(), _config(HANG, timeout_seconds=1))
    assert time.perf_counter() - start < 10


def test_missing_command_is_config_error() -> None:
    with pytest.raises(ConfigError):
        SubprocessDriver().run(_case(), {})


def test_driver_receives_no_ground_truth() -> None:
    driver = SubprocessDriver()
    payload = driver.build_payload(_case())
    assert "oracle" not in payload
    assert "expect" not in payload
