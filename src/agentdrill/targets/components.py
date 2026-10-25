"""Deployed-stack target adapters (M5 work item 5.2).

One adapter per enforcement component. Each drives its real enforcement path
(through its configured command) and reads back a decision + evidence.
"""

from __future__ import annotations

from agentdrill.targets.base import CommandTarget


class AgentGateTarget(CommandTarget):
    """MCP OAuth 2.1 authorization proxy."""

    component = "agentgate"


class AgentKeysTarget(CommandTarget):
    """Never-in-context credential broker."""

    component = "agentkeys"


class AgentSeatbeltTarget(CommandTarget):
    """Portable local enforcement (macOS-first)."""

    component = "agentseatbelt"


class AgentKernelTarget(CommandTarget):
    """Linux eBPF visibility + enforcement."""

    component = "agentkernel"


class PolicyweaveOutputTarget(CommandTarget):
    """Compiled-policy output (policyweave)."""

    component = "policyweave-output"


class AgentHaltTarget(CommandTarget):
    """Universal kill-switch + evidence preservation."""

    component = "agenthalt"


#: The deployed-stack target classes, in registry order.
COMPONENTS: tuple[type[CommandTarget], ...] = (
    AgentGateTarget,
    AgentKeysTarget,
    AgentSeatbeltTarget,
    AgentKernelTarget,
    PolicyweaveOutputTarget,
    AgentHaltTarget,
)
