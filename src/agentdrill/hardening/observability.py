"""Self-observability (M22 22.6).

A shareable run summary (dimensions + outcome split + exit code) so one summary
answers "what happened". Design: ``docs/prd/13-non-functional-requirements.md``.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from pydantic import BaseModel, Field

from agentdrill.oracles.base import Verdict
from agentdrill.oracles.engine import OutcomeSplit, outcome_split


class RunSummary(BaseModel):
    """A shareable run summary."""

    run_id: str
    outcome: OutcomeSplit = Field(default_factory=OutcomeSplit)
    dimensions: dict[str, int] = Field(default_factory=dict)
    exit_code: int = 0

    def render(self) -> str:
        """Render the summary as text."""
        dims = ", ".join(f"{name}={count}" for name, count in sorted(self.dimensions.items()))
        return (
            f"run {self.run_id}: blocked {self.outcome.blocked}, "
            f"missed {self.outcome.missed}, degraded {self.outcome.degraded} | "
            f"dimensions: {dims} | exit {self.exit_code}\n"
        )


def build_summary(run_id: str, *, verdicts: Iterable[Verdict], exit_code: int) -> RunSummary:
    """Build a run summary from a run's verdicts."""
    collected = list(verdicts)
    dimensions: Counter[str] = Counter()
    for verdict in collected:
        dimensions.update(verdict.dimensions)
    return RunSummary(
        run_id=run_id,
        outcome=outcome_split(collected),
        dimensions=dict(dimensions),
        exit_code=exit_code,
    )
