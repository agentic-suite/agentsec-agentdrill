"""M25 25.1 — Defense Contract + SDK, F90 (RED → GREEN).

A contract (decision points, I/O shape, evidence, config digest, fail-mode,
version, ToS notes) + an SDK; a request/response defense adapts.
"""

from __future__ import annotations

from typing import Any

from agentdrill.byod import DefenseContract, DefenseSDK, build_contract, config_digest


def _contract() -> DefenseContract:
    return build_contract(
        name="acme-guard",
        decision_points=["pre_tool", "post_tool"],
        io_shape="request/response",
        evidence=["decision", "rationale"],
        config={"policy": "deny-destructive"},
        fail_mode="closed",
        version="1.0.0",
        tos_notes="OSS, Apache-2.0",
    )


def test_contract_carries_its_fields() -> None:
    contract = _contract()
    assert isinstance(contract, DefenseContract)
    assert contract.decision_points == ["pre_tool", "post_tool"]
    assert contract.io_shape == "request/response"
    assert contract.fail_mode == "closed"
    assert contract.version == "1.0.0"
    assert contract.tos_notes
    assert contract.config_digest


def test_digest_binds_the_config() -> None:
    assert config_digest({"a": 1}) == config_digest({"a": 1})
    assert config_digest({"a": 1}) != config_digest({"a": 2})
    assert _contract().config_digest == config_digest({"policy": "deny-destructive"})


def test_sdk_round_trips_a_request_response_defense() -> None:
    def decide(request: dict[str, Any]) -> dict[str, Any]:
        return {"decision": "deny" if request.get("tool") == "shell" else "allow"}

    sdk = DefenseSDK(_contract(), decide=decide)
    assert sdk.evaluate({"tool": "shell"})["decision"] == "deny"
    assert sdk.evaluate({"tool": "http"})["decision"] == "allow"
