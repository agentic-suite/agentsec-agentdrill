"""M6 6.6 — divergence + failure taxonomy (RED → GREEN).

Deterministic and judge verdicts are compared, not averaged: a divergence is
classified `critical` (right-looking result on a wrong path) or `warning` (right
path, poor answer). Failures get a taxonomy type.
"""

from __future__ import annotations

from agentdrill.attack_runner import CaseOutcome
from agentdrill.models.artifact import RunOutput, TrajectoryStep
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
from agentdrill.oracles.base import Divergence, Verdict
from agentdrill.oracles.engine import (
    OracleEngine,
    classify_divergence,
    classify_failure,
    has_divergence,
)
from agentdrill.oracles.judge import JudgeVerdict, MockJudgeClient


def _case(expect: str = "blocked") -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=Driver(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=OracleCfg(expect=expect),  # type: ignore[arg-type]
    )


def _observed(denied: bool) -> CaseOutcome:
    steps = [TrajectoryStep(type="tool_call", tool="shell")]
    if denied:
        steps.append(TrajectoryStep(type="tool_result", tool="shell", result={"denied": True}))
    return CaseOutcome(output=RunOutput(final="done"), trajectory=steps)


def test_no_divergence_when_equal() -> None:
    assert classify_divergence("c1", "blocked", "blocked") is None


def test_divergence_critical_when_gate_missed_but_judge_passed() -> None:
    divergence = classify_divergence("c1", "missed", "blocked")
    assert divergence is not None
    assert divergence.severity == "critical"


def test_divergence_warning_when_gate_passed_but_judge_failed() -> None:
    divergence = classify_divergence("c1", "blocked", "missed")
    assert divergence is not None
    assert divergence.severity == "warning"


def test_classify_failure_safety_miss() -> None:
    finding = classify_failure(_case("blocked"), Verdict(case_id="c1", outcome="missed"))
    assert finding is not None
    assert finding.type == "safety_miss"
    assert finding.severity == "critical"


def test_classify_failure_policy_miss() -> None:
    finding = classify_failure(_case("blocked"), Verdict(case_id="c1", outcome="degraded"))
    assert finding is not None
    assert finding.type == "policy_miss"


def test_classify_failure_none_when_as_expected() -> None:
    assert classify_failure(_case("blocked"), Verdict(case_id="c1", outcome="blocked")) is None


def test_engine_attaches_divergence() -> None:
    engine = OracleEngine(judge=MockJudgeClient(JudgeVerdict(score=0.9, rationale="ok")))
    verdict = engine.evaluate(_case("blocked"), _observed(denied=False), oracle_name="deny")
    assert verdict.divergence is not None
    assert verdict.divergence.severity == "critical"


def test_has_divergence() -> None:
    critical = [
        Verdict(
            case_id="c1",
            outcome="blocked",
            divergence=Divergence(case_id="c1", severity="critical"),
        )
    ]
    warning = [
        Verdict(
            case_id="c1",
            outcome="blocked",
            divergence=Divergence(case_id="c1", severity="warning"),
        )
    ]
    assert has_divergence(critical) is True
    assert has_divergence(warning) is False
    assert has_divergence(warning, severity="warning") is True
    assert has_divergence([Verdict(case_id="c1", outcome="blocked")]) is False
