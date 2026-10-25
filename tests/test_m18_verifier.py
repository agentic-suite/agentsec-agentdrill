"""M18 18.5 — standalone verifier, F64 (RED → GREEN).

Zero-install, offline verification of a bundle: signatures, hashes, manifest,
labels and statistical shape — three verdicts (intact / complete /
honest-shaped).
"""

from __future__ import annotations

from agentdrill.lifecycle import Bundle, VerifyVerdict, verify_bundle
from agentdrill.oracles.engine import OutcomeSplit
from agentdrill.registry import HmacSigner

KEY = b"verify-key"


def _bundle(signer: HmacSigner, *, seeds: list[int] | None = None, tamper: bool = False) -> Bundle:
    import hashlib

    artifacts = {"run.json": '{"pack": "p"}', "artifacts/c1.json": '{"case_id": "c1"}'}
    content = dict(artifacts)
    if tamper:
        content["run.json"] = '{"pack": "tampered"}'
    hashes = {
        name: "sha256:" + hashlib.sha256(value.encode()).hexdigest()
        for name, value in artifacts.items()
    }
    signatures = {name: signer.sign(value.encode()) for name, value in artifacts.items()}
    manifest = {
        "pack_hash": "sha256:abc",
        "host": {"os": "macOS"},
        "seeds": seeds if seeds is not None else [1, 2, 3],
        "environment": ["OPENAI_API_KEY"],
        "hashes": hashes,
    }
    return Bundle(
        artifacts=content,
        signatures=signatures,
        manifest=manifest,
        labels={"policyweave-output": "fixture"},
        outcome=OutcomeSplit(blocked=2, missed=1),
    )


def test_a_good_bundle_verifies_offline() -> None:
    signer = HmacSigner(key=KEY, key_id="verify")
    verdict = verify_bundle(_bundle(signer), verifier=signer)
    assert isinstance(verdict, VerifyVerdict)
    assert verdict.intact is True
    assert verdict.complete is True
    assert verdict.honest_shaped is True
    assert verdict.ok is True


def test_a_tampered_artifact_is_not_intact() -> None:
    signer = HmacSigner(key=KEY, key_id="verify")
    verdict = verify_bundle(_bundle(signer, tamper=True), verifier=signer)
    assert verdict.intact is False


def test_a_missing_manifest_field_is_not_complete() -> None:
    signer = HmacSigner(key=KEY, key_id="verify")
    bundle = _bundle(signer)
    del bundle.manifest["pack_hash"]
    verdict = verify_bundle(bundle, verifier=signer)
    assert verdict.complete is False


def test_a_single_seed_bundle_is_not_honest_shaped() -> None:
    signer = HmacSigner(key=KEY, key_id="verify")
    verdict = verify_bundle(_bundle(signer, seeds=[1]), verifier=signer)
    assert verdict.honest_shaped is False


def test_reasons_are_reported() -> None:
    signer = HmacSigner(key=KEY, key_id="verify")
    verdict = verify_bundle(_bundle(signer, seeds=[1]), verifier=signer)
    assert verdict.reasons
