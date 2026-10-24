"""Parity gate (M21 21.3).

An executable gate asserting the absorption ledger + gap closure; it is green
for the default ledger/gaps and **blocks on drift**. Design:
``docs/prd/10-feature-parity.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentdrill.parity.gaps import Gap, GapError, validate_gaps
from agentdrill.parity.ledger import AbsorptionLedger, LedgerError, validate_ledger


class ParityError(ValueError):
    """Raised when the parity gate is red (ledger or gap drift)."""


class ParityResult(BaseModel):
    """The parity gate outcome."""

    ok: bool
    problems: list[str] = Field(default_factory=list)


def parity_gate(ledger: AbsorptionLedger, gaps: Sequence[Gap]) -> ParityResult:
    """Run the parity gate: ledger complete + gaps closed/waived."""
    problems: list[str] = []
    if not ledger.rows:
        problems.append("absorption ledger is empty")
    else:
        try:
            validate_ledger(ledger)
        except LedgerError as exc:
            problems.append(str(exc))
    try:
        validate_gaps(gaps)
    except GapError as exc:
        problems.append(str(exc))
    return ParityResult(ok=not problems, problems=problems)


def require_parity(result: ParityResult) -> None:
    """Fail loudly if the parity gate is red.

    Raises:
        ParityError: The ledger or gap closure has drifted.
    """
    if not result.ok:
        raise ParityError("parity gate red: " + "; ".join(result.problems))
