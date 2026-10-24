"""Untrusted-pack hardening (M22 22.3).

An OS-level sandbox (``--network none``, read-only root, resource caps) is
**required** for ``external`` trust, and the audit log is hash-chained so tamper
is detected (predecessor G4). Design:
``docs/prd/06-security-baseline.md``.
"""

from __future__ import annotations

import hashlib

from pydantic import BaseModel, Field


class SandboxError(ValueError):
    """Raised when an external pack's sandbox is not isolated."""


class SandboxSpec(BaseModel):
    """An OS-level sandbox specification."""

    network: str = "none"
    read_only_root: bool = True
    memory_limit: str = "512m"
    cpu_limit: float = 1.0


def sandbox_spec_for(trust: str) -> SandboxSpec:
    """The sandbox spec for a trust level (external ⇒ strict isolation)."""
    if trust == "external":
        return SandboxSpec(network="none", read_only_root=True, memory_limit="512m", cpu_limit=1.0)
    return SandboxSpec(network="bridge", read_only_root=False, memory_limit="", cpu_limit=0.0)


def require_sandbox(trust: str, spec: SandboxSpec) -> None:
    """Fail loudly if an external pack's sandbox is not isolated.

    Raises:
        SandboxError: An external pack's sandbox permits network, a writable
            root, or has no resource caps.
    """
    if trust != "external":
        return
    if spec.network != "none":
        raise SandboxError(f"external pack sandbox must use --network none; got {spec.network!r}")
    if not spec.read_only_root:
        raise SandboxError("external pack sandbox must use a read-only root")
    if not spec.memory_limit:
        raise SandboxError("external pack sandbox must set a memory cap")


class AuditEntry(BaseModel):
    """A hash-chained audit entry."""

    seq: int
    payload: str
    prev: str
    digest: str


class AuditChain(BaseModel):
    """An append-only, hash-chained audit log (tamper-evident)."""

    entries: list[AuditEntry] = Field(default_factory=list)

    @property
    def head(self) -> str:
        """The chain head (the last entry's digest)."""
        return self.entries[-1].digest if self.entries else ""

    def add(self, payload: str) -> AuditEntry:
        """Append a chained entry (its digest binds the previous head)."""
        seq = len(self.entries)
        prev = self.head
        digest = hashlib.sha256(f"{prev}|{seq}|{payload}".encode()).hexdigest()
        entry = AuditEntry(seq=seq, payload=payload, prev=prev, digest=digest)
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        """Whether the chain is intact (no entry tampered)."""
        prev = ""
        for index, entry in enumerate(self.entries):
            expected = hashlib.sha256(f"{prev}|{entry.seq}|{entry.payload}".encode()).hexdigest()
            if entry.seq != index or entry.prev != prev or entry.digest != expected:
                return False
            prev = entry.digest
        return True
