"""M7 7.3 — expected-telemetry validation (F52) (RED → GREEN).

A case declares the agentwatch events a *true block* must produce. A `blocked`
verdict without those events is a `telemetry_gap` finding — the observability of
the defense is proven too.
"""

from __future__ import annotations

from typing import Any

from agentdrill.evidence.schema import read_events
from agentdrill.evidence.telemetry import validate_expected_telemetry
from agentdrill.models.attack_pack import (
    Attack,
    AttackCase,
    AttackStep,
    AttackTarget,
    Driver,
)
from agentdrill.models.attack_pack import (
    Oracle as OracleCfg,
)
from agentdrill.oracles.base import Verdict


def _case(expected_telemetry: list[str]) -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=Driver(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=OracleCfg(expect="blocked", expect_telemetry=expected_telemetry),
    )


def _events(*names: str) -> Any:
    return read_events(
        [{"event": n, "ref": f"evt-{i}", "case_id": "c1"} for i, n in enumerate(names)]
    )


def test_blocked_with_all_expected_telemetry_passes() -> None:
    case = _case(["policy-fired", "halted"])
    verdict = Verdict(case_id="c1", outcome="blocked")
    assert validate_expected_telemetry(case, verdict, _events("policy-fired", "halted")) is None


def test_blocked_without_telemetry_is_flagged() -> None:
    case = _case(["policy-fired", "halted"])
    verdict = Verdict(case_id="c1", outcome="blocked")
    finding = validate_expected_telemetry(case, verdict, _events("policy-fired"))
    assert finding is not None
    assert finding.type == "telemetry_gap"
    assert "halted" in finding.detail


def test_missed_does_not_require_telemetry() -> None:
    case = _case(["policy-fired"])
    verdict = Verdict(case_id="c1", outcome="missed")
    assert validate_expected_telemetry(case, verdict, _events()) is None


def test_no_declared_telemetry_is_a_pass() -> None:
    case = _case([])
    verdict = Verdict(case_id="c1", outcome="blocked")
    assert validate_expected_telemetry(case, verdict, _events()) is None
