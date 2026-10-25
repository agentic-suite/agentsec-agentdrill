"""Closes-the-loop policy suggestion (M18 18.9, F21).

A confirmed miss emits an **advisory** rule and a what-if replay proving the
rule closes the miss. The fix is proposed as a **reviewed PR** and is **never
auto-applied**. Design: ``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AdvisoryRule(BaseModel):
    """A suggested policy rule (advisory — never auto-applied)."""

    case_id: str
    rule: str
    rationale: str
    applied: bool = False


class WhatIfResult(BaseModel):
    """The what-if replay of an advisory rule."""

    case_id: str
    rule: str
    before: str
    after: str
    closes: bool


def suggest_rule(case_id: str, *, attack_class: str, rationale: str) -> AdvisoryRule:
    """Emit an advisory rule for a confirmed miss (advisory, not applied)."""
    return AdvisoryRule(
        case_id=case_id,
        rule=f"deny {attack_class}",
        rationale=rationale,
        applied=False,
    )


def what_if(rule: AdvisoryRule, *, before: str, after: str) -> WhatIfResult:
    """Replay the rule: it closes the miss when the outcome becomes ``blocked``."""
    return WhatIfResult(
        case_id=rule.case_id,
        rule=rule.rule,
        before=before,
        after=after,
        closes=before != "blocked" and after == "blocked",
    )


def propose_pr(rule: AdvisoryRule, replay: WhatIfResult) -> dict[str, Any]:
    """Build a reviewed-PR payload for the advisory rule (never auto-applied)."""
    return {
        "title": f"policy: {rule.rule} (closes {rule.case_id})",
        "body": (
            "Advisory rule proposed for human review — never auto-applied.\n\n"
            f"- case: {rule.case_id}\n"
            f"- rule: {rule.rule}\n"
            f"- rationale: {rule.rationale}\n"
            f"- what-if: {replay.before} -> {replay.after} (closes={replay.closes})\n"
        ),
        "auto_applied": False,
    }
