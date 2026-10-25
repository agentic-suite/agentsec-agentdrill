"""Drill attestation — the claim model + in-toto predicate (M28 28.4, F96).

A drill **attestation** is an in-toto statement whose predicate
(``agentdrill/drill-result/v1``) binds a ``config_digest`` and carries every
field a consumable claim needs: packs@version/hash, tiers/k, outcomes **with
CIs**, witness coverage, ``live|fixture|mock``, oracle versions, known
misses/waivers, the lab, standards pins, issued/expires — and, always, **what was
NOT drilled**. The statement is signed and verifier-checked; a ``mock``/``fixture``
attestation is **non-evidence** and is refused. Design:
``docs/design/exposure-attestation-roe.md``; PRD 34 (R70).
"""

from __future__ import annotations

import hashlib
import hmac
import json

from pydantic import BaseModel, ConfigDict, Field

#: The in-toto statement type.
PREDICATE_TYPE = "https://in-toto.io/Statement/v1"

#: The agentdrill drill-result predicate kind.
PREDICATE_KIND = "agentdrill/drill-result/v1"


class AttestationError(ValueError):
    """Raised when an attestation is invalid or non-evidence."""


class OutcomeCI(BaseModel):
    """An outcome rate with its confidence interval."""

    point: float
    low: float
    high: float
    n: int


class DrillClaim(BaseModel):
    """The drill-result claim (the attestation predicate body)."""

    config_digest: str
    issued: str
    expires: str
    packs: list[str] = Field(default_factory=list)
    tiers: list[str] = Field(default_factory=list)
    k: int | None = None
    outcomes: dict[str, OutcomeCI] = Field(default_factory=dict)
    witness_coverage: float = 0.0
    realness: str = "mock"
    oracle_versions: dict[str, str] = Field(default_factory=dict)
    known_misses: list[str] = Field(default_factory=list)
    waivers: list[str] = Field(default_factory=list)
    lab: str | None = None
    standards_pins: dict[str, str] = Field(default_factory=dict)
    #: What the drill did NOT cover (always non-empty).
    not_drilled: list[str] = Field(default_factory=list)


class Subject(BaseModel):
    """An in-toto subject (the digested artifact)."""

    name: str
    digest: dict[str, str]


class DrillStatement(BaseModel):
    """The in-toto statement wrapping a :class:`DrillClaim`."""

    model_config = ConfigDict(populate_by_name=True)

    statement_type: str = Field(default=PREDICATE_TYPE, alias="_type")
    subject: list[Subject]
    predicateType: str = PREDICATE_KIND
    predicate: DrillClaim


class Signature(BaseModel):
    """One signature over the statement."""

    keyid: str
    sig: str


class SignedAttestation(BaseModel):
    """A signed drill attestation (Sigstore-envelope shaped)."""

    statement: DrillStatement
    signatures: list[Signature] = Field(default_factory=list)
    transparency_log: str | None = None


def is_evidence(realness: str) -> bool:
    """Whether a realness label is evidence (only ``live`` is)."""
    return realness == "live"


def require_evidence(realness: str) -> None:
    """Fail loudly unless ``realness`` is evidence.

    Raises:
        AttestationError: The realness is ``mock`` or ``fixture``.
    """
    if not is_evidence(realness):
        raise AttestationError(
            f"realness {realness!r} is non-evidence (mock/fixture never attest)"
        )


def build_statement(claim: DrillClaim) -> DrillStatement:
    """Wrap ``claim`` in an in-toto statement.

    Raises:
        AttestationError: The claim lists nothing under ``not_drilled`` (the
            predicate must always state what was NOT tested), or its realness is
            not evidence.
    """
    if not claim.not_drilled:
        raise AttestationError(
            "an attestation must list what was NOT drilled (not_drilled is empty)"
        )
    require_evidence(claim.realness)
    return DrillStatement(
        subject=[Subject(name="agentdrill-drill", digest={"sha256": claim.config_digest})],
        predicate=claim,
    )


def _canonical(statement: DrillStatement) -> str:
    """The canonical signing payload (stable key order, compact separators)."""
    return json.dumps(statement.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))


def sign_statement(statement: DrillStatement, *, keyid: str, secret: str) -> SignedAttestation:
    """Sign ``statement`` (HMAC-SHA256 over a canonical payload)."""
    digest = hmac.new(
        secret.encode("utf-8"), _canonical(statement).encode("utf-8"), hashlib.sha256
    )
    return SignedAttestation(
        statement=statement,
        signatures=[Signature(keyid=keyid, sig=f"sha256={digest.hexdigest()}")],
    )


def verify_statement(signed: SignedAttestation, *, secret: str) -> bool:
    """Whether ``signed`` carries a valid signature for ``secret`` (fast, forgery-safe)."""
    if not signed.signatures:
        return False
    expected = sign_statement(signed.statement, keyid=signed.signatures[0].keyid, secret=secret)
    return hmac.compare_digest(signed.signatures[0].sig, expected.signatures[0].sig)


def attest(claim: DrillClaim, *, keyid: str, secret: str) -> SignedAttestation:
    """Build and sign a drill attestation from ``claim``."""
    return sign_statement(build_statement(claim), keyid=keyid, secret=secret)
