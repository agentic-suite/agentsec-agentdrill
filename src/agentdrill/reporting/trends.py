"""Trend store (M10 10.8, F23).

Per-defense-class deltas across releases, and a one-call "what got worse"
query. Design: ``docs/design/reporting.md``.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel


class ClassTrend(BaseModel):
    """A defense class's rate change between two releases."""

    klass: str
    previous: float
    current: float
    delta: float


class TrendStore:
    """Record per-release defense-class rates and query their trend."""

    def __init__(self) -> None:
        self._series: list[tuple[str, dict[str, float]]] = []

    def record(self, release: str, rates: Mapping[str, float]) -> None:
        """Record (or replace) a release's per-defense-class rates."""
        entry = (release, dict(rates))
        for index, (name, _) in enumerate(self._series):
            if name == release:
                self._series[index] = entry
                return
        self._series.append(entry)

    @property
    def releases(self) -> list[str]:
        """The recorded release names, in order."""
        return [name for name, _ in self._series]

    def deltas(self, klass: str) -> list[ClassTrend]:
        """Per-consecutive-release deltas for ``klass`` (empty if absent)."""
        series: list[ClassTrend] = []
        for (_, previous), (_, current) in zip(self._series, self._series[1:], strict=False):
            if klass in previous and klass in current:
                series.append(
                    ClassTrend(
                        klass=klass,
                        previous=previous[klass],
                        current=current[klass],
                        delta=current[klass] - previous[klass],
                    )
                )
        return series

    def what_got_worse(self) -> list[ClassTrend]:
        """Classes whose rate dropped between the two latest releases.

        Answers the "what got worse" query in one call; sorted worst-first.
        """
        if len(self._series) < 2:
            return []
        previous = self._series[-2][1]
        current = self._series[-1][1]
        worse = [
            ClassTrend(
                klass=klass,
                previous=previous[klass],
                current=current[klass],
                delta=current[klass] - previous[klass],
            )
            for klass in current
            if klass in previous and current[klass] < previous[klass]
        ]
        return sorted(worse, key=lambda t: t.delta)
