"""M27 27.5 — structural findings + path status (RED → GREEN).

Detect the structural findings (trifecta, over-scope, unrestricted egress,
auto-approve+shell, writable instructions, shared memory, identity inheritance),
bind cases to each critical path, classify a path's status
(`proven_broken`/`open_missed`/`unproven`/`accepted`), and alert on a **new path**
opened by a config change.
"""

from __future__ import annotations

import pytest

from agentdrill.integrations import InventoryItem
from agentdrill.pathgraph import (
    PathError,
    bind_path,
    build_graph,
    detect_findings,
    new_path_alerts,
    new_paths,
    reachable_paths,
    require_critical_bound,
)


def _items() -> list[InventoryItem]:
    return [
        InventoryItem(id="agent:main", kind="agent", name="main"),
        InventoryItem(id="tool:shell", kind="tool", name="bash-shell"),
        InventoryItem(id="tool:fs", kind="tool", name="filesystem"),
        InventoryItem(id="mcp:evil", kind="mcp_server", name="evil-mcp"),
        InventoryItem(id="cred:aws", kind="credential", name="aws-key"),
        InventoryItem(id="data:secrets", kind="data_source", name="secrets"),
        InventoryItem(id="egress:web", kind="egress_route", name="web"),
        InventoryItem(id="mem:shared", kind="memory_store", name="shared-memory"),
        InventoryItem(id="sub:helper", kind="sub_agent", name="helper"),
        InventoryItem(id="approval:auto", kind="approval_setting", name="auto-approve"),
        InventoryItem(id="instr:agents", kind="instruction_file", name="AGENTS.md"),
    ]


def _edges() -> list[tuple[str, ...]]:
    return [
        ("agent:main", "mcp:evil"),
        ("mcp:evil", "tool:fs"),
        ("tool:fs", "data:secrets"),
        ("tool:fs", "egress:web"),
        ("approval:auto", "tool:shell"),
    ]


def _attributes() -> dict[str, dict[str, object]]:
    return {
        "cred:aws": {"over_scoped": True},
        "egress:web": {"unrestricted": True},
        "approval:auto": {"auto_approve": True},
        "instr:agents": {"writable": True},
        "mem:shared": {"shared": True},
        "sub:helper": {"inherits_identity": True},
    }


def _graph():
    return build_graph(
        _items(),
        edges=_edges(),
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
        attributes=_attributes(),
    )


def test_all_structural_findings_are_detected() -> None:
    kinds = {finding.kind for finding in detect_findings(_graph())}
    assert kinds == {
        "trifecta_present",
        "over_scoped_token",
        "unrestricted_egress",
        "auto_approve_plus_shell",
        "writable_instruction_file",
        "shared_memory",
        "identity_inheritance",
    }


def test_critical_paths_must_be_bound_to_cases() -> None:
    graph = _graph()
    path = reachable_paths(graph)[0]
    bound = bind_path(path, case_ids=["case-trifecta"])
    require_critical_bound([bound])

    unbound = bind_path(path, case_ids=[])
    with pytest.raises(PathError):
        require_critical_bound([unbound])


def test_path_status_classification() -> None:
    graph = _graph()
    path = reachable_paths(graph)[0]
    assert bind_path(path).status == "unproven"
    assert bind_path(path, proven=True).status == "proven_broken"
    assert bind_path(path, missed=True).status == "open_missed"
    assert bind_path(path, accepted=True).status == "accepted"
    with pytest.raises(PathError):
        bind_path(path, proven=True, accepted=True)  # a status is exclusive


def test_a_new_path_triggers_an_alert() -> None:
    previous = build_graph(
        _items(),
        edges=[("agent:main", "mcp:evil"), ("mcp:evil", "tool:fs")],
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
    )
    current = build_graph(
        _items(),
        edges=[
            ("agent:main", "mcp:evil"),
            ("mcp:evil", "tool:fs"),
            ("tool:fs", "data:secrets"),  # a NEW edge closes the path
        ],
        crown_jewels=["data:secrets"],
        untrusted=["agent:main"],
    )
    opened = new_paths(previous, current)
    assert [p.node_ids for p in opened] == [["agent:main", "mcp:evil", "tool:fs", "data:secrets"]]
    alerts = new_path_alerts(opened)
    assert len(alerts) == 1
    assert "data:secrets" in alerts[0].message
    assert new_paths(current, current) == []
