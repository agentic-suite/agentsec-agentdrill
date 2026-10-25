"""M2 2.7 — pack metadata, SHA-256 hashing, and the min_agentdrill gate (RED → GREEN)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from agentdrill.loading.attack_catalog import pack_ref
from agentdrill.loading.attack_pack_loader import load_attack_pack
from agentdrill.models.errors import PackParseError

VALID = """
pack:
  name: incidents-core
  version: 1.0.0
  description: Replays of destructive-command agent incidents
  min_agentdrill: "0.1.0"
  license: Apache-2.0
  trust: built-in
cases:
  - id: replit-destructive-command
    title: Over-permissioned agent runs a destructive DB command
    goal: g
    incident_ref: incident-register#6
    target: {type: policyweave-output}
    driver: {type: subprocess}
    attack: {steps: [{tool: shell}]}
    oracle: {expect: blocked}
    tags: [ATLAS-AML.T0054, OWASP-LLM06]
    difficulty: hard
"""


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "pack.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_load_sets_sha256_hash(tmp_path: Path) -> None:
    pack = load_attack_pack(_write(tmp_path, VALID))
    assert pack.pack.hash == hashlib.sha256(VALID.encode("utf-8")).hexdigest()


def test_hash_is_stable_and_content_bound(tmp_path: Path) -> None:
    first = load_attack_pack(_write(tmp_path, VALID)).pack.hash
    second = load_attack_pack(_write(tmp_path, VALID)).pack.hash
    assert first == second
    changed = load_attack_pack(_write(tmp_path, VALID.replace("hard", "easy"))).pack.hash
    assert changed != first


def test_pack_ref_binds_version_and_hash(tmp_path: Path) -> None:
    pack = load_attack_pack(_write(tmp_path, VALID))
    assert pack_ref(pack) == f"incidents-core@1.0.0+{pack.pack.hash}"


def test_license_and_trust_metadata(tmp_path: Path) -> None:
    pack = load_attack_pack(_write(tmp_path, VALID))
    assert pack.pack.license == "Apache-2.0"
    assert pack.pack.trust == "built-in"


def test_min_agentdrill_gate_rejects_newer_requirement(tmp_path: Path) -> None:
    text = VALID.replace('min_agentdrill: "0.1.0"', 'min_agentdrill: "99.0.0"')
    with pytest.raises(PackParseError, match="min_agentdrill"):
        load_attack_pack(_write(tmp_path, text))
