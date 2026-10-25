"""M18 18.8 — MCP + memory pack classes, F19/F20 (RED → GREEN).

Tool poisoning / rug-pull / shadowing / WhatsApp-class (via agentgate); memory
poisoning / cross-task leakage / multi-agent abuse. Each class reproduces its
pattern.
"""

from __future__ import annotations

from pathlib import Path

from agentdrill.loading.attack_pack_loader import load_attack_pack

PACKS = Path(__file__).parent.parent / "packs"

MCP_CASES = {"mcp-tool-poisoning", "mcp-rug-pull", "mcp-tool-shadowing", "mcp-whatsapp-class"}
MEMORY_CASES = {"memory-poisoning", "cross-task-leakage", "multi-agent-abuse"}


def test_mcp_class_reproduces_its_patterns() -> None:
    pack = load_attack_pack(PACKS / "mcp-tool-surface.yaml")
    assert {c.id for c in pack.cases} == MCP_CASES
    assert all(c.target.type == "agentgate" for c in pack.cases)


def test_memory_class_reproduces_its_patterns() -> None:
    pack = load_attack_pack(PACKS / "memory-multiagent.yaml")
    assert {c.id for c in pack.cases} == MEMORY_CASES


def test_every_case_fails_closed() -> None:
    for name in ("mcp-tool-surface.yaml", "memory-multiagent.yaml"):
        pack = load_attack_pack(PACKS / name)
        assert all(c.oracle.expect == "blocked" for c in pack.cases), name
