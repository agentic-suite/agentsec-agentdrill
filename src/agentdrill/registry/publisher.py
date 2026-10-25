"""Signing + verified publishers (M16 16.2).

A pack entry is signed and bound to a **verified publisher identity**; an
unsigned pack, a tampered pack, or an unknown publisher is rejected before
install. Design: ``docs/prd/17-pack-registry-and-governance.md``.
"""

from __future__ import annotations

import json

from pydantic import BaseModel

from agentdrill.registry.index import RegistryEntry
from agentdrill.registry.signing import Signer as SignerProtocol
from agentdrill.registry.signing import Verifier


class PackVerificationError(ValueError):
    """Raised when a pack entry is not verifiably signed by a known publisher."""


class Publisher(BaseModel):
    """A verified publisher identity and its signing key id."""

    identity: str
    key_id: str


class PublisherRegistry:
    """The set of verified publishers."""

    def __init__(self) -> None:
        self._publishers: dict[str, Publisher] = {}

    def add(self, publisher: Publisher) -> None:
        """Register a verified publisher."""
        self._publishers[publisher.identity] = publisher

    def verified(self, identity: str) -> bool:
        """Whether ``identity`` is a verified publisher."""
        return identity in self._publishers

    def key_id(self, identity: str) -> str | None:
        """The signing key id bound to ``identity`` (or ``None``)."""
        publisher = self._publishers.get(identity)
        return publisher.key_id if publisher else None


class PackVerification(BaseModel):
    """The verification verdict for one pack entry."""

    identity: str
    verified: bool
    reason: str = ""


def _pack_payload(entry: RegistryEntry) -> bytes:
    """The canonical bytes a pack entry's signature covers."""
    payload = {
        "name": entry.name,
        "version": entry.version,
        "content_hash": entry.content_hash,
        "publisher": entry.publisher,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_entry(entry: RegistryEntry, signer: SignerProtocol) -> RegistryEntry:
    """Sign ``entry`` over its content address; returns the signed entry."""
    entry.signature = signer.sign(_pack_payload(entry))
    return entry


def verify_entry(entry: RegistryEntry, verifier: Verifier) -> bool:
    """Whether ``entry``'s signature verifies over its content (unsigned ⇒ False)."""
    if not entry.signature:
        return False
    return verifier.verify(_pack_payload(entry), entry.signature)


def verify_pack(
    entry: RegistryEntry,
    *,
    verifier: Verifier,
    publishers: PublisherRegistry,
) -> PackVerification:
    """Verify a pack entry: unsigned, tampered, or unknown publisher ⇒ rejected."""
    if not entry.signature:
        return PackVerification(identity=entry.publisher, verified=False, reason="unsigned pack")
    if not verify_entry(entry, verifier):
        return PackVerification(
            identity=entry.publisher, verified=False, reason="signature does not verify (tampered)"
        )
    if not publishers.verified(entry.publisher):
        return PackVerification(
            identity=entry.publisher,
            verified=False,
            reason=f"unknown publisher: {entry.publisher!r}",
        )
    expected_key = publishers.key_id(entry.publisher)
    if expected_key is not None and getattr(verifier, "key_id", None) != expected_key:
        return PackVerification(
            identity=entry.publisher,
            verified=False,
            reason=f"publisher key mismatch: {expected_key!r}",
        )
    return PackVerification(identity=entry.publisher, verified=True, reason="verified")


def require_verified(
    entry: RegistryEntry,
    *,
    verifier: Verifier,
    publishers: PublisherRegistry,
) -> None:
    """Fail loudly unless ``entry`` is a verified, signed pack.

    Raises:
        PackVerificationError: Unsigned, tampered, or an unknown/mismatched
            publisher.
    """
    verdict = verify_pack(entry, verifier=verifier, publishers=publishers)
    if not verdict.verified:
        raise PackVerificationError(f"pack {entry.name}@{entry.version}: {verdict.reason}")
