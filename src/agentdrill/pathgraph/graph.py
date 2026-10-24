"""Capability / attack-path graph (M27 27.4, F93).

Build a graph of the deployed system from inventory — agents, tools, MCP
servers, credentials/scopes, data sources, egress routes, memory stores,
sub-agents, approval settings and instruction files — and enumerate the paths
from an **untrusted input** to a **crown jewel**, each with AIVSS-compatible
**severity factors that are never aggregated**. An unknown inventory kind is a
visible blind spot, never dropped. Design:
``docs/design/backtest-path-intake.md``; PRD 31 (R67).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from agentdrill.integrations.importer import InventoryItem

#: The documented capability node vocabulary (plus ``unknown`` for blind spots).
NODE_KINDS: tuple[str, ...] = (
    "agent",
    "tool",
    "mcp_server",
    "credential",
    "data_source",
    "egress_route",
    "memory_store",
    "sub_agent",
    "approval_setting",
    "instruction_file",
    "unknown",
)

#: A path severity level.
SeverityLevel = Literal["critical", "high", "medium", "low"]

#: The default cap on enumerated paths.
DEFAULT_PATH_LIMIT = 100


class GraphError(ValueError):
    """Raised when a graph cannot be built (a dangling reference)."""


class Node(BaseModel):
    """One capability node."""

    id: str
    kind: str
    name: str
    crown_jewel: bool = False
    untrusted_input: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict)

    @property
    def unknown(self) -> bool:
        """Whether this node's kind is outside the documented vocabulary."""
        return self.kind not in NODE_KINDS or self.kind == "unknown"


class Edge(BaseModel):
    """A directed capability edge."""

    source: str
    target: str
    kind: str = "reaches"


class PathSeverity(BaseModel):
    """AIVSS-compatible severity *factors* for one path (never aggregated)."""

    factors: list[str] = Field(default_factory=list)
    level: SeverityLevel
    rationale: str = ""


class ReachablePath(BaseModel):
    """A path from an untrusted input to a crown jewel, with its severity."""

    node_ids: list[str]
    severity: PathSeverity


class CapabilityGraph(BaseModel):
    """The capability graph: nodes, edges, and graph queries."""

    nodes: dict[str, Node] = Field(default_factory=dict)
    edges: list[Edge] = Field(default_factory=list)

    def unknown_nodes(self) -> list[str]:
        """Sorted ids of nodes whose kind is unknown (blind spots)."""
        return sorted(node.id for node in self.nodes.values() if node.unknown)

    def successors(self, node_id: str) -> list[str]:
        """The ids reachable in one hop from ``node_id`` (in edge order)."""
        return [edge.target for edge in self.edges if edge.source == node_id]

    def crown_jewels(self) -> list[str]:
        """Sorted ids of crown-jewel nodes."""
        return sorted(node.id for node in self.nodes.values() if node.crown_jewel)


def build_graph(
    items: Sequence[InventoryItem],
    *,
    edges: Sequence[tuple[str, ...]] = (),
    crown_jewels: Sequence[str] = (),
    untrusted: Sequence[str] = (),
) -> CapabilityGraph:
    """Build a :class:`CapabilityGraph` from inventory items and edges.

    Raises:
        GraphError: An edge, crown jewel or untrusted entry references a node
            that is not in the inventory.
    """
    nodes: dict[str, Node] = {}
    for item in items:
        kind = item.kind if item.kind in NODE_KINDS else "unknown"
        nodes[item.id] = Node(id=item.id, kind=kind, name=item.name)

    for node_id in [*crown_jewels, *untrusted]:
        if node_id not in nodes:
            raise GraphError(f"reference to a node not in inventory: {node_id!r}")
    for node_id in crown_jewels:
        nodes[node_id].crown_jewel = True
    for node_id in untrusted:
        nodes[node_id].untrusted_input = True

    built: list[Edge] = []
    for edge in edges:
        source, target = edge[0], edge[1]
        edge_kind = edge[2] if len(edge) > 2 else "reaches"
        for node_id in (source, target):
            if node_id not in nodes:
                raise GraphError(f"edge references a node not in inventory: {node_id!r}")
        built.append(Edge(source=source, target=target, kind=edge_kind))
    return CapabilityGraph(nodes=nodes, edges=built)


def path_severity(graph: CapabilityGraph, node_ids: list[str]) -> PathSeverity:
    """AIVSS-compatible factors for a path (a rubric, never an org-wide score)."""
    factors: list[str] = []
    if graph.nodes[node_ids[0]].untrusted_input:
        factors.append("untrusted_input")
    kinds = {graph.nodes[node_id].kind for node_id in node_ids}
    if kinds & {"tool", "mcp_server"}:
        factors.append("invokes_tool")
    if kinds & {"credential"}:
        factors.append("credential_scope")
    if graph.nodes[node_ids[-1]].crown_jewel:
        factors.append("reaches_crown_jewel")
    egress = kinds & {"egress_route"} or any(
        graph.nodes[successor].kind == "egress_route"
        for node_id in node_ids
        for successor in graph.successors(node_id)
    )
    if egress:
        factors.append("external_egress")

    if "reaches_crown_jewel" in factors and egress:
        level: SeverityLevel = "critical"
    elif "reaches_crown_jewel" in factors:
        level = "high"
    elif "invokes_tool" in factors:
        level = "medium"
    else:
        level = "low"
    return PathSeverity(factors=factors, level=level, rationale=" + ".join(factors))


def reachable_paths(
    graph: CapabilityGraph, *, limit: int = DEFAULT_PATH_LIMIT
) -> list[ReachablePath]:
    """Enumerate simple paths from an untrusted input to a crown jewel.

    Reachability is a **hypothesis** until a drill proves the path (27.5); here
    it is only structural.
    """
    jewels = set(graph.crown_jewels())
    paths: list[ReachablePath] = []

    def walk(path: list[str]) -> None:
        if len(paths) >= limit:
            return
        current = path[-1]
        if current in jewels and len(path) > 1:
            paths.append(ReachablePath(node_ids=path, severity=path_severity(graph, path)))
            return
        for successor in graph.successors(current):
            if successor in path:
                continue
            walk([*path, successor])

    for start in sorted(
        node.id for node in graph.nodes.values() if node.untrusted_input
    ):
        walk([start])
    return paths
