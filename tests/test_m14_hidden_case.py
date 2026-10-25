"""M14 14.5 — hidden adversarial case (RED → GREEN).

An independent-reviewer-authored **secret** case kept inside the meta pack; it
**escapes a single-layer defense** (it needs every required layer present).
"""

from __future__ import annotations

from pathlib import Path

from agentdrill.loading.attack_pack_loader import load_attack_pack
from agentdrill.security.hidden_case import (
    HIDDEN_CASE_ID,
    HIDDEN_REQUIRED_LAYERS,
    escapes_single_layer,
    hidden_cases,
    is_hidden_case,
)

META_PACK = Path(__file__).parent.parent / "self-attack" / "meta-verification.yaml"


def test_hidden_case_is_kept_in_the_meta_pack() -> None:
    pack = load_attack_pack(META_PACK)
    ids = [case.id for case in pack.cases]
    assert HIDDEN_CASE_ID in ids


def test_hidden_case_is_marked_hidden_from_an_independent_reviewer() -> None:
    pack = load_attack_pack(META_PACK)
    cases = hidden_cases(pack)
    assert [c.id for c in cases] == [HIDDEN_CASE_ID]
    assert "independent-reviewer" in cases[0].tags


def test_is_hidden_case_recognizes_the_tag() -> None:
    assert is_hidden_case(["hidden", "meta"]) is True
    assert is_hidden_case(["tamper"]) is False


def test_the_hidden_case_escapes_a_single_layer_defense() -> None:
    assert len(HIDDEN_REQUIRED_LAYERS) >= 2
    assert escapes_single_layer(["policyweave-output"]) is True


def test_a_full_defense_stops_the_hidden_case() -> None:
    assert escapes_single_layer(list(HIDDEN_REQUIRED_LAYERS)) is False
