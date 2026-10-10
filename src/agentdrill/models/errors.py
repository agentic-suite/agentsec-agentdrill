"""Error hierarchy for AgentDrill.

Every AgentDrill-specific exception derives from :class:`AgentDrillError` so
callers can catch one base type without leaking framework exceptions into
public APIs. Location-aware errors (:class:`PackParseError`) carry an optional
``file``/``line`` pair that render as ``file:line: message`` when both are
present, which is what makes loader diagnostics actionable.
"""

from __future__ import annotations


class AgentDrillError(Exception):
    """Base class for all AgentDrill errors."""


class PackParseError(AgentDrillError):
    """A scenario pack could not be parsed or validated.

    Args:
        message: Human-readable description of the failure.
        file: Path of the offending pack file, if known.
        line: 1-based line number where the problem occurred, if known.
    """

    def __init__(self, message: str, file: str | None = None, line: int | None = None) -> None:
        self.file = file
        self.line = line
        if file is not None and line is not None:
            rendered = f"{file}:{line}: {message}"
        else:
            rendered = message
        super().__init__(rendered)


class AdapterError(AgentDrillError):
    """An agent adapter failed to invoke or normalize a run."""


class AgentTimeoutError(AdapterError):
    """The agent exceeded its timeout budget."""


class ConfigError(AgentDrillError):
    """Invalid configuration (unknown metric, bad scoring config)."""


class JudgeError(AgentDrillError):
    """A judge call failed (unavailable, timeout, malformed verdict)."""
