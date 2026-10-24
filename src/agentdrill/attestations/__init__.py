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

__all__ = [
    "PREDICATE_KIND",
    "PREDICATE_TYPE",
    "AttestationError",
    "DrillClaim",
    "DrillStatement",
    "OutcomeCI",
    "Signature",
    "SignedAttestation",
    "Subject",
    "attest",
    "build_statement",
    "is_evidence",
    "require_evidence",
    "sign_statement",
    "verify_statement",
]
