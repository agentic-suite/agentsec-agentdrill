"""Deprecation + takedown (M16 16.5).

Explicit deprecation carries migration notes; a takedown removes the index
entry but is recorded on the **signature chain**, so nothing disappears
silently. Design: ``docs/prd/17-pack-registry-and-governance.md``.
"""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field

from agentdrill.registry.index import RegistryIndex

#: The governance event kinds.
GovernanceKind = Literal["deprecate", "takedown"]


class GovernanceEvent(BaseModel):
    """One recorded governance action, chained to the previous event."""

    seq: int
    kind: GovernanceKind
    name: str
    version: str
    note: str = ""
    digest: str = ""


class GovernanceLog(BaseModel):
    """Append-only, hash-chained log of deprecations and takedowns."""

    events: list[GovernanceEvent] = Field(default_factory=list)

    def record(
        self, kind: GovernanceKind, name: str, version: str, note: str = ""
    ) -> GovernanceEvent:
        """Append a chained governance event (digest binds the previous head)."""
        previous = self.events[-1].digest if self.events else ""
        seq = len(self.events)
        canonical = f"{previous}|{seq}|{kind}|{name}|{version}|{note}"
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        event = GovernanceEvent(
            seq=seq, kind=kind, name=name, version=version, note=note, digest=digest
        )
        self.events.append(event)
        return event

    @property
    def head(self) -> str:
        """The chain head (the last event's digest), or empty when no events."""
        return self.events[-1].digest if self.events else ""


def apply_deprecation(
    index: RegistryIndex, log: GovernanceLog, *, name: str, version: str, note: str
) -> RegistryIndex:
    """Mark an entry deprecated with a migration note; recorded on the chain."""
    log.record("deprecate", name, version, note)
    entry = index.entry(name, version)
    if entry is not None:
        entry.deprecated = True
        entry.migration_note = note
    return index


def apply_takedown(
    index: RegistryIndex,
    log: GovernanceLog,
    *,
    name: str,
    version: str,
    reason: str = "",
) -> RegistryIndex:
    """Remove an entry from the index; the takedown is recorded on the chain."""
    log.record("takedown", name, version, reason)
    index.entries = [e for e in index.entries if not (e.name == name and e.version == version)]
    return index
