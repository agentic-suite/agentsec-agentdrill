"""Run models for attack packs (M3 work item 3.1).

``Run`` is the pack-level index written to ``.agentdrill/runs/<run_id>/run.json``.
``CaseArtifact`` is the per-case artifact written to ``artifacts/<case_id>.json``.
``docs/design/runner.md`` calls the two ``Run`` / ``RunArtifact``; ``CaseArtifact``
avoids clashing with the ported scenario ``RunArtifact`` (which carries
``scenario_id``).

``TrajectoryStep`` / ``Cost`` / ``RunOutput`` / ``RunTimestamps`` are reused from
:mod:`agentdrill.models.artifact` — single source of truth, not duplicated.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from agentdrill.models.artifact import Cost, RunOutput, RunTimestamps, TrajectoryStep

#: Terminal status of a case run.
RunStatus = Literal["completed", "timeout", "error", "aborted"]


class CaseArtifact(BaseModel):
    """Normalized result of running one attack case (design: ``RunArtifact``).

    Round-trips losslessly through JSON so artifacts re-load identically across
    processes and CI runs.
    """

    id: str
    case_id: str
    timestamps: RunTimestamps
    output: RunOutput = Field(default_factory=RunOutput)
    trajectory: list[TrajectoryStep] = Field(default_factory=list)
    cost: Cost = Field(default_factory=Cost)
    status: RunStatus = "completed"
    error: str | None = None


class Run(BaseModel):
    """Pack-level index for one execution of a pack (``run.json``).

    Binds the run to ``pack_ref`` (``name@version+hash``) and records the target,
    driver, timing and case order so results are reproducible and attributable.
    """

    run_id: str
    pack_ref: str
    target: dict[str, Any] = Field(default_factory=dict)
    driver: dict[str, Any] = Field(default_factory=dict)
    timestamps: RunTimestamps
    case_order: list[str] = Field(default_factory=list)
