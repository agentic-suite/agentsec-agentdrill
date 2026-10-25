"""Scheduled drills (M11 11.8, F71).

Cadence runs for out-of-PR drift (vendor model, MCP rug-pull, marketplace
skill): a due schedule produces a finding file labeled with its **trigger**.
Design: ``docs/design/ci-gate.md`` §Change-driven execution.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel, Field

#: Cadence name → period in seconds.
_CADENCE_SECONDS: dict[str, float] = {
    "hourly": 3600.0,
    "daily": 86400.0,
    "weekly": 604800.0,
}


class DrillSchedule(BaseModel):
    """A cadence definition for a drift drill."""

    name: str
    cadence: str
    packs: list[str] = Field(default_factory=list)
    #: The drift trigger this drill watches (e.g. vendor-model, mcp-rug-pull).
    trigger: str = ""


class ScheduledFinding(BaseModel):
    """A finding produced by a scheduled drill."""

    drill: str
    trigger: str
    generated: str
    packs: list[str] = Field(default_factory=list)


def is_due(schedule: DrillSchedule, *, now: float, last_run: float | None) -> bool:
    """Whether ``schedule`` is due at ``now`` given its ``last_run``.

    Raises:
        ValueError: The cadence is unknown.
    """
    period = _CADENCE_SECONDS.get(schedule.cadence)
    if period is None:
        raise ValueError(
            f"unknown cadence: {schedule.cadence!r}; known: {sorted(_CADENCE_SECONDS)}"
        )
    if last_run is None:
        return True
    return now - last_run >= period


def due_drills(
    schedules: Sequence[DrillSchedule],
    *,
    now: float,
    last_runs: Mapping[str, float] | None = None,
) -> list[DrillSchedule]:
    """The schedules that are due at ``now`` (by name in ``last_runs``)."""
    runs = last_runs or {}
    return [
        schedule
        for schedule in schedules
        if is_due(schedule, now=now, last_run=runs.get(schedule.name))
    ]


def record_finding(schedule: DrillSchedule, dest_dir: str | Path, *, generated: str) -> Path:
    """Write a scheduled finding labeled with its trigger; returns the path."""
    finding = ScheduledFinding(
        drill=schedule.name,
        trigger=schedule.trigger,
        generated=generated,
        packs=list(schedule.packs),
    )
    directory = Path(dest_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"finding-{schedule.trigger}-{schedule.name}.json"
    path.write_text(finding.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path
