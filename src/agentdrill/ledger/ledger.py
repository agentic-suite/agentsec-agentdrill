"""Exposure ledger store (M28 28.1, F95).

The ledger records findings and never hides one: an accepted waiver changes gate
impact, never visibility (28.2). Design:
``docs/design/exposure-attestation-roe.md``; PRD 33 (R69).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.ledger.finding import LedgerEntry, LedgerError


class Ledger(BaseModel):
    """The exposure ledger: findings keyed by id, with their lifecycle."""

    entries: dict[str, LedgerEntry] = Field(default_factory=dict)

    def record(self, entry: LedgerEntry) -> LedgerEntry:
        """Insert or replace a finding's entry by id."""
        self.entries[entry.finding.id] = entry
        return entry

    def get(self, finding_id: str) -> LedgerEntry:
        """The entry for ``finding_id``.

        Raises:
            LedgerError: The finding is not in the ledger.
        """
        if finding_id not in self.entries:
            raise LedgerError(f"finding {finding_id!r} is not in the ledger")
        return self.entries[finding_id]

    def all(self) -> list[LedgerEntry]:
        """Every entry, in insertion order (never filtered — visibility is total)."""
        return list(self.entries.values())
