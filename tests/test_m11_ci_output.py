"""M11 11.3 — CI output (RED → GREEN).

GitHub Actions / GitLab output plus `$GITHUB_STEP_SUMMARY`, so the gate is
visible in the PR.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdrill.ci import GateFailure, render_ci_output, write_step_summary


def _failures() -> list[GateFailure]:
    return [
        GateFailure(
            kind="dimension",
            dimension="enforcement",
            detail="enforcement blocked rate 0.50 < 0.8",
        ),
        GateFailure(kind="divergence", severity="critical", detail="judge passed a missed case"),
    ]


def test_github_output_has_annotations_and_summary() -> None:
    out = render_ci_output(4, _failures(), output_format="github-actions")
    assert "::error" in out
    assert "###" in out or "##" in out
    assert "enforcement" in out


def test_gitlab_output_is_markdown_without_annotations() -> None:
    out = render_ci_output(4, _failures(), output_format="gitlab")
    assert "::error" not in out
    assert "enforcement" in out
    assert "###" in out or "##" in out


def test_unknown_format_fails_loudly() -> None:
    with pytest.raises(ValueError, match="output_format"):
        render_ci_output(0, [], output_format="xml")


def test_summary_reports_exit_code() -> None:
    out = render_ci_output(4, _failures(), output_format="github-actions")
    assert "4" in out


def test_write_step_summary_writes_when_env_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    written = write_step_summary("### gate\nfailed\n")
    assert written == summary
    hidden = summary.read_text(encoding="utf-8")
    assert "gate" in hidden


def test_write_step_summary_noop_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    assert write_step_summary("nothing") is None
