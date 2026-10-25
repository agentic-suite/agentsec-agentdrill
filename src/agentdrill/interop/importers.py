"""Interop importer (M17 17.1, F12).

Import the community's attack suites (promptfoo / garak / AgentDojo / PyRIT)
into attack packs. This is **format translation only** — the imported pack runs
through the same core runner, untouched. Design: ``docs/prd/03-landscape.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.models.attack_pack import AttackPack

#: The supported source tools.
SUPPORTED_TOOLS: tuple[str, ...] = ("promptfoo", "garak", "agentdojo", "pyrit")


class InteropError(ValueError):
    """Raised when a source suite cannot be translated."""


class ImportedCase(BaseModel):
    """A source-tool case normalized into an importable form."""

    id: str
    tool: str = "prompt"
    args: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    source_tool: str = ""


def _as_list(data: Any) -> list[Any]:
    """Accept a list or a single mapping as a case list."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise InteropError(f"expected a list or mapping, got {type(data).__name__}")


def parse_promptfoo(data: Any) -> list[ImportedCase]:
    """Translate promptfoo tests → imported cases."""
    tests = data.get("tests", []) if isinstance(data, dict) else data
    cases: list[ImportedCase] = []
    for index, test in enumerate(_as_list(tests)):
        variables = test.get("vars", {}) if isinstance(test, dict) else {}
        tool = str(variables.get("tool", "prompt"))
        args = {k: v for k, v in variables.items() if k != "tool"}
        cases.append(
            ImportedCase(
                id=str(test.get("description", f"promptfoo-{index}")).replace(" ", "-"),
                tool=tool,
                args=args,
                tags=["promptfoo"],
                source_tool="promptfoo",
            )
        )
    return cases


def parse_garak(data: Any) -> list[ImportedCase]:
    """Translate garak probes → imported cases."""
    cases: list[ImportedCase] = []
    for index, probe in enumerate(_as_list(data)):
        name = (
            str(probe.get("probe", f"garak-{index}"))
            if isinstance(probe, dict)
            else f"garak-{index}"
        )
        cases.append(
            ImportedCase(
                id=name.replace(".", "-"),
                tool="prompt",
                args={"prompt": probe.get("prompt", "")} if isinstance(probe, dict) else {},
                tags=["garak", "probe"],
                source_tool="garak",
            )
        )
    return cases


def parse_agentdojo(data: Any) -> list[ImportedCase]:
    """Translate AgentDojo tasks → imported cases."""
    tasks = data.get("tasks", []) if isinstance(data, dict) else data
    cases: list[ImportedCase] = []
    for index, task in enumerate(_as_list(tasks)):
        tools = task.get("tools", []) if isinstance(task, dict) else []
        tool = str(tools[0]) if tools else "prompt"
        cases.append(
            ImportedCase(
                id=str(task.get("id", f"agentdojo-{index}"))
                if isinstance(task, dict)
                else f"agentdojo-{index}",
                tool=tool,
                args={"prompt": task.get("prompt", "")} if isinstance(task, dict) else {},
                tags=["agentdojo", "task"],
                source_tool="agentdojo",
            )
        )
    return cases


def parse_pyrit(data: Any) -> list[ImportedCase]:
    """Translate PyRIT objectives → imported cases."""
    objectives = data.get("objectives", []) if isinstance(data, dict) else data
    cases: list[ImportedCase] = []
    for index, objective in enumerate(_as_list(objectives)):
        cases.append(
            ImportedCase(
                id=str(objective.get("id", f"pyrit-{index}"))
                if isinstance(objective, dict)
                else f"pyrit-{index}",
                tool="prompt",
                args={"prompt": objective.get("prompt", "")} if isinstance(objective, dict) else {},
                tags=["pyrit", "objective"],
                source_tool="pyrit",
            )
        )
    return cases


_PARSERS: Mapping[str, Callable[[Any], list[ImportedCase]]] = {
    "promptfoo": parse_promptfoo,
    "garak": parse_garak,
    "agentdojo": parse_agentdojo,
    "pyrit": parse_pyrit,
}


def import_suite(data: Any, tool: str) -> list[ImportedCase]:
    """Translate a source suite for ``tool`` into imported cases.

    Raises:
        InteropError: The tool is unknown.
    """
    parser = _PARSERS.get(tool)
    if parser is None:
        raise InteropError(f"unknown interop tool: {tool!r}; supported: {list(SUPPORTED_TOOLS)}")
    return parser(data)


def to_pack(
    imported: list[ImportedCase],
    *,
    name: str,
    version: str = "1.0.0",
    target: str = "policyweave-output",
) -> AttackPack:
    """Translate imported cases into a runnable attack pack."""
    cases = [
        {
            "id": case.id,
            "title": f"Imported from {case.source_tool}: {case.id}",
            "goal": f"Verify the stack stops the imported {case.source_tool} case",
            "incident_ref": f"interop:{case.source_tool}",
            "target": {"type": target},
            "driver": {"type": "subprocess"},
            "attack": {"steps": [{"tool": case.tool, "args": case.args}]},
            "oracle": {"expect": "blocked"},
            "tags": sorted(set(case.tags) | {"imported", case.source_tool}),
        }
        for case in imported
    ]
    return AttackPack.model_validate(
        {
            "pack": {
                "name": name,
                "version": version,
                "description": f"Imported suite ({name})",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
            },
            "cases": cases,
        }
    )
