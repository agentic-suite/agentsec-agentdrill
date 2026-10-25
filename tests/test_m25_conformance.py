"""M25 25.2 — conformance kit, F90 (RED → GREEN).

Round-trip, determinism, evidence integrity and fail-mode checks award a
conformance level; 100% pass before listing.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentdrill.byod import (
    ConformanceError,
    ConformanceResult,
    DefenseSDK,
    build_contract,
    require_conformant,
    run_conformance,
)

REQUESTS = [{"tool": "shell"}, {"tool": "http"}]


def _contract(*, evidence: list[str] | None = None):
    return build_contract(
        name="acme",
        decision_points=["pre_tool"],
        io_shape="request/response",
        evidence=evidence if evidence is not None else ["decision"],
        config={"policy": "deny"},
        fail_mode="closed",
        version="1.0.0",
    )


def _sdk(contract, decide):  # type: ignore[no-untyped-def]
    return DefenseSDK(contract, decide=decide)


def test_conformant_adapter_passes() -> None:
    sdk = _sdk(_contract(), lambda r: {"decision": "deny"})
    result = run_conformance(_contract(), sdk, sample_requests=REQUESTS)
    assert isinstance(result, ConformanceResult)
    assert result.passed is True
    assert result.level == "conformant"
    require_conformant(result)  # no raise


def test_non_deterministic_adapter_fails() -> None:
    counter = {"n": 0}

    def decide(r: dict[str, Any]) -> dict[str, Any]:
        counter["n"] += 1
        return {"decision": "deny", "n": counter["n"]}

    result = run_conformance(_contract(), _sdk(_contract(), decide), sample_requests=REQUESTS)
    assert result.passed is False
    with pytest.raises(ConformanceError):
        require_conformant(result)


def test_missing_evidence_fails() -> None:
    sdk = _sdk(_contract(evidence=[]), lambda r: {"decision": "deny"})
    result = run_conformance(_contract(evidence=[]), sdk, sample_requests=REQUESTS)
    assert result.passed is False
