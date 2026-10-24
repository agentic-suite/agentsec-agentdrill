"""M17 17.6 — competitor benchmark, R12 (RED → GREEN).

Run packs against third-party stacks; an honest-coverage table whose rows are
reproducible via the PR-submission path (F57).
"""

from __future__ import annotations

import json
from pathlib import Path

from agentdrill.interop import (
    CompetitorRow,
    CompetitorTable,
    build_table,
    competitor_row,
    export_table,
    reproduces,
)
from agentdrill.oracles.engine import OutcomeSplit


def _row(stack: str = "acme-guard", blocked: int = 3, missed: int = 2) -> CompetitorRow:
    return competitor_row(
        stack=stack,
        pack_ref="p@1.0.0+abc",
        outcome=OutcomeSplit(blocked=blocked, missed=missed, degraded=0),
        seeds=[1, 2, 3],
    )


def test_row_carries_its_outcome_split() -> None:
    row = _row()
    assert row.stack == "acme-guard"
    assert row.outcome.blocked == 3
    assert row.seeds == [1, 2, 3]


def test_a_third_party_row_is_reproducible() -> None:
    expected = build_table([_row()])
    same = build_table([_row()])
    assert isinstance(expected, CompetitorTable)
    assert reproduces(expected, same) is True


def test_a_number_change_is_detected() -> None:
    expected = build_table([_row(blocked=3)])
    changed = build_table([_row(blocked=1)])
    assert reproduces(expected, changed) is False


def test_table_export_writes_a_file(tmp_path: Path) -> None:
    path = export_table(build_table([_row()]), tmp_path / "competitors")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["rows"][0]["stack"] == "acme-guard"
