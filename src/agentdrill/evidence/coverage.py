"""Coverage reconciliation (M7 work item 7.5, F26).

Consume the agentwatch inventory (``ReconSnapshot``) and report exercised vs.
unexercised surfaces. ``gap:unexplained`` counts unexercised surfaces with no
explanation; the goal is zero (design/evidence-integration.md).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.recon import ReconSnapshot


class CoverageReport(BaseModel):
    """Exercised vs. unexercised surface coverage for a run."""

    total: int
    exercised: int
    unexercised: list[str] = Field(default_factory=list)
    #: ``gap:unexplained`` — unexercised surfaces with no explanation.
    unexplained: int = 0

    @property
    def gap_unexplained(self) -> int:
        return self.unexplained


def all_surfaces(snapshot: ReconSnapshot) -> set[str]:
    """Every surface the snapshot exposes (tools + MCP servers + capabilities)."""
    return set(snapshot.tools) | set(snapshot.mcp_servers) | set(snapshot.capabilities)


def coverage_report(
    snapshot: ReconSnapshot,
    exercised: set[str],
    explained: set[str] | None = None,
) -> CoverageReport:
    """Build a coverage report; ``unexplained = (all - exercised) - explained``."""
    explained = explained or set()
    surfaces = all_surfaces(snapshot)
    covered = surfaces & exercised
    unexercised = sorted(surfaces - covered)
    unexplained = sorted((surfaces - covered) - explained)
    return CoverageReport(
        total=len(surfaces),
        exercised=len(covered),
        unexercised=unexercised,
        unexplained=len(unexplained),
    )
