"""Evidence model (shared).

An :class:`Evidence` is one agentwatch security event bound to a result. It is
the single source of truth imported by targets, oracles, and run artifacts.
"""

from __future__ import annotations

from pydantic import BaseModel


class Evidence(BaseModel):
    """An agentwatch security event tied to a result."""

    event: str
    summary: str = ""
    ref: str | None = None
