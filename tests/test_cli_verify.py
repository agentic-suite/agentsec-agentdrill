"""Tests for the wired ``agentdrill verify`` CLI (M31 — closes plan §4.5.8).

The engine (``lifecycle/verifier.py``) has its own tests; these cover the CLI
surface: bundle loading, the three printed verdicts, the failure reasons, the
exit codes, and the fail-closed paths (missing/invalid bundle).
"""

from __future__ import annotations

import hashlib
import json
import secrets
from pathlib import Path

import pytest
from click.testing import CliRunner

from agentdrill.cli.verify import verify
from agentdrill.registry.signing import HmacSigner


def _make_bundle(tmp_path: Path, *, tamper: bool = False) -> Path:
    """Build a signed, complete, honest-shaped bundle (optionally tampered)."""
    key = secrets.token_bytes(32)
    signer = HmacSigner(key=key, key_id="local")
    artifacts = {"result.json": json.dumps({"blocked": 3, "missed": 1})}
    if tamper:
        # Change the content WITHOUT re-signing — intact must fail.
        artifacts["result.json"] = json.dumps({"blocked": 9, "missed": 1})
    signatures = {
        name: signer.sign(content.encode())
        for name, content in (
            {"result.json": json.dumps({"blocked": 3, "missed": 1})}.items()
        )
    }
    hashes = {
        name: "sha256:" + hashlib.sha256(content.encode()).hexdigest()
        for name, content in artifacts.items()
    }
    bundle = {
        "artifacts": artifacts,
        "signatures": signatures,
        "manifest": {
            "pack_hash": "sha256:abc",
            "host": "test",
            "seeds": [1, 2, 3],
            "environment": [],
            "hashes": hashes,
            "key": key.hex(),
            "key_id": "local",
        },
        "labels": {"target_attestation": "fixture"},
        "outcome": {"blocked": 3, "missed": 1, "degraded": 0},
    }
    path = tmp_path / ("tampered-bundle.json" if tamper else "bundle.json")
    path.write_text(json.dumps(bundle), encoding="utf-8")
    return path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_verify_good_bundle_passes(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(verify, [str(_make_bundle(tmp_path))])
    assert result.exit_code == 0, result.output
    assert "intact:       PASS" in result.output
    assert "complete:      PASS" in result.output
    assert "honest-shaped: PASS" in result.output


def test_verify_tampered_bundle_fails_with_reasons(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(verify, [str(_make_bundle(tmp_path, tamper=True))])
    assert result.exit_code == 3, result.output
    assert "intact:       FAIL" in result.output
    assert "signature does not verify" in result.output


def test_verify_json_output(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(verify, [str(_make_bundle(tmp_path)), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["intact"] is True
    assert data["complete"] is True
    assert data["honest_shaped"] is True


def test_verify_missing_path_fails_closed(runner: CliRunner) -> None:
    result = runner.invoke(verify, [])
    assert result.exit_code != 0
    assert "requires a bundle path" in result.output


def test_verify_nonexistent_bundle_fails_closed(runner: CliRunner) -> None:
    result = runner.invoke(verify, ["/nonexistent/bundle.json"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_verify_invalid_json_fails_closed(runner: CliRunner, tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = runner.invoke(verify, [str(bad)])
    assert result.exit_code != 0
    assert "cannot read bundle" in result.output


def test_verify_incomplete_bundle_fails_complete(runner: CliRunner, tmp_path: Path) -> None:
    """A bundle missing manifest fields fails the complete verdict (loudly)."""
    path = _make_bundle(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["manifest"]["seeds"]  # completeness requires seeds
    del data["manifest"]["key"]
    path.write_text(json.dumps(data), encoding="utf-8")
    result = runner.invoke(verify, [str(path)])
    assert result.exit_code == 3, result.output
    assert "complete:      FAIL" in result.output
