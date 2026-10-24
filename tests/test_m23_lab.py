"""M23 23.6 — Adversary Lab core, F88 (RED → GREEN).

A versioned loopback lab (evil MCP server, test IdP, hostile registries, rogue
upstream API, evil A2A peer, sinks); same seed ⇒ same lab event log.
"""

from __future__ import annotations

from agentdrill.lab import (
    EVIL_MCP_BEHAVIORS,
    LAB_COMPONENTS,
    AdversaryLab,
    build_lab,
    event_log,
)


def test_lab_has_all_evil_components() -> None:
    assert set(LAB_COMPONENTS) == {
        "evil-mcp",
        "test-idp",
        "hostile-registry",
        "rogue-upstream",
        "evil-a2a",
        "sink",
    }


def test_evil_mcp_behaviors_are_available() -> None:
    assert set(EVIL_MCP_BEHAVIORS) == {
        "poisoning",
        "shadow",
        "overlap",
        "preference",
        "rug-pull",
        "return-injection",
    }


def test_same_seed_yields_the_same_event_log() -> None:
    def scenario(lab: AdversaryLab) -> None:
        lab.serve_mcp("poisoning")
        lab.serve_mcp("rug-pull")
        lab.hit_sink("http://sink")

    a = build_lab(version="0.3.0", seed=7)
    b = build_lab(version="0.3.0", seed=7)
    scenario(a)
    scenario(b)
    assert event_log(a) == event_log(b)
    assert a.version == "0.3.0"
