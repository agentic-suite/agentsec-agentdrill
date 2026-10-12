"""M2 2.3 — oracle/target/driver resolution at load (RED → GREEN).

Every target/driver/oracle a case references is resolved against the registry at
load; an unknown reference fails with `ConfigError` (exit 2) — never a silent
pass (docs/reference/errors.md).
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from agentdrill.loading.attack_pack_loader import load_attack_pack
from agentdrill.models.errors import ConfigError

BASE: dict[str, Any] = {
    "pack": {
        "name": "p",
        "version": "1.0.0",
        "description": "d",
        "min_agentdrill": "0.1.0",
        "license": "Apache-2.0",
        "trust": "built-in",
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
            "oracle": {"expect": "blocked", "dimensions": ["enforcement"], "expect_telemetry": []},
        }
    ],
}


def _load(tmp_path: Any, mutate: Any) -> Any:
    import copy

    data = copy.deepcopy(BASE)
    case = data["cases"][0]
    mutate(data, case)
    path = tmp_path / "pack.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return load_attack_pack(path)


def test_known_target_and_driver_resolve(tmp_path: Any) -> None:
    pack = _load(tmp_path, lambda d, c: None)
    assert pack.cases[0].target.type == "policyweave-output"
    assert pack.cases[0].driver.type == "subprocess"


def test_unknown_target_type_fails_config_error(tmp_path: Any) -> None:
    with pytest.raises(ConfigError, match="widget"):
        _load(tmp_path, lambda d, c: c["target"].update({"type": "widget"}))


def test_unknown_driver_type_fails_config_error(tmp_path: Any) -> None:
    with pytest.raises(ConfigError, match="hoverboard"):
        _load(tmp_path, lambda d, c: c["driver"].update({"type": "hoverboard"}))


def test_unknown_oracle_dimension_fails_config_error(tmp_path: Any) -> None:
    with pytest.raises(ConfigError, match="vibes"):
        _load(tmp_path, lambda d, c: c["oracle"].update({"dimensions": ["vibes"]}))


def test_unknown_oracle_expectation_fails_config_error(tmp_path: Any) -> None:
    with pytest.raises(ConfigError, match="maybe"):
        _load(tmp_path, lambda d, c: c["oracle"].update({"expect": "maybe"}))


def test_unknown_telemetry_event_fails_config_error(tmp_path: Any) -> None:
    with pytest.raises(ConfigError, match="not-a-real-event"):
        _load(tmp_path, lambda d, c: c["oracle"].update({"expect_telemetry": ["not-a-real-event"]}))


def test_external_trust_requires_sandbox_driver(tmp_path: Any) -> None:
    def mutate(data: dict[str, Any], case: dict[str, Any]) -> None:
        data["pack"]["trust"] = "external"
        case["driver"]["type"] = "claude-code"

    with pytest.raises(ConfigError, match="external"):
        _load(tmp_path, mutate)
