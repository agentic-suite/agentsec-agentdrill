"""M16 16.1 — registry model + content-addressed signed index (RED → GREEN).

A `registry.json` index: content-addressed entries, signed, and verifiable
**offline** (no mandatory central service).
"""

from __future__ import annotations

from agentdrill.models.attack_pack import AttackPack
from agentdrill.registry import (
    HmacSigner,
    RegistryEntry,
    RegistryIndex,
    build_index,
    content_address,
    entry_for_pack,
    sign_index,
    verify_index,
)


def _pack(name: str = "p", version: str = "1.0.0", tool: str = "shell") -> AttackPack:
    return AttackPack.model_validate(
        {
            "pack": {
                "name": name,
                "version": version,
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
                    "attack": {"steps": [{"tool": tool}]},
                    "oracle": {"expect": "blocked"},
                }
            ],
        }
    )


def test_entries_are_content_addressed() -> None:
    a = entry_for_pack(_pack(), publisher="acme")
    b = entry_for_pack(_pack(), publisher="acme")
    c = entry_for_pack(_pack(tool="http_get"), publisher="acme")
    assert isinstance(a, RegistryEntry)
    assert a.content_hash == b.content_hash
    assert a.content_hash != c.content_hash
    assert a.content_hash == content_address(_pack())


def test_identical_content_is_independent_of_publisher() -> None:
    assert content_address(_pack()) == content_address(_pack())


def test_signed_index_verifies_offline() -> None:
    signer = HmacSigner(key=b"secret-key", key_id="acme-key")
    index = sign_index(build_index([entry_for_pack(_pack())]), signer)
    assert isinstance(index, RegistryIndex)
    assert index.signature
    assert verify_index(index, HmacSigner(key=b"secret-key", key_id="acme-key")) is True


def test_a_tampered_index_fails_verification() -> None:
    signer = HmacSigner(key=b"secret-key", key_id="acme-key")
    index = sign_index(build_index([entry_for_pack(_pack())]), signer)
    index.entries[0].content_hash = "deadbeef"
    assert verify_index(index, signer) is False


def test_an_unsigned_index_fails_verification() -> None:
    index = build_index([entry_for_pack(_pack())])
    assert verify_index(index, HmacSigner(key=b"secret-key")) is False


def test_entry_lookup_by_name_and_version() -> None:
    index = build_index([entry_for_pack(_pack(), publisher="acme")])
    assert index.entry("p", "1.0.0") is not None
    assert index.entry("p", "9.9.9") is None
