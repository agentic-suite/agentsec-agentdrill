"""Golden expected results + golden-lock (M9 9.1).

A :class:`Golden` is a **preregistered, locked** expected outcome per pack
version, bound to ``pack@version+hash``. A candidate result differing from its
golden is **flagged** with a re-pin note — never silently corrected (DD-28).
Design: ``docs/design/comparison.md``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.oracles.base import Outcome


class GoldenCase(BaseModel):
    """One case's locked expected outcome in a golden."""

    case_id: str
    outcome: Outcome
    tags: list[str] = Field(default_factory=list)


class Golden(BaseModel):
    """A preregistered, locked golden expected result for one pack version.

    Attributes:
        pack_ref: ``name@version+hash`` the golden is bound to.
        created: ISO-8601 creation timestamp.
        locked: Always True — a golden is never silently overwritten.
        pins: The pins the golden was recorded under (M8 8.3).
        cases: The per-case expected outcomes.
    """

    pack_ref: str
    created: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    locked: bool = True
    pins: dict[str, Any] = Field(default_factory=dict)
    cases: list[GoldenCase] = Field(default_factory=list)

    @classmethod
    def from_outcomes(
        cls,
        pack_ref: str,
        outcomes: Mapping[str, Outcome],
        *,
        tags: Mapping[str, list[str]] | None = None,
        pins: Mapping[str, Any] | None = None,
    ) -> Golden:
        """Preregister a golden from observed outcomes (sorted by case id)."""
        tag_map = tags or {}
        cases = [
            GoldenCase(case_id=cid, outcome=outcome, tags=list(tag_map.get(cid, [])))
            for cid, outcome in sorted(outcomes.items())
        ]
        return cls(pack_ref=pack_ref, pins=dict(pins or {}), cases=cases)

    def expected(self) -> dict[str, Outcome]:
        """The golden's expected outcome per case id."""
        return {case.case_id: case.outcome for case in self.cases}


@dataclass(frozen=True)
class GoldenChange:
    """A case whose candidate outcome differs from its golden."""

    case_id: str
    golden_outcome: str
    candidate_outcome: str


@dataclass(frozen=True)
class GoldenCheck:
    """The result of checking a candidate against a golden.

    Attributes:
        changed: Every case whose outcome differs from the golden.
        note: The declaration (re-pin note) explaining the change, if any.
    """

    changed: list[GoldenChange]
    note: str | None = None

    @property
    def ok(self) -> bool:
        """Whether the candidate matched its golden (a change is never ok)."""
        return not self.changed


def check_golden(
    golden: Golden,
    candidate: Mapping[str, Outcome],
    *,
    declared_repin: str | None = None,
) -> GoldenCheck:
    """Flag every case whose ``candidate`` outcome differs from ``golden``.

    The golden is never mutated. A change is always flagged (``ok`` is False);
    ``declared_repin`` only annotates the declaration, it never hides a change.
    """
    changes: list[GoldenChange] = []
    for case in golden.cases:
        observed = candidate.get(case.case_id)
        if observed is not None and observed != case.outcome:
            changes.append(
                GoldenChange(
                    case_id=case.case_id,
                    golden_outcome=case.outcome,
                    candidate_outcome=observed,
                )
            )
    if not changes:
        return GoldenCheck(changed=[])
    detail = "; ".join(f"{c.case_id}: {c.golden_outcome} -> {c.candidate_outcome}" for c in changes)
    note = f"golden change flagged: {detail}"
    if declared_repin:
        note = f"{note} ({declared_repin})"
    return GoldenCheck(changed=changes, note=note)
