"""Kill-time budgets published in policy (M12 12.5, F78).

A per-case ``max_seconds`` budget is published **inside policyweave output**
alongside the rule it accompanies, and versioned: so a latency regression lands
in the same PR as the rule change that caused it. Design:
``docs/design/killchain.md`` §Budgets as policy.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel


class KillTimeBudget(BaseModel):
    """A per-case kill-time budget, bound to the rule it accompanies."""

    case_id: str
    rule_id: str
    max_seconds: float
    version: str = ""


def _version(case_id: str, rule_id: str, max_seconds: float) -> str:
    canonical = json.dumps(
        {"case_id": case_id, "rule_id": rule_id, "max_seconds": max_seconds},
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def publish_budget(case_id: str, rule_id: str, max_seconds: float) -> dict[str, Any]:
    """The versioned budget block published alongside the rule."""
    budget = KillTimeBudget(
        case_id=case_id,
        rule_id=rule_id,
        max_seconds=max_seconds,
        version=_version(case_id, rule_id, max_seconds),
    )
    return budget.model_dump()


def read_budgets(policy: Mapping[str, Any]) -> list[KillTimeBudget]:
    """Read the budgets published in ``policy`` (rules without one are absent)."""
    budgets: list[KillTimeBudget] = []
    for rule in policy.get("rules", []):
        block = rule.get("kill_time")
        if not isinstance(block, dict):
            continue
        budgets.append(
            KillTimeBudget(
                case_id=str(block.get("case_id", rule.get("id", ""))),
                rule_id=str(rule.get("id", block.get("rule_id", ""))),
                max_seconds=float(block["max_seconds"]),
                version=str(block.get("version", "")),
            )
        )
    return budgets
