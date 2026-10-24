"""Human adjudication layer (M19 19.5, F83).

Every HITL verdict is stored as **labeled data** (it feeds the calibration
corpus and future deterministic oracles); the **human-adjudication coverage**
stat is published. Design: ``docs/prd/23-oracle-credibility.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HitlVerdict(BaseModel):
    """A human (HITL) verdict for one case."""

    case_id: str
    verdict: str
    reviewer: str


class AdjudicationStore(BaseModel):
    """The store of human-labeled verdicts."""

    verdicts: list[HitlVerdict] = Field(default_factory=list)

    def record(self, verdict: HitlVerdict) -> None:
        """Record a human verdict (replacing any prior verdict for the case)."""
        self.verdicts = [v for v in self.verdicts if v.case_id != verdict.case_id]
        self.verdicts.append(verdict)

    def labeled(self) -> list[HitlVerdict]:
        """The stored labeled verdicts."""
        return list(self.verdicts)

    def labels(self) -> dict[str, str]:
        """The case → human label mapping (feeds the corpus)."""
        return {verdict.case_id: verdict.verdict for verdict in self.verdicts}


def adjudication_coverage(store: AdjudicationStore, *, total: int) -> float:
    """The human-adjudication coverage stat: labeled / total."""
    if total <= 0:
        return 0.0
    return len(store.verdicts) / total
