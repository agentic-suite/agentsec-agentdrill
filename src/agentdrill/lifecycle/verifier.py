"""Standalone verifier (M18 18.5, F64).

Zero-install, **offline** verification of a bundle: signatures, hashes,
manifest, labels and statistical shape. Three verdicts — ``intact``,
``complete`` and ``honest_shaped``. Design:
``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.oracles.engine import OutcomeSplit
from agentdrill.registry.signing import Verifier

#: Minimum distinct seeds for an honest-shaped result.
MIN_SEEDS = 3

#: Manifest fields a complete bundle must carry.
_REQUIRED_MANIFEST: tuple[str, ...] = (
    "pack_hash",
    "host",
    "seeds",
    "environment",
    "hashes",
)


class VerifyVerdict(BaseModel):
    """The three offline verdicts for a bundle."""

    intact: bool
    complete: bool
    honest_shaped: bool
    reasons: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether all three verdicts pass."""
        return self.intact and self.complete and self.honest_shaped


class Bundle(BaseModel):
    """A verifiable release bundle."""

    artifacts: dict[str, str] = Field(default_factory=dict)
    signatures: dict[str, str] = Field(default_factory=dict)
    manifest: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    outcome: OutcomeSplit = Field(default_factory=OutcomeSplit)


def _sha256(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _check_intact(bundle: Bundle, verifier: Verifier, reasons: list[str]) -> bool:
    hashes = bundle.manifest.get("hashes", {})
    intact = True
    for name, content in bundle.artifacts.items():
        signature = bundle.signatures.get(name)
        if not signature or not verifier.verify(content.encode("utf-8"), signature):
            reasons.append(f"{name}: signature does not verify")
            intact = False
        if hashes.get(name) != _sha256(content):
            reasons.append(f"{name}: hash mismatch")
            intact = False
    return intact


def _check_complete(bundle: Bundle, reasons: list[str]) -> bool:
    missing = [field for field in _REQUIRED_MANIFEST if field not in bundle.manifest]
    if missing:
        reasons.append(f"manifest missing fields: {missing}")
    if not bundle.labels:
        reasons.append("no attestation labels present")
    return not missing and bool(bundle.labels)


def _check_honest_shaped(bundle: Bundle, reasons: list[str]) -> bool:
    seeds = bundle.manifest.get("seeds", [])
    distinct = len(set(seeds))
    if distinct < MIN_SEEDS:
        reasons.append(f"only {distinct} distinct seeds (need ≥{MIN_SEEDS})")
    if bundle.outcome.total == 0:
        reasons.append("empty outcome split")
    if "score" in bundle.manifest:
        reasons.append("a composite score is present")
    return distinct >= MIN_SEEDS and bundle.outcome.total > 0 and "score" not in bundle.manifest


def verify_bundle(bundle: Bundle, *, verifier: Verifier) -> VerifyVerdict:
    """Verify a bundle offline — intact, complete and honest-shaped."""
    reasons: list[str] = []
    intact = _check_intact(bundle, verifier, reasons)
    complete = _check_complete(bundle, reasons)
    honest_shaped = _check_honest_shaped(bundle, reasons)
    return VerifyVerdict(
        intact=intact, complete=complete, honest_shaped=honest_shaped, reasons=reasons
    )
