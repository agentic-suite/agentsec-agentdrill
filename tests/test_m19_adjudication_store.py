"""M19 19.5 — human adjudication layer, F83 (RED → GREEN).

Every HITL verdict is stored as labeled data (feeds the corpus + future
deterministic oracles); the human-adjudication coverage stat is published.
"""

from __future__ import annotations

from agentdrill.credibility import (
    AdjudicationStore,
    HitlVerdict,
    adjudication_coverage,
)


def test_hitl_verdicts_are_stored_as_labeled_data() -> None:
    store = AdjudicationStore()
    store.record(HitlVerdict(case_id="c1", verdict="blocked", reviewer="r1"))
    store.record(HitlVerdict(case_id="c2", verdict="missed", reviewer="r2"))
    labels = store.labels()
    assert labels == {"c1": "blocked", "c2": "missed"}
    assert len(store.labeled()) == 2


def test_coverage_stat_published() -> None:
    store = AdjudicationStore()
    store.record(HitlVerdict(case_id="c1", verdict="blocked", reviewer="r1"))
    store.record(HitlVerdict(case_id="c2", verdict="missed", reviewer="r2"))
    assert adjudication_coverage(store, total=4) == 0.5


def test_coverage_is_one_when_everything_is_adjudicated() -> None:
    store = AdjudicationStore()
    store.record(HitlVerdict(case_id="c1", verdict="blocked", reviewer="r"))
    assert adjudication_coverage(store, total=1) == 1.0
