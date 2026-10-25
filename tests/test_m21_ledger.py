"""M21 21.1 — absorption ledger verification (RED → GREEN).

Every capability row is delivered **and tested**, delegated to a named tool, or
waived with a reason — no capability is silently dropped.
"""

from __future__ import annotations

import pytest

from agentdrill.parity import (
    DEFAULT_LEDGER,
    AbsorptionLedger,
    LedgerError,
    LedgerRow,
    build_ledger,
    validate_ledger,
)


def test_default_ledger_is_complete() -> None:
    ledger = build_ledger(list(DEFAULT_LEDGER))
    assert isinstance(ledger, AbsorptionLedger)
    assert ledger.rows
    validate_ledger(ledger)  # no raise


def test_a_waived_row_requires_a_reason() -> None:
    ledger = build_ledger([LedgerRow(capability="c", status="waived", detail="")])
    with pytest.raises(LedgerError, match="reason"):
        validate_ledger(ledger)


def test_a_delegated_row_requires_a_named_tool() -> None:
    ledger = build_ledger([LedgerRow(capability="c", status="delegated", detail="")])
    with pytest.raises(LedgerError, match="named tool"):
        validate_ledger(ledger)


def test_unknown_status_fails_loudly() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LedgerRow(capability="c", status="ghost", detail="")  # type: ignore[arg-type]
