"""Evidence in run artifacts (M7 work item 7.4).

Bind agentwatch evidence refs into each case's artifact so a result reconstructs
its evidence (design/evidence-integration.md rule 4).
"""

from __future__ import annotations

from agentdrill.evidence.schema import AgentWatchEvent
from agentdrill.models.attack_run import CaseArtifact
from agentdrill.models.evidence import Evidence


def evidence_for(case_id: str, events: list[AgentWatchEvent]) -> list[Evidence]:
    """The typed evidence belonging to ``case_id``."""
    return [
        Evidence(event=event.event, ref=event.ref, summary=event.detail or "")
        for event in events
        if event.case_id == case_id
    ]


def attach_evidence(artifact: CaseArtifact, events: list[AgentWatchEvent]) -> CaseArtifact:
    """Bind the case's evidence into ``artifact`` (mutates and returns it)."""
    artifact.evidence = evidence_for(artifact.case_id, events)
    return artifact
