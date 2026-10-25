"""Read-only MCP drill surface (M20 20.7, F77).

A read-only MCP server exposing pack/run/result queries — **no write tools** —
with queries recorded. Design: ``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

#: Substrings that mark a write/destructive tool.
WRITE_TOKENS: tuple[str, ...] = (
    "write",
    "edit",
    "create",
    "delete",
    "update",
    "put",
    "post",
    "apply",
    "publish",
)


class McpError(ValueError):
    """Raised when the MCP surface is violated (a write tool, or an unknown tool)."""


class McpTool(BaseModel):
    """An MCP tool exposed by the drill surface."""

    name: str
    description: str = ""
    read_only: bool = True


def is_write_tool(name: str) -> bool:
    """Whether a tool name looks like a write/destructive tool."""
    lowered = name.lower()
    return any(token in lowered for token in WRITE_TOKENS)


#: The read-only tools the drill surface exposes.
_READ_TOOLS: tuple[McpTool, ...] = (
    McpTool(name="list_packs", description="List attack packs"),
    McpTool(name="get_pack", description="Get one pack"),
    McpTool(name="list_runs", description="List runs"),
    McpTool(name="get_run", description="Get one run"),
    McpTool(name="query_results", description="Query results"),
)


class McpDrillSurface:
    """A read-only MCP drill surface."""

    def __init__(self) -> None:
        self._tools: list[McpTool] = list(_READ_TOOLS)
        self._queries: list[dict[str, Any]] = []

    def tools(self) -> list[McpTool]:
        """The exposed tools."""
        return list(self._tools)

    def add_tool(self, tool: McpTool) -> None:
        """Add a tool to the surface (used to demonstrate the write-tool guard)."""
        self._tools.append(tool)

    def queries(self) -> list[dict[str, Any]]:
        """The recorded queries."""
        return list(self._queries)

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Invoke a read tool and record the query.

        Raises:
            McpError: The tool is unknown.
        """
        if name not in {tool.name for tool in self._tools}:
            raise McpError(f"unknown MCP tool: {name!r}")
        self._queries.append({"tool": name, "args": kwargs})
        return {"tool": name, "args": kwargs}


def require_read_only(surface: McpDrillSurface) -> None:
    """Fail loudly if the surface exposes any write tool.

    Raises:
        McpError: A write tool is present.
    """
    write_tools = [tool.name for tool in surface.tools() if is_write_tool(tool.name)]
    if write_tools:
        raise McpError(f"MCP drill surface must be read-only; write tool(s): {write_tools}")
