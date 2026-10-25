"""Adversary Lab core (M23 23.6, F88).

A versioned loopback lab — evil MCP server (poisoning / shadow / overlap /
preference / rug-pull / return-injection), test IdP, hostile registries, a rogue
upstream API, an evil A2A peer and sinks. Same seed ⇒ same lab event log.
Design: ``docs/prd/27-adversary-lab.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

#: The lab components.
LAB_COMPONENTS: tuple[str, ...] = (
    "evil-mcp",
    "test-idp",
    "hostile-registry",
    "rogue-upstream",
    "evil-a2a",
    "sink",
)

#: The evil MCP server's behaviours.
EVIL_MCP_BEHAVIORS: tuple[str, ...] = (
    "poisoning",
    "shadow",
    "overlap",
    "preference",
    "rug-pull",
    "return-injection",
)


class LabEvent(BaseModel):
    """One recorded lab event."""

    seq: int
    component: str
    detail: str


class AdversaryLab(BaseModel):
    """A versioned, seeded adversary lab."""

    version: str
    seed: int
    events: list[LabEvent] = Field(default_factory=list)
    loopback_only: bool = True

    def _emit(self, component: str, detail: str) -> None:
        self.events.append(LabEvent(seq=len(self.events), component=component, detail=detail))

    def serve_mcp(self, behavior: str) -> None:
        """Serve an evil-MCP behaviour (poisoning/rug-pull/...)."""
        self._emit("evil-mcp", behavior)

    def hit_sink(self, url: str) -> None:
        """Record an attempt against a lab sink."""
        self._emit("sink", url)


def build_lab(*, version: str, seed: int) -> AdversaryLab:
    """Build a versioned, seeded adversary lab."""
    return AdversaryLab(version=version, seed=seed, events=[])


def event_log(lab: AdversaryLab) -> list[tuple[int, str, str]]:
    """The lab's event log as stable tuples."""
    return [(event.seq, event.component, event.detail) for event in lab.events]
