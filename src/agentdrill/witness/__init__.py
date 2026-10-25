"""Independent effect witness package (M23).

Effect declarations (23.1), FS/network/credential/process witnesses (23.2/23.3),
the side-effect ledger + human-surface (23.4) and the two-oracle verdict +
integrity (23.5). Design: ``docs/prd/26-independent-effect-witness.md``.
"""

from agentdrill.witness.effects import (
    Effect,
    EffectDeclaration,
    EffectError,
    declares_effects,
    require_effects,
)
from agentdrill.witness.sensors import HoneyCredential, ProcessWitness
from agentdrill.witness.side_effects import (
    ApprovalCheck,
    MockSaas,
    SideEffectLedger,
    check_approval,
)
from agentdrill.witness.verdict import TwoOracleVerdict, two_oracle_verdict
from agentdrill.witness.watchers import (
    CanaryWatch,
    Sinkhole,
    file_fingerprint,
    measure_overhead,
    watch_canary,
)

__all__ = [
    "ApprovalCheck",
    "CanaryWatch",
    "Effect",
    "EffectDeclaration",
    "EffectError",
    "HoneyCredential",
    "MockSaas",
    "ProcessWitness",
    "SideEffectLedger",
    "Sinkhole",
    "TwoOracleVerdict",
    "check_approval",
    "declares_effects",
    "file_fingerprint",
    "measure_overhead",
    "require_effects",
    "two_oracle_verdict",
    "watch_canary",
]
