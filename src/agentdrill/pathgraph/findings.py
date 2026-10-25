"""Structural findings + path status (M27 27.5, F93).

Detect the structural weaknesses that matter for blast radius — the lethal
**trifecta** (untrusted input + crown-jewel data + unrestricted egress),
over-scoped tokens, unrestricted egress, auto-approve-plus-shell, writable
instruction files, shared memory and identity inheritance — **bind** the cases
that should prove each critical path broken, classify a path's status, and alert
when a config change opens a **new path**. Design:
``docs/design/backtest-path-intake.md``; PRD 31 (R67).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

from agentdrill.pathgraph.graph import CapabilityGraph, PathSeverity, ReachablePath, reachable_paths

#: The structural-finding vocabulary.
StructuralKind = Literal[
    "trifecta_present",
    "over_scoped_token",
    "unrestricted_egress",
    "auto_approve_plus_shell",
    "writable_instruction_file",
    "shared_memory",
    "identity_inheritance",
]

#: The status of a path (a hypothesis until a drill proves it).
PathStatus = Literal["proven_broken", "open_missed", "unproven", "accepted"]

#: Substrings that mark a tool as a command/shell surface.
_SHELL_HINTS = ("shell", "bash", "sh", "exec", "command", "cmd")

#: The attribute-flagged structural findings: (node kind, attribute, finding kind).
_SIMPLE_FINDINGS: tuple[tuple[str, str, StructuralKind], ...] = (
    ("credential", "over_scoped", "over_scoped_token"),
    ("egress_route", "unrestricted", "unrestricted_egress"),
    ("instruction_file", "writable", "writable_instruction_file"),
    ("memory_store", "shared", "shared_memory"),
    ("sub_agent", "inherits_identity", "identity_inheritance"),
)


class PathError(ValueError):
    """Raised for an inconsistent path binding or an unbound critical path."""


class StructuralFinding(BaseModel):
    """One structural weakness in the capability graph."""

    kind: StructuralKind
    node_ids: list[str] = Field(default_factory=list)
    detail: str = ""


class Alert(BaseModel):
    """A drift alert (a new path opened by a config change)."""

    message: str
    path: list[str] = Field(default_factory=list)


class BoundPath(BaseModel):
    """A reachable path bound to the cases that should prove it broken."""

    node_ids: list[str]
    severity: PathSeverity
    case_ids: list[str] = Field(default_factory=list)
    status: PathStatus = "unproven"


def _flagged(graph: CapabilityGraph, kind: str, attribute: str) -> list[str]:
    """Sorted node ids of ``kind`` whose ``attribute`` is truthy."""
    return sorted(
        node.id
        for node in graph.nodes.values()
        if node.kind == kind and node.attributes.get(attribute) is True
    )


def _is_shell(name: str) -> bool:
    lower = name.lower()
    return any(hint in lower for hint in _SHELL_HINTS)


def detect_findings(graph: CapabilityGraph) -> list[StructuralFinding]:
    """Detect every structural finding present in ``graph``."""
    findings: list[StructuralFinding] = []

    for path in reachable_paths(graph):
        factors = set(path.severity.factors)
        if {"reaches_crown_jewel", "external_egress"} <= factors:
            findings.append(
                StructuralFinding(
                    kind="trifecta_present",
                    node_ids=path.node_ids,
                    detail="untrusted input reaches crown-jewel data with external egress",
                )
            )

    for node_kind, attribute, finding_kind in _SIMPLE_FINDINGS:
        for node_id in _flagged(graph, node_kind, attribute):
            findings.append(
                StructuralFinding(kind=finding_kind, node_ids=[node_id], detail=finding_kind)
            )
    for node_id in _flagged(graph, "approval_setting", "auto_approve"):
        shell = [
            successor
            for successor in graph.successors(node_id)
            if _is_shell(graph.nodes[successor].name)
        ]
        if shell:
            findings.append(
                StructuralFinding(
                    kind="auto_approve_plus_shell",
                    node_ids=[node_id, *shell],
                    detail="auto-approve reaches a shell-capable tool",
                )
            )
    return findings


def bind_path(
    path: ReachablePath,
    *,
    case_ids: Sequence[str] = (),
    proven: bool = False,
    missed: bool = False,
    accepted: bool = False,
) -> BoundPath:
    """Bind a path to the cases that should prove it broken and set its status.

    Raises:
        PathError: More than one exclusive status flag is set.
    """
    if sum((proven, missed, accepted)) > 1:
        raise PathError("a path has exactly one status; proven/missed/accepted are exclusive")
    if accepted:
        status: PathStatus = "accepted"
    elif proven:
        status = "proven_broken"
    elif missed:
        status = "open_missed"
    else:
        status = "unproven"
    return BoundPath(
        node_ids=path.node_ids,
        severity=path.severity,
        case_ids=list(case_ids),
        status=status,
    )


def require_critical_bound(paths: Sequence[BoundPath]) -> None:
    """Fail loudly unless every critical path is bound to at least one case.

    Raises:
        PathError: A critical path has no bound case (100 % coverage required).
    """
    unbound = [p for p in paths if p.severity.level == "critical" and not p.case_ids]
    if unbound:
        offender = " -> ".join(unbound[0].node_ids)
        raise PathError(f"critical path is not bound to any case: {offender}")


def new_paths(previous: CapabilityGraph, current: CapabilityGraph) -> list[ReachablePath]:
    """The paths present in ``current`` but not in ``previous``."""
    before = {tuple(path.node_ids) for path in reachable_paths(previous)}
    return [path for path in reachable_paths(current) if tuple(path.node_ids) not in before]


def new_path_alerts(paths: Sequence[ReachablePath]) -> list[Alert]:
    """One alert per newly-opened path (a config change that needs a drill)."""
    return [
        Alert(
            message=f"new attack path to {path.node_ids[-1]}: {' -> '.join(path.node_ids)}",
            path=path.node_ids,
        )
        for path in paths
    ]
