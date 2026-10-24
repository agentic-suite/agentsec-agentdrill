"""Judge drift detection (M19 19.3, F81).

Seeded **canary** cases track judge-vs-deterministic / judge-vs-human agreement.
A canary flip **without a pin change** is ``judge_drift`` —
release-blocking. Judge prompts are hashed into the manifest. Design:
``docs/prd/23-oracle-credibility.md``.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

#: The release-blocking finding raised on judge drift.
JUDGE_DRIFT = "judge_drift"


class JudgeDriftError(ValueError):
    """Raised when a canary flips without a pin change (judge drift)."""


class CanaryCase(BaseModel):
    """A seeded canary case and the judge's verdict."""

    case_id: str
    expected: str
    judge_outcome: str


class DriftReport(BaseModel):
    """The judge-drift assessment for a release."""

    drift: bool
    flips: list[str] = Field(default_factory=list)
    pin_changed: bool = False
    judge_prompt_hash: str = ""


def hash_prompt(prompt: str) -> str:
    """The SHA-256 of a judge prompt (recorded in the manifest)."""
    return "sha256:" + hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def detect_drift(
    canaries: Sequence[CanaryCase],
    *,
    previous_outcomes: Mapping[str, str],
    pin_changed: bool,
    judge_prompt_hash: str,
) -> DriftReport:
    """Detect judge drift: a canary flip without a pin change."""
    flips = [
        canary.case_id
        for canary in canaries
        if canary.case_id in previous_outcomes
        and previous_outcomes[canary.case_id] != canary.judge_outcome
    ]
    return DriftReport(
        drift=bool(flips) and not pin_changed,
        flips=flips,
        pin_changed=pin_changed,
        judge_prompt_hash=judge_prompt_hash,
    )


def require_no_drift(report: DriftReport) -> None:
    """Fail loudly (release-blocking) if judge drift was detected.

    Raises:
        JudgeDriftError: A canary flipped without a declared pin change.
    """
    if report.drift:
        raise JudgeDriftError(
            f"{JUDGE_DRIFT}: canary flip(s) without a pin change: {sorted(report.flips)}"
        )
