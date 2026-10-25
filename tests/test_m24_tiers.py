"""M24 24.1 — attacker tiers, F85 (RED → GREEN).

T0 static · T1 repeated (k∈{1,5,10,25}, seeded) · T2 documented-pattern
mutation · T3 stub deferred, RoE-gated, local-only. Results carry tier + k +
effort.
"""

from __future__ import annotations

import pytest

from agentdrill.attacker import (
    K_VALUES,
    TIERS,
    TierError,
    TierLabel,
    label_tier,
    t3_deferred,
)


def test_tier_label_carries_tier_k_effort() -> None:
    label = label_tier("T1", k=5)
    assert isinstance(label, TierLabel)
    assert label.tier == "T1"
    assert label.k == 5
    assert label.effort == "repeated"


def test_t1_k_values() -> None:
    assert set(K_VALUES) == {1, 5, 10, 25}


def test_tier_effort_labels() -> None:
    assert label_tier("T0").effort == "static"
    assert label_tier("T2").effort == "mutation"
    assert TIERS == ("T0", "T1", "T2", "T3")


def test_t3_is_deferred_and_roe_gated() -> None:
    label = label_tier("T3")
    assert label.effort == "deferred"
    assert t3_deferred() is True


def test_unknown_tier_fails_loudly() -> None:
    with pytest.raises(TierError, match="T9"):
        label_tier("T9")
