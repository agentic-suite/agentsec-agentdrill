"""Attacker-strength & bypass-search package (M24).

Attacker tiers (24.1), `Hold@k`/`ASR@k` metrics (24.2), pressure curves + claim
scope (24.3), the `Hold@k` gate (24.4), the route-family library (24.5), the
bounded search engine (24.6), minimization + promotion (24.7) and the coverage
report (24.8). Design: ``docs/prd/25-attacker-strength-and-pressure.md`` and
``docs/prd/28-policy-bypass-search.md``.
"""

from agentdrill.attacker.metrics import HoldAtK, hold_at_k
from agentdrill.attacker.pressure import PressureCurve, claim_scope, pressure_curve
from agentdrill.attacker.tiers import (
    K_VALUES,
    TIERS,
    TierError,
    TierLabel,
    label_tier,
    t3_deferred,
)

__all__ = [
    "K_VALUES",
    "TIERS",
    "HoldAtK",
    "PressureCurve",
    "TierError",
    "TierLabel",
    "claim_scope",
    "hold_at_k",
    "label_tier",
    "pressure_curve",
    "t3_deferred",
]
