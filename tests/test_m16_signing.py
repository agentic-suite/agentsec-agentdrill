"""M16 16.2 — signing + verified publishers (RED → GREEN).

A pack is signed and bound to a verified publisher identity; an unsigned or
tampered pack (or an unknown publisher) is rejected before install.
"""

from __future__ import annotations

import pytest

from agentdrill.models.attack_pack import AttackPack
from agentdrill.registry import (
    HmacSigner,
    PackVerification,
    PackVerificationError,
    Publisher,
    PublisherRegistry,
    entry_for_pack,
    require_verified,
    sign_entry,
    verify_entry,
    verify_pack,
)


def _entry():
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
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                }
            ],
        }
    )
    return entry_for_pack(pack, publisher="github:acme", trust="local")


def _publishers() -> PublisherRegistry:
    reg = PublisherRegistry()
    reg.add(Publisher(identity="github:acme", key_id="acme-key"))
    return reg


def test_signed_pack_verifies_with_a_verified_publisher() -> None:
    signer = HmacSigner(key=b"k", key_id="acme-key")
    entry = sign_entry(_entry(), signer)
    assert verify_entry(entry, signer) is True
    verdict = verify_pack(entry, verifier=signer, publishers=_publishers())
    assert isinstance(verdict, PackVerification)
    assert verdict.verified is True


def test_unsigned_pack_is_rejected() -> None:
    signer = HmacSigner(key=b"k", key_id="acme-key")
    with pytest.raises(PackVerificationError, match="unsigned"):
        require_verified(_entry(), verifier=signer, publishers=_publishers())


def test_tampered_pack_is_rejected() -> None:
    signer = HmacSigner(key=b"k", key_id="acme-key")
    entry = sign_entry(_entry(), signer)
    entry.content_hash = "sha256:deadbeef"
    assert verify_entry(entry, signer) is False
    with pytest.raises(PackVerificationError):
        require_verified(entry, verifier=signer, publishers=_publishers())


def test_unknown_publisher_is_rejected() -> None:
    signer = HmacSigner(key=b"k", key_id="acme-key")
    entry = sign_entry(_entry(), signer)
    with pytest.raises(PackVerificationError, match="publisher"):
        require_verified(entry, verifier=signer, publishers=PublisherRegistry())


def test_publisher_is_bound_to_an_identity_key() -> None:
    signer = HmacSigner(key=b"k", key_id="other-key")
    entry = sign_entry(_entry(), signer)
    with pytest.raises(PackVerificationError, match="publisher"):
        require_verified(entry, verifier=signer, publishers=_publishers())


def test_verify_pack_reports_the_reason() -> None:
    signer = HmacSigner(key=b"k", key_id="acme-key")
    verdict = verify_pack(_entry(), verifier=signer, publishers=_publishers())
    assert verdict.verified is False
    assert "unsigned" in verdict.reason
