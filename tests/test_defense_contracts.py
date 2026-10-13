"""M6 6.7 — defense contracts (R22 / CUJ-15) (RED → GREEN).

Each ecosystem enforcer ships a required minimal pack; a contract regression
(a case it must block that it no longer blocks) blocks that enforcer's release.
"""

from __future__ import annotations

from agentdrill.oracles.base import Verdict
from agentdrill.oracles.contracts import (
    ContractResult,
    DefenseContract,
    defense_contracts,
    enforce_contract,
)


def _verdicts(*outcomes: str) -> list[Verdict]:
    return [Verdict(case_id=f"c{i}", outcome=o) for i, o in enumerate(outcomes)]  # type: ignore[arg-type]


def test_contract_passes_when_all_blocked() -> None:
    contract = DefenseContract(tool="agentgate", pack_ref="incidents-security@1.0.0", min_pass=1.0)
    result = enforce_contract(contract, _verdicts("blocked", "blocked"))
    assert isinstance(result, ContractResult)
    assert result.passed is True
    assert result.pass_rate == 1.0


def test_contract_regression_blocks_release() -> None:
    contract = DefenseContract(tool="agentgate", pack_ref="incidents-security@1.0.0", min_pass=1.0)
    result = enforce_contract(contract, _verdicts("blocked", "missed"))
    assert result.passed is False
    assert result.split.missed == 1


def test_contract_threshold() -> None:
    contract = DefenseContract(tool="x", pack_ref="p@1.0.0", min_pass=0.5)
    assert enforce_contract(contract, _verdicts("blocked", "missed")).passed is True


def test_wave0_enforcer_contracts_defined() -> None:
    contracts = defense_contracts()
    assert {
        "agentgate",
        "agentkeys",
        "agentseatbelt",
        "agentkernel",
        "policyweave-output",
        "agenthalt",
    } <= set(contracts)
    assert all(c.min_pass == 1.0 for c in contracts.values())
