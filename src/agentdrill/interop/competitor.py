"""Competitor honest-coverage benchmark (M17 17.6, R12).

Run packs against third-party stacks and publish an honest-coverage table whose
rows are reproducible via the PR-submission path (F57). Design:
``docs/prd/03-landscape.md``.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, Field

from agentdrill.oracles.engine import OutcomeSplit


class CompetitorRow(BaseModel):
    """One third-party stack's honest-coverage row."""

    stack: str
    pack_ref: str
    outcome: OutcomeSplit = Field(default_factory=OutcomeSplit)
    seeds: list[int] = Field(default_factory=list)


class CompetitorTable(BaseModel):
    """The honest-coverage table across third-party stacks."""

    rows: list[CompetitorRow] = Field(default_factory=list)


def competitor_row(
    *, stack: str, pack_ref: str, outcome: OutcomeSplit, seeds: Sequence[int]
) -> CompetitorRow:
    """Build one competitor row."""
    return CompetitorRow(stack=stack, pack_ref=pack_ref, outcome=outcome, seeds=sorted(seeds))


def build_table(rows: Sequence[CompetitorRow]) -> CompetitorTable:
    """Build a competitor table (sorted by stack)."""
    return CompetitorTable(rows=sorted(rows, key=lambda r: r.stack))


def export_table(table: CompetitorTable, dest: str | Path) -> Path:
    """Write the competitor table for PR submission."""
    directory = Path(dest)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "competitor-table.json"
    path.write_text(table.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def reproduces(expected: CompetitorTable, actual: CompetitorTable) -> bool:
    """Whether ``actual`` reproduces ``expected``'s rows (numbers + seeds)."""
    expected_by_stack = {row.stack: row for row in expected.rows}
    actual_by_stack = {row.stack: row for row in actual.rows}
    if expected_by_stack.keys() != actual_by_stack.keys():
        return False
    for stack, wanted in expected_by_stack.items():
        got = actual_by_stack[stack]
        if wanted.pack_ref != got.pack_ref:
            return False
        if sorted(wanted.seeds) != sorted(got.seeds):
            return False
        if wanted.outcome.model_dump() != got.outcome.model_dump():
            return False
    return True
