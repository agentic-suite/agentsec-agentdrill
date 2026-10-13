"""M5 5.4 — target config + attestation hooks (RED → GREEN).

Every component records its realness (`live`/`fixture`/`mock`); a run's label is
the weakest link in its chain.
"""

from __future__ import annotations

from agentdrill.attestation import Attestation, chain_attestation, weakest_link
from agentdrill.targets.registry import get_target


def test_weakest_link_picks_the_weakest() -> None:
    assert weakest_link(["live", "fixture"]) == "fixture"
    assert weakest_link(["live", "fixture", "mock"]) == "mock"
    assert weakest_link(["live", "live"]) == "live"


def test_weakest_link_empty_is_conservative() -> None:
    assert weakest_link([]) == "mock"


def test_attestation_model() -> None:
    att = Attestation(component="agentgate", level="fixture")
    assert att.component == "agentgate"
    assert att.level == "fixture"
    assert Attestation(component="agentgate").level == "mock"


def test_target_attestation_from_config() -> None:
    assert get_target("agentgate", {}).attestation == "mock"
    assert get_target("agentkeys", {"attestation": "live"}).attestation == "live"


def test_chain_attestation_reads_components() -> None:
    live = get_target("agentgate", {"attestation": "live"})
    fixture = get_target("agentkeys", {"attestation": "fixture"})
    assert chain_attestation([live, fixture]) == "fixture"
