"""Pack registry package (M16).

Content-addressed signed index (16.1), signing + verified publishers (16.2),
trust levels (16.3), the contribution flow (16.4), deprecation/takedown (16.5)
and registry sync (16.6). Design: ``docs/prd/17-pack-registry-and-governance.md``.
"""

from agentdrill.registry.contribution import (
    ContributionError,
    LintFinding,
    LintResult,
    ReviewDecision,
    anyone_approved,
    lint_pack,
    require_publishable,
)
from agentdrill.registry.governance import (
    GovernanceEvent,
    GovernanceKind,
    GovernanceLog,
    apply_deprecation,
    apply_takedown,
)
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
from agentdrill.registry.trust import (
    TRUST_LEVELS,
    TrustError,
    enforce_trust,
    is_benchmark_publishable,
    is_sandbox_required,
    normalize_trust,
)

__all__ = [
    "TRUST_LEVELS",
    "ContributionError",
    "GovernanceEvent",
    "GovernanceKind",
    "GovernanceLog",
    "HmacSigner",
    "LintFinding",
    "LintResult",
    "PackVerification",
    "PackVerificationError",
    "Publisher",
    "PublisherRegistry",
    "RegistryEntry",
    "RegistryIndex",
    "ReviewDecision",
    "Signer",
    "TrustError",
    "Verifier",
    "anyone_approved",
    "apply_deprecation",
    "apply_takedown",
    "build_index",
    "content_address",
    "enforce_trust",
    "entry_for_pack",
    "is_benchmark_publishable",
    "is_sandbox_required",
    "lint_pack",
    "normalize_trust",
    "require_publishable",
    "require_verified",
    "sign_entry",
    "sign_index",
    "verify_entry",
    "verify_index",
    "verify_pack",
]
