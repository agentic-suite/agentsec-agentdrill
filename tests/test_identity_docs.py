"""M1 1.6 / 1.D — identity & governance docs match the project identity."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_matches_identity() -> None:
    text = (ROOT / "README.md").read_text()
    assert text.startswith("# agentdrill")
    assert "agentic-suite" in text
    assert "LICENSE" in text
    assert "SECURITY.md" in text


def test_codeowners_is_finalized() -> None:
    text = (ROOT / "CODEOWNERS").read_text()
    assert "@deghosal-2026" in text
    assert "Replace with" not in text


def test_security_policy_present() -> None:
    text = (ROOT / "SECURITY.md").read_text().lower()
    assert "vulnerab" in text


def test_traceability_doc_exists_and_covers_foundation() -> None:
    text = (ROOT / "docs/prd/12-traceability.md").read_text()
    assert "M0" in text and "M1" in text


def test_readme_make_targets_exist_in_makefile() -> None:
    readme = (ROOT / "README.md").read_text()
    makefile = (ROOT / "Makefile").read_text()
    declared = set(re.findall(r"(?m)^([A-Za-z0-9_.-]+)\s*:", makefile))
    referenced = set(re.findall(r"\bmake\s+([a-z][a-z0-9-]+)", readme))
    missing = referenced - declared
    assert not missing, f"README references non-existent make targets: {sorted(missing)}"
