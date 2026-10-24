"""Predecessor absorption & gap closure package (M21).

The absorption ledger (21.1), predecessor gap closure G1-G14 (21.2), the parity
gate (21.3) and the predecessor retention plan (21.4). Design:
``docs/prd/10-feature-parity.md`` and ``docs/prd/24-predecessor-gap-closure.md``.
"""

from agentdrill.parity.gaps import (
    Gap,
    GapError,
    GapStatus,
    closed_gaps,
    default_gaps,
    validate_gaps,
    waived_gaps,
)
from agentdrill.parity.gate import ParityError, ParityResult, parity_gate, require_parity
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
    "Gap",
    "GapError",
    "GapStatus",
    "LedgerError",
    "LedgerRow",
    "ParityError",
    "ParityResult",
    "Status",
    "build_ledger",
    "closed_gaps",
    "default_gaps",
    "parity_gate",
    "require_parity",
    "validate_gaps",
    "validate_ledger",
    "waived_gaps",
]
