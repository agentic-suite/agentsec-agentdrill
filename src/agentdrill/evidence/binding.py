"""Evidence binding (M7 work item 7.2).

Bind every result to the agentwatch evidence behind it. A result with no bound
evidence yields an explicit :class:`~agentdrill.oracles.base.Finding` of type
``evidence_gap`` — never a silent pass (design/evidence-integration.md rule 2).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.evidence.schema import AgentWatchEvent
from agentdrill.oracles.base import Finding


class EvidenceBinding(BaseModel):
    """The evidence refs a case's result references."""

    case_id: str
    refs: list[str] = Field(default_factory=list)
    #: True when no evidence was found for the case (an explicit gap).
    gap: bool = False


def bind_case(case_id: str, events: list[AgentWatchEvent]) -> EvidenceBinding:
    """Collect the evidence refs belonging to ``case_id``."""
    refs: list[str] = []
    for index, event in enumerate(events):
        if event.case_id == case_id:
            refs.append(event.ref or f"{event.event}:{index}")
    return EvidenceBinding(case_id=case_id, refs=refs, gap=len(refs) == 0)


def bind_all(case_ids: list[str], events: list[AgentWatchEvent]) -> list[EvidenceBinding]:
    """Bind each case id in ``case_ids`` to its evidence."""
    return [bind_case(case_id, events) for case_id in case_ids]


def evidence_gap(binding: EvidenceBinding) -> Finding | None:
    """An ``evidence_gap`` finding when the binding has no evidence, else ``None``."""
    if not binding.gap:
        return None
    return Finding(
        case_id=binding.case_id,
        type="evidence_gap",
        severity="warning",
        detail="no agentwatch evidence bound to this result",
    )
