"""Deterministic adaptive runs (M15 15.4).

Adaptive runs are reproducible like everything else: a **pinned** attacker model
+ seed, with the mutation **path** recorded in the manifest. Two identical runs
produce identical mutation paths. Design:
``docs/prd/16-attack-chain-orchestration.md``.
"""

from __future__ import annotations

import hashlib
import json
import random
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.chains.adaptive import MUTATION_KINDS, AdaptiveCase


class MutationStep(BaseModel):
    """One mutation in an adaptive run's path."""

    index: int
    mutation: str
    detail: str = ""


class AdaptiveRun(BaseModel):
    """A reproducible adaptive run: pinned model + seed + mutation path."""

    case_id: str
    model: str
    seed: int
    steps: list[MutationStep] = Field(default_factory=list)

    def digest(self) -> str:
        """A stable signature of the run (model + seed + mutation path)."""
        canonical = json.dumps(
            {
                "case_id": self.case_id,
                "model": self.model,
                "seed": self.seed,
                "steps": [s.model_dump() for s in self.steps],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_manifest_entry(self) -> dict[str, Any]:
        """The manifest record for this adaptive run (model/seed/path)."""
        return {
            "model": self.model,
            "seed": self.seed,
            "path_digest": self.digest(),
            "steps": [s.model_dump() for s in self.steps],
        }


def run_adaptive(case: AdaptiveCase, *, model: str, seed: int) -> AdaptiveRun:
    """Run an adaptive case deterministically from a pinned model + seed.

    The mutation path is a pure function of ``(case, model, seed)``.
    """
    rng = random.Random(f"{model}:{seed}")  # noqa: S311 - seeded path selection, not crypto
    count = max(0, case.max_mutations)
    steps = [
        MutationStep(
            index=index,
            mutation=MUTATION_KINDS[rng.randrange(len(MUTATION_KINDS))],
            detail=f"from {case.parent_pattern}",
        )
        for index in range(count)
    ]
    return AdaptiveRun(case_id=case.id, model=model, seed=seed, steps=steps)


def record_adaptive(manifest: dict[str, Any], run: AdaptiveRun) -> dict[str, Any]:
    """Record ``run``'s mutation path into ``manifest`` under ``adaptive``."""
    manifest["adaptive"] = run.to_manifest_entry()
    return manifest
