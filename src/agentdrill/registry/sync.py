"""Registry sync + outdated (M16 16.6, F75).

``agentdrill registry sync`` is read-only and **signature-verified** — a bad
signature is rejected; ``pack outdated`` reports newer remote versions.
Design: ``docs/prd/17-pack-registry-and-governance.md``.
"""

from __future__ import annotations

from pydantic import BaseModel

from agentdrill.registry.index import RegistryIndex, verify_index
from agentdrill.registry.signing import Verifier


class SyncError(ValueError):
    """Raised when a remote index fails signature verification."""


class OutdatedEntry(BaseModel):
    """A pack whose remote version is newer than the local one."""

    name: str
    local_version: str
    remote_version: str


def sync_index(remote: RegistryIndex, *, verifier: Verifier) -> RegistryIndex:
    """Verify and adopt a remote index (read-only).

    Raises:
        SyncError: The remote index signature does not verify.
    """
    if not verify_index(remote, verifier):
        raise SyncError("registry signature does not verify — refusing to sync (read-only)")
    return remote


def is_outdated(local: RegistryIndex, remote: RegistryIndex) -> list[OutdatedEntry]:
    """Packs whose remote version differs from the local one (by name)."""
    local_by_name = {entry.name: entry.version for entry in local.entries}
    outdated: list[OutdatedEntry] = []
    for entry in remote.entries:
        local_version = local_by_name.get(entry.name)
        if local_version is not None and local_version != entry.version:
            outdated.append(
                OutdatedEntry(
                    name=entry.name,
                    local_version=local_version,
                    remote_version=entry.version,
                )
            )
    return sorted(outdated, key=lambda o: o.name)
