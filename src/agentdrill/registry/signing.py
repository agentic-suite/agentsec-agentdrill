"""Registry signing (M16 16.1/16.2).

A :class:`Signer`/:class:`Verifier` abstraction over a canonical payload. The
default :class:`HmacSigner` is a stdlib keyed signature so an index verifies
**offline** without a central service or an extra dependency; the production
path binds a Sigstore identity (16.2).
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Protocol


class Signer(Protocol):
    """Signs a canonical payload."""

    key_id: str

    def sign(self, payload: bytes) -> str: ...


class Verifier(Protocol):
    """Verifies a canonical payload against a signature."""

    def verify(self, payload: bytes, signature: str) -> bool: ...


class HmacSigner:
    """A keyed HMAC-SHA256 signer/verifier (stdlib, offline-verifiable).

    Args:
        key: The shared secret key.
        key_id: A stable identifier for the key (bound into the signature).
    """

    def __init__(self, key: bytes, key_id: str = "local") -> None:
        self._key = key
        self.key_id = key_id

    def _digest(self, payload: bytes) -> str:
        return hmac.new(self._key, payload, hashlib.sha256).hexdigest()

    def sign(self, payload: bytes) -> str:
        """Sign ``payload``; the signature is ``<key_id>:<hexdigest>``."""
        return f"{self.key_id}:{self._digest(payload)}"

    def verify(self, payload: bytes, signature: str) -> bool:
        """Verify ``signature`` over ``payload`` (constant-time compare)."""
        key_id, _, digest = signature.partition(":")
        if key_id != self.key_id or not digest:
            return False
        return hmac.compare_digest(digest, self._digest(payload))
