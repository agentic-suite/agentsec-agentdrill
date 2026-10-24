"""Attestation freshness + reference consumers (M28 28.5, F96).

An attestation is a claim about a moment: **auto-invalidate** it when the world
moves on — a config-digest change, a security-deprecated pack, a relevant new
incident, an oracle major bump, a waiver expiry, or the attestation's own expiry.
The ≥4 reference consumers (CLI, GitHub Action, K8s admission policy, agentgate
start-time check) accept only a **valid, fresh, evidence** attestation. Design:
``docs/design/exposure-attestation-roe.md``; PRD 34 (R70).
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from agentdrill.attestations.drill import (
    AttestationError,
    DrillClaim,
    SignedAttestation,
    is_evidence,
    verify_statement,
)

#: The reference consumers of a drill attestation.
CONSUMERS: tuple[str, ...] = ("cli", "github-action", "k8s-admission", "agentgate")


class FreshnessContext(BaseModel):
    """What has changed since an attestation was issued."""

    config_digest: str
    deprecated_packs: list[str] = Field(default_factory=list)
    new_incidents: list[str] = Field(default_factory=list)
    oracle_versions: dict[str, str] = Field(default_factory=dict)
    expired_waivers: list[str] = Field(default_factory=list)


class Invalidity(BaseModel):
    """Whether an attestation is stale, and why."""

    stale: bool
    reasons: list[str] = Field(default_factory=list)


class ConsumerVerdict(BaseModel):
    """One consumer's accept/reject decision."""

    consumer: str
    accept: bool
    reason: str = ""


class Assessment(BaseModel):
    """The full assessment of an attestation for its consumers."""

    valid: bool
    fresh: bool
    evidence: bool
    reasons: list[str] = Field(default_factory=list)
    consumers: list[ConsumerVerdict] = Field(default_factory=list)


def _major(version: str) -> int:
    """The major component of a version string (0 when unparseable)."""
    head = version.split(".", 1)[0]
    return int(head) if head.isdigit() else 0


def check_freshness(claim: DrillClaim, context: FreshnessContext, *, now: str) -> Invalidity:
    """Whether ``claim`` is stale relative to ``context`` at ``now``."""
    reasons: list[str] = []
    if claim.config_digest != context.config_digest:
        reasons.append("config_changed")
    if any(pack in context.deprecated_packs for pack in claim.packs):
        reasons.append("pack_deprecated")
    if context.new_incidents:
        reasons.append("new_incident")
    for oracle, version in claim.oracle_versions.items():
        current = context.oracle_versions.get(oracle)
        if current is not None and _major(current) != _major(version):
            reasons.append("oracle_major_bump")
    if any(waiver in context.expired_waivers for waiver in claim.waivers):
        reasons.append("waiver_expired")
    if date.fromisoformat(now) > date.fromisoformat(claim.expires):
        reasons.append("attestation_expired")
    return Invalidity(stale=bool(reasons), reasons=reasons)


def require_fresh(invalidity: Invalidity) -> None:
    """Fail loudly unless the attestation is fresh.

    Raises:
        AttestationError: The attestation is stale.
    """
    if invalidity.stale:
        raise AttestationError(f"attestation is stale: {invalidity.reasons}")


def assess(
    signed: SignedAttestation, context: FreshnessContext, *, now: str, secret: str
) -> Assessment:
    """Verify, freshness-check and evidence-check an attestation for all consumers."""
    valid = verify_statement(signed, secret=secret)
    claim = signed.statement.predicate
    invalidity = check_freshness(claim, context, now=now)
    evidence = is_evidence(claim.realness)

    reasons = list(invalidity.reasons)
    if not valid:
        reasons.append("signature_invalid")
    if not evidence:
        reasons.append("non_evidence")
    accept = valid and not invalidity.stale and evidence
    consumers = [
        ConsumerVerdict(consumer=consumer, accept=accept, reason="; ".join(reasons))
        for consumer in CONSUMERS
    ]
    return Assessment(
        valid=valid,
        fresh=not invalidity.stale,
        evidence=evidence,
        reasons=reasons,
        consumers=consumers,
    )
