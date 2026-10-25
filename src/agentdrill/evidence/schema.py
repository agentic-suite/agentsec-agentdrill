"""agentwatch schema reader (M7 work item 7.1).

Reads the agentwatch record/security events and types them. agentdrill **consumes**
the agentwatch schema, never forks it (DD-05): event names outside the vocabulary
(`denied`, `policy-fired`, `secret-detected`, `revoked`, `halted`) fail loudly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from agentdrill.loading.attack_registry import AGENTWATCH_EVENTS
from agentdrill.models.errors import ConfigError


class AgentWatchEvent(BaseModel):
    """One typed agentwatch security event."""

    event: str
    ref: str | None = None
    ts: str | None = None
    actor: str | None = None
    detail: str | None = None
    #: The case this event belongs to, when the recorder tags it (M7 binding).
    case_id: str | None = None


def read_events(source: Any) -> list[AgentWatchEvent]:
    """Parse and type agentwatch events from a list, envelope, or JSON file.

    Args:
        source: A list of event dicts, a ``{"events": [...]}`` envelope, or a path
            to a JSON file holding either.

    Returns:
        The typed events, in order.

    Raises:
        ConfigError: If the source is malformed or an event name is unknown.
    """
    data = _load(source)
    items = data.get("events") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ConfigError('agentwatch source must be a list of events or {"events": [...]}')
    events: list[AgentWatchEvent] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ConfigError(f"agentwatch event {index} must be a mapping")
        event = AgentWatchEvent.model_validate(item)
        if event.event not in AGENTWATCH_EVENTS:
            raise ConfigError(
                f"unknown agentwatch event: {event.event!r}; "
                f"known: {sorted(AGENTWATCH_EVENTS)}"
            )
        events.append(event)
    return events


def _load(source: Any) -> Any:
    """Load JSON from a path, or use the value directly."""
    if isinstance(source, str | Path):
        path = Path(source)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ConfigError(f"could not read agentwatch source {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ConfigError(f"agentwatch source {path} is not valid JSON: {exc}") from exc
    return source
