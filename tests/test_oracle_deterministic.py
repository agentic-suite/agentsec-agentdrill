"""M6 6.2 — deterministic oracles (RED → GREEN).

deny/allowed, confinement, budget, sequence, grounding — read only the
trajectory / evidence / config, so verdicts are reproducible.
"""

from __future__ import annotations

from agentdrill.attack_runner import CaseOutcome
from agentdrill.models.artifact import Cost, RunOutput, TrajectoryStep
from agentdrill.models.attack_pack import (
    Attack,
    AttackCase,
    AttackStep,
    AttackTarget,
    Budget,
    Driver,
)
from agentdrill.models.attack_pack import (
    Oracle as OracleCfg,
)
from agentdrill.oracles.registry import SCORERS, get_oracle
from agentdrill.targets.base import Evidence


def _case(steps: int = 1, budget: Budget | None = None) -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=Driver(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell") for _ in range(steps)]),
        oracle=OracleCfg(expect="blocked"),
        budget=budget,
    )


def _observed(
    tool_calls: int = 1,
    denied: bool = False,
    final: str | None = "done",
    cost_usd: float = 0.0,
) -> CaseOutcome:
    steps = [TrajectoryStep(type="tool_call", tool="shell") for _ in range(tool_calls)]
    if denied:
        steps.append(TrajectoryStep(type="tool_result", tool="shell", result={"denied": True}))
    return CaseOutcome(
        output=RunOutput(final=final), trajectory=steps, cost=Cost(cost_usd=cost_usd)
    )


def test_builtin_deterministic_oracles_registered() -> None:
    assert {"deny", "allowed", "confinement", "budget", "sequence", "grounding"} <= set(SCORERS)


def test_deny_oracle() -> None:
    oracle = get_oracle("deny")
    assert oracle.evaluate(_case(), _observed(denied=True)).outcome == "blocked"
    assert oracle.evaluate(_case(), _observed(denied=False)).outcome == "missed"


def test_deny_from_evidence_event() -> None:
    oracle = get_oracle("deny")
    evidence = [Evidence(event="policy-fired")]
    assert oracle.evaluate(_case(), _observed(), evidence).outcome == "blocked"


def test_allowed_oracle_is_inverse() -> None:
    oracle = get_oracle("allowed")
    assert oracle.evaluate(_case(), _observed(denied=False)).outcome == "missed"
    assert oracle.evaluate(_case(), _observed(denied=True)).outcome == "blocked"


def test_confinement_oracle() -> None:
    oracle = get_oracle("confinement")
    assert oracle.evaluate(_case(), _observed(), [Evidence(event="denied")]).outcome == "blocked"
    assert oracle.evaluate(_case(), _observed()).outcome == "missed"


def test_budget_oracle() -> None:
    oracle = get_oracle("budget")
    case = _case(budget=Budget(max_cost_usd=0.05))
    assert oracle.evaluate(case, _observed(cost_usd=0.5)).outcome == "missed"
    assert oracle.evaluate(case, _observed(cost_usd=0.01)).outcome == "blocked"


def test_sequence_oracle() -> None:
    oracle = get_oracle("sequence")
    # 2-step attack, defense stopped after 1 call → blocked; both attempted → missed
    assert oracle.evaluate(_case(steps=2), _observed(tool_calls=1)).outcome == "blocked"
    assert oracle.evaluate(_case(steps=2), _observed(tool_calls=2)).outcome == "missed"


def test_grounding_oracle() -> None:
    oracle = get_oracle("grounding")
    assert oracle.evaluate(_case(), _observed(final="done")).outcome == "blocked"
    assert oracle.evaluate(_case(), _observed(final=None)).outcome == "degraded"


def test_verdicts_are_reproducible() -> None:
    oracle = get_oracle("deny")
    first = oracle.evaluate(_case(), _observed(denied=True))
    second = oracle.evaluate(_case(), _observed(denied=True))
    assert first == second
