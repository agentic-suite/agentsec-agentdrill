"""M18 18.9 — closes-the-loop policy suggestion, F21 (RED → GREEN).

A confirmed miss emits an **advisory** rule + what-if replay; the fix is
proposed as a reviewed PR and **never auto-applied**.
"""

from __future__ import annotations

from agentdrill.lifecycle import (
    AdvisoryRule,
    WhatIfResult,
    propose_pr,
    suggest_rule,
    what_if,
)


def test_confirmed_miss_emits_an_advisory_rule() -> None:
    rule = suggest_rule("c1", attack_class="destructive", rationale="rm -rf reached the shell")
    assert isinstance(rule, AdvisoryRule)
    assert rule.applied is False
    assert "destructive" in rule.rule


def test_what_if_replay_proves_the_rule_closes_the_miss() -> None:
    rule = suggest_rule("c1", attack_class="destructive", rationale="r")
    replay = what_if(rule, before="missed", after="blocked")
    assert isinstance(replay, WhatIfResult)
    assert replay.closes is True


def test_a_rule_that_does_not_close_is_reported() -> None:
    rule = suggest_rule("c1", attack_class="destructive", rationale="r")
    assert what_if(rule, before="missed", after="missed").closes is False


def test_the_fix_is_proposed_as_a_reviewed_pr() -> None:
    rule = suggest_rule("c1", attack_class="destructive", rationale="r")
    replay = what_if(rule, before="missed", after="blocked")
    pr = propose_pr(rule, replay)
    assert pr["title"]
    assert "reviewed" in pr["body"].lower() or "review" in pr["body"].lower()
    assert pr["auto_applied"] is False
