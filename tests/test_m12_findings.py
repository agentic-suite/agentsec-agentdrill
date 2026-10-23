"""M12 12.4 — kill-chain timeline + typed findings (RED → GREEN).

Findings `kill_slow`, `detect_gap`, `decision_gap`, `halt_gap`, `cease_gap` —
so a stage bottleneck is named, and "revoked but still acting" is first-class.
"""

from __future__ import annotations

from agentdrill.killchain import KillChainFinding, analyze_timeline, build_timeline


def _timeline(**stages: float) -> object:
    return build_timeline("c1", stages)


def test_detect_gap_when_delivery_to_detection_dominates() -> None:
    timeline = _timeline(
        attack_start=0.0,
        delivered=0.0,
        detected=2.0,
        decided=2.1,
        halted=2.2,
        revoked=2.3,
        ceased=2.4,
    )
    findings = analyze_timeline(timeline)
    assert [f.type for f in findings] == ["detect_gap"]
    assert isinstance(findings[0], KillChainFinding)


def test_decision_gap() -> None:
    timeline = _timeline(
        attack_start=0.0,
        delivered=0.0,
        detected=0.1,
        decided=2.0,
        halted=2.1,
        revoked=2.2,
        ceased=2.3,
    )
    assert [f.type for f in analyze_timeline(timeline)] == ["decision_gap"]


def test_halt_gap() -> None:
    timeline = _timeline(
        attack_start=0.0,
        delivered=0.0,
        detected=0.1,
        decided=0.2,
        halted=2.0,
        revoked=2.1,
        ceased=2.2,
    )
    assert [f.type for f in analyze_timeline(timeline)] == ["halt_gap"]


def test_cease_gap_when_revoked_but_never_ceased() -> None:
    timeline = _timeline(
        attack_start=0.0, delivered=0.0, detected=0.1, decided=0.2, halted=0.3, revoked=0.4
    )
    findings = analyze_timeline(timeline)
    assert [f.type for f in findings] == ["cease_gap"]
    assert findings[0].severity == "critical"


def test_cease_gap_when_revoke_to_cease_dominates() -> None:
    timeline = _timeline(
        attack_start=0.0,
        delivered=0.0,
        detected=0.1,
        decided=0.2,
        halted=0.3,
        revoked=0.4,
        ceased=3.0,
    )
    assert [f.type for f in analyze_timeline(timeline)] == ["cease_gap"]


def test_kill_slow_when_total_exceeds_the_budget() -> None:
    timeline = _timeline(
        attack_start=0.0,
        delivered=0.1,
        detected=0.2,
        decided=0.3,
        halted=0.4,
        revoked=0.5,
        ceased=9.0,
    )
    findings = analyze_timeline(timeline, max_seconds=5.0)
    assert "kill_slow" in [f.type for f in findings]


def test_a_clean_timeline_has_no_findings() -> None:
    timeline = _timeline(
        attack_start=0.0,
        delivered=0.1,
        detected=0.2,
        decided=0.3,
        halted=0.4,
        revoked=0.45,
        ceased=0.5,
    )
    assert analyze_timeline(timeline) == []
