"""M6 6.4 — hybrid + offline safety (RED → GREEN).

The deterministic gate always runs. The judge runs only where needed (when the
gate cannot confirm the expected outcome). With no judge, the gate result stands
with `judge_not_evaluated: true` — enforcement is never silently skipped.
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
from agentdrill.oracles.engine import OracleEngine
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


class _SpyClient(MockJudgeClient):
    def __init__(self) -> None:
        super().__init__(JudgeVerdict(score=0.9, rationale="spy"))
        self.calls = 0

    def score(self, criteria: str, observed: str) -> JudgeVerdict:
        self.calls += 1
        return super().score(criteria, observed)


def test_gate_confirms_and_judge_is_skipped() -> None:
    spy = _SpyClient()
    engine = OracleEngine(judge=spy)
    verdict = engine.evaluate(_case("blocked"), _observed(denied=True), oracle_name="deny")
    assert verdict.outcome == "blocked"
    assert spy.calls == 0


def test_judge_runs_when_gate_cannot_confirm() -> None:
    engine = OracleEngine(judge=MockJudgeClient(JudgeVerdict(score=0.9, rationale="ok")))
    # case expects blocked, but nothing was denied → the gate cannot confirm → judge runs
    verdict = engine.evaluate(_case("blocked"), _observed(denied=False), oracle_name="deny")
    assert verdict.outcome == "blocked"
    assert verdict.score == 0.9


def test_missing_judge_keeps_gate_result() -> None:
    engine = OracleEngine(judge=None)
    verdict = engine.evaluate(_case("blocked"), _observed(denied=False), oracle_name="deny")
    assert verdict.judge_not_evaluated is True
    assert verdict.outcome == "missed"


def test_enforcement_never_skipped_offline() -> None:
    engine = OracleEngine(judge=None)
    verdict = engine.evaluate(_case("blocked"), _observed(denied=True), oracle_name="deny")
    assert verdict.outcome == "blocked"
