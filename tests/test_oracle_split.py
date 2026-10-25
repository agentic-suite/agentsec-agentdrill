"""M6 6.5 — dimensions + outcome split (RED → GREEN).

The three dimensions (`compatibility`/`enforcement`/`integrity`) with the
hierarchy enforcement > integrity > compatibility, and the honest per-run split
`blocked`/`missed`/`degraded`.
"""

from __future__ import annotations

from agentdrill.oracles.base import Verdict
from agentdrill.oracles.engine import OutcomeSplit, highest_dimension, outcome_split


def test_outcome_split_counts() -> None:
    verdicts = [
        Verdict(case_id="a", outcome="blocked"),
        Verdict(case_id="b", outcome="missed"),
        Verdict(case_id="c", outcome="missed"),
        Verdict(case_id="d", outcome="degraded"),
    ]
    split = outcome_split(verdicts)
    assert isinstance(split, OutcomeSplit)
    assert split.blocked == 1
    assert split.missed == 2
    assert split.degraded == 1
    assert split.total == 4


def test_outcome_split_empty() -> None:
    split = outcome_split([])
    assert (split.blocked, split.missed, split.degraded, split.total) == (0, 0, 0, 0)


def test_highest_dimension_hierarchy() -> None:
    assert highest_dimension(["compatibility", "enforcement"]) == "enforcement"
    assert highest_dimension(["compatibility", "integrity"]) == "integrity"
    assert highest_dimension(["enforcement", "integrity"]) == "enforcement"
    assert highest_dimension([]) is None


def test_verdict_carries_dimensions() -> None:
    from agentdrill.attack_runner import CaseOutcome
    from agentdrill.models.artifact import TrajectoryStep
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
    from agentdrill.oracles.registry import get_oracle

    case = AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=Driver(type="subprocess"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=OracleCfg(expect="blocked"),
    )
    observed = CaseOutcome(
        trajectory=[TrajectoryStep(type="tool_result", tool="shell", result={"denied": True})]
    )
    verdict = get_oracle("deny").evaluate(case, observed)
    assert verdict.dimensions == ["enforcement"]
