"""M20 20.7 — read-only MCP drill surface, F77 (RED → GREEN).

A read-only MCP server exposing pack/run/result queries; the tool list contains
**no write tools**; queries are recorded.
"""

from __future__ import annotations

import pytest

from agentdrill.dx import (
    McpDrillSurface,
    McpError,
    McpTool,
    is_write_tool,
    require_read_only,
)


def test_tool_list_contains_no_write_tools() -> None:
    surface = McpDrillSurface()
    names = {tool.name for tool in surface.tools()}
    assert {"list_packs", "get_pack", "list_runs", "get_run", "query_results"} <= names
    require_read_only(surface)  # no raise
    assert all(tool.read_only for tool in surface.tools())


def test_is_write_tool_detects_write_names() -> None:
    assert is_write_tool("edit_policy") is True
    assert is_write_tool("delete_pack") is True
    assert is_write_tool("list_packs") is False


def test_a_write_tool_would_be_rejected() -> None:
    surface = McpDrillSurface()
    surface.add_tool(McpTool(name="edit_policy", read_only=False))
    with pytest.raises(McpError, match="write"):
        require_read_only(surface)


def test_queries_are_recorded() -> None:
    surface = McpDrillSurface()
    surface.call("list_packs")
    surface.call("get_run", run_id="r1")
    assert [q["tool"] for q in surface.queries()] == ["list_packs", "get_run"]


def test_unknown_tool_fails_loudly() -> None:
    with pytest.raises(McpError, match="unknown"):
        McpDrillSurface().call("nope")
