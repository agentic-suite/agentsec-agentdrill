"""Pack registry package (M16).

Content-addressed signed index (16.1), signing + verified publishers (16.2),
trust levels (16.3), the contribution flow (16.4), deprecation/takedown (16.5)
and registry sync (16.6). Design: ``docs/prd/17-pack-registry-and-governance.md``.
"""

from agentdrill.registry.index import (
    RegistryEntry,
    RegistryIndex,
    build_index,
    content_address,
    entry_for_pack,
    sign_index,
    verify_index,
)
from agentdrill.registry.publisher import (
    PackVerification,
    PackVerificationError,
    Publisher,
    PublisherRegistry,
    require_verified,
    sign_entry,
    verify_entry,
    verify_pack,
)
from agentdrill.registry.signing import HmacSigner, Signer, Verifier

__all__ = [
    "HmacSigner",
    "PackVerification",
    "PackVerificationError",
    "Publisher",
    "PublisherRegistry",
    "RegistryEntry",
    "RegistryIndex",
    "Signer",
    "Verifier",
    "build_index",
    "content_address",
    "entry_for_pack",
    "require_verified",
    "sign_entry",
    "sign_index",
    "verify_entry",
    "verify_index",
    "verify_pack",
]
