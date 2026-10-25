"""Attack comparison engine — per-case / per-tag / aggregate deltas (M9 9.2).

Compares a candidate run's outcomes against a **golden** (M9 9.1) at three
levels: per-case, per-tag and aggregate outcome-split. Direction ranks
``blocked`` > ``degraded`` > ``missed``, so a ``blocked → missed`` flip is a
regression. Design: ``docs/design/comparison.md``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, Field

from agentdrill.comparison.golden import Golden
from agentdrill.models.attack_pack import AttackPack
from agentdrill.oracles.base import Outcome
from agentdrill.oracles.engine import OutcomeSplit

#: Direction of a case change.
Direction = Literal["improved", "regressed", "unchanged", "new", "missing"]

#: Rank of each outcome from worst (0) to best (2); higher is a better defense.
_OUTCOME_RANK: dict[str, int] = {"missed": 0, "degraded": 1, "blocked": 2}


class CaseDelta(BaseModel):
    """One case's change between the golden and the candidate."""

    case_id: str
    golden_outcome: str | None
    candidate_outcome: str | None
    changed: bool
    direction: Direction


class TagDelta(BaseModel):
    """A tag's outcome-split change between the golden and the candidate."""

    tag: str
    golden: OutcomeSplit
    candidate: OutcomeSplit


class AggregateDelta(BaseModel):
    """The run-level outcome-split change and change counts."""

    golden: OutcomeSplit
    candidate: OutcomeSplit
    changed: int = 0
    regressed: int = 0
    improved: int = 0
    new: int = 0
    missing: int = 0


class AttackComparison(BaseModel):
    """The full comparison result: case, tag and aggregate deltas."""

    pack_ref: str
    case_deltas: list[CaseDelta] = Field(default_factory=list)
    tag_deltas: list[TagDelta] = Field(default_factory=list)
    aggregate: AggregateDelta


def _direction(
    golden_outcome: Outcome | None, candidate_outcome: Outcome | None
) -> tuple[bool, Direction]:
    """Classify a case change into ``changed`` + ``direction``."""
    if golden_outcome is None and candidate_outcome is None:
        return False, "unchanged"
    if golden_outcome is None:
        return True, "new"
    if candidate_outcome is None:
        return True, "missing"
    if golden_outcome == candidate_outcome:
        return False, "unchanged"
    if _OUTCOME_RANK[candidate_outcome] < _OUTCOME_RANK[golden_outcome]:
        return True, "regressed"
    return True, "improved"


def _split(outcomes: Mapping[str, Outcome]) -> OutcomeSplit:
    """Count ``{blocked, missed, degraded}`` across an outcome mapping."""
    split = OutcomeSplit()
    for outcome in outcomes.values():
        if outcome == "blocked":
            split.blocked += 1
        elif outcome == "missed":
            split.missed += 1
        else:
            split.degraded += 1
    return split


class AttackComparisonEngine:
    """Compute case/tag/aggregate deltas between a candidate and a golden.

    Args:
        pack: The attack pack; used to resolve each case's tags for the
            per-tag aggregation.
    """

    def __init__(self, pack: AttackPack) -> None:
        self._pack = pack
        self._tags = {case.id: list(case.tags) for case in pack.cases}

    def compare(self, golden: Golden, candidate: Mapping[str, Outcome]) -> AttackComparison:
        """Compare a candidate outcome mapping against ``golden``."""
        golden_expected = golden.expected()
        all_ids = sorted(set(golden_expected) | set(candidate))

        case_deltas: list[CaseDelta] = []
        for cid in all_ids:
            gold = golden_expected.get(cid)
            cand = candidate.get(cid)
            changed, direction = _direction(gold, cand)
            case_deltas.append(
                CaseDelta(
                    case_id=cid,
                    golden_outcome=gold,
                    candidate_outcome=cand,
                    changed=changed,
                    direction=direction,
                )
            )

        aggregate = AggregateDelta(
            golden=_split(golden_expected),
            candidate=_split(candidate),
            changed=sum(1 for d in case_deltas if d.changed),
            regressed=sum(1 for d in case_deltas if d.direction == "regressed"),
            improved=sum(1 for d in case_deltas if d.direction == "improved"),
            new=sum(1 for d in case_deltas if d.direction == "new"),
            missing=sum(1 for d in case_deltas if d.direction == "missing"),
        )

        return AttackComparison(
            pack_ref=golden.pack_ref,
            case_deltas=case_deltas,
            tag_deltas=self._tag_deltas(golden_expected, candidate),
            aggregate=aggregate,
        )

    def _tag_deltas(
        self, golden_expected: Mapping[str, Outcome], candidate: Mapping[str, Outcome]
    ) -> list[TagDelta]:
        """Aggregate golden/candidate outcomes per tag, sorted by tag."""
        golden_by_tag: dict[str, dict[str, Outcome]] = {}
        candidate_by_tag: dict[str, dict[str, Outcome]] = {}
        for cid, outcome in golden_expected.items():
            for tag in self._tags.get(cid, []):
                golden_by_tag.setdefault(tag, {})[cid] = outcome
        for cid, outcome in candidate.items():
            for tag in self._tags.get(cid, []):
                candidate_by_tag.setdefault(tag, {})[cid] = outcome

        return [
            TagDelta(
                tag=tag,
                golden=_split(golden_by_tag.get(tag, {})),
                candidate=_split(candidate_by_tag.get(tag, {})),
            )
            for tag in sorted(set(golden_by_tag) | set(candidate_by_tag))
        ]
