"""Predecessor gap closure G1-G14 (M21 21.2).

Every acknowledged predecessor gap is **closed** with a passing test, or
**waived** with a written reason (G7 SQLite is waived by design). Design:
``docs/prd/24-predecessor-gap-closure.md``.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel

#: A gap's closure status.
GapStatus = Literal["closed", "waived"]


class GapError(ValueError):
    """Raised when a gap is neither closed with evidence nor waived with a reason."""


class Gap(BaseModel):
    """A predecessor gap and its closure/waiver."""

    id: str
    description: str
    status: GapStatus
    evidence: str = ""


_GAP_TABLE: tuple[tuple[str, str, GapStatus, str], ...] = (
    ("G1", "trust enforcement", "closed", "tests/test_m16_trust.py"),
    ("G2", "signed packs", "closed", "tests/test_m16_signing.py"),
    ("G3", "path-safety invariant", "closed", "tests/test_pack_loader.py"),
    ("G4", "audit rotation / hash-chain", "closed", "tests/test_security_audit.py"),
    ("G5", "OS-level sandbox", "closed", "tests/test_security_sandbox.py"),
    ("G6", "SBOM", "closed", "tests/test_release.py"),
    ("G7", "SQLite (waived by design)", "waived", "waived: SQLite persistence dropped by design"),
    ("G8", "trust matrix", "closed", "tests/test_m16_trust.py"),
    ("G9", "attestation", "closed", "tests/test_m18_attestation.py"),
    ("G10", "exit-code/scoring meta-cases", "closed", "tests/test_m14_meta.py"),
    ("G11", "criteria-interpolation meta-case", "closed", "tests/test_m14_meta.py"),
    ("G12", "model-surface sanity", "closed", "tests/test_target_base.py"),
    ("G13", "env resolution in manifest", "closed", "tests/test_m8_manifest.py"),
    ("G14", "cost governor", "closed", "tests/test_attack_runner_budget.py"),
)


def default_gaps() -> list[Gap]:
    """The G1-G14 gap table."""
    return [
        Gap(id=gap_id, description=description, status=status, evidence=evidence)
        for gap_id, description, status, evidence in _GAP_TABLE
    ]


def closed_gaps(gaps: Iterable[Gap]) -> list[Gap]:
    """The gaps closed with evidence."""
    return [gap for gap in gaps if gap.status == "closed"]


def waived_gaps(gaps: Iterable[Gap]) -> list[Gap]:
    """The gaps waived with a reason."""
    return [gap for gap in gaps if gap.status == "waived"]


def validate_gaps(gaps: Iterable[Gap]) -> None:
    """Fail loudly if a gap lacks closure evidence or a waiver reason.

    Raises:
        GapError: A gap has no evidence.
    """
    for gap in gaps:
        if not gap.evidence:
            raise GapError(
                f"gap {gap.id}: needs a passing test (closed) or a written reason (waived)"
            )
