"""Tests for the wired ``agentdrill run --dry-run`` / ``--explain`` CLI (M31).

The engine (``dx/dry_run.py``) has its own tests (``test_m20_dry_run.py``);
these cover the CLI surface: the flag prints the plan, performs **zero**
executions, and exits 0 before any agent is invoked.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from agentdrill.cli.run import run

PACK = "packs/incidents-core.yaml"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_dry_run_prints_plan_zero_executions(runner: CliRunner) -> None:
    result = runner.invoke(run, ["--pack", PACK, "--agent", "python:my_agent.run", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "dry-run:" in result.output
    assert "executions: 0" in result.output
    # the plan names the cases and their expected verdicts
    assert "replit-destructive-command" in result.output
    assert "expect blocked" in result.output


def test_dry_run_explain_annotates_reasons(runner: CliRunner) -> None:
    result = runner.invoke(
        run, ["--pack", PACK, "--agent", "python:my_agent.run", "--dry-run", "--explain"]
    )
    assert result.exit_code == 0, result.output
    assert "because:" in result.output


def test_dry_run_performs_no_executions(runner: CliRunner) -> None:
    """A dry-run against a nonexistent agent still exits 0 — nothing runs."""
    result = runner.invoke(
        run, ["--pack", PACK, "--agent", "python:does_not_exist.anywhere", "--dry-run"]
    )
    assert result.exit_code == 0, result.output
    assert "executions: 0" in result.output


def test_dry_run_missing_pack_fails_loudly(runner: CliRunner) -> None:
    result = runner.invoke(
        run, ["--pack", "/nonexistent/pack.yaml", "--agent", "python:x.run", "--dry-run"]
    )
    assert result.exit_code != 0
