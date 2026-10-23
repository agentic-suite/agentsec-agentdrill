"""Coverage heat-map (M10 10.6, F53).

A pack/tag x control matrix: each cell is ``blocked`` / ``partial`` /
``missed`` / ``untested``, with a delta against a previous release.
Design: ``docs/design/reporting.md``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from agentdrill.reporting.model import Report

#: A heat-map cell's status.
CellStatus = Literal["blocked", "partial", "missed", "untested"]


class HeatMapCell(BaseModel):
    """One (pack, control) cell of the heat-map."""

    pack: str
    control: str
    status: CellStatus
    blocked: int = 0
    other: int = 0


class HeatMapDelta(BaseModel):
    """A status change for one (pack, control) cell between two releases."""

    pack: str
    control: str
    previous: CellStatus
    current: CellStatus


class HeatMap(BaseModel):
    """The coverage heat-map: one cell per (pack, control)."""

    cells: list[HeatMapCell] = Field(default_factory=list)

    def status(self, pack: str, control: str) -> CellStatus:
        """The status of a cell, or ``untested`` when the cell is absent."""
        for cell in self.cells:
            if cell.pack == pack and cell.control == control:
                return cell.status
        return "untested"

    def delta(self, other: HeatMap) -> list[HeatMapDelta]:
        """Per-cell status changes from ``self`` (before) to ``other`` (after)."""
        keys = sorted(
            {(c.pack, c.control) for c in self.cells} | {(c.pack, c.control) for c in other.cells}
        )
        changes: list[HeatMapDelta] = []
        for pack, control in keys:
            previous = self.status(pack, control)
            current = other.status(pack, control)
            if previous != current:
                changes.append(
                    HeatMapDelta(pack=pack, control=control, previous=previous, current=current)
                )
        return changes


def build_heatmap(report: Report) -> HeatMap:
    """Build the heat-map from a report's rows (pack x tag)."""
    aggregates: dict[tuple[str, str], list[str]] = {}
    for row in report.rows:
        pack = row.pack or report.pack_ref
        for tag in row.tags:
            aggregates.setdefault((pack, tag), []).append(row.outcome)

    cells: list[HeatMapCell] = []
    for pack, control in sorted(aggregates):
        outcomes = aggregates[(pack, control)]
        blocked = sum(1 for outcome in outcomes if outcome == "blocked")
        total = len(outcomes)
        if blocked == total:
            status: CellStatus = "blocked"
        elif blocked == 0:
            status = "missed"
        else:
            status = "partial"
        cells.append(
            HeatMapCell(
                pack=pack,
                control=control,
                status=status,
                blocked=blocked,
                other=total - blocked,
            )
        )
    return HeatMap(cells=cells)
