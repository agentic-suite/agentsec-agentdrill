"""M25 25.4 — neutral head-to-head, F91 (RED → GREEN).

Same pack/seeds/env/twins across N defenses: Hold@k/ASR@k+CI, false-block on
twins, $/1k + latency, fail-open/closed; **no composite/ranking**.
"""

from __future__ import annotations

import pytest

from agentdrill.byod import (
    DefenseCell,
    HeadToHead,
    NeutralityError,
    build_head_to_head,
    rank_defenses,
)
from agentdrill.reporting import RateCI


def _rate(metric: str, point: float) -> RateCI:
    return RateCI(
        metric=metric, point=point, low=point - 0.05, high=point + 0.05, n=5, seeds=[1, 2, 3]
    )


def _cell(defense: str) -> DefenseCell:
    return DefenseCell(
        defense=defense,
        config_digest="sha256:x",
        hold_at_k=_rate("hold_at_k", 0.9),
        asr_at_k=_rate("asr_at_k", 0.1),
        false_block=0.0,
        cost_per_1k=1.5,
        latency_ms=12.0,
        fail_mode="closed",
    )


def test_identical_input_across_defenses() -> None:
    h2h = build_head_to_head("p@1.0.0+abc", seeds=[1, 2, 3], cells=[_cell("a"), _cell("b")])
    assert isinstance(h2h, HeadToHead)
    assert h2h.pack_ref == "p@1.0.0+abc"
    assert h2h.seeds == [1, 2, 3]
    assert [c.defense for c in h2h.cells] == ["a", "b"]


def test_cells_carry_the_metrics() -> None:
    cell = _cell("a")
    assert cell.hold_at_k.point == 0.9
    assert cell.cost_per_1k == 1.5
    assert cell.fail_mode == "closed"


def test_there_is_no_composite_or_ranking() -> None:
    h2h = build_head_to_head("p", seeds=[1], cells=[_cell("a"), _cell("b")])
    assert h2h.composite_score is None
    with pytest.raises(NeutralityError, match="ranking"):
        rank_defenses(h2h)
