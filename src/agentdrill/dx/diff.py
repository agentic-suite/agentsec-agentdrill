"""Pack diff & coverage delta (M20 20.1, F67).

``pack diff <a> <b>`` reports the case delta (added/removed/changed) and the
coverage delta by tag. Design: ``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.models.attack_pack import AttackPack


class PackDiff(BaseModel):
    """The delta between two pack versions."""

    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    changed: list[str] = Field(default_factory=list)
    coverage_delta: dict[str, int] = Field(default_factory=dict)


def _case_hash(case: Any) -> str:
    canonical = json.dumps(case.model_dump(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _tag_counts(pack: AttackPack) -> Counter[str]:
    counts: Counter[str] = Counter()
    for case in pack.cases:
        counts.update(case.tags)
    return counts


def diff_packs(a: AttackPack, b: AttackPack) -> PackDiff:
    """Diff two packs: case delta + coverage (tag) delta."""
    a_ids = {case.id: case for case in a.cases}
    b_ids = {case.id: case for case in b.cases}

    added = sorted(set(b_ids) - set(a_ids))
    removed = sorted(set(a_ids) - set(b_ids))
    changed = sorted(
        case_id
        for case_id in set(a_ids) & set(b_ids)
        if _case_hash(a_ids[case_id]) != _case_hash(b_ids[case_id])
    )

    a_tags = _tag_counts(a)
    b_tags = _tag_counts(b)
    coverage_delta = {
        tag: b_tags.get(tag, 0) - a_tags.get(tag, 0)
        for tag in set(a_tags) | set(b_tags)
        if b_tags.get(tag, 0) - a_tags.get(tag, 0) != 0
    }

    return PackDiff(added=added, removed=removed, changed=changed, coverage_delta=coverage_delta)
