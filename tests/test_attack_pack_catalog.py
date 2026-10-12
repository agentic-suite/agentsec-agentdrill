"""M2 2.5 — the v0.1.0 pack catalog (RED → GREEN).

Each shipped pack reproduces its named incident pattern; every case carries an
`incident_ref` and ATLAS/OWASP coverage tags (PRD 21).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdrill.loading.attack_pack_loader import discover_attack_packs
from agentdrill.models.attack_pack import AttackPack

PACK_DIR = Path(__file__).parent.parent / "packs"


@pytest.fixture(scope="module")
def catalog() -> dict[str, AttackPack]:
    packs = discover_attack_packs([str(PACK_DIR)])
    return {pack.pack.name: pack for pack in packs}


def test_catalog_has_the_four_launch_packs(catalog: dict[str, AttackPack]) -> None:
    assert set(catalog) == {"quickstart-demo", "incidents-core", "incidents-security", "kill-chain"}


def test_every_case_has_incident_ref_and_atlas_owasp_tags(catalog: dict[str, AttackPack]) -> None:
    for pack in catalog.values():
        for case in pack.cases:
            assert case.incident_ref, f"{case.id} missing incident_ref"
            assert any(t.startswith("ATLAS-") for t in case.tags), f"{case.id} missing ATLAS tag"
            assert any(t.startswith("OWASP-") for t in case.tags), f"{case.id} missing OWASP tag"


def test_incidents_core_reproduces_replit_destructive_command(
    catalog: dict[str, AttackPack],
) -> None:
    case = next(c for c in catalog["incidents-core"].cases if c.id == "replit-destructive-command")
    assert case.incident_ref == "incident-register#6"
    assert case.oracle.expect == "blocked"
    assert case.oracle.kill_time is not None
    assert case.oracle.kill_time.max_seconds == 5
    assert "halted" in case.oracle.expect_telemetry
    assert case.cleanup  # stateful case declares cleanup


def test_incidents_security_reproduces_exfil_chain(catalog: dict[str, AttackPack]) -> None:
    case = next(c for c in catalog["incidents-security"].cases if c.id == "slack-exfil-chain")
    assert case.oracle.expect == "blocked"
    assert "secret-detected" in case.oracle.expect_telemetry
    assert len(case.attack.steps) >= 2  # lookup -> external send


def test_kill_chain_declares_kill_time(catalog: dict[str, AttackPack]) -> None:
    case = next(c for c in catalog["kill-chain"].cases if c.id == "killchain-destructive-command")
    assert case.oracle.kill_time is not None
    assert case.oracle.kill_time.max_seconds == 10
    cease_gap = next(
        c for c in catalog["kill-chain"].cases if c.id == "cease-gap-revoked-still-acting"
    )
    assert cease_gap.oracle.expect == "degraded"


def test_quickstart_demo_is_honest(catalog: dict[str, AttackPack]) -> None:
    cases = catalog["quickstart-demo"].cases
    assert len(cases) == 5
    missed = [c for c in cases if c.oracle.expect == "missed"]
    assert missed, "the demo must show a miss, not a fake green"
    assert any("demo" in c.tags for c in cases)
