"""Recon / scoping (M5 work item 5.3, F42).

Probe the exposed surface (tools, MCP servers, capabilities — via an agentwatch
inventory or a probe command), produce a :class:`ReconSnapshot`, and bind each
case to what actually exists. A case bound to a nonexistent surface fails
**loudly** — never silently passes.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

import httpx
from pydantic import BaseModel, Field

from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.errors import AdapterError, ConfigError


class ReconSnapshot(BaseModel):
    """The exposed surface at run time, and the case→surface bindings."""

    tools: list[str] = Field(default_factory=list)
    mcp_servers: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    case_bindings: dict[str, list[str]] = Field(default_factory=dict)

    def has_tool(self, tool: str) -> bool:
        """Whether ``tool`` exists on the surface (MCP tools bind to their server)."""
        if tool in self.tools:
            return True
        if tool.startswith("mcp__"):
            parts = tool.split("__")
            if len(parts) >= 2 and parts[1] in self.mcp_servers:
                return True
        return False


def probe(
    command: list[str] | None = None,
    inventory: dict[str, Any] | None = None,
) -> ReconSnapshot:
    """Produce a :class:`ReconSnapshot` from an inventory or a probe command.

    Raises:
        ConfigError: If neither an inventory nor a command is supplied.
        AdapterError: If the probe command fails or emits non-JSON.
    """
    if command is not None:
        return _probe_command(command)
    if inventory is not None:
        return ReconSnapshot.model_validate(inventory)
    raise ConfigError("recon requires an inventory or a command to probe the surface")


class ModelSurface(BaseModel):
    """A declared model endpoint the run depends on (G12)."""

    model: str
    base_url: str


def check_model_surface(surface: ModelSurface, *, timeout: float = 5.0) -> None:
    """Fail loudly if the model surface is unreachable or the model is absent.

    Turns an opaque 404 / connection error into a clear :class:`ConfigError`
    *before* any case runs (predecessor G12).
    """
    url = surface.base_url.rstrip("/") + "/models"
    try:
        response = httpx.get(url, timeout=timeout)
    except httpx.HTTPError as exc:
        raise ConfigError(
            f"model surface unreachable: {surface.base_url} ({exc})"
        ) from exc
    if response.status_code == 404:
        raise ConfigError(
            f"model {surface.model!r} not found at {surface.base_url} (HTTP 404)"
        )
    if response.status_code != 200:
        raise ConfigError(
            f"model surface {surface.base_url} returned HTTP {response.status_code}"
        )


def _probe_command(command: list[str]) -> ReconSnapshot:
    try:
        proc = subprocess.run(  # noqa: S603 - command comes from trusted target config
            command, capture_output=True, text=True, check=False
        )
    except OSError as exc:
        raise AdapterError(f"recon probe failed to start: {exc}") from exc
    if proc.returncode != 0:
        raise AdapterError(f"recon probe exited {proc.returncode}: {proc.stderr.strip()}")
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AdapterError("recon probe output is not JSON") from exc
    return ReconSnapshot.model_validate(data)


def bind_cases(pack: AttackPack, snapshot: ReconSnapshot) -> ReconSnapshot:
    """Bind every case to the surface; raise loudly on a missing surface."""
    for case in pack.cases:
        tools = sorted({step.tool for step in case.attack.steps})
        missing = [tool for tool in tools if not snapshot.has_tool(tool)]
        if missing:
            raise ConfigError(
                f"case {case.id} references a surface not present: {missing}"
            )
        snapshot.case_bindings[case.id] = tools
    return snapshot


def recon(
    pack: AttackPack,
    *,
    command: list[str] | None = None,
    inventory: dict[str, Any] | None = None,
    model: ModelSurface | None = None,
) -> ReconSnapshot:
    """Probe the surface and bind ``pack``'s cases (fails loudly if absent).

    When a ``model`` surface is declared it is checked first — an unreachable or
    missing model fails before any case runs (G12).
    """
    if model is not None:
        check_model_surface(model)
    snapshot = probe(command=command, inventory=inventory)
    return bind_cases(pack, snapshot)
