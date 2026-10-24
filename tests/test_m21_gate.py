"""M21 21.3 — parity gate (RED → GREEN).

An executable gate asserting the absorption ledger + gap closure; it is green
for the default ledger/gaps and **blocks on drift**.
"""

from __future__ import annotations

import pytest

from agentdrill.parity import (
    AbsorptionLedger,
    Gap,
    LedgerRow,
    ParityError,
    ParityResult,
    build_ledger,
    default_gaps,
    parity_gate,
    require_parity,
)
from agentdrill.parity.ledger import DEFAULT_LEDGER


def test_parity_gate_is_green_for_the_default_ledger_and_gaps() -> None:
    result = parity_gate(build_ledger(list(DEFAULT_LEDGER)), default_gaps())
    assert isinstance(result, ParityResult)
    assert result.ok is True
    assert result.problems == []


def test_gate_blocks_on_ledger_drift() -> None:
    bad = build_ledger([LedgerRow(capability="c", status="waived", detail="")])
    result = parity_gate(bad, default_gaps())
    assert result.ok is False
    assert result.problems
    with pytest.raises(ParityError):
        require_parity(result)


def test_gate_blocks_on_gap_drift() -> None:
    bad_gaps = [Gap(id="GX", description="d", status="closed", evidence="")]
    result = parity_gate(build_ledger(list(DEFAULT_LEDGER)), bad_gaps)
    assert result.ok is False


def test_empty_ledger_blocks() -> None:
    assert parity_gate(AbsorptionLedger(rows=[]), default_gaps()).ok is False
