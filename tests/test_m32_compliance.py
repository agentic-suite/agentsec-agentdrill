"""M32 32.5 — the published compliance matrix keeps its honesty invariants.

Guards: the matrix is published; every ASI category is listed (none omitted);
the consolidated gaps section is present; the text passes the claims linter
(no unquoted banned words).
"""

from __future__ import annotations

from pathlib import Path

from agentdrill.standards.claims import lint_claims

REPO = Path(__file__).resolve().parents[1]
MATRIX = REPO / "docs" / "release" / "v0.1.0" / "compliance-matrix.md"


def _text() -> str:
    return MATRIX.read_text(encoding="utf-8")


def test_matrix_is_published() -> None:
    text = _text()
    assert "published" in text
    assert "🚧 **pending**" not in text


def test_matrix_lists_every_asi_category() -> None:
    text = _text()
    missing = [f"ASI{n:02d}" for n in range(1, 11) if f"ASI{n:02d}" not in text]
    assert not missing, f"compliance matrix omits ASI categories: {missing}"


def test_matrix_states_what_is_not_covered() -> None:
    text = _text()
    assert "Not covered" in text
    assert "None" in text  # ASI08/ASI09 are real, listed gaps


def test_matrix_passes_the_claims_linter() -> None:
    violations = lint_claims(_text())
    assert violations == [], [v.word for v in violations]


def test_compliance_readme_is_published() -> None:
    readme = (REPO / "docs" / "compliance" / "README.md").read_text(encoding="utf-8")
    assert "Design intent." not in readme
