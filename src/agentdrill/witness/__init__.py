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

__all__ = [
    "Effect",
    "EffectDeclaration",
    "EffectError",
    "declares_effects",
    "require_effects",
]
