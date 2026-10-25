"""M23 23.1 — effect declarations, F87 (RED → GREEN).

Cases declare **forbidden effects** and **required-preserved effects**; a case
without effects is flagged.
"""

from __future__ import annotations

import pytest

from agentdrill.witness import (
    Effect,
    EffectDeclaration,
    EffectError,
    declares_effects,
    require_effects,
)


def test_effect_declaration_carries_forbidden_and_preserved() -> None:
    decl = EffectDeclaration(
        case_id="c1",
        forbidden=[Effect(kind="file", target="/etc/canary")],
        required_preserved=[Effect(kind="network", target="sinkhole")],
    )
    assert declares_effects(decl) is True
    require_effects(decl)  # no raise


def test_a_case_without_effects_is_flagged() -> None:
    decl = EffectDeclaration(case_id="c1")
    assert declares_effects(decl) is False
    with pytest.raises(EffectError, match="c1"):
        require_effects(decl)
