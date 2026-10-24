"""M27 27.2 — shadow mode + false-block budget (RED → GREEN).

Run a candidate policy **log-only** beside the enforced one: report the
divergence rate, cluster it, prove the shadow was side-effect-free (M23 witness),
and gate on the policy's declared **false-block budget** with a bootstrap CI.
"""

from __future__ import annotations

import pytest

from agentdrill.backtest import (
    ShadowDecision,
    ShadowError,
    ShadowReport,
    false_block_rate,
    require_false_block_budget,
    require_side_effect_free,
    run_shadow,
)


def _decisions() -> list[ShadowDecision]:
    return [
        # unchanged
        ShadowDecision(action="read_file", enforced_allowed=True, candidate_allowed=True),
        # false block on a benign call (candidate blocks what production allowed)
        ShadowDecision(action="list_dir", enforced_allowed=True, candidate_allowed=False),
        ShadowDecision(action="list_dir", enforced_allowed=True, candidate_allowed=False),
        # a regression (candidate allowed what production denied) — not a false block
        ShadowDecision(action="exfil", enforced_allowed=False, candidate_allowed=True),
        # divergent on a non-benign call (allowed by both is impossible; here both block)
        ShadowDecision(action="rm_rf", enforced_allowed=False, candidate_allowed=False),
    ]


def test_shadow_divergence_rate_and_clusters() -> None:
    report = run_shadow(_decisions())
    assert isinstance(report, ShadowReport)
    assert report.total == 5
    assert report.divergent == 3  # two false blocks + one regression
    assert report.divergence_rate == pytest.approx(3 / 5)
    assert report.clusters == {"list_dir": 2}


def test_false_block_rate_is_over_benign_calls_only() -> None:
    report = run_shadow(_decisions())
    # benign = enforced_allowed True (read_file, list_dir, list_dir) → 2 of 3 blocked
    assert report.benign_total == 3
    assert false_block_rate(report) == pytest.approx(2 / 3)
    assert report.false_block_ci[0] <= report.false_block_rate <= report.false_block_ci[1]


def test_false_block_budget_gate() -> None:
    report = run_shadow(_decisions())
    with pytest.raises(ShadowError):
        require_false_block_budget(report, budget=0.005)
    require_false_block_budget(report, budget=0.75)


def test_shadow_is_side_effect_free_only_without_side_effects() -> None:
    clean = run_shadow(_decisions(), side_effects=[])
    assert clean.side_effect_free is True
    require_side_effect_free(clean)

    dirty = run_shadow(_decisions(), side_effects=["network-egress:evil.example"])
    assert dirty.side_effect_free is False
    assert dirty.side_effects == ["network-egress:evil.example"]
    with pytest.raises(ShadowError):
        require_side_effect_free(dirty)


def test_ci_is_reproducible() -> None:
    first = run_shadow(_decisions(), seed=7)
    second = run_shadow(_decisions(), seed=7)
    assert first.false_block_ci == second.false_block_ci
