"""Adapter factory: resolve an adapter from an agent config dict.

``agent_config["type"]`` selects which adapter to build. The factory is the
single lookup point so the Runner (and, later, the CLI) can turn a YAML agent
block into a ready adapter without import gymnastics. Adding a new adapter
type means registering it in ``ADAPTERS``.

Exports:
    ADAPTERS: Mapping of type strings to adapter classes.
    create_adapter: Factory function to instantiate an adapter from config.
"""

from __future__ import annotations

from typing import Any

from agentdrill.adapters.adk import ADKAdapter
from agentdrill.adapters.autogen import AutoGenAdapter
from agentdrill.adapters.base import Adapter
from agentdrill.adapters.claude import ClaudeAgentSDKAdapter
from agentdrill.adapters.crewai import CrewAIAdapter
from agentdrill.adapters.http import HttpAdapter
from agentdrill.adapters.isolated import IsolatedAdapter
from agentdrill.adapters.langgraph import LangGraphAdapter
from agentdrill.adapters.llamaindex import LlamaIndexAdapter
from agentdrill.adapters.openai_agents import OpenAIAgentsAdapter
from agentdrill.adapters.pydantic_ai import PydanticAIAdapter
from agentdrill.adapters.python_import import PythonImportAdapter
from agentdrill.adapters.smolagents import SmolagentsAdapter
from agentdrill.adapters.subprocess import SubprocessAdapter

ADAPTERS: dict[str, type[Adapter]] = {
    "subprocess": SubprocessAdapter,
    "python": PythonImportAdapter,
    "http": HttpAdapter,
    "langgraph": LangGraphAdapter,
    "pydantic-ai": PydanticAIAdapter,
    "crewai": CrewAIAdapter,
    "openai-agents": OpenAIAgentsAdapter,
    "smolagents": SmolagentsAdapter,
    "autogen": AutoGenAdapter,
    "llamaindex": LlamaIndexAdapter,
    "claude": ClaudeAgentSDKAdapter,
    "adk": ADKAdapter,
    "isolated": IsolatedAdapter,
}


def create_adapter(config: dict[str, Any]) -> Adapter:
    """Return an adapter instance for the given agent config.

    Args:
        config: Agent configuration dict; must contain a ``type`` key
            matching one of the keys in :data:`ADAPTERS`.

    Returns:
        An initialized adapter instance.

    Raises:
        ValueError: If ``config["type"]`` is not a registered adapter type.
    """
    adapter_type = config.get("type")
    if not isinstance(adapter_type, str):
        raise ValueError(f"invalid adapter type: {adapter_type}")
    try:
        adapter_cls = ADAPTERS[adapter_type]
    except KeyError as exc:
        raise ValueError(f"unknown adapter type: {adapter_type}") from exc
    return adapter_cls()
