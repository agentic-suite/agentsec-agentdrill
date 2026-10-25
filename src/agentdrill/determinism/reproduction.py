"""Reproducibility check for attack runs (M8 8.5).

Rerun a pinned pack: the result must be identical. A difference is only
acceptable when a pin changed and that change is **declared** — a silent
non-determinism fails the check (CI verifies reproduction). Design:
``docs/design/storage-design.md`` §Reproducibility test.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass

from agentdrill.determinism.pins import PinSet, repin_note
from agentdrill.models.attack_run import CaseArtifact

#: Fields excluded from a fingerprint — they vary per run, not per result.
_VOLATILE_FIELDS = {"id", "timestamps"}


def fingerprint_artifacts(artifacts: Sequence[CaseArtifact]) -> str:
    """A stable fingerprint of a run's results, ignoring run identity/time.

    Excludes each artifact's run-scoped ``id`` and ``timestamps`` so two runs
    of the same pinned pack fingerprint identically.
    """
    canonical = [
        artifact.model_dump(mode="json", exclude=_VOLATILE_FIELDS) for artifact in artifacts
    ]
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReproductionResult:
    """The verdict of a reproducibility check.

    Attributes:
        reproduced: Whether the two runs produced identical results.
        declared: Whether a pin change was declared (the sanctioned exception).
        note: The re-pin declaration, when pins changed.
    """

    reproduced: bool
    declared: bool
    note: str | None = None

    @property
    def ok(self) -> bool:
        """The CI verdict: reproduced, or a difference declared by a re-pin."""
        return self.reproduced or self.declared


def verify_reproduction(
    first: Sequence[CaseArtifact],
    second: Sequence[CaseArtifact],
    *,
    previous_pins: PinSet,
    current_pins: PinSet,
) -> ReproductionResult:
    """Check that ``second`` reproduces ``first`` unless a pin changed.

    Args:
        first: The baseline run's artifacts.
        second: The rerun's artifacts.
        previous_pins: The pins the baseline was produced under.
        current_pins: The pins the rerun was produced under.

    Returns:
        A :class:`ReproductionResult`; ``ok`` is False only for a silent
        (undeclared) difference.
    """
    note = repin_note(previous_pins, current_pins)
    reproduced = fingerprint_artifacts(first) == fingerprint_artifacts(second)
    if reproduced:
        return ReproductionResult(reproduced=True, declared=False, note=note)
    return ReproductionResult(reproduced=False, declared=note is not None, note=note)
