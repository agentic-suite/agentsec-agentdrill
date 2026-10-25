"""M12 12.5 — kill-time budgets published in policy (F78) (RED → GREEN).

Per-case `max_seconds` is published inside policyweave output alongside the
rule; the budget is versioned, so a latency regression lands in the same PR as
the rule change that caused it.
"""

from __future__ import annotations

from agentdrill.killchain import KillTimeBudget, publish_budget, read_budgets


def _policy() -> dict:
    return {
        "rules": [
            {
                "id": "r1",
                "policy": "deny destructive shell",
                "kill_time": publish_budget(case_id="c1", rule_id="r1", max_seconds=5.0),
            },
            {"id": "r2", "policy": "deny secret exfil"},  # no budget — not inferred
        ]
    }


def test_budget_is_published_with_its_rule() -> None:
    block = publish_budget(case_id="c1", rule_id="r1", max_seconds=5.0)
    assert block["case_id"] == "c1"
    assert block["rule_id"] == "r1"
    assert block["max_seconds"] == 5.0
    assert block["version"]


def test_budget_version_changes_when_the_budget_changes() -> None:
    a = publish_budget(case_id="c1", rule_id="r1", max_seconds=5.0)["version"]
    b = publish_budget(case_id="c1", rule_id="r1", max_seconds=6.0)["version"]
    assert a != b


def test_budget_version_is_stable_for_equal_budgets() -> None:
    a = publish_budget(case_id="c1", rule_id="r1", max_seconds=5.0)["version"]
    b = publish_budget(case_id="c1", rule_id="r1", max_seconds=5.0)["version"]
    assert a == b


def test_read_budgets_from_policy() -> None:
    budgets = read_budgets(_policy())
    assert len(budgets) == 1
    assert isinstance(budgets[0], KillTimeBudget)
    assert budgets[0].case_id == "c1"
    assert budgets[0].max_seconds == 5.0


def test_a_rule_without_a_budget_is_absent_not_inferred() -> None:
    ids = {b.rule_id for b in read_budgets(_policy())}
    assert ids == {"r1"}
