"""Capability / attack-path graph (M27, F93).

Build the deployed system's capability graph from inventory and enumerate the
reachable paths from an untrusted input to a crown jewel. Structural findings and
per-path status (`proven_broken`/`open_missed`/`unproven`/`accepted`) land in
27.5. Design: ``docs/design/backtest-path-intake.md``; PRD 31 (R67).
"""

from agentdrill.pathgraph.graph import (
    DEFAULT_PATH_LIMIT,
    NODE_KINDS,
    CapabilityGraph,
    Edge,
    GraphError,
    Node,
    PathSeverity,
    ReachablePath,
    SeverityLevel,
    build_graph,
    path_severity,
    reachable_paths,
)

__all__ = [
    "DEFAULT_PATH_LIMIT",
    "NODE_KINDS",
    "CapabilityGraph",
    "Edge",
    "GraphError",
    "Node",
    "PathSeverity",
    "ReachablePath",
    "SeverityLevel",
    "build_graph",
    "path_severity",
    "reachable_paths",
]
