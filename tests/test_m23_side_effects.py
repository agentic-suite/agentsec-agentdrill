"""M23 23.4 — side-effect ledger + human-surface, F87 (RED → GREEN).

A witness DB / mock SaaS recording calls, and an approval-dialog vs
executed-action check; business-logic and approval effects are detected.
"""

from __future__ import annotations

from agentdrill.witness import (
    ApprovalCheck,
    MockSaas,
    SideEffectLedger,
    check_approval,
)


def test_mock_saas_records_calls() -> None:
    saas = MockSaas(name="billing")
    saas.call("charge_customer")
    assert saas.calls == ["charge_customer"]

    ledger = SideEffectLedger()
    ledger.record("billing:charge_customer")
    assert ledger.recorded == ["billing:charge_customer"]


def test_executed_without_approval_is_a_mismatch() -> None:
    check = check_approval(approved=False, executed=True)
    assert isinstance(check, ApprovalCheck)
    assert check.mismatch is True


def test_approved_and_executed_is_consistent() -> None:
    assert check_approval(approved=True, executed=True).mismatch is False
    assert check_approval(approved=False, executed=False).mismatch is False
