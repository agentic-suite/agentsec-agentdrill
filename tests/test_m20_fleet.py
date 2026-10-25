"""M20 20.8 — fleet mode, F45 (RED → GREEN).

One pack across many stacks (opt-in, self-hosted); per-stack honest coverage
rollups with a per-stack outlier query.
"""

from __future__ import annotations

from agentdrill.dx import FleetRollup, StackResult, build_fleet
from agentdrill.oracles.engine import OutcomeSplit


def _stack(name: str, blocked: int, missed: int) -> StackResult:
    return StackResult(stack=name, outcome=OutcomeSplit(blocked=blocked, missed=missed))


def _fleet() -> FleetRollup:
    return build_fleet(
        "p@1.0.0+abc",
        [
            _stack("acme-guard", 3, 0),
            _stack("globex-gate", 1, 3),
        ],
    )


def test_fleet_rollup_across_stacks() -> None:
    fleet = _fleet()
    assert isinstance(fleet, FleetRollup)
    assert fleet.pack_ref == "p@1.0.0+abc"
    assert fleet.total.blocked == 4
    assert fleet.total.missed == 3
    assert fleet.opt_in is True  # self-hosted, opt-in


def test_per_stack_coverage() -> None:
    coverage = _fleet().coverage()
    assert coverage["acme-guard"] == 1.0
    assert coverage["globex-gate"] == 0.25


def test_outlier_query_finds_the_weak_stack() -> None:
    assert _fleet().outliers(threshold=0.8) == ["globex-gate"]
    assert _fleet().outliers(threshold=0.0) == []
