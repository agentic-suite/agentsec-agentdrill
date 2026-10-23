"""M11 11.8 — scheduled drills, F71 (RED → GREEN).

Cadence runs for out-of-PR drift (vendor model, MCP rug-pull, marketplace
skill): a due schedule produces a finding file labeled with its trigger.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdrill.ci import DrillSchedule, due_drills, is_due, record_finding


def _daily(trigger: str = "vendor-model") -> DrillSchedule:
    return DrillSchedule(name="drift", cadence="daily", packs=["p@1.0.0+aaa"], trigger=trigger)


def test_never_run_is_due() -> None:
    assert is_due(_daily(), now=1000.0, last_run=None) is True


def test_due_after_the_cadence() -> None:
    assert is_due(_daily(), now=86_400.0, last_run=0.0) is True
    assert is_due(_daily(), now=100.0, last_run=0.0) is False


def test_due_drills_filters_by_cadence() -> None:
    schedules = [
        _daily("vendor-model"),
        DrillSchedule(name="weekly", cadence="weekly", trigger="mcp-rug-pull"),
    ]
    due = due_drills(schedules, now=86_400.0, last_runs={"drift": 0.0, "weekly": 0.0})
    assert [d.trigger for d in due] == ["vendor-model"]


def test_unknown_cadence_fails_loudly() -> None:
    bad = DrillSchedule(name="x", cadence="fortnightly")
    with pytest.raises(ValueError, match="cadence"):
        is_due(bad, now=0.0, last_run=None)


def test_scheduled_finding_file_has_trigger_label(tmp_path: Path) -> None:
    path = record_finding(
        _daily("mcp-rug-pull"), tmp_path / "findings", generated="2026-10-23T00:00:00Z"
    )
    assert path.exists()
    assert "mcp-rug-pull" in path.name
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["trigger"] == "mcp-rug-pull"
    assert data["drill"] == "drift"
    assert data["packs"] == ["p@1.0.0+aaa"]


def test_schedule_cli_once_exits_cleanly() -> None:
    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main

    result = CliRunner().invoke(main, ["schedule", "--once", "--cadence", "daily"])
    assert result.exit_code == 0, result.output
    assert "due drill" in result.output
