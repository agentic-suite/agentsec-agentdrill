"""M24 24.3 — pressure curves + claim scope, F86 (RED → GREEN).

Curves (ASR vs k / budget); an auto claim-scope statement; a `brittle` label
(T0-hold / T2-break).
"""

from __future__ import annotations

from agentdrill.attacker import PressureCurve, claim_scope, pressure_curve


def test_pressure_curve_has_points_and_scope() -> None:
    curve = pressure_curve(
        "c1",
        asr_by_k={1: 0.1, 5: 0.3, 10: 0.6},
        t0_holds=True,
        t2_breaks=True,
    )
    assert isinstance(curve, PressureCurve)
    assert curve.points == [(1, 0.1), (5, 0.3), (10, 0.6)]
    assert curve.claim_scope
    assert curve.brittle is True


def test_brittle_when_t0_holds_and_t2_breaks() -> None:
    assert pressure_curve("c1", asr_by_k={1: 0.0}, t0_holds=True, t2_breaks=True).brittle


def test_not_brittle_when_t2_holds() -> None:
    assert not pressure_curve("c1", asr_by_k={1: 0.0}, t0_holds=True, t2_breaks=False).brittle


def test_claim_scope_statement_names_k_and_brittleness() -> None:
    curve = pressure_curve("c1", asr_by_k={1: 0.1, 5: 0.4}, t0_holds=True, t2_breaks=True)
    scope = claim_scope(curve)
    assert "k" in scope.lower()
    assert "brittle" in scope.lower()
