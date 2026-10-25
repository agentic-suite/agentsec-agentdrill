"""M14 14.1 — evasion / self-attack pack (RED → GREEN).

Cases that attack the ecosystem's **own** tools (pack tamper, hook-disable,
policy-edit, telemetry-injection, evidence-edit, update-hijack, agent-instructed
evasion). Each attack must declare an expected **fail-closed** defense.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdrill.loading.attack_pack_loader import load_attack_pack
from agentdrill.models.attack_pack import AttackPack
from agentdrill.security.self_attack import (
    EVASION_ATTACKS,
    SelfAttackError,
    assert_fail_closed,
    evasion_case_ids,
)

PACK = Path(__file__).parent.parent / "self-attack" / "evasion-self-attack.yaml"


def _pack() -> AttackPack:
    return load_attack_pack(PACK)


def test_evasion_pack_loads_and_validates() -> None:
    pack = _pack()
    assert pack.pack.name == "evasion-self-attack"


def test_every_documented_attack_is_present() -> None:
    assert set(evasion_case_ids(_pack())) == set(EVASION_ATTACKS)


def test_each_attack_has_an_expected_fail_closed_defense() -> None:
    assert_fail_closed(_pack())  # no raise


def test_every_case_expects_blocked_with_an_enforcement_or_integrity_dimension() -> None:
    for case in _pack().cases:
        assert case.oracle.expect == "blocked", case.id
        assert set(case.oracle.dimensions) & {"enforcement", "integrity"}, case.id


def test_a_non_fail_closed_case_is_rejected() -> None:
    pack = AttackPack.model_validate(
        {
            "pack": {
                "name": "bad",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "built-in",
            },
            "cases": [
                {
                    "id": "x",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "tamper_pack"}]},
                    "oracle": {"expect": "missed", "dimensions": ["enforcement"]},
                }
            ],
        }
    )
    with pytest.raises(SelfAttackError, match="x"):
        assert_fail_closed(pack)
