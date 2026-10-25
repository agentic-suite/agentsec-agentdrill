"""M16 16.6 — registry sync, F75 (RED → GREEN).

`agentdrill registry sync` is read-only and signature-verified; a bad signature
is rejected. `pack outdated` reports newer remote versions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from agentdrill.cli.__main__ import main
from agentdrill.models.attack_pack import AttackPack
from agentdrill.registry import (
    HmacSigner,
    SyncError,
    build_index,
    entry_for_pack,
    is_outdated,
    sign_index,
    sync_index,
)


def _pack(version: str = "1.0.0"):
    return AttackPack.model_validate(
        {
            "pack": {
                "name": "p",
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
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                }
            ],
        }
    )


KEY = b"registry-secret"


def test_sync_accepts_a_validly_signed_index() -> None:
    signer = HmacSigner(key=KEY, key_id="registry")
    remote = sign_index(build_index([entry_for_pack(_pack(), publisher="acme")]), signer)
    synced = sync_index(remote, verifier=signer)
    assert synced.entry("p", "1.0.0") is not None


def test_sync_rejects_a_bad_signature() -> None:
    signer = HmacSigner(key=KEY, key_id="registry")
    remote = sign_index(build_index([entry_for_pack(_pack(), publisher="acme")]), signer)
    remote.entries[0].content_hash = "sha256:tampered"
    with pytest.raises(SyncError, match="signature"):
        sync_index(remote, verifier=signer)


def test_outdated_reports_newer_remote_versions() -> None:
    local = build_index([entry_for_pack(_pack("1.0.0"), publisher="acme")])
    remote = build_index([entry_for_pack(_pack("2.0.0"), publisher="acme")])
    outdated = is_outdated(local, remote)
    assert [(o.name, o.local_version, o.remote_version) for o in outdated] == [
        ("p", "1.0.0", "2.0.0")
    ]


def test_up_to_date_yields_nothing() -> None:
    index = build_index([entry_for_pack(_pack("1.0.0"), publisher="acme")])
    assert is_outdated(index, index) == []


def test_registry_sync_cli_verifies_a_signed_index(tmp_path: Path) -> None:
    signer = HmacSigner(key=KEY, key_id="registry")
    remote = sign_index(build_index([entry_for_pack(_pack(), publisher="acme")]), signer)
    source = tmp_path / "registry.json"
    source.write_text(remote.model_dump_json(), encoding="utf-8")
    result = CliRunner().invoke(
        main, ["registry", "sync", "--from", str(source), "--key", KEY.hex()]
    )
    assert result.exit_code == 0, result.output
    assert "p" in result.output


def test_registry_sync_cli_rejects_a_bad_signature(tmp_path: Path) -> None:
    signer = HmacSigner(key=KEY, key_id="registry")
    remote = sign_index(build_index([entry_for_pack(_pack(), publisher="acme")]), signer)
    remote.entries[0].content_hash = "sha256:tampered"
    source = tmp_path / "registry.json"
    source.write_text(json.dumps(remote.model_dump()), encoding="utf-8")
    result = CliRunner().invoke(
        main, ["registry", "sync", "--from", str(source), "--key", KEY.hex()]
    )
    assert result.exit_code != 0
