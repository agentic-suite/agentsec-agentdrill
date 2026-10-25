"""Capability / attack-path graph (M27, F93).

Build the deployed system's capability graph from inventory and enumerate the
reachable paths from an untrusted input to a crown jewel. Structural findings and
per-path status (`proven_broken`/`open_missed`/`unproven`/`accepted`) land in
27.5. Design: ``docs/design/backtest-path-intake.md``; PRD 31 (R67).
"""

from agentdrill.pathgraph.findings import (
    Alert,
    BoundPath,
    PathError,
    PathStatus,
    StructuralFinding,
    StructuralKind,
    bind_path,
    detect_findings,
    new_path_alerts,
    new_paths,
    require_critical_bound,
)
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
    "Alert",
    "BoundPath",
    "CapabilityGraph",
    "Edge",
    "GraphError",
    "Node",
    "PathError",
    "PathSeverity",
    "PathStatus",
    "ReachablePath",
    "SeverityLevel",
    "StructuralFinding",
    "StructuralKind",
    "bind_path",
    "build_graph",
    "detect_findings",
    "new_path_alerts",
    "new_paths",
    "path_severity",
    "reachable_paths",
    "require_critical_bound",
]
