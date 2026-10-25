"""Absorption ledger (M21 21.1).

Every capability inherited from the predecessor is **delivered and tested**,
**delegated** to a named tool, or **waived** with a reason — nothing carries
forward silently. Design: ``docs/prd/10-feature-parity.md``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

#: A capability's absorption status.
Status = Literal["delivered", "delegated", "waived"]


class LedgerError(ValueError):
    """Raised when a ledger row is incomplete (a silent drop)."""


class LedgerRow(BaseModel):
    """One capability's absorption row."""

    capability: str
    status: Status
    detail: str = ""


class AbsorptionLedger(BaseModel):
    """The absorption ledger (PRD 10 §A/§B)."""

    rows: list[LedgerRow] = Field(default_factory=list)


#: The default absorption ledger (a representative set of capabilities).
DEFAULT_LEDGER: tuple[LedgerRow, ...] = (
    LedgerRow(capability="scenario/attack-pack format", status="delivered", detail="M2"),
    LedgerRow(capability="adapter contract", status="delivered", detail="M4"),
    LedgerRow(capability="runner + trajectory capture", status="delivered", detail="M3"),
    LedgerRow(capability="deterministic + judge scoring", status="delivered", detail="M6"),
    LedgerRow(capability="fixture system / ToolStub", status="delivered", detail="M8"),
    LedgerRow(capability="baselines + comparison", status="delivered", detail="M9"),
    LedgerRow(capability="report generation + CI exit codes", status="delivered", detail="M10/M11"),
    LedgerRow(capability="sandbox / trust / audit", status="delivered", detail="M16/M22"),
    LedgerRow(capability="plugin registry", status="delivered", detail="M4/M6"),
    LedgerRow(
        capability="launch + security + adversarial packs", status="delivered", detail="M2/M14"
    ),
)


def build_ledger(rows: list[LedgerRow]) -> AbsorptionLedger:
    """Build the absorption ledger from rows."""
    return AbsorptionLedger(rows=list(rows))


def validate_ledger(ledger: AbsorptionLedger) -> None:
    """Fail loudly if any row is a silent drop.

    Raises:
        LedgerError: A waived row lacks a reason, or a delegated row lacks a
            named tool.
    """
    for row in ledger.rows:
        if row.status == "waived" and not row.detail:
            raise LedgerError(f"capability {row.capability!r}: a waived row requires a reason")
        if row.status == "delegated" and not row.detail:
            raise LedgerError(
                f"capability {row.capability!r}: a delegated row requires a named tool"
            )
