"""Fleet mode (M20 20.8, F45).

One pack across many stacks (opt-in, self-hosted); per-stack honest coverage
rollups with an outlier query (CUJ-18). Design:
``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentdrill.oracles.engine import OutcomeSplit


class StackResult(BaseModel):
    """One stack's outcome for a pack."""

    stack: str
    outcome: OutcomeSplit = Field(default_factory=OutcomeSplit)


class FleetRollup(BaseModel):
    """A pack's rollup across a fleet of stacks."""

    pack_ref: str
    stacks: list[StackResult] = Field(default_factory=list)
    mode: str = "self-hosted"
    opt_in: bool = True

    @property
    def total(self) -> OutcomeSplit:
        """The fleet-wide outcome split."""
        split = OutcomeSplit()
        for stack in self.stacks:
            split.blocked += stack.outcome.blocked
            split.missed += stack.outcome.missed
            split.degraded += stack.outcome.degraded
        return split

    def coverage(self) -> dict[str, float]:
        """Per-stack blocked coverage (blocked / total)."""
        coverage: dict[str, float] = {}
        for stack in self.stacks:
            total = stack.outcome.total
            coverage[stack.stack] = (
                stack.outcome.blocked / total if total else 0.0
            )
        return coverage

    def outliers(self, *, threshold: float) -> list[str]:
        """Stacks whose coverage is below ``threshold`` (sorted)."""
        return sorted(
            stack
            for stack, value in self.coverage().items()
            if value < threshold
        )


def build_fleet(pack_ref: str, stacks: Sequence[StackResult]) -> FleetRollup:
    """Build a fleet rollup (sorted by stack)."""
    return FleetRollup(
        pack_ref=pack_ref, stacks=sorted(stacks, key=lambda s: s.stack)
    )
