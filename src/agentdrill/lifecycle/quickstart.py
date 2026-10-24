"""Quickstart + demo stack (M18 18.7, F66).

``agentdrill quickstart`` boots a bundled **demo** target and reaches a first
honest result in **≤15 minutes**. The result is **mock-attested** and
watermarked ``demo — never evidence``. Design:
``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from agentdrill.attack_runner import AttackRunner, CaseOutcome
from agentdrill.loading.attack_pack_loader import load_attack_pack
from agentdrill.models.attack_pack import AttackPack
from agentdrill.oracles.engine import OutcomeSplit

#: The quickstart time budget in minutes.
BUDGET_MINUTES = 15

#: The watermark on every demo result.
DEMO_WATERMARK = "demo — never evidence"

#: The bundled demo pack.
DEFAULT_DEMO_PACK = "packs/quickstart-demo.yaml"


class QuickstartResult(BaseModel):
    """The first honest result from a quickstart run."""

    target: str = "bundled-demo"
    attestation: str = "mock"
    outcome: OutcomeSplit
    watermark: str = DEMO_WATERMARK
    elapsed_seconds: float = 0.0


def _demo_driver(case: object) -> CaseOutcome:
    """A mock driver for the bundled demo target."""
    return CaseOutcome()


def _split(pack: AttackPack) -> OutcomeSplit:
    """The demo outcome split, taken from each case's expected outcome."""
    split = OutcomeSplit()
    for case in pack.cases:
        if case.oracle.expect == "blocked":
            split.blocked += 1
        elif case.oracle.expect == "missed":
            split.missed += 1
        else:
            split.degraded += 1
    return split


def run_quickstart(
    *,
    pack_path: str | None = None,
    timer: Callable[[], float] = time.perf_counter,
) -> QuickstartResult:
    """Boot the bundled demo target and produce a first result."""
    start = timer()
    pack = load_attack_pack(pack_path or DEFAULT_DEMO_PACK)
    with tempfile.TemporaryDirectory(prefix="agentdrill-quickstart-") as tmp:
        AttackRunner(_demo_driver, runs_dir=Path(tmp) / "runs").run_all(pack, run_id="demo")
    elapsed = timer() - start
    return QuickstartResult(outcome=_split(pack), elapsed_seconds=elapsed)


def within_budget(result: QuickstartResult) -> bool:
    """Whether the quickstart result was reached within the time budget."""
    return result.elapsed_seconds <= BUDGET_MINUTES * 60
