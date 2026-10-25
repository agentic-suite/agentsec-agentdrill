"""Neutral head-to-head (M25 25.4, F91).

The same pack, seeds, environment and twins across N defenses: `Hold@k`/`ASR@k`
with CIs, false-block on twins, cost/1k and latency, and fail-open/closed — with
**no composite score and no ranking**. Design:
``docs/prd/29-bring-your-own-defense.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.reporting import RateCI


class NeutralityError(ValueError):
    """Raised when a caller asks for a composite score or a ranking."""


class DefenseCell(BaseModel):
    """One defense's column in a neutral head-to-head."""

    defense: str
    config_digest: str
    hold_at_k: RateCI
    asr_at_k: RateCI
    false_block: float = 0.0
    cost_per_1k: float = 0.0
    latency_ms: float = 0.0
    fail_mode: str = "closed"


class HeadToHead(BaseModel):
    """A neutral head-to-head across defenses (no ranking)."""

    pack_ref: str
    seeds: list[int] = Field(default_factory=list)
    cells: list[DefenseCell] = Field(default_factory=list)
    composite_score: None = None


def build_head_to_head(pack_ref: str, *, seeds: list[int], cells: list[DefenseCell]) -> HeadToHead:
    """Build a head-to-head table sharing one pack and its seeds across defenses."""
    return HeadToHead(pack_ref=pack_ref, seeds=list(seeds), cells=list(cells))


def rank_defenses(head_to_head: HeadToHead) -> None:
    """Refuse to rank defenses — neutrality means no composite or ordering.

    Raises:
        NeutralityError: Always — a ranking is never produced.
    """
    raise NeutralityError(
        "neutral head-to-head produces no composite score or ranking; "
        "publish the per-defence cells (pack + seeds) and let the reader decide"
    )
