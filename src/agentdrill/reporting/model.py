"""Report data model (M10).

A :class:`Report` is the renderable summary of one run: the outcome split, a
row per case (with severity, rationale and a trace reference), and the
limitations register. Later M10 items extend it (multi-seed stats, heat-map,
trends). Design: ``docs/design/reporting.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.oracles.engine import OutcomeSplit


class ReportRow(BaseModel):
    """One case's row in a report."""

    case_id: str
    outcome: str
    tags: list[str] = Field(default_factory=list)
    pack: str | None = None
    severity: str | None = None
    rationale: str = ""
    trace_ref: str | None = None


class Report(BaseModel):
    """A renderable report for one run.

    Attributes:
        title: Human title of the report.
        pack_ref: ``name@version+hash`` the report binds to.
        generated: ISO-8601 generation timestamp.
        outcome: The blocked/missed/degraded split.
        rows: One row per case.
        limitations: The honest "what this does NOT test" notes.
    """

    title: str
    pack_ref: str
    generated: str
    outcome: OutcomeSplit = Field(default_factory=OutcomeSplit)
    rows: list[ReportRow] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
