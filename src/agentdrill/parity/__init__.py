"""Predecessor absorption & gap closure package (M21).

The absorption ledger (21.1), predecessor gap closure G1-G14 (21.2), the parity
gate (21.3) and the predecessor retention plan (21.4). Design:
``docs/prd/10-feature-parity.md`` and ``docs/prd/24-predecessor-gap-closure.md``.
"""

from agentdrill.parity.ledger import (
    DEFAULT_LEDGER,
    AbsorptionLedger,
    LedgerError,
    LedgerRow,
    Status,
    build_ledger,
    validate_ledger,
)

__all__ = [
    "DEFAULT_LEDGER",
    "AbsorptionLedger",
    "LedgerError",
    "LedgerRow",
    "Status",
    "build_ledger",
    "validate_ledger",
]
