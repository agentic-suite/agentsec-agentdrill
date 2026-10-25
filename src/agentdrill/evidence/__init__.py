"""Evidence integration (M7).

Reads the agentwatch schema, binds evidence to results, validates expected
telemetry, and reconciles surface coverage. Design:
``docs/design/evidence-integration.md``.
"""

from __future__ import annotations

from agentdrill.evidence.schema import AgentWatchEvent, read_events

__all__ = ["AgentWatchEvent", "read_events"]
