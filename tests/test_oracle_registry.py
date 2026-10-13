"""M6 6.1 — oracle base + registry (RED → GREEN).

An `Oracle` evaluates a case's observation into a `Verdict`. Registration is via
`@register_oracle` (plus entry-point discovery); an unknown oracle name fails at
load with `ConfigError`.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentdrill.attack_runner import CaseOutcome
from agentdrill.models.attack_pack import AttackCase
from agentdrill.models.errors import ConfigError
from agentdrill.oracles.base import Oracle, Verdict
from agentdrill.oracles.registry import SCORERS, discover, get_oracle, register_oracle


@register_oracle
class _CustomOracle(Oracle):
    name = "custom-test-oracle"
    kind = "deterministic"

    def evaluate(
        self, case: AttackCase, observed: CaseOutcome, evidence: Any = None
    ) -> Verdict:
        return Verdict(case_id=case.id, outcome="blocked")


class _FakeEntryPoint:
    name = "custom-test-oracle"

    def load(self) -> type[Oracle]:
        return _CustomOracle


def _case() -> AttackCase:
    from agentdrill.models.attack_pack import Attack, AttackStep, AttackTarget, Driver
    from agentdrill.models.attack_pack import Oracle as OracleCfg

    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=Driver(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=OracleCfg(expect="blocked"),
    )


def test_register_and_get() -> None:
    oracle = get_oracle("custom-test-oracle")
    assert isinstance(oracle, _CustomOracle)
    assert oracle.kind == "deterministic"
    assert oracle.evaluate(_case(), CaseOutcome()).outcome == "blocked"


def test_unknown_oracle_is_config_error() -> None:
    with pytest.raises(ConfigError, match="nope"):
        get_oracle("nope")


def test_entry_point_discovery_registers() -> None:
    SCORERS.pop("custom-test-oracle", None)
    registered = discover([_FakeEntryPoint()])
    assert "custom-test-oracle" in registered
    assert isinstance(get_oracle("custom-test-oracle"), _CustomOracle)


def test_oracle_is_abstract() -> None:
    with pytest.raises(TypeError):
        Oracle()  # type: ignore[abstract]
