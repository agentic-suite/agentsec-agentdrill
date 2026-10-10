"""M1 1.1 — build/quality-gate Makefile with the documented targets.

The milestone requires ``make setup/lint/typecheck/test`` to work; this guards
that the Makefile exists and declares those targets.
"""

from __future__ import annotations

import re
from pathlib import Path

MAKEFILE = Path(__file__).resolve().parents[1] / "Makefile"
REQUIRED_TARGETS = {"setup", "lint", "typecheck", "test"}


def _declared_targets(text: str) -> set[str]:
    return set(re.findall(r"(?m)^([A-Za-z0-9_.-]+)\s*:", text))


def test_makefile_exists() -> None:
    assert MAKEFILE.is_file(), "Makefile is missing"


def test_makefile_declares_quality_gate_targets() -> None:
    targets = _declared_targets(MAKEFILE.read_text())
    missing = REQUIRED_TARGETS - targets
    assert not missing, f"Makefile is missing targets: {sorted(missing)}"
