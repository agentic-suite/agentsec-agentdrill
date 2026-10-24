"""M27 27.4 — capability / attack-path graph (RED → GREEN).

Build a capability graph from inventory (agents, tools, MCP servers,
credentials/scopes, data, egress, memory, sub-agents, approvals, instruction
files), keep unknown kinds as visible blind spots, and enumerate the reachable
paths from an untrusted input to a crown jewel with AIVSS-compatible severity
factors (never aggregated).
"""

from __future__ import annotations

import pytest

from agentdrill.integrations import InventoryItem
from agentdrill.pathgraph import (
    NODE_KINDS,
    CapabilityGraph,
    GraphError,
    ReachablePath,
    build_graph,
    path_severity,
    reachable_paths,
)


def _items() -> list[InventoryItem]:
    return [
        InventoryItem(id="agent:main", kind="agent", name="main"),
        InventoryItem(id="tool:fs", kind="tool", name="filesystem"),
        InventoryItem(id="mcp:evil", kind="mcp_server", name="evil-mcp"),
        InventoryItem(id="cred:aws", kind="credential", name="aws-key"),
        InventoryItem(id="data:secrets", kind="data_source", name="secrets"),
        InventoryItem(id="egress:web", kind="egress_route", name="web"),
        InventoryItem(id="mem:shared", kind="memory_store", name="shared-memory"),
        InventoryItem(id="sub:helper", kind="sub_agent", name="helper"),
        InventoryItem(id="approval:auto", kind="approval_setting", name="auto-approve"),
        InventoryItem(id="instr:agents", kind="instruction_file", name="AGENTS.md"),
        InventoryItem(id="widget:odd", kind="widget", name="odd"),  # unknown kind
    ]


def test_node_kinds_are_the_documented_vocabulary() -> None:
    assert "agent" in NODE_KINDS
    assert "instruction_file" in NODE_KINDS
    assert "unknown" in NODE_KINDS


def test_build_graph_types_nodes_and_keeps_blind_spots() -> None:
    graph = build_graph(_items())
    assert isinstance(graph, CapabilityGraph)
    assert graph.nodes["agent:main"].kind == "agent"
    assert graph.nodes["instr:agents"].kind == "instruction_file"
    # an unknown kind is a visible blind spot, never dropped
    assert graph.nodes["widget:odd"].kind == "unknown"
    assert graph.nodes["widget:odd"].unknown is True
    assert graph.unknown_nodes() == ["widget:odd"]


def test_dangling_edge_fails_loudly() -> None:
    with pytest.raises(GraphError):
        build_graph(_items(), edges=[("agent:main", "nope:missing")])
    with pytest.raises(GraphError):
        build_graph(_items(), crown_jewels=["nope:missing"])
    with pytest.raises(GraphError):
        build_graph(_items(), untrusted=["nope:missing"])


def test_reachable_paths_to_a_crown_jewel() -> None:
    graph = build_graph(
        _items(),
        edges=[
            ("agent:main", "mcp:evil"),
            ("mcp:evil", "tool:fs"),
            ("tool:fs", "data:secrets"),
            ("tool:fs", "egress:web"),
        ],
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
    )
    paths = reachable_paths(graph)
    assert paths
    assert all(isinstance(p, ReachablePath) for p in paths)
    node_paths = [p.node_ids for p in paths]
    assert ["agent:main", "mcp:evil", "tool:fs", "data:secrets"] in node_paths
    # the crown jewel itself must be reachable; severity is per-path, never aggregated
    severity = paths[0].severity
    assert "reaches_crown_jewel" in severity.factors
    assert severity.level in ("critical", "high", "medium", "low")


def test_no_route_means_no_path() -> None:
    graph = build_graph(
        _items(),
        edges=[("agent:main", "tool:fs")],
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
    )
    assert reachable_paths(graph) == []


def test_external_egress_escalates_the_path_severity() -> None:
    connected = build_graph(
        _items(),
        edges=[("agent:main", "tool:fs"), ("tool:fs", "data:secrets"), ("tool:fs", "egress:web")],
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
    )
    without_egress = build_graph(
        _items(),
        edges=[("agent:main", "tool:fs"), ("tool:fs", "data:secrets")],
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
    )
    assert reachable_paths(connected)[0].severity.level == "critical"
    assert reachable_paths(without_egress)[0].severity.level == "high"


def test_credential_scope_factor_and_cycles_and_limit() -> None:
    cyclic = build_graph(
        _items(),
        edges=[
            ("agent:main", "cred:aws"),
            ("cred:aws", "tool:fs"),
            ("tool:fs", "agent:main"),  # a cycle must not hang the walk
            ("tool:fs", "data:secrets"),
        ],
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
    )
    paths = reachable_paths(cyclic)
    assert paths
    assert "credential_scope" in paths[0].severity.factors
    assert paths[0].node_ids[-1] == "data:secrets"
    assert len(reachable_paths(cyclic, limit=1)) == 1


def test_path_severity_rubric_for_non_jewel_paths() -> None:
    graph = build_graph(_items(), edges=[("agent:main", "tool:fs")])
    assert path_severity(graph, ["agent:main", "tool:fs"]).level == "medium"
    assert path_severity(graph, ["agent:main"]).level == "low"
