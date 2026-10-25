"""Rules of engagement (M28 28.6, F97).

A **signed, versioned** RoE declares what may be fired at, in what environment,
with which effect classes, under which ceilings and windows — and a **fail-closed
preflight** that refuses a case that violates any rule, emitting a per-action
**scope receipt** for the audit trail. Zero out-of-scope actions is the invariant.
Design: ``docs/design/exposure-attestation-roe.md``; PRD 35 (R71).
"""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

#: The environment class an RoE covers.
EnvClass = Literal["ephemeral", "purple", "prod"]

#: The attacker-tier ranking (T0 strongest control … T3 deferred).
_TIER_RANK: dict[str, int] = {"T0": 0, "T1": 1, "T2": 2, "T3": 3}

#: Effect classes a production environment must never permit.
_PROD_FORBIDDEN_EFFECTS = frozenset({"destructive"})


class RoEError(ValueError):
    """Raised when an RoE is unsigned, or a case is refused by preflight."""


class RoE(BaseModel):
    """A signed, versioned rules-of-engagement document."""

    version: str
    targets: list[str] = Field(default_factory=list)
    ownership: dict[str, str] = Field(default_factory=dict)
    env_class: EnvClass = "ephemeral"
    allowed_effect_classes: list[str] = Field(default_factory=list)
    canary_only: bool = True
    windows: list[str] = Field(default_factory=list)
    rate_ceiling: int | None = None
    cost_ceiling_usd: float | None = None
    blast_radius_cap: int | None = None
    tier_ceiling: str = "T2"
    approvers: list[str] = Field(default_factory=list)
    contacts: list[str] = Field(default_factory=list)
    abort_conditions: list[str] = Field(default_factory=list)
    signature: str = ""


class CaseRequest(BaseModel):
    """What a case proposes to do (checked against the RoE)."""

    case_id: str
    target: str
    effect_class: str
    now: str
    tier: str = "T0"
    canary: bool = True
    rate: int = 0
    cost_usd: float = 0.0
    blast_radius: int = 0
    third_party_hosts: list[str] = Field(default_factory=list)
    witness_healthy: bool = True
    cleanup_verified: bool = True


class PreflightResult(BaseModel):
    """The fail-closed preflight outcome (allowed, or the reasons refused)."""

    allowed: bool
    refusals: list[str] = Field(default_factory=list)


class ScopeReceipt(BaseModel):
    """A per-action scope receipt (hash-chained)."""

    case_id: str
    target: str
    effect_class: str
    at: str
    roe_version: str = ""
    hash_prev: str = ""
    digest: str = ""


def _canonical_roe(roe: RoE) -> str:
    return json.dumps(roe.model_dump(exclude={"signature"}), sort_keys=True, separators=(",", ":"))


def sign_roe(roe: RoE, *, secret: str) -> RoE:
    """Return a copy of ``roe`` carrying an HMAC-SHA256 signature."""
    digest = hmac.new(secret.encode("utf-8"), _canonical_roe(roe).encode("utf-8"), hashlib.sha256)
    return roe.model_copy(update={"signature": f"sha256={digest.hexdigest()}"})


def verify_roe(roe: RoE, *, secret: str) -> bool:
    """Whether ``roe`` carries a valid signature for ``secret``."""
    if not roe.signature:
        return False
    return hmac.compare_digest(roe.signature, sign_roe(roe, secret=secret).signature)


def require_signed(roe: RoE) -> None:
    """Fail loudly unless the RoE is signed.

    Raises:
        RoEError: The RoE carries no signature.
    """
    if not roe.signature:
        raise RoEError("the RoE is unsigned; a non-demo run requires a signed RoE")


def _in_window(windows: Sequence[str], now: str) -> bool:
    for window in windows:
        start, _, end = window.partition("/")
        if start <= now <= end:
            return True
    return False


def preflight(roe: RoE, request: CaseRequest) -> PreflightResult:
    """Check ``request`` against ``roe``; refuse (fail-closed) on any violation."""
    refusals: list[str] = []
    if not roe.signature:
        refusals.append("roe_unsigned")
    if request.target not in roe.targets:
        refusals.append("target_out_of_scope")
    if not roe.ownership.get(request.target):
        refusals.append("ownership_unverified")
    if request.effect_class not in roe.allowed_effect_classes:
        refusals.append("effect_class_not_allowed")
    if roe.env_class == "prod" and request.effect_class in _PROD_FORBIDDEN_EFFECTS:
        refusals.append("env_would_not_permit_effect")
    if roe.canary_only and not request.canary:
        refusals.append("canary_required")
    if roe.windows and not _in_window(roe.windows, request.now):
        refusals.append("outside_window")
    if roe.rate_ceiling is not None and request.rate > roe.rate_ceiling:
        refusals.append("rate_ceiling_exceeded")
    if roe.cost_ceiling_usd is not None and request.cost_usd > roe.cost_ceiling_usd:
        refusals.append("cost_ceiling_exceeded")
    if roe.blast_radius_cap is not None and request.blast_radius > roe.blast_radius_cap:
        refusals.append("blast_radius_cap_exceeded")
    if _TIER_RANK.get(request.tier, 9) > _TIER_RANK.get(roe.tier_ceiling, 0):
        refusals.append("tier_ceiling_exceeded")
    if request.third_party_hosts:
        refusals.append("third_party_hosts_resolvable")
    if not request.witness_healthy:
        refusals.append("witness_unhealthy")
    if not request.cleanup_verified:
        refusals.append("cleanup_unverified")
    return PreflightResult(allowed=not refusals, refusals=refusals)


def require_allowed(result: PreflightResult) -> None:
    """Fail loudly unless the preflight allowed the case.

    Raises:
        RoEError: The case was refused.
    """
    if not result.allowed:
        raise RoEError(f"preflight refused the case: {result.refusals}")


def _canonical_receipt(receipt: ScopeReceipt) -> str:
    return json.dumps(receipt.model_dump(exclude={"digest"}), sort_keys=True, separators=(",", ":"))


def scope_receipt(
    roe: RoE, request: CaseRequest, *, prev: ScopeReceipt | None = None
) -> ScopeReceipt:
    """Emit a hash-chained scope receipt for a fired action."""
    receipt = ScopeReceipt(
        case_id=request.case_id,
        target=request.target,
        effect_class=request.effect_class,
        at=request.now,
        roe_version=roe.version,
        hash_prev=prev.digest if prev is not None else "",
    )
    digest = hashlib.sha256(
        (receipt.hash_prev + _canonical_receipt(receipt)).encode("utf-8")
    ).hexdigest()
    return receipt.model_copy(update={"digest": digest})


def verify_receipt_chain(receipts: Sequence[ScopeReceipt]) -> bool:
    """Whether a sequence of scope receipts is an intact, unbroken chain."""
    prev = ""
    for receipt in receipts:
        if receipt.hash_prev != prev:
            return False
        expected = hashlib.sha256(
            (receipt.hash_prev + _canonical_receipt(receipt)).encode("utf-8")
        ).hexdigest()
        if not hmac.compare_digest(receipt.digest, expected):
            return False
        prev = receipt.digest
    return True
