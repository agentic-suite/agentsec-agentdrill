"""M16 16.5 — deprecation + takedown (RED → GREEN).

Explicit deprecation with migration notes; a takedown removes the index entry
but is **recorded on the signature chain** (no silent disappearance).
"""

from __future__ import annotations

from agentdrill.models.attack_pack import AttackPack
from agentdrill.registry import (
    GovernanceEvent,
    GovernanceLog,
    apply_deprecation,
    apply_takedown,
    build_index,
    entry_for_pack,
)


def _pack():
    return AttackPack.model_validate(
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
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                }
            ],
        }
    )


def _index():
    return build_index([entry_for_pack(_pack(), publisher="acme")])


def test_deprecation_marks_the_entry_with_a_migration_note() -> None:
    log = GovernanceLog()
    index = apply_deprecation(_index(), log, name="p", version="1.0.0", note="use p@2")
    entry = index.entry("p", "1.0.0")
    assert entry is not None
    assert entry.deprecated is True
    assert entry.migration_note == "use p@2"


def test_takedown_removes_the_entry() -> None:
    log = GovernanceLog()
    index = apply_takedown(_index(), log, name="p", version="1.0.0", reason="malicious")
    assert index.entry("p", "1.0.0") is None


def test_takedown_is_recorded_on_the_chain() -> None:
    log = GovernanceLog()
    apply_takedown(_index(), log, name="p", version="1.0.0", reason="malicious")
    assert [e.kind for e in log.events] == ["takedown"]
    assert log.events[0].name == "p"
    assert log.head  # a signature-chain head exists


def test_deprecation_is_recorded_too() -> None:
    log = GovernanceLog()
    apply_deprecation(_index(), log, name="p", version="1.0.0", note="use p@2")
    assert isinstance(log.events[0], GovernanceEvent)
    assert log.events[0].kind == "deprecate"
    assert log.events[0].note == "use p@2"


def test_the_chain_head_changes_with_each_event() -> None:
    log = GovernanceLog()
    apply_deprecation(_index(), log, name="p", version="1.0.0", note="a")
    first = log.head
    apply_takedown(_index(), log, name="p", version="1.0.0", reason="b")
    assert log.head != first
