"""M20 20.2 — dry-run & explain, F69 (RED → GREEN).

`run --dry-run` prints bound cases, targets, expected verdicts + evidence;
`--explain` annotates why each case exists. A dry-run performs **zero**
executions.
"""

from __future__ import annotations

from agentdrill.dx import DryRunPlan, dry_run, render_dry_run
from agentdrill.models.attack_pack import AttackPack


def _pack() -> AttackPack:
    return AttackPack.model_validate(
        {
            "pack": {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
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
                    "oracle": {"expect": "blocked", "expect_telemetry": ["policy-fired"]},
                }
            ],
        }
    )


def test_dry_run_lists_bound_cases_with_targets_and_verdicts() -> None:
    plan = dry_run(_pack())
    assert isinstance(plan, DryRunPlan)
    case = plan.cases[0]
    assert case.case_id == "c1"
    assert case.target == "policyweave-output"
    assert case.expected == "blocked"
    assert case.evidence == ["policy-fired"]


def test_dry_run_performs_zero_executions() -> None:
    assert dry_run(_pack()).executions == 0


def test_explain_annotates_why_each_case_exists() -> None:
    plan = dry_run(_pack(), explain=True)
    assert plan.cases[0].exists_because == "incident-register#1"


def test_render_dry_run_includes_evidence() -> None:
    rendered = render_dry_run(dry_run(_pack(), explain=True))
    assert "c1" in rendered
    assert "policy-fired" in rendered
    assert "incident-register#1" in rendered
