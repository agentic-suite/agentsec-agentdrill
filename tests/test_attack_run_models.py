"""M3 3.1 — run models + artifact: full JSON round-trip (RED → GREEN).

`Run` is the pack-level index (`.agentdrill/runs/<run_id>/run.json`);
`CaseArtifact` is the per-case artifact (`artifacts/<case_id>.json`). Design:
docs/design/runner.md (which calls these `Run` / `RunArtifact`).
"""

from __future__ import annotations

import json

from agentdrill.models.artifact import (
    Cost,
    RunOutput,
    RunTimestamps,
    TrajectoryStep,
)
from agentdrill.models.attack_run import CaseArtifact, Run

STEPS = [
    TrajectoryStep(type="tool_call", tool="shell", args={"cmd": "drop database prod"}),
    TrajectoryStep(type="tool_result", tool="shell", result={"denied": True}),
    TrajectoryStep(type="note", content="policy fired"),
    TrajectoryStep(type="response", content="blocked"),
]


def _ts(duration_ms: int = 0) -> RunTimestamps:
    return RunTimestamps(
        start="2026-01-01T00:00:00Z", end="2026-01-01T00:00:02Z", duration_ms=duration_ms
    )


def test_case_artifact_full_roundtrip() -> None:
    artifact = CaseArtifact(
        id="run-1::replit-destructive-command",
        case_id="replit-destructive-command",
        timestamps=_ts(2000),
        output=RunOutput(final="blocked", structured={"denied": True}),
        trajectory=STEPS,
        cost=Cost(input_tokens=10, output_tokens=5, total_tokens=15, cost_usd=0.001),
        status="completed",
    )
    restored = CaseArtifact.model_validate(json.loads(artifact.model_dump_json()))
    assert restored == artifact
    assert restored.case_id == "replit-destructive-command"
    assert [s.type for s in restored.trajectory] == [
        "tool_call",
        "tool_result",
        "note",
        "response",
    ]


def test_case_artifact_status_values() -> None:
    for status in ("completed", "timeout", "error", "aborted"):
        a = CaseArtifact(
            id="x",
            case_id="c",
            timestamps=RunTimestamps(start="s", end="e", duration_ms=0),
            status=status,  # type: ignore[arg-type]
        )
        assert a.status == status


def test_case_artifact_defaults() -> None:
    a = CaseArtifact(
        id="x",
        case_id="c",
        timestamps=RunTimestamps(start="s", end="e", duration_ms=0),
    )
    assert a.status == "completed"
    assert a.trajectory == []
    assert a.cost == Cost()
    assert a.error is None


def test_case_artifact_error_carries_message() -> None:
    a = CaseArtifact(
        id="x",
        case_id="c",
        timestamps=RunTimestamps(start="s", end="e", duration_ms=0),
        status="error",
        error="Traceback: boom",
    )
    assert a.status == "error"
    assert "boom" in (a.error or "")


def test_run_full_roundtrip() -> None:
    run = Run(
        run_id="run-1",
        pack_ref="incidents-core@1.0.0+abc123",
        target={"type": "policyweave-output"},
        driver={"type": "subprocess"},
        timestamps=_ts(5000),
        case_order=["a", "b", "c"],
    )
    restored = Run.model_validate(json.loads(run.model_dump_json()))
    assert restored == run
    assert restored.pack_ref == "incidents-core@1.0.0+abc123"
    assert restored.case_order == ["a", "b", "c"]
