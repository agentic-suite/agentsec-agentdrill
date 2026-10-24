"""Rules of engagement & safe-fire interlocks (M28, F97).

RoE signing + fail-closed preflight + scope receipts (28.6); the safe-fire
interlocks (abort, dead-man switch, watchdogs, verified teardown, consent gate)
land in 28.7. Design: ``docs/design/exposure-attestation-roe.md``; PRD 35 (R71).
"""

from agentdrill.roe.rules import (
    CaseRequest,
    EnvClass,
    PreflightResult,
    RoE,
    RoEError,
    ScopeReceipt,
    preflight,
    require_allowed,
    require_signed,
    scope_receipt,
    sign_roe,
    verify_receipt_chain,
    verify_roe,
)

__all__ = [
    "CaseRequest",
    "EnvClass",
    "PreflightResult",
    "RoE",
    "RoEError",
    "ScopeReceipt",
    "preflight",
    "require_allowed",
    "require_signed",
    "scope_receipt",
    "sign_roe",
    "verify_receipt_chain",
    "verify_roe",
]
