"""M10 10.7 — traces per row, F56 (RED → GREEN).

Every benchmark cell links its full trajectory + evidence in one hop.
"""

from __future__ import annotations

import pytest

from agentdrill.models.artifact import TrajectoryStep
from agentdrill.models.evidence import Evidence
from agentdrill.reporting import ReportRow, Trace, TraceNotFoundError, TraceStore


def _trace(case_id: str, ref: str | None = None) -> Trace:
    return Trace(
        case_id=case_id,
        trace_ref=ref,
        trajectory=[TrajectoryStep(type="tool_call", tool="shell")],
        evidence=[Evidence(event="policy-fired", summary="rule matched")],
    )


def test_cell_resolves_to_its_trajectory_and_evidence() -> None:
    store = TraceStore()
    store.add(_trace("c1", "t:c1"))
    row = ReportRow(case_id="c1", outcome="blocked", trace_ref="t:c1")
    trace = store.resolve(row)
    assert isinstance(trace, Trace)
    assert trace.trajectory[0].tool == "shell"
    assert trace.evidence[0].event == "policy-fired"


def test_resolve_falls_back_to_case_id() -> None:
    store = TraceStore()
    store.add(_trace("c9"))
    row = ReportRow(case_id="c9", outcome="missed")
    assert store.resolve(row).case_id == "c9"


def test_missing_trace_fails_loudly() -> None:
    store = TraceStore()
    row = ReportRow(case_id="nope", outcome="missed")
    with pytest.raises(TraceNotFoundError):
        store.resolve(row)


def test_trace_links_one_hop_from_a_report_row() -> None:
    store = TraceStore()
    store.add(_trace("c2", "run-1/c2"))
    row = ReportRow(case_id="c2", outcome="blocked", trace_ref="run-1/c2")
    # one hop: row.trace_ref -> trace.trajectory + trace.evidence
    assert store.resolve(row).trajectory
