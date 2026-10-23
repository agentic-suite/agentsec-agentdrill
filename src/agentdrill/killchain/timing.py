"""Repeated trials → per-stage percentiles (M12 12.3).

≥5 trials per kill-time case → **p50/p95/max** per stage segment and total.
Means are never published alone (DD-27). Design: ``docs/design/killchain.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentdrill.killchain.model import KILL_CHAIN_STAGES, KillChainTimeline

#: The stage segments a duration is measured over.
SEGMENTS: tuple[tuple[str, str], ...] = tuple(
    (KILL_CHAIN_STAGES[i], KILL_CHAIN_STAGES[i + 1]) for i in range(len(KILL_CHAIN_STAGES) - 1)
)

#: Minimum trials required to publish a kill-time number.
MIN_TRIALS = 5


class InsufficientTrialsError(ValueError):
    """Raised when a kill-time number is published from fewer than 5 trials."""


class StagePercentiles(BaseModel):
    """p50/p95/max of one stage segment (or the total) across trials."""

    stage: str
    n: int
    p50: float
    p95: float
    max: float


class TimingReport(BaseModel):
    """Per-stage and total percentiles for a case's kill-time trials."""

    case_id: str
    trials: int
    segments: list[StagePercentiles] = Field(default_factory=list)
    total: StagePercentiles


def require_trials(n: int, *, min_trials: int = MIN_TRIALS) -> None:
    """Require at least ``min_trials`` trials.

    Raises:
        InsufficientTrialsError: Too few trials to publish a number.
    """
    if n < min_trials:
        raise InsufficientTrialsError(f"a kill-time number requires ≥{min_trials} trials, got {n}")


def _percentile(sorted_values: list[float], q: float) -> float:
    """Nearest-rank percentile of a sorted list."""
    if not sorted_values:
        return 0.0
    index = min(len(sorted_values) - 1, max(0, int(q * len(sorted_values))))
    return sorted_values[index]


def _percentiles(stage: str, values: list[float]) -> StagePercentiles:
    ordered = sorted(values)
    return StagePercentiles(
        stage=stage,
        n=len(ordered),
        p50=_percentile(ordered, 0.5),
        p95=_percentile(ordered, 0.95),
        max=ordered[-1] if ordered else 0.0,
    )


def stage_durations(timeline: KillChainTimeline) -> dict[str, float]:
    """The duration of each segment whose two stages are both present."""
    durations: dict[str, float] = {}
    for start, end in SEGMENTS:
        t_start = timeline.stages.get(start)
        t_end = timeline.stages.get(end)
        if t_start is not None and t_end is not None:
            durations[f"{start}->{end}"] = t_end - t_start
    return durations


def total_duration(timeline: KillChainTimeline) -> float | None:
    """``attack_start`` → the last present stage, or ``None`` if not measurable."""
    start = timeline.stages.get("attack_start")
    if start is None:
        return None
    end: float | None = None
    for stage in KILL_CHAIN_STAGES[1:]:
        value = timeline.stages.get(stage)
        if value is not None:
            end = value
    return None if end is None else end - start


def compute_timing(
    case_id: str,
    timelines: Sequence[KillChainTimeline],
    *,
    min_trials: int = MIN_TRIALS,
    require_min: bool = True,
) -> TimingReport:
    """Compute per-segment and total percentiles over ``timelines``.

    Raises:
        InsufficientTrialsError: Fewer than ``min_trials`` trials (unless
            ``require_min`` is False).
    """
    if require_min:
        require_trials(len(timelines), min_trials=min_trials)

    segment_values: dict[str, list[float]] = {}
    totals: list[float] = []
    for timeline in timelines:
        for name, value in stage_durations(timeline).items():
            segment_values.setdefault(name, []).append(value)
        total = total_duration(timeline)
        if total is not None:
            totals.append(total)

    segments = [
        _percentiles(f"{start}->{end}", segment_values.get(f"{start}->{end}", []))
        for start, end in SEGMENTS
    ]
    return TimingReport(
        case_id=case_id,
        trials=len(timelines),
        segments=segments,
        total=_percentiles("total", totals),
    )
