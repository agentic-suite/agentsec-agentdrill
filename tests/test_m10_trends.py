"""M10 10.8 — trend store, F23 (RED → GREEN).

Per-defense-class deltas across releases, and a one-call "what got worse"
query.
"""

from __future__ import annotations

from agentdrill.reporting import ClassTrend, TrendStore


def _store() -> TrendStore:
    store = TrendStore()
    store.record("r1", {"destructive": 1.0, "injection": 1.0})
    store.record("r2", {"destructive": 0.5, "injection": 1.0})
    store.record("r3", {"destructive": 0.75, "injection": 0.9})
    return store


def test_what_got_worse_across_the_latest_releases() -> None:
    worse = _store().what_got_worse()
    assert [t.klass for t in worse] == ["injection"]
    injection = worse[0]
    assert isinstance(injection, ClassTrend)
    assert injection.previous == 1.0
    assert injection.current == 0.9
    assert injection.delta < 0


def test_a_change_appears_in_deltas_but_improvement_is_not_worse() -> None:
    store = _store()
    # destructive improved 0.5 -> 0.75 (a delta, but not "worse")
    assert any(d.delta > 0 for d in store.deltas("destructive"))
    assert "destructive" not in [t.klass for t in store.what_got_worse()]


def test_improvement_is_not_reported_as_worse() -> None:
    store = TrendStore()
    store.record("r1", {"destructive": 0.5})
    store.record("r2", {"destructive": 1.0})
    assert store.what_got_worse() == []


def test_deltas_series_for_a_class() -> None:
    series = _store().deltas("destructive")
    assert [(d.previous, d.current) for d in series] == [(1.0, 0.5), (0.5, 0.75)]


def test_single_release_has_no_trend() -> None:
    store = TrendStore()
    store.record("r1", {"destructive": 0.5})
    assert store.what_got_worse() == []
    assert store.deltas("destructive") == []


def test_unknown_class_has_no_series() -> None:
    assert _store().deltas("telepathy") == []
