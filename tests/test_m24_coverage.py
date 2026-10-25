"""M24 24.8 — search coverage report, F89 (RED → GREEN).

Per-effect tried/blocked/bypassed/untried; a diff-aware subset for rule
changes. Coverage is explicit; the rest is `untried`.
"""

from __future__ import annotations

from agentdrill.attacker import CoverageReport, EffectCoverage, build_coverage, diff_aware

EFFECTS = ["write-forbidden-file", "read-secret", "exec-shell"]


def test_coverage_lists_tried_blocked_bypassed_untried() -> None:
    report = build_coverage(
        EFFECTS,
        statuses={"write-forbidden-file": "blocked", "read-secret": "bypassed"},
    )
    assert isinstance(report, CoverageReport)
    by_effect = {row.effect: row for row in report.effects}
    assert isinstance(by_effect["write-forbidden-file"], EffectCoverage)
    assert by_effect["write-forbidden-file"].blocked == 1
    assert by_effect["read-secret"].bypassed == 1
    assert by_effect["exec-shell"].untried == 1


def test_untried_effects_are_explicit() -> None:
    report = build_coverage(EFFECTS, statuses={})
    assert all(row.untried == 1 for row in report.effects)


def test_diff_aware_subset() -> None:
    report = build_coverage(EFFECTS, statuses={})
    subset = diff_aware(report, changed_effects=["read-secret"])
    assert subset == ["read-secret"]
