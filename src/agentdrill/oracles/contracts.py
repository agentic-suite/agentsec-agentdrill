"""Defense contracts (M6 work item 6.7, R22 / CUJ-15).

Each ecosystem enforcer ships a **required minimal pack** that gates its own
release — a *contract regression* (a case it must block that it no longer
blocks) blocks the enforcer's release, because the same engine grades everything.
"""

from __future__ import annotations

from pydantic import BaseModel

from agentdrill.oracles.base import Verdict
from agentdrill.oracles.engine import OutcomeSplit, outcome_split


class DefenseContract(BaseModel):
    """The required minimal pack an enforcer ships to gate its own release."""

    tool: str
    pack_ref: str
    min_pass: float = 1.0


class ContractResult(BaseModel):
    """The outcome of enforcing a contract against a run's verdicts."""

    tool: str
    passed: bool
    pass_rate: float
    split: OutcomeSplit
    detail: str = ""


def enforce_contract(contract: DefenseContract, verdicts: list[Verdict]) -> ContractResult:
    """Check a contract: is the block rate at least ``min_pass``?"""
    split = outcome_split(verdicts)
    total = split.total
    pass_rate = (split.blocked / total) if total else 0.0
    passed = pass_rate >= contract.min_pass
    detail = (
        f"{split.blocked}/{total} blocked (>= {contract.min_pass:.2f})"
        if passed
        else f"contract regression: {split.blocked}/{total} blocked (< {contract.min_pass:.2f})"
    )
    return ContractResult(
        tool=contract.tool,
        passed=passed,
        pass_rate=pass_rate,
        split=split,
        detail=detail,
    )


def defense_contracts() -> dict[str, DefenseContract]:
    """The Wave-0 enforcer contracts (each gates its own release)."""
    specs = {
        "agentgate": "incidents-security@1.0.0",
        "agentkeys": "incidents-security@1.0.0",
        "agentseatbelt": "incidents-core@1.0.0",
        "agentkernel": "incidents-security@1.0.0",
        "policyweave-output": "incidents-core@1.0.0",
        "agenthalt": "kill-chain@1.0.0",
    }
    return {
        tool: DefenseContract(tool=tool, pack_ref=pack_ref, min_pass=1.0)
        for tool, pack_ref in specs.items()
    }
