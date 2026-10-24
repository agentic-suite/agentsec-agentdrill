"""Pressure curves + claim scope (M24 24.3, F86).

A pressure curve (ASR vs k / budget) with an **auto claim-scope** statement and
a ``brittle`` label (a defense that holds at T0 but breaks under T2 mutation).
Design: ``docs/prd/25-attacker-strength-and-pressure.md``.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, Field


class PressureCurve(BaseModel):
    """A case's pressure curve and claim scope."""

    case_id: str
    points: list[tuple[int, float]] = Field(default_factory=list)
    claim_scope: str = ""
    brittle: bool = False


def pressure_curve(
    case_id: str,
    *,
    asr_by_k: Mapping[int, float],
    t0_holds: bool,
    t2_breaks: bool,
) -> PressureCurve:
    """Build a pressure curve; ``brittle`` when T0 holds but T2 breaks."""
    points = sorted((int(k), float(v)) for k, v in asr_by_k.items())
    brittle = t0_holds and t2_breaks
    ks = ", ".join(str(k) for k, _ in points)
    scope = f"claim scope: {case_id} measured at k in {{{ks}}}; " + (
        "brittle (holds at T0, breaks under documented-pattern mutation)"
        if brittle
        else "holds across the measured tiers"
    )
    return PressureCurve(case_id=case_id, points=points, claim_scope=scope, brittle=brittle)


def claim_scope(curve: PressureCurve) -> str:
    """The claim-scope statement for a curve."""
    return curve.claim_scope
