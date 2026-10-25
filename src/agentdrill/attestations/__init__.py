"""Drill attestations (M28, F96).

The in-toto ``agentdrill/drill-result/v1`` claim model + signing/verification
(28.4); freshness/invalidation and consumers land in 28.5. Design:
``docs/design/exposure-attestation-roe.md``; PRD 34 (R70).
"""

from agentdrill.attestations.drill import (
    PREDICATE_KIND,
    PREDICATE_TYPE,
    AttestationError,
    DrillClaim,
    DrillStatement,
    OutcomeCI,
    Signature,
    SignedAttestation,
    Subject,
    attest,
    build_statement,
    is_evidence,
    require_evidence,
    sign_statement,
    verify_statement,
)
from agentdrill.attestations.freshness import (
    CONSUMERS,
    Assessment,
    ConsumerVerdict,
    FreshnessContext,
    Invalidity,
    assess,
    check_freshness,
    require_fresh,
)

__all__ = [
    "CONSUMERS",
    "PREDICATE_KIND",
    "PREDICATE_TYPE",
    "Assessment",
    "AttestationError",
    "ConsumerVerdict",
    "DrillClaim",
    "DrillStatement",
    "FreshnessContext",
    "Invalidity",
    "OutcomeCI",
    "Signature",
    "SignedAttestation",
    "Subject",
    "assess",
    "attest",
    "build_statement",
    "check_freshness",
    "is_evidence",
    "require_evidence",
    "require_fresh",
    "sign_statement",
    "verify_statement",
]
