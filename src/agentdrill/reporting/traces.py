"""Traces per row (M10 10.7, F56).

Every benchmark cell links its full trajectory + evidence in one hop: a
:class:`TraceStore` resolves a report row to its :class:`Trace`.
Design: ``docs/design/reporting.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.models.artifact import TrajectoryStep
from agentdrill.models.evidence import Evidence
from agentdrill.reporting.model import ReportRow


class TraceNotFoundError(KeyError):
    """Raised when a report row has no resolvable trace."""


class Trace(BaseModel):
    """A case's full trajectory + evidence, keyed by ``trace_ref`` or case id."""

    case_id: str
    trace_ref: str | None = None
    trajectory: list[TrajectoryStep] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)

    @property
    def key(self) -> str:
        """The lookup key: the trace ref when present, else the case id."""
        return self.trace_ref or self.case_id


class TraceStore:
    """Resolve a report cell to its trajectory + evidence in one hop."""

    def __init__(self) -> None:
        self._traces: dict[str, Trace] = {}

    def add(self, trace: Trace) -> None:
        """Register ``trace`` under its key (``trace_ref`` or case id)."""
        self._traces[trace.key] = trace

    def resolve(self, row: ReportRow) -> Trace:
        """Return the trace for ``row`` (loudly if absent)."""
        key = row.trace_ref or row.case_id
        trace = self._traces.get(key)
        if trace is None:
            raise TraceNotFoundError(f"no trace for {key!r} (case {row.case_id!r})")
        return trace

    def __contains__(self, key: str) -> bool:
        return key in self._traces
