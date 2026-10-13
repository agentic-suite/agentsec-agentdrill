"""M7 7.4 — evidence in artifacts (RED → GREEN).

Evidence refs are written into `artifacts/<case_id>.json`, so a result
reconstructs its evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentdrill.evidence.artifacts import attach_evidence, evidence_for
from agentdrill.evidence.schema import read_events
from agentdrill.models.artifact import RunTimestamps
from agentdrill.models.attack_run import CaseArtifact

EVENTS: list[dict[str, Any]] = [
    {"event": "denied", "ref": "evt-1", "case_id": "c1", "detail": "policy denied"},
    {"event": "policy-fired", "ref": "evt-2", "case_id": "c2"},
]


def _artifact() -> CaseArtifact:
    return CaseArtifact(
        id="run-1::c1",
        case_id="c1",
        timestamps=RunTimestamps(
            start="2026-01-01T00:00:00Z", end="2026-01-01T00:00:01Z", duration_ms=1000
        ),
    )


def test_evidence_for_case() -> None:
    evidence = evidence_for("c1", read_events(EVENTS))
    assert [e.ref for e in evidence] == ["evt-1"]
    assert evidence[0].event == "denied"
    assert evidence[0].summary == "policy denied"


def test_attach_evidence() -> None:
    artifact = attach_evidence(_artifact(), read_events(EVENTS))
    assert [e.ref for e in artifact.evidence] == ["evt-1"]


def test_artifact_roundtrip_keeps_evidence() -> None:
    artifact = attach_evidence(_artifact(), read_events(EVENTS))
    restored = CaseArtifact.model_validate(json.loads(artifact.model_dump_json()))
    assert restored == artifact
    assert restored.evidence[0].event == "denied"


def test_artifact_file_reconstructs_evidence(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "run-1"
    (run_dir / "artifacts").mkdir(parents=True)
    artifact = attach_evidence(_artifact(), read_events(EVENTS))
    (run_dir / "artifacts" / "c1.json").write_text(
        artifact.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    restored = CaseArtifact.model_validate(
        json.loads((run_dir / "artifacts" / "c1.json").read_text(encoding="utf-8"))
    )
    assert [e.ref for e in restored.evidence] == ["evt-1"]
