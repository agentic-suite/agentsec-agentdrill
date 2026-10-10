"""Environment and target sanity checks for ``agentdrill doctor``.

Pure check functions (no I/O side effects beyond creating the output dir) so the
CLI and tests can call them directly.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

from agentdrill import __version__
from agentdrill.config import AgentDrillConfig

_MIN_PYTHON = (3, 11)
_OPTIONAL_FRAMEWORKS: dict[str, str] = {
    "langgraph": "langgraph",
    "pydantic-ai": "pydantic_ai",
    "crewai": "crewai",
    "openai-agents": "agents",
    "smolagents": "smolagents",
    "autogen": "autogen_agentchat",
    "llamaindex": "llama_index",
    "claude": "claude_agent_sdk",
    "adk": "google.adk",
}


@dataclass(frozen=True)
class Check:
    """A single doctor check result."""

    name: str
    ok: bool
    detail: str
    critical: bool = True


def _module_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def _check_python() -> Check:
    need = ".".join(str(p) for p in _MIN_PYTHON)
    ok = sys.version_info >= _MIN_PYTHON
    return Check("python", ok, f"{sys.version.split()[0]} (need >= {need})")


def _check_version() -> Check:
    return Check("version", bool(__version__), __version__ or "unknown")


def _check_output_dir(config: AgentDrillConfig) -> Check:
    path = Path(config.output_dir)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return Check("output_dir", False, f"{path} is not writable: {exc}")
    return Check("output_dir", True, str(path))


def _check_optional_frameworks() -> Check:
    present = sorted(
        name for name, module in _OPTIONAL_FRAMEWORKS.items() if _module_available(module)
    )
    detail = ", ".join(present) if present else "none installed (only built-in adapters)"
    return Check("adapters", True, detail, critical=False)


def run_checks(config: AgentDrillConfig) -> list[Check]:
    """Run all doctor checks and return their results."""
    return [
        _check_python(),
        _check_version(),
        _check_output_dir(config),
        _check_optional_frameworks(),
    ]


def has_failures(checks: list[Check]) -> bool:
    """True if any *critical* check failed."""
    return any(c.critical and not c.ok for c in checks)
