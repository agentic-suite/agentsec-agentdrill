"""Tests for the AgentDrill pytest plugin and test CLI command."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import agentdrill.pytest_plugin  # noqa: F401 — ensures plugin loads

pytest_plugins = ["agentdrill.pytest_plugin"]

PACK_YAML = Path(__file__).parent / "fixtures" / "valid_pack.yaml"
ECHO_AGENT = Path(__file__).parent / "fixtures" / "echo_agent.py"
SCENARIOS_DIR = Path(__file__).parent.parent / "scenarios"


@pytest.mark.agentdrill(pack=str(PACK_YAML))
def test_plugin_parametrize_scenarios(scenario: object) -> None:
    """@pytest.mark.agentdrill(pack=...) parametrizes over scenarios."""
    from agentdrill.models.pack import Scenario

    assert isinstance(scenario, Scenario)
    assert scenario.id


@pytest.mark.agentdrill(pack=str(PACK_YAML))
@pytest.mark.agentdrill_tags("tag-a")
def test_plugin_tags_marker_filters(scenario: object) -> None:
    """@pytest.mark.agentdrill_tags filters parametrized scenarios."""
    from agentdrill.models.pack import Scenario

    assert isinstance(scenario, Scenario)
    assert "tag-a" in scenario.tags


def test_plugin_agent_config_skips_without_opts() -> None:
    """agent_config fixture skips when no --agentdrill-agent is provided."""
    code = subprocess.call(  # noqa: S603
        [
            sys.executable, "-m", "pytest",
            "-c", str(Path(__file__).parent.parent / "pyproject.toml"),
            "-p", "agentdrill.pytest_plugin",
            "--no-header",
            "-q",
            str(Path(__file__).parent / "fixtures" / "pytest_skip_agent.py"),
        ],
        cwd=Path(__file__).parent.parent,
    )
    assert code == 0  # skip is a pass in pytest


def test_plugin_pack_skips_without_opts() -> None:
    """scenario_pack fixture skips when no --agentdrill-pack is provided."""
    code = subprocess.call(  # noqa: S603
        [
            sys.executable, "-m", "pytest",
            "-c", str(Path(__file__).parent.parent / "pyproject.toml"),
            "-p", "agentdrill.pytest_plugin",
            "--no-header",
            "-q",
            str(Path(__file__).parent / "fixtures" / "pytest_skip_pack.py"),
        ],
        cwd=Path(__file__).parent.parent,
    )
    assert code == 0


def test_plugin_fixtures_resolve_with_cli_opts() -> None:
    """Fixtures resolve when CLI options are provided."""
    code = subprocess.call(  # noqa: S603
        [
            sys.executable, "-m", "pytest",
            "-c", str(Path(__file__).parent.parent / "pyproject.toml"),
            "-p", "agentdrill.pytest_plugin",
            "--no-header",
            "-q",
            f"--agentdrill-pack={PACK_YAML}",
            "--agentdrill-agent=python:fixtures.agents",
            str(Path(__file__).parent / "fixtures" / "pytest_resolve.py"),
        ],
        cwd=Path(__file__).parent.parent,
    )
    assert code == 0


def test_cli_test_run_with_mock_agent(tmp_path: Path) -> None:
    """agentdrill test run discovers and runs scenarios with mock agent."""
    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "test", "run",
            "--scenarios-dir", str(SCENARIOS_DIR),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
        ],
    )
    assert result.exit_code in (0, 1), f"test run failed: {result.output}"
    assert "Test run complete" in result.output
    report_json = tmp_path / "test-report.json"
    assert report_json.exists()
    data = json.loads(report_json.read_text())
    assert data["packs"] >= 1
    assert data["total_scenarios"] >= 20  # core + security packs


def test_cli_test_run_empty_directory(tmp_path: Path) -> None:
    """agentdrill test run fails gracefully with no packs found."""
    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "test", "run",
            "--scenarios-dir", str(tmp_path),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "No scenario packs found" in result.output


def test_cli_test_run_help() -> None:
    """agentdrill test run --help displays usage."""
    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main

    runner = CliRunner()
    result = runner.invoke(main, ["test", "run", "--help"])
    assert result.exit_code == 0
    assert "--scenarios-dir" in result.output
    assert "--agent" in result.output
    assert "--output-format" in result.output


def test_output_formatter_github_actions_run(tmp_path: Path) -> None:
    """GitHub Actions output format produces expected sections."""
    from agentdrill.cli.formatter import OutputFormatter

    formatter = OutputFormatter("github-actions")
    result = {
        "run_id": "run-test-001",
        "pack_name": "test-pack",
        "pack_version": "1.0.0",
        "total_scenarios": 5,
        "passed": 4,
        "warned": 0,
        "failed": 1,
        "exit_code": 1,
        "duration_ms": 1234,
        "safety_violations": [],
    }
    output = formatter.format_run_result(result)
    assert output is not None
    assert "AgentDrill Run Results" in output
    assert "✅ Passed" in output
    assert "❌ Failed" in output


def test_output_formatter_github_actions_comparison() -> None:
    """GitHub Actions output for comparison report."""

    from agentdrill.cli.formatter import OutputFormatter
    from agentdrill.comparison.engine import ComparisonResult
    from agentdrill.comparison.report import ComparisonReport
    from agentdrill.scoring.result import RunScore

    formatter = OutputFormatter("github-actions")
    comp_result = ComparisonResult(
        scenario_deltas={},
        family_deltas={},
        aggregate={
            "total_scenarios": 5,
            "regressed": 1,
            "improved": 2,
            "new_failures": 0,
            "new_passes": 1,
            "unchanged": 3,
            "overall_score_delta": -0.05,
        },
    )
    candidate_score = RunScore(
        scenario_scores={},
        totals={"passed": 0, "warned": 0, "failed": 0},
        safety_violations=[],
        exit_code=1,
    )
    report = ComparisonReport(
        baseline_name="v1.0.0",
        candidate_name="run-test-001",
        result=comp_result,
        candidate_score=candidate_score,
    )
    output = formatter.format_comparison(report)
    assert output is not None
    assert "AgentDrill Comparison Report" in output
    assert "regressed" in output.lower()


def test_output_formatter_github_actions_validation() -> None:
    """GitHub Actions output for validation results."""
    from agentdrill.cli.formatter import OutputFormatter

    formatter = OutputFormatter("github-actions")
    results = {
        "pack": {"valid": True, "message": "Pack loaded"},
        "agent": {"valid": True, "message": "Adapter created"},
    }
    output = formatter.format_validation(results)
    assert output is not None
    assert "AgentDrill Validation Results" in output


def test_output_formatter_github_actions_test_result() -> None:
    """GitHub Actions output for multi-pack test results."""
    from agentdrill.cli.formatter import OutputFormatter

    formatter = OutputFormatter("github-actions")
    summary = {
        "packs": 2,
        "total_scenarios": 10,
        "passed": 8,
        "warned": 1,
        "failed": 1,
        "duration_ms": 5000,
        "safety_violations": [],
    }
    output = formatter.format_test_result(summary)
    assert output is not None
    assert "AgentDrill Test Run Results" in output


def test_pytest_plugin_agentdrill_run(tmp_path: Path) -> None:
    """Invoke agentdrill test run to exercise the pytest plugin end-to-end."""
    echo_agent = f"{sys.executable} {ECHO_AGENT}"
    cwd = tmp_path / "project"
    cwd.mkdir()
    # Create a test scenarios dir with a valid pack
    test_scenarios = cwd / "scenarios"
    test_scenarios.mkdir()
    import shutil
    shutil.copy2(PACK_YAML, test_scenarios / "test_pack.yaml")
    cp = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "agentdrill", "test", "run",
         "--agent", f"subprocess:{echo_agent}",
         "--judge", "mock",
         "--scenarios-dir", str(test_scenarios),
         "--output", str(cwd / ".agentdrill"),
         "--output-format", "json"],
        capture_output=True, text=True, cwd=cwd,
        env={**__import__("os").environ, "PYTHONPATH": f"{Path(__file__).parent.parent / 'src'}"},
    )
    assert cp.returncode == 0, f"stdout: {cp.stdout}\nstderr: {cp.stderr}"
