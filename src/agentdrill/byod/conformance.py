"""Conformance kit (M25 25.2, F90).

Round-trip, determinism, evidence-integrity and fail-mode checks; an adapter
must pass 100% before listing. Design:
``docs/prd/29-bring-your-own-defense.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentdrill.byod.contract import DefenseContract, DefenseSDK


class ConformanceError(ValueError):
    """Raised when a defense does not pass the conformance kit."""


class ConformanceCheck(BaseModel):
    """One conformance check."""

    name: str
    ok: bool


class ConformanceResult(BaseModel):
    """The conformance verdict for a defense."""

    level: str
    checks: list[ConformanceCheck] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Whether every check passed (100%)."""
        return bool(self.checks) and all(check.ok for check in self.checks)


def run_conformance(
    contract: DefenseContract,
    sdk: DefenseSDK,
    *,
    sample_requests: Sequence[dict[str, object]],
) -> ConformanceResult:
    """Run the conformance kit: round-trip, determinism, evidence, fail-mode."""
    round_trip = all(isinstance(sdk.evaluate(dict(request)), dict) for request in sample_requests)
    deterministic = all(
        sdk.evaluate(dict(request)) == sdk.evaluate(dict(request)) for request in sample_requests
    )
    checks = [
        ConformanceCheck(name="round_trip", ok=round_trip),
        ConformanceCheck(name="determinism", ok=deterministic),
        ConformanceCheck(name="evidence_integrity", ok=bool(contract.evidence)),
        ConformanceCheck(name="fail_mode", ok=contract.fail_mode in ("open", "closed")),
    ]
    passed = all(check.ok for check in checks)
    return ConformanceResult(level="conformant" if passed else "none", checks=checks)


def require_conformant(result: ConformanceResult) -> None:
    """Fail loudly if a defense did not pass the kit 100%.

    Raises:
        ConformanceError: One or more conformance checks failed.
    """
    if not result.passed:
        failed = [check.name for check in result.checks if not check.ok]
        raise ConformanceError(f"defense is not conformant (failed: {failed})")
