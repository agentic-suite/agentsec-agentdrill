"""M7 7.1 — agentwatch schema reader (RED → GREEN).

Read the agentwatch record/security events and type them. Events outside the
agentwatch vocabulary (`denied`, `policy-fired`, `secret-detected`, `revoked`,
`halted`) fail loudly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agentdrill.evidence.schema import AgentWatchEvent, read_events
from agentdrill.models.errors import ConfigError

EVENTS: list[dict[str, Any]] = [
    {"event": "denied", "ref": "evt-1", "ts": "2026-01-01T00:00:00Z", "actor": "agentgate"},
    {"event": "policy-fired", "ref": "evt-2"},
]


def test_read_events_from_list() -> None:
    events = read_events(EVENTS)
    assert all(isinstance(e, AgentWatchEvent) for e in events)
    assert events[0].event == "denied"
    assert events[0].actor == "agentgate"
    assert events[1].event == "policy-fired"


def test_read_events_from_envelope() -> None:
    events = read_events({"events": EVENTS})
    assert len(events) == 2


def test_read_events_from_json_file(tmp_path: Path) -> None:
    path = tmp_path / "events.json"
    path.write_text(json.dumps({"events": EVENTS}), encoding="utf-8")
    assert len(read_events(path)) == 2


def test_unknown_event_fails_loudly() -> None:
    with pytest.raises(ConfigError, match="not-a-real-event"):
        read_events([{"event": "not-a-real-event"}])


def test_malformed_source_fails() -> None:
    with pytest.raises(ConfigError):
        read_events("not a list or path")


def test_all_vocabulary_events_accepted() -> None:
    events = read_events(
        [{"event": e} for e in ("denied", "policy-fired", "secret-detected", "revoked", "halted")]
    )
    assert [e.event for e in events] == [
        "denied",
        "policy-fired",
        "secret-detected",
        "revoked",
        "halted",
    ]
