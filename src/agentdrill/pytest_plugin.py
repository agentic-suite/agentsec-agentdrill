"""Pytest plugin for AgentDrill — run scenarios as pytest tests.

Allows developers to run AgentDrill scenario packs as native pytest tests,
with automatic parametrization over scenarios, tag filtering, and injected
fixtures for agent configuration and adapter instances.

**Usage via CLI:**

.. code-block:: bash

    pytest --agentdrill-pack scenarios/core-launch.yaml \\
           --agentdrill-agent python:my_agent.run \\
           --agentdrill-judge mock

**Usage via marker:**

.. code-block:: python

    # conftest.py
    pytest_plugins = ["agentdrill.pytest_plugin"]

    # test_my_agent.py
    import pytest

    @pytest.mark.agentdrill(pack="scenarios/core-launch.yaml")
    def test_agent_runs_scenario(scenario, agent_adapter):
        artifact = agent_adapter.run(scenario, {"run_id": scenario.id})
        assert artifact.status == "completed"

**Available fixtures:**

- ``scenario`` — Parametrized over scenarios in the pack (requires marker).
- ``agent_config`` — Parsed agent config dict from CLI or marker.
- ``agent_adapter`` — Instantiated adapter from the agent config.
- ``scenario_pack`` — The loaded ``ScenarioPack`` from CLI or marker.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentdrill.cli.util import parse_agent_spec
from agentdrill.loading.pack_loader import load_pack
from agentdrill.runner import generate_run_id


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register AgentDrill command-line options with pytest."""
    group = parser.getgroup("agentdrill")
    group.addoption(
        "--agentdrill-pack",
        type=str,
        help="Path to a scenario pack for AgentDrill tests",
    )
    group.addoption(
        "--agentdrill-agent",
        type=str,
        help="Agent spec for AgentDrill tests (e.g. 'python:my_module.run')",
    )
    group.addoption(
        "--agentdrill-judge",
        type=str,
        default=None,
        help="Judge spec for AgentDrill tests (e.g. 'openai:gpt-4o-mini')",
    )
    group.addoption(
        "--agentdrill-tags",
        type=str,
        default=None,
        help="Comma-separated tag filter for AgentDrill tests",
    )
    group.addoption(
        "--agentdrill-output",
        type=str,
        default=".agentdrill",
        help="Output directory for AgentDrill artifacts",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register AgentDrill markers for documentation and warning suppression."""
    config.addinivalue_line(
        "markers",
        "agentdrill(pack=None, agent=None): mark test to run with AgentDrill scenarios. "
        "If pack is provided, parametrize over scenarios in that pack.",
    )
    config.addinivalue_line(
        "markers",
        "agentdrill_tags(tag1, tag2, ...): "
        "filter scenarios by tags. "
        "Use with @pytest.mark.agentdrill(pack=...).",
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize tests over scenarios when the ``scenario`` fixture is requested.

    If a test requests a ``scenario`` parameter, this hook:

    1. Looks for an ``@pytest.mark.agentdrill(pack=...)`` marker.
    2. Falls back to the ``--agentdrill-pack`` CLI option.
    3. Optionally filters by ``@pytest.mark.agentdrill_tags(...)`` or
       ``--agentdrill-tags`` CLI option.
    4. Parametrizes the test with one parametrization per matching scenario.

    The scenario objects are instances of ``agentdrill.models.pack.Scenario``.
    """
    if "scenario" not in metafunc.fixturenames:
        return

    # Resolve pack path from marker or CLI option
    marker = metafunc.definition.get_closest_marker("agentdrill")
    pack_path = marker.kwargs.get("pack") if marker else None
    if not pack_path:
        pack_path = metafunc.config.getoption("--agentdrill-pack")
    if not pack_path:
        return

    pack = load_pack(pack_path)

    # Apply optional tag filter from marker or CLI option
    tags_marker = metafunc.definition.get_closest_marker("agentdrill_tags")
    tag_filter = metafunc.config.getoption("--agentdrill-tags")
    tag_set: set[str] | None = None
    if tags_marker:
        tag_set = set(tags_marker.args)
    elif tag_filter:
        tag_set = set(tag_filter.split(","))

    scenarios = pack.scenarios
    if tag_set:
        scenarios = [s for s in scenarios if tag_set & set(s.tags)]

    ids = [s.id for s in scenarios]
    metafunc.parametrize("scenario", scenarios, ids=ids)


@pytest.fixture
def agent_config(request: pytest.FixtureRequest) -> dict[str, Any]:
    """Provide the parsed agent configuration.

    Resolves from (in priority order):
    1. ``@pytest.mark.agentdrill(agent=...)`` marker kwarg.
    2. ``--agentdrill-agent`` CLI option.

    Skips the test if neither is provided.
    """
    agent_spec = request.config.getoption("--agentdrill-agent")
    if not agent_spec:
        marker = request.node.get_closest_marker("agentdrill")
        if marker:
            agent_spec = marker.kwargs.get("agent")
    if not agent_spec:
        pytest.skip(
            "No agent spec provided"
            " (use --agentdrill-agent or @pytest.mark.agentdrill(agent=...))"
        )

    cfg = parse_agent_spec(agent_spec)
    cfg["run_id"] = generate_run_id()
    return cfg


@pytest.fixture
def agent_adapter(agent_config: dict[str, Any]) -> Any:
    """Provide an instantiated adapter from the agent configuration.

    Depends on ``agent_config``, which will skip the test if no agent spec
    is configured.
    """
    from agentdrill.adapters.factory import create_adapter

    return create_adapter(agent_config)


@pytest.fixture
def scenario_pack(request: pytest.FixtureRequest) -> Any:
    """Provide the loaded scenario pack.

    Resolves from (in priority order):
    1. ``@pytest.mark.agentdrill(pack=...)`` marker kwarg.
    2. ``--agentdrill-pack`` CLI option.

    Skips the test if neither is provided.
    """
    pack_path = request.config.getoption("--agentdrill-pack")
    if not pack_path:
        marker = request.node.get_closest_marker("agentdrill")
        if marker:
            pack_path = marker.kwargs.get("pack")
    if not pack_path:
        pytest.skip(
            "No pack specified"
            " (use --agentdrill-pack or @pytest.mark.agentdrill(pack=...))"
        )
    return load_pack(pack_path)
