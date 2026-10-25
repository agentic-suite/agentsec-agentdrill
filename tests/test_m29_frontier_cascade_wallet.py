"""M29 29.6 — frontier classes 7 (denial-of-wallet) & 6 (multi-agent cascade).

Class 7 (LLM10) keeps runaway cost within the ceiling (+5 % tolerance); class 6
(ASI07/08/10) bounds an agent handoff to **≤ 1 hop**.
"""

from __future__ import annotations

import pytest

from agentdrill.frontier import (
    FRONTIER_CLASSES,
    FrontierError,
    require_bounded_handoff,
    require_cost_within_ceiling,
)


def test_registry_knows_classes_six_and_seven() -> None:
    assert FRONTIER_CLASSES[6].asi == ["ASI07", "ASI08", "ASI10"]
    assert "cascade" in FRONTIER_CLASSES[6].name.lower()
    assert FRONTIER_CLASSES[7].asi == ["LLM10"]
    assert "exhaustion" in FRONTIER_CLASSES[7].name.lower()


def test_cost_stays_within_the_ceiling_plus_five_percent() -> None:
    require_cost_within_ceiling(cost_usd=100.0, ceiling=100.0)
    require_cost_within_ceiling(cost_usd=104.9, ceiling=100.0)  # ≤ 105 %
    with pytest.raises(FrontierError):
        require_cost_within_ceiling(cost_usd=106.0, ceiling=100.0)


def test_handoff_depth_is_bounded_to_one_hop() -> None:
    require_bounded_handoff(depth=0)
    require_bounded_handoff(depth=1)
    with pytest.raises(FrontierError):
        require_bounded_handoff(depth=2)


def test_tolerance_is_configurable() -> None:
    with pytest.raises(FrontierError):
        require_cost_within_ceiling(cost_usd=101.0, ceiling=100.0, tolerance=0.0)
