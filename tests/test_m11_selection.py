"""M11 11.6 — diff-aware re-runs, F76 (RED → GREEN).

Compute the affected cases from the changed surface; the changed-surface set
equals the bound set, so CI time scales with diff size.
"""

from __future__ import annotations

from agentdrill.ci import Selection, affected_cases, case_surfaces, selection
from agentdrill.models.attack_pack import AttackCase


def _case(case_id: str, target: str, tool: str, tags: list[str]) -> AttackCase:
    return AttackCase.model_validate(
        {
            "id": case_id,
            "title": "t",
            "goal": "g",
            "incident_ref": "incident-register#1",
            "target": {"type": target},
            "driver": {"type": "subprocess"},
            "attack": {"steps": [{"tool": tool}]},
            "oracle": {"expect": "blocked"},
            "tags": tags,
        }
    )


CASES = [
    _case("c1", "policyweave-output", "shell", ["destructive"]),
    _case("c2", "agenthalt", "http", ["secret"]),
]


def test_case_surfaces_bundle_target_tools_and_tags() -> None:
    assert case_surfaces(CASES[0]) == {"policyweave-output", "shell", "destructive"}


def test_a_changed_tool_selects_bound_cases() -> None:
    assert affected_cases(CASES, ["shell"]) == ["c1"]


def test_a_changed_target_selects_bound_cases() -> None:
    assert affected_cases(CASES, ["agenthalt"]) == ["c2"]


def test_changed_surface_set_equals_bound_set() -> None:
    assert set(affected_cases(CASES, ["policyweave-output", "agenthalt"])) == {"c1", "c2"}
    assert affected_cases(CASES, ["unknown"]) == []


def test_selection_fraction_reflects_diff_size() -> None:
    sel = selection(CASES, ["shell"])
    assert isinstance(sel, Selection)
    assert sel.selected == ["c1"]
    assert sel.total == 2
    assert sel.fraction == 0.5


def test_empty_diff_selects_nothing() -> None:
    sel = selection(CASES, [])
    assert sel.selected == []
    assert sel.fraction == 0.0
