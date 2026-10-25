"""Kill-chain stage model + per-case timeline (M12 12.1).

The shared stage model — attack_start → delivered → detected → decided →
halted → revoked → ceased. Each case records per-stage timestamps (seconds
since ``attack_start``); a stage that never happened is ``null`` **and
flagged**, never inferred or back-filled. Design:
``docs/design/killchain.md``.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, Field

#: The kill-chain stages, in order.
KILL_CHAIN_STAGES: tuple[str, ...] = (
    "attack_start",
    "delivered",
    "detected",
    "decided",
    "halted",
    "revoked",
    "ceased",
)


class KillChainTimeline(BaseModel):
    """One case's kill-chain timeline.

    Attributes:
        case_id: The case the timeline belongs to.
        stages: Stage name → seconds since ``attack_start`` (or ``None``).
        missing: Stages that never happened (flagged, never inferred).
    """

    case_id: str
    stages: dict[str, float | None] = Field(default_factory=dict)
    missing: list[str] = Field(default_factory=list)

    @property
    def flagged(self) -> bool:
        """Whether any stage is missing (the timeline carries a flag)."""
        return bool(self.missing)


def build_timeline(case_id: str, timestamps: Mapping[str, float | None]) -> KillChainTimeline:
    """Build a timeline, filling absent stages with ``None`` + a flag.

    Raises:
        ValueError: An unknown stage name is supplied.
    """
    for name in timestamps:
        if name not in KILL_CHAIN_STAGES:
            raise ValueError(f"unknown stage: {name!r}; known: {list(KILL_CHAIN_STAGES)}")
    stages: dict[str, float | None] = {name: timestamps.get(name) for name in KILL_CHAIN_STAGES}
    missing = [name for name in KILL_CHAIN_STAGES if stages[name] is None]
    return KillChainTimeline(case_id=case_id, stages=stages, missing=missing)
