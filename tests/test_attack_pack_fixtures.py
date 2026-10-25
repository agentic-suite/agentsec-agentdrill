"""M2 2.6 — fixture corpus, benign-twin linkage, twin-driver hook (RED → GREEN)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agentdrill.loading.attack_catalog import (
    case_tools,
    linked_twins,
    missing_fixtures,
    register_twin_driver,
    twin_driver,
)
from agentdrill.loading.attack_pack_loader import discover_attack_packs, load_attack_pack
from agentdrill.models.attack_pack import (
    Attack,
    AttackCase,
    AttackPack,
    AttackStep,
    AttackTarget,
    Driver,
    Oracle,
)
from agentdrill.models.errors import PackParseError

PACK_DIR = Path(__file__).parent.parent / "packs"
FIXTURE_DIR = PACK_DIR / "fixtures"


def test_catalog_fixtures_cover_every_case_tool() -> None:
    packs = discover_attack_packs([str(PACK_DIR)])
    assert packs
    for pack in packs:
        missing = missing_fixtures(pack, FIXTURE_DIR)
        assert not missing, f"{pack.pack.name} missing fixtures: {sorted(missing)}"


def test_missing_fixtures_reports_gaps() -> None:
    pack = AttackPack.model_validate(
        {
            "pack": {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
            },
            "cases": [
                {
                    "id": "c1",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "shell"}, {"tool": "widget"}]},
                    "oracle": {"expect": "blocked"},
                }
            ],
        }
    )
    assert case_tools(pack) == {"shell", "widget"}
    assert missing_fixtures(pack, FIXTURE_DIR) == {"widget"}


def _pack_with_twin(twin: str) -> str:
    return yaml.safe_dump(
        {
            "pack": {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
            },
            "cases": [
                {
                    "id": "attack",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                    "benign_twin": twin,
                },
                {
                    "id": "attack-benign",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "missed"},
                },
            ],
        }
    )


def test_benign_twin_link_resolves(tmp_path: Path) -> None:
    path = tmp_path / "pack.yaml"
    path.write_text(_pack_with_twin("attack-benign"), encoding="utf-8")
    pack = load_attack_pack(path)
    assert linked_twins(pack) == {"attack": "attack-benign"}


def test_benign_twin_dangling_reference_rejected(tmp_path: Path) -> None:
    path = tmp_path / "pack.yaml"
    path.write_text(_pack_with_twin("does-not-exist"), encoding="utf-8")
    with pytest.raises(PackParseError, match="benign_twin"):
        load_attack_pack(path)


def _case(driver_type: str) -> AttackCase:
    return AttackCase(
        id="c",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=Driver(type=driver_type),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=Oracle(expect="blocked"),
    )


def test_twin_driver_defaults_to_case_driver() -> None:
    driver = twin_driver(_case("cursor"))
    assert driver.type == "cursor"


def test_twin_driver_uses_registered_factory() -> None:
    from agentdrill.loading import attack_catalog

    register_twin_driver("python", lambda case: {"guard": "off", "tool": case.id})
    try:
        driver = twin_driver(_case("python"))
        assert driver.config == {"guard": "off", "tool": "c"}
    finally:
        attack_catalog._TWIN_DRIVERS.pop("python", None)
