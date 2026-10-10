"""M1 1.4 — CI runs the quality gate; DCO is enforced.

Guards that the placeholder CI was replaced by real lint/type/test/coverage
steps and that a DCO workflow exists.
"""

from __future__ import annotations

from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
CI = WORKFLOWS / "ci.yml"
DCO = WORKFLOWS / "dco.yml"


def test_ci_workflow_exists_and_is_not_a_placeholder() -> None:
    assert CI.is_file(), "ci.yml is missing"
    text = CI.read_text()
    assert "Placeholder" not in text, "ci.yml still contains the starter placeholder"


def test_ci_runs_the_quality_gate() -> None:
    text = CI.read_text()
    for needle in (
        "python-version",
        "ruff check",
        "mypy",
        "pytest",
        "--cov=agentdrill",
        "--cov-fail-under=95",
    ):
        assert needle in text, f"ci.yml is missing: {needle!r}"


def test_dco_workflow_exists() -> None:
    assert DCO.is_file(), "dco.yml (DCO enforcement) is missing"
    assert "Signed-off-by" in DCO.read_text()
