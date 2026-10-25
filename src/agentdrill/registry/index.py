"""Registry model + content-addressed signed index (M16 16.1).

A :class:`RegistryIndex` is a content-addressed, signed ``registry.json``:
each :class:`RegistryEntry` is addressed by the SHA-256 of the pack content,
and the whole index carries a signature so it verifies **offline** — no
mandatory central service. Design: [PRD 17](../../docs/prd/17-pack-registry-and-governance.md).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.models.attack_pack import AttackPack
from agentdrill.registry.signing import Signer as SignerProtocol
from agentdrill.registry.signing import Verifier


class RegistryEntry(BaseModel):
    """One pack in the registry index."""

    name: str
    version: str
    content_hash: str
    publisher: str = ""
    trust: str = "local"
    signature: str = ""
    deprecated: bool = False
    migration_note: str | None = None


class RegistryIndex(BaseModel):
    """A content-addressed, signed index of registry entries."""

    version: int = 1
    entries: list[RegistryEntry] = Field(default_factory=list)
    signature: str = ""

    def entry(self, name: str, version: str) -> RegistryEntry | None:
        """The entry for ``name@version``, or ``None``."""
        return next((e for e in self.entries if e.name == name and e.version == version), None)

    def canonical(self) -> bytes:
        """The canonical (signature-excluded) bytes the signature covers."""
        payload = {
            "version": self.version,
            "entries": [e.model_dump(exclude={"signature"}) for e in self.entries],
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_address(content: BaseModel | dict[str, Any]) -> str:
    """The SHA-256 content address of a pack (or any JSON-serializable content)."""
    if isinstance(content, BaseModel):
        data: Any = content.model_dump()
    else:
        data = content
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def entry_for_pack(
    pack: AttackPack,
    *,
    publisher: str = "",
    trust: str = "local",
    signature: str = "",
) -> RegistryEntry:
    """Build a content-addressed registry entry for ``pack``."""
    return RegistryEntry(
        name=pack.pack.name,
        version=pack.pack.version,
        content_hash=content_address(pack),
        publisher=publisher,
        trust=trust,
        signature=signature,
    )


def build_index(entries: list[RegistryEntry]) -> RegistryIndex:
    """Build an unsigned index from ``entries`` (sorted by name, version)."""
    ordered = sorted(entries, key=lambda e: (e.name, e.version))
    return RegistryIndex(entries=ordered)


def sign_index(index: RegistryIndex, signer: SignerProtocol) -> RegistryIndex:
    """Sign ``index`` over its canonical bytes; returns the signed index."""
    index.signature = signer.sign(index.canonical())
    return index


def verify_index(index: RegistryIndex, verifier: Verifier) -> bool:
    """Verify an index's signature offline; ``False`` when unsigned/invalid."""
    if not index.signature:
        return False
    return verifier.verify(index.canonical(), index.signature)
