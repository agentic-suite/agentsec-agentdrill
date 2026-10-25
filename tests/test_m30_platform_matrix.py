"""M30 30.3 - compatibility levels + matrix (RED -> GREEN).

Levels L0-L4 with **evidence** required at L2+ (measured, never asserted);
per-surface rows; the prioritization model; the **reference-harness policy** (>=2
open-source harnesses at L3+); and the single published number, **AWC**.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agentdrill.platform import (
    LEVEL_LABELS,
    LEVELS,
    PRIORITY_WEIGHTS,
    PlatformEntry,
    PlatformError,
    awc,
    priority_score,
    rank_entries,
    require_awc,
    require_levels,
    require_reference_harnesses,
)


def _entry(**over: object) -> PlatformEntry:
    base = dict(
        name="harness-x",
        level="L3",
        surface="cli",
        tier=1,
        open_source=True,
        adoption=5,
        attack_surface=4,
        driveability=3,
        reproducibility=2,
        strategic=1,
        evidence=["canary run #1"],
    )
    base.update(over)
    return PlatformEntry.model_validate(base)


def test_levels_and_labels() -> None:
    assert LEVELS == ("L0", "L1", "L2", "L3", "L4")
    assert LEVEL_LABELS["L3"] == "observed"
    assert sum(PRIORITY_WEIGHTS.values()) == pytest.approx(1.0)


def test_priority_score_and_ranking() -> None:
    high = _entry(name="high", adoption=5, attack_surface=5, driveability=5)
    low = _entry(name="low", adoption=1, attack_surface=1, driveability=1)
    assert priority_score(high) > priority_score(low)
    assert [e.name for e in rank_entries([low, high])] == ["high", "low"]


def test_evidence_is_required_from_l2() -> None:
    require_levels([_entry(level="L1", evidence=[])])
    with pytest.raises(PlatformError):
        require_levels([_entry(level="L2", evidence=[])])
    with pytest.raises(ValidationError):
        _entry(level="L9")  # an unknown level cannot even be constructed


def test_awc_is_the_adoption_weighted_coverage() -> None:
    entries = [
        _entry(name="a", adoption=5, level="L4", evidence=["e"]),
        _entry(name="b", adoption=5, level="L2", evidence=["e"]),
    ]
    assert awc(entries) == pytest.approx(0.75)
    require_awc(entries)  # ≥0.60

    weak = [
        _entry(name="a", adoption=5, level="L2", evidence=["e"]),
        _entry(name="b", adoption=5, level="L0", open_source=False),
    ]
    assert awc(weak) == pytest.approx(0.25)
    with pytest.raises(PlatformError):
        require_awc(weak)


def test_reference_harness_policy_needs_two_open_at_l3() -> None:
    good = [
        _entry(name="a", level="L3", open_source=True),
        _entry(name="b", level="L4", open_source=True),
    ]
    require_reference_harnesses(good)
    with pytest.raises(PlatformError):
        require_reference_harnesses([good[0]])
    with pytest.raises(PlatformError):
        require_reference_harnesses([_entry(name="c", level="L3", open_source=False)])


def test_empty_matrix_has_full_coverage_by_definition() -> None:
    assert awc([]) == 1.0
