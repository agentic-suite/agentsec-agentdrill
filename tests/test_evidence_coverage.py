"""M7 7.5 — coverage reconciliation (F26) (RED → GREEN).

Consume the agentwatch inventory and report exercised vs. unexercised surfaces;
`gap:unexplained` must reach zero.
"""

from __future__ import annotations

from agentdrill.evidence.coverage import CoverageReport, coverage_report
from agentdrill.recon import ReconSnapshot

SNAPSHOT = ReconSnapshot(
    tools=["shell", "query"],
    mcp_servers=["evil"],
    capabilities=["filesystem_write"],
    case_bindings={"c1": ["shell"]},
)


def test_all_surfaces_exercised() -> None:
    report = coverage_report(SNAPSHOT, exercised={"shell", "query", "evil", "filesystem_write"})
    assert isinstance(report, CoverageReport)
    assert report.exercised == 4
    assert report.unexercised == []
    assert report.unexplained == 0


def test_unexercised_surface_is_unexplained() -> None:
    report = coverage_report(SNAPSHOT, exercised={"shell"})
    assert report.unexercised == ["evil", "filesystem_write", "query"]
    assert report.unexplained == 3


def test_explained_surface_closes_the_gap() -> None:
    report = coverage_report(
        SNAPSHOT,
        exercised={"shell"},
        explained={"query", "evil", "filesystem_write"},
    )
    assert report.unexplained == 0
    assert report.unexercised == ["evil", "filesystem_write", "query"]


def test_gap_unexplained_property() -> None:
    report = coverage_report(SNAPSHOT, exercised={"shell", "query", "evil", "filesystem_write"})
    assert report.gap_unexplained == 0
