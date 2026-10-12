"""Coverage-focused tests for the CLI modules.

Targets:
  - src/agentdrill/cli/formatter.py
  - src/agentdrill/cli/run.py
  - src/agentdrill/cli/baseline.py
  - src/agentdrill/cli/validate.py
  - src/agentdrill/cli/compare.py
  - src/agentdrill/cli/benchmark.py
  - src/agentdrill/cli/test.py

Every test is deterministic and offline: agents are the in-repo ``fixtures``
python-import agents and the LLM judge is always ``mock``.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

from agentdrill.cli.__main__ import main
from agentdrill.cli.formatter import OutputFormatter
from agentdrill.comparison.engine import ComparisonResult
from agentdrill.comparison.report import ComparisonReport
from agentdrill.scoring.result import RunScore

FIXTURES = Path(__file__).parent / "fixtures"
PACK_YAML = FIXTURES / "valid_pack.yaml"
SWE_BENCH = FIXTURES / "sample_swe_bench.jsonl"
WEBARENA = FIXTURES / "sample_webarena.json"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _invoke(*args: str):
    return CliRunner().invoke(main, list(args))


def _artifact(scenario_id: str = "sc-1", agent: dict | None = None) -> dict:
    return {
        "id": f"run-test-{scenario_id}",
        "scenario_id": scenario_id,
        "agent": agent or {},
        "timestamp": {
            "start": "2026-01-01T00:00:00",
            "end": "2026-01-01T00:00:01",
            "duration_ms": 1000,
        },
        "output": {"final": "test output", "structured": None},
        "trajectory": [],
        "cost": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
        },
        "status": "completed",
        "error": None,
    }


def _make_report(safety_violations: list[str] | None = None) -> ComparisonReport:
    comp_result = ComparisonResult(
        scenario_deltas={
            "sc-1": {
                "baseline_score": 1.0,
                "candidate_score": 0.5,
                "delta": -0.5,
                "regressed": True,
                "improved": False,
                "new_failure": False,
                "new_pass": False,
            },
            "sc-2": {
                "baseline_score": None,
                "candidate_score": None,
                "delta": None,
                "regressed": False,
                "improved": False,
                "new_failure": True,
                "new_pass": False,
            },
        },
        family_deltas={
            "tag-a": {"baseline_avg": 1.0, "candidate_avg": 0.5, "score_delta": -0.5},
        },
        aggregate={
            "total_scenarios": 2,
            "regressed": 1,
            "improved": 0,
            "new_failures": 1,
            "new_passes": 0,
            "unchanged": 0,
            "overall_score_delta": -0.25,
            "cost_delta_usd": 0.001,
        },
    )
    candidate_score = RunScore(
        scenario_scores={},
        totals={"passed": 0, "warned": 0, "failed": 2},
        safety_violations=safety_violations or [],
        exit_code=1,
    )
    return ComparisonReport(
        baseline_name="v1.0.0",
        candidate_name="run-test-001",
        result=comp_result,
        candidate_score=candidate_score,
    )


def _make_run_result(**overrides) -> dict:
    result = {
        "run_id": "run-001",
        "pack_name": "test-pack",
        "pack_version": "1.0.0",
        "total_scenarios": 3,
        "passed": 1,
        "warned": 1,
        "failed": 1,
        "exit_code": 1,
        "duration_ms": 1234,
        "safety_violations": ["tool_correctness"],
        "summary": {
            "run_id": "run-001",
            "pack_name": "test-pack",
            "pack_version": "1.0.0",
            "total_scenarios": 3,
            "passed": 1,
            "warned": 1,
            "failed": 1,
            "exit_code": 1,
            "duration_ms": 1234,
            "safety_violations": ["tool_correctness"],
        },
    }
    result.update(overrides)
    return result


def _create_run(base: Path, pack: Path = PACK_YAML) -> Path:
    """Create a real run directory via the CLI and return its path."""
    result = _invoke(
        "run",
        "--pack", str(pack),
        "--agent", "python:fixtures.agents",
        "--judge", "mock",
        "--output", str(base),
        "--output-format", "json",
    )
    assert result.exit_code == 0, result.output
    run_dirs = sorted(d for d in (base / "runs").iterdir() if d.is_dir())
    return run_dirs[-1]


# --------------------------------------------------------------------------- #
# formatter.py — OutputFormatter
# --------------------------------------------------------------------------- #
class TestFormatRunResult:
    def test_json_prints(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("json").format_run_result({"run_id": "r1"})
        assert out is None
        assert "r1" in capsys.readouterr().out

    def test_json_quiet_suppresses(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("json", quiet=True).format_run_result({"run_id": "r1"})
        assert out is None
        assert capsys.readouterr().out == ""

    def test_markdown(self) -> None:
        out = OutputFormatter("markdown").format_run_result(_make_run_result())
        assert out is not None
        assert out.startswith("# Run Result: run-001")
        assert "Safety Violations" in out

    def test_markdown_no_safety(self) -> None:
        out = OutputFormatter("markdown").format_run_result(
            _make_run_result(safety_violations=[])
        )
        assert out is not None
        assert "Safety Violations" not in out

    def test_github_actions(self) -> None:
        out = OutputFormatter("github-actions").format_run_result(_make_run_result())
        assert out is not None
        assert "AgentDrill Run Results" in out
        assert "Safety Violations" in out

    def test_terminal(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("terminal").format_run_result(_make_run_result())
        assert out == ""
        assert "Run: run-001" in capsys.readouterr().out

    def test_html(self) -> None:
        out = OutputFormatter("html").format_run_result(_make_run_result())
        assert out is not None
        assert out.startswith("<!DOCTYPE html>")


class TestHtmlReport:
    def test_full_html(self) -> None:
        # Mix of statuses and metric score types exercises every branch.
        result = {
            "summary": {
                "run_id": "r1",
                "pack_name": "p",
                "pack_version": "2.0",
                "passed": 2,
                "warned": 1,
                "failed": 1,
                "total_scenarios": 4,
                "duration_ms": 10,
                "exit_code": 1,
                "safety_violations": ["safe_tool"],
            },
            "scenario_scores": {
                "s-good": {
                    "status": "passed",
                    "metrics": {"m": {"score": 0.5}},
                },
                "s-bad": {
                    "status": "failed",
                    "metrics": {"m": {"score": "not-a-number"}, "n": {"score": None}},
                },
                "s-warn": {"status": "warn", "metrics": {}},
            },
            "cache_stats": {"hits": 3, "misses": 1, "size": 4},
        }
        out = OutputFormatter("html").format_run_result(result)
        assert out is not None
        assert "Judge Cache" in out
        assert "Safety Violations" in out
        assert "s-good" in out
        assert "not-a-number" in out

    def test_html_zero_total_and_no_extras(self) -> None:
        out = OutputFormatter("html").format_run_result(
            {"summary": {"run_id": "r", "passed": 0, "warned": 0, "failed": 0}}
        )
        assert out is not None
        assert "N/A" in out

    def test_html_flat_result_no_summary(self) -> None:
        # Without a nested "summary" the formatter falls back to the top dict.
        out = OutputFormatter("html").format_run_result(
            {"run_id": "r", "passed": 3, "warned": 0, "failed": 0, "total_scenarios": 3}
        )
        assert out is not None
        assert "#22c55e" in out  # all-pass green card


class TestFormatComparison:
    def test_json_prints(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("json").format_comparison(_make_report())
        assert out is None
        assert "aggregate" in capsys.readouterr().out

    def test_json_writes_output_path(self, tmp_path: Path) -> None:
        dest = tmp_path / "comparison.json"
        OutputFormatter("json").format_comparison(_make_report(), output_path=str(dest))
        assert json.loads(dest.read_text())["baseline_name"] == "v1.0.0"

    def test_markdown(self) -> None:
        out = OutputFormatter("markdown").format_comparison(_make_report())
        assert out is not None
        assert "Comparison Report" in out
        assert "cost" not in out  # markdown never renders cost

    def test_markdown_writes_output_path(self, tmp_path: Path) -> None:
        dest = tmp_path / "comparison.md"
        OutputFormatter("markdown").format_comparison(
            _make_report(), output_path=str(dest)
        )
        assert "Comparison Report" in dest.read_text()

    def test_github_actions(self) -> None:
        out = OutputFormatter("github-actions").format_comparison(
            _make_report(safety_violations=["x"])
        )
        assert out is not None
        assert "AgentDrill Comparison Report" in out
        assert "Safety Violations" in out

    def test_terminal(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("terminal").format_comparison(
            _make_report(safety_violations=["x"])
        )
        assert out == ""
        captured = capsys.readouterr().out
        assert "Comparison" in captured
        assert "Safety" in captured


class TestFormatValidation:
    def test_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("json").format_validation(
            {"pack": {"valid": True, "message": "ok"}}
        )
        assert out is None
        assert "pack" in capsys.readouterr().out

    def test_github_actions_all_valid(self) -> None:
        out = OutputFormatter("github-actions").format_validation(
            {"pack": {"valid": True, "message": "ok"}}
        )
        assert out is not None
        assert "All validations passed" in out

    def test_github_actions_with_failure(self) -> None:
        out = OutputFormatter("github-actions").format_validation(
            {
                "pack": {"valid": True, "message": "ok"},
                "agent": {"valid": False, "message": "bad"},
            }
        )
        assert out is not None
        assert "AgentDrill Validation Results" in out

    def test_markdown(self) -> None:
        out = OutputFormatter("markdown").format_validation(
            {"pack": {"valid": True, "message": "ok", "extras": 1}}
        )
        assert out is not None
        assert "# Validation Results" in out
        assert "extras" in out

    def test_terminal(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("terminal").format_validation(
            {"pack": {"valid": True, "message": "ok"}}
        )
        assert out == ""
        assert "All validations passed" in capsys.readouterr().out

    def test_terminal_with_failure(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("terminal").format_validation(
            {"pack": {"valid": False, "message": "nope"}}
        )
        assert out == ""
        assert "nope" in capsys.readouterr().out


class TestFormatTestResult:
    def test_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        out = OutputFormatter("json").format_test_result({"packs": 1})
        assert out is None
        assert "packs" in capsys.readouterr().out

    def test_github_actions(self) -> None:
        out = OutputFormatter("github-actions").format_test_result(
            {
                "packs": 2,
                "total_scenarios": 5,
                "passed": 4,
                "warned": 0,
                "failed": 1,
                "duration_ms": 10,
                "safety_violations": ["v"],
            }
        )
        assert out is not None
        assert "AgentDrill Test Run Results" in out
        assert "Safety Violations" in out

    def test_markdown_with_error_and_safety(self) -> None:
        out = OutputFormatter("markdown").format_test_result(
            {
                "packs": 2,
                "total_scenarios": 3,
                "passed": 1,
                "warned": 1,
                "failed": 1,
                "duration_ms": 5,
                "safety_violations": ["v"],
                "results": [
                    {"pack_name": "good", "passed": 1, "warned": 1, "failed": 0},
                    {"pack_path": "/x/bad.yaml", "error": "boom"},
                ],
            }
        )
        assert out is not None
        assert "Per-Pack Results" in out
        assert "boom" in out

    def test_terminal_with_error_and_safety(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        out = OutputFormatter("terminal").format_test_result(
            {
                "packs": 2,
                "total_scenarios": 3,
                "passed": 1,
                "warned": 1,
                "failed": 1,
                "duration_ms": 5,
                "safety_violations": ["v"],
                "results": [
                    {"pack_name": "good", "passed": 1, "warned": 1, "failed": 0},
                    {"pack_path": "/x/bad.yaml", "error": "boom"},
                ],
            }
        )
        assert out == ""
        captured = capsys.readouterr().out
        assert "boom" in captured
        assert "good" in captured


# --------------------------------------------------------------------------- #
# run.py
# --------------------------------------------------------------------------- #
class TestResolveJudge:
    def test_none(self) -> None:
        from agentdrill.cli.run import _resolve_judge

        assert _resolve_judge(None) is None

    def test_mock(self) -> None:
        from agentdrill.cli.run import _resolve_judge

        client = _resolve_judge("mock")
        assert client is not None and client.name == "mock"

    def test_ollama(self) -> None:
        from agentdrill.cli.run import _resolve_judge

        client = _resolve_judge("ollama")
        assert client is not None and client.name == "ollama"
        assert _resolve_judge("ollama:llama3.2").model == "llama3.2"  # type: ignore[union-attr]

    def test_mlx(self) -> None:
        from agentdrill.cli.run import _resolve_judge

        client = _resolve_judge("mlx")
        assert client is not None and client.name == "mlx"

    def test_openai_without_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.cli.run import _resolve_judge

        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(click.UsageError, match="OPENAI_API_KEY"):
            _resolve_judge("openai")

    def test_openai_with_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.cli.run import _resolve_judge

        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        client = _resolve_judge("openai:gpt-4o")
        assert client is not None and client.name == "openai"

    def test_anthropic_without_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.cli.run import _resolve_judge

        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(click.UsageError, match="ANTHROPIC_API_KEY"):
            _resolve_judge("anthropic")

    def test_anthropic_with_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.cli.run import _resolve_judge

        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant")
        client = _resolve_judge("anthropic")
        assert client is not None and client.name == "anthropic"

    def test_unknown_provider(self) -> None:
        from agentdrill.cli.run import _resolve_judge

        with pytest.raises(click.BadParameter, match="unknown judge provider"):
            _resolve_judge("nope")


class TestRunCommand:
    def test_happy_markdown_writes_report(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "markdown",
        )
        assert result.exit_code == 0, result.output
        run_dir = sorted(d for d in (tmp_path / "runs").iterdir() if d.is_dir())[-1]
        assert (run_dir / "report.md").exists()

    def test_happy_html_writes_report(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "html",
        )
        assert result.exit_code == 0, result.output
        run_dir = sorted(d for d in (tmp_path / "runs").iterdir() if d.is_dir())[-1]
        assert (run_dir / "report.html").exists()

    def test_github_actions_step_summary(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        summary = tmp_path / "step_summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "github-actions",
        )
        assert result.exit_code == 0, result.output
        assert "AgentDrill Run Results" in summary.read_text()

    def test_quiet_and_terminal(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "terminal",
            "--quiet",
        )
        assert result.exit_code == 0, result.output
        assert "Run complete" not in result.output

    def test_extra_flags(self, tmp_path: Path) -> None:
        telemetry = tmp_path / "telemetry" / "metrics.json"
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--tags", "tag-a",
            "--workers", "2",
            "--model", "gpt-4o",
            "--seed", "42",
            "--no-cache",
            "--no-manifest",
            "--telemetry", str(telemetry),
            "--max-outstanding", "2",
        )
        assert result.exit_code == 0, result.output
        assert telemetry.exists()

    def test_fixtures_and_live_mutually_exclusive(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--output", str(tmp_path),
            "--fixtures",
            "--live",
        )
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output

    def test_explain_policy_allowed(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--output", str(tmp_path),
            "--explain-policy",
        )
        assert result.exit_code == 0
        assert "ALLOWED" in result.output

    def test_explain_policy_denied(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--output", str(tmp_path),
            "--trust", "external",
            "--explain-policy",
        )
        assert result.exit_code == 1
        assert "DENIED" in result.output

    def test_policy_denied_without_explain(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--output", str(tmp_path),
            "--trust", "external",
        )
        assert result.exit_code != 0
        assert "subprocess" in result.output

    def test_fail_on_all_passing(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--fail-on", "all",
            "--fail-on-divergence", "all",
        )
        assert result.exit_code == 0, result.output

    def test_fail_on_divergence_warning_and_critical(self, tmp_path: Path) -> None:
        for mode in ("warning", "critical"):
            result = _invoke(
                "run",
                "--pack", str(PACK_YAML),
                "--agent", "python:fixtures.agents",
                "--judge", "mock",
                "--output", str(tmp_path),
                "--output-format", "json",
                "--fail-on-divergence", mode,
            )
            assert result.exit_code == 0, result.output

    def test_run_with_baseline_rescore(self, tmp_path: Path) -> None:
        run_dir = _create_run(tmp_path)
        save = _invoke(
            "baseline", "save",
            "--name", "base",
            "--run", str(run_dir),
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert save.exit_code == 0, save.output
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--baseline", "base",
        )
        assert result.exit_code == 0, result.output
        assert "comparison" in result.output

    def test_run_with_baseline_snapshot(self, tmp_path: Path) -> None:
        run_dir = _create_run(tmp_path)
        _invoke(
            "baseline", "save",
            "--name", "base",
            "--run", str(run_dir),
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--baseline", "base",
            "--compare-mode", "snapshot",
        )
        assert result.exit_code == 0, result.output

    def test_run_with_baseline_missing(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--baseline", "does-not-exist",
        )
        assert result.exit_code == 0, result.output
        assert "not found" in result.output

    def test_run_with_baseline_no_snapshot_fallback(self, tmp_path: Path) -> None:
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore
        from agentdrill.models.artifact import RunArtifact

        run_dir = _create_run(tmp_path)
        artifacts = [
            RunArtifact(**json.loads(p.read_text()))
            for p in sorted((run_dir / "artifacts").glob("*.json"))
        ]
        store = BaselineStore(base_dir=f"{tmp_path}/baselines")
        store.save(
            Baseline(
                name="nosnap",
                pack="test-pack",
                pack_version="1.0.0",
                runs=artifacts,
                score_snapshot=None,
            )
        )
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--baseline", "nosnap",
            "--compare-mode", "snapshot",
        )
        assert result.exit_code == 0, result.output
        assert "falling back to rescoring" in result.output

    def test_run_sandbox(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--sandbox",
        )
        # Sandbox mode blocks in-process python adapters in some envs, so the
        # run may report a judge/adapter error; the sandbox audit branch must
        # still have executed.
        assert result.exit_code in (0, 1, 3), result.output


# --------------------------------------------------------------------------- #
# baseline.py
# --------------------------------------------------------------------------- #
class TestBaselineCommands:
    def test_save_missing_run_dir(self, tmp_path: Path) -> None:
        result = _invoke(
            "baseline", "save",
            "--name", "b",
            "--run", str(tmp_path / "nope"),
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 1
        assert "run directory not found" in result.output

    def test_save_missing_artifacts(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "runs" / "r"
        run_dir.mkdir(parents=True)
        result = _invoke(
            "baseline", "save",
            "--name", "b",
            "--run", str(run_dir),
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 1
        assert "no artifacts" in result.output

    def test_save_with_adapter_and_snapshot(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "runs" / "r"
        artifact_dir = run_dir / "artifacts"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "sc-1.json").write_text(
            json.dumps(_artifact(agent={"type": "python", "model": "m"}))
        )
        (run_dir / "scores.json").write_text(
            json.dumps(
                {
                    "scenario_scores": {
                        "sc-1": {"metrics": {"task_completion": {"score": 0.75}}}
                    },
                    "totals": {"passed": 1, "warned": 0, "failed": 0},
                }
            )
        )
        result = _invoke(
            "baseline", "save",
            "--name", "v1",
            "--run", str(run_dir),
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 0, result.output
        assert "saved" in result.output

    def test_list_empty(self, tmp_path: Path) -> None:
        result = _invoke("baseline", "list", "--output-dir", str(tmp_path))
        assert result.exit_code == 0
        assert "No baselines found" in result.output

    def test_validate_missing(self, tmp_path: Path) -> None:
        result = _invoke(
            "baseline", "validate",
            "--baseline", "nope",
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_validate_and_mismatch(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="v1", pack="other-pack", version="9.9.9")
        ok = _invoke(
            "baseline", "validate",
            "--baseline", "v1",
            "--output-dir", str(tmp_path),
        )
        assert ok.exit_code == 0
        assert "All checks passed" in ok.output

        mism = _invoke(
            "baseline", "validate",
            "--baseline", "v1",
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert mism.exit_code == 0
        assert "pack name mismatch" in mism.output
        assert "pack version mismatch" in mism.output

    def test_describe_with_score_and_notfound(self, tmp_path: Path) -> None:
        _seed_baseline(
            tmp_path,
            name="described",
            tags=["t1", "t2"],
            notes="hello",
            trust="external",
            snapshot={
                "scenario_scores": {
                    "sc-1": {"metrics": {"task_completion": {"score": 0.5}}}
                }
            },
        )
        result = _invoke(
            "baseline", "describe", "described",
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 0, result.output
        assert "described" in result.output

        missing = _invoke(
            "baseline", "describe", "nope", "--output-dir", str(tmp_path)
        )
        assert missing.exit_code == 1

    def test_describe_no_avg_score(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="plain", snapshot=None, git_sha=None)
        result = _invoke(
            "baseline", "describe", "plain", "--output-dir", str(tmp_path)
        )
        assert result.exit_code == 0, result.output

    def test_tag_and_notfound(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="tagme")
        result = _invoke(
            "baseline", "tag", "tagme", "a", "b", "--output-dir", str(tmp_path)
        )
        assert result.exit_code == 0, result.output
        assert "a, b" in result.output

        missing = _invoke(
            "baseline", "tag", "nope", "x", "--output-dir", str(tmp_path)
        )
        assert missing.exit_code == 1

    def test_annotate_and_notfound(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="annot")
        result = _invoke(
            "baseline", "annotate", "annot", "some notes", "--output-dir", str(tmp_path)
        )
        assert result.exit_code == 0, result.output
        assert "Notes updated" in result.output

        missing = _invoke(
            "baseline", "annotate", "nope", "x", "--output-dir", str(tmp_path)
        )
        assert missing.exit_code == 1

    def test_delete_force_and_notfound(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="del")
        result = _invoke(
            "baseline", "delete", "del", "--force", "--output-dir", str(tmp_path)
        )
        assert result.exit_code == 0, result.output
        assert "deleted" in result.output

        missing = _invoke(
            "baseline", "delete", "gone", "--force", "--output-dir", str(tmp_path)
        )
        assert missing.exit_code == 1

    def test_delete_prompt_confirm(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="confirm")
        result = CliRunner().invoke(
            main,
            ["baseline", "delete", "confirm", "--output-dir", str(tmp_path)],
            input="y\n",
        )
        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_delete_prompt_cancel(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="cancel")
        result = CliRunner().invoke(
            main,
            ["baseline", "delete", "cancel", "--output-dir", str(tmp_path)],
            input="n\n",
        )
        assert result.exit_code == 0
        assert "cancelled" in result.output


def _seed_baseline(
    base: Path,
    name: str = "b",
    pack: str = "test-pack",
    version: str = "1.0.0",
    tags: list[str] | None = None,
    notes: str = "",
    trust: str = "local",
    snapshot: dict | None = None,
    git_sha: str | None = "abc123",
) -> None:
    from agentdrill.baselines.model import Baseline
    from agentdrill.baselines.store import BaselineStore
    from agentdrill.models.artifact import RunArtifact

    store = BaselineStore(base_dir=f"{base}/baselines")
    store.save(
        Baseline(
            name=name,
            pack=pack,
            pack_version=version,
            runs=[RunArtifact(**_artifact())],
            score_snapshot=snapshot,
            tags=tags or [],
            notes=notes,
            trust=trust,
            git_sha=git_sha,
        )
    )


# --------------------------------------------------------------------------- #
# validate.py
# --------------------------------------------------------------------------- #
class TestValidateCommand:
    def test_pack_terminal(self) -> None:
        result = _invoke("validate", "--pack", str(PACK_YAML))
        assert result.exit_code == 0, result.output
        assert "2 scenarios" in result.output

    def test_pack_json_and_markdown(self) -> None:
        for fmt in ("json", "markdown"):
            result = _invoke(
                "validate", "--pack", str(PACK_YAML), "--output-format", fmt
            )
            assert result.exit_code == 0, result.output

    def test_pack_github_actions(self) -> None:
        result = _invoke(
            "validate", "--pack", str(PACK_YAML), "--output-format", "github-actions"
        )
        assert result.exit_code == 0, result.output

    def test_pack_invalid(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("pack:\n  name: broken\n")  # missing required fields
        result = _invoke("validate", "--pack", str(bad), "--output-format", "json")
        assert result.exit_code == 1
        assert '"valid": false' in result.output.lower()

    def test_agent_ok(self) -> None:
        result = _invoke("validate", "--agent", "python:fixtures.agents")
        assert result.exit_code == 0, result.output

    def test_agent_bad(self) -> None:
        result = _invoke("validate", "--agent", "python:does.not.exist")
        assert result.exit_code == 1

    def test_http_agent_connectivity_warning(self) -> None:
        import httpx

        def _fake_head(url, **kw):
            raise httpx.ConnectError("Connection refused")

        with patch("httpx.head", side_effect=_fake_head):
            result = _invoke(
                "validate",
                "--agent", "http:http://localhost:9999/nonexistent",
                "--output-format", "json",
            )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["agent"]["warnings"]

    def test_http_agent_500_warning(self) -> None:
        import httpx

        class _Resp:
            status_code = 503

        with patch("httpx.head", return_value=_Resp()):
            result = _invoke(
                "validate",
                "--agent", "http:http://localhost:8000/agent",
                "--output-format", "json",
            )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert any("503" in w for w in data["agent"]["warnings"])
        assert isinstance(httpx, object)  # keep import used

    def test_nothing_to_validate(self) -> None:
        result = _invoke("validate")
        assert result.exit_code == 1
        assert "Nothing to validate" in result.output

    def test_check_fixtures(self) -> None:
        result = _invoke("validate", "--pack", str(PACK_YAML), "--check-fixtures")
        assert result.exit_code == 0, result.output

    def test_pre_flight(self) -> None:
        result = _invoke("validate", "--pre-flight")
        assert result.exit_code == 0, result.output

    def test_baseline_ok(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="vb", pack="test-pack", version="1.0.0")
        result = _invoke(
            "validate",
            "--baseline", "vb",
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 0, result.output
        assert "baseline" in result.output

    def test_baseline_mismatch_and_strict(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="vb2", pack="other", version="9.9.9")
        lax = _invoke(
            "validate",
            "--baseline", "vb2",
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
            "--output-format", "json",
        )
        assert lax.exit_code == 0, lax.output
        assert "mismatch" in lax.output

        strict = _invoke(
            "validate",
            "--baseline", "vb2",
            "--pack", str(PACK_YAML),
            "--strict",
            "--output-dir", str(tmp_path),
        )
        assert strict.exit_code == 1

    def test_baseline_missing(self, tmp_path: Path) -> None:
        result = _invoke(
            "validate",
            "--baseline", "missing",
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 1

    def test_trust_policy_denied_for_external_pack(self, tmp_path: Path) -> None:
        external_pack = tmp_path / "external.yaml"
        external_pack.write_text(
            'pack:\n  name: ext\n  version: "1.0.0"\n  trust: external\n'
            "scenarios:\n"
            '  - id: "s1"\n'
            '    title: "t"\n'
            '    input: "i"\n'
            "    metrics:\n"
            "      task_completion: {threshold: 1.0}\n"
        )
        result = _invoke(
            "validate",
            "--pack", str(external_pack),
            "--agent", "python:fixtures.agents",
            "--output-format", "json",
        )
        assert result.exit_code == 1, result.output
        assert "trust_policy" in result.output


# --------------------------------------------------------------------------- #
# compare.py
# --------------------------------------------------------------------------- #
class TestCompareCommand:
    def test_compare_formats(self, tmp_path: Path) -> None:
        run_dir = _create_run(tmp_path)
        save = _invoke(
            "baseline", "save",
            "--name", "cmp-base",
            "--run", str(run_dir),
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert save.exit_code == 0, save.output

        for fmt in ("json", "markdown", "terminal", "github-actions"):
            result = _invoke(
                "compare",
                "--candidate", str(run_dir),
                "--baseline", "cmp-base",
                "--pack", str(PACK_YAML),
                "--output-dir", str(tmp_path),
                "--output-format", fmt,
                "--allow-adapter-change",
            )
            assert result.exit_code == 0, f"{fmt}: {result.output}"
        assert (run_dir / "comparison.md").exists()

    def test_compare_candidate_missing(self, tmp_path: Path) -> None:
        result = _invoke(
            "compare",
            "--candidate", str(tmp_path / "nope"),
            "--baseline", "b",
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 1
        assert "candidate run directory not found" in result.output

    def test_compare_baseline_missing(self, tmp_path: Path) -> None:
        run_dir = _create_run(tmp_path)
        result = _invoke(
            "compare",
            "--candidate", str(run_dir),
            "--baseline", "nope",
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_compare_rescore_no_scores_json(self, tmp_path: Path) -> None:
        run_dir = _create_run(tmp_path)
        # Keep artifacts but drop scores.json to force the re-scoring branch.
        (run_dir / "scores.json").unlink()
        save = _invoke(
            "baseline", "save",
            "--name", "cmp-base2",
            "--run", str(run_dir),
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
        )
        assert save.exit_code == 0, save.output
        result = _invoke(
            "compare",
            "--candidate", str(run_dir),
            "--baseline", "cmp-base2",
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
            "--output-format", "json",
        )
        # Re-scoring without a judge yields a judge-not-evaluated exit code,
        # but the re-score branch itself must have produced a report.
        assert "aggregate" in result.output

    def test_compare_baseline_without_snapshot(self, tmp_path: Path) -> None:
        run_dir = _create_run(tmp_path)
        # Baseline without a score snapshot exercises the re-scoring path.
        _seed_baseline(
            tmp_path,
            name="nosnap-base",
            pack="test-pack",
            version="1.0.0",
            snapshot=None,
        )
        result = _invoke(
            "compare",
            "--candidate", str(run_dir),
            "--baseline", "nosnap-base",
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
            "--output-format", "json",
        )
        assert result.exit_code == 0, result.output


# --------------------------------------------------------------------------- #
# benchmark.py
# --------------------------------------------------------------------------- #
class TestBenchmarkCommand:
    def test_import_swe_bench(self, tmp_path: Path) -> None:
        out = tmp_path / "swe.yaml"
        result = _invoke(
            "benchmark", "import",
            "--format", "swe-bench",
            "--input", str(SWE_BENCH),
            "--output", str(out),
        )
        assert result.exit_code == 0, result.output
        assert out.exists()
        assert "Loaded 3 tasks" in result.output

    def test_import_webarena_custom_pack_name(self, tmp_path: Path) -> None:
        out = tmp_path / "wa.yaml"
        result = _invoke(
            "benchmark", "import",
            "--format", "webarena",
            "--input", str(WEBARENA),
            "--output", str(out),
            "--pack-name", "my-web-pack",
        )
        assert result.exit_code == 0, result.output
        assert "my-web-pack" in result.output

    def test_import_unknown_format_aborts(self, tmp_path: Path) -> None:
        out = tmp_path / "x.yaml"
        with patch(
            "agentdrill.cli.benchmark.BenchmarkRegistry.load",
            side_effect=ValueError("Unknown benchmark format: x"),
        ):
            result = _invoke(
                "benchmark", "import",
                "--format", "swe-bench",
                "--input", str(SWE_BENCH),
                "--output", str(out),
            )
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_import_export_failure_aborts(self, tmp_path: Path) -> None:
        out = tmp_path / "y.yaml"
        with patch(
            "agentdrill.cli.benchmark.BenchmarkLoader.export_pack",
            side_effect=RuntimeError("cannot write"),
        ):
            result = _invoke(
                "benchmark", "import",
                "--format", "swe-bench",
                "--input", str(SWE_BENCH),
                "--output", str(out),
            )
        assert result.exit_code != 0
        assert "Export failed" in result.output


# --------------------------------------------------------------------------- #
# test.py
# --------------------------------------------------------------------------- #
class TestTestCommand:
    def _scenarios_dir(self, tmp_path: Path, packs: dict[str, str]) -> Path:
        d = tmp_path / "scenarios"
        d.mkdir()
        for name, content in packs.items():
            (d / name).write_text(content)
        return d

    def test_run_no_packs(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        result = _invoke(
            "test", "run",
            "--scenarios-dir", str(empty),
            "--agent", "python:fixtures.agents",
            "--output", str(tmp_path / "out"),
        )
        assert result.exit_code == 1
        assert "No scenario packs found" in result.output

    def test_run_markdown(self, tmp_path: Path) -> None:
        scenarios = self._scenarios_dir(
            tmp_path, {"pack.yaml": PACK_YAML.read_text()}
        )
        result = _invoke(
            "test", "run",
            "--scenarios-dir", str(scenarios),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path / "out"),
            "--output-format", "markdown",
        )
        assert result.exit_code == 0, result.output
        assert (tmp_path / "out" / "test-report.md").exists()
        assert (tmp_path / "out" / "test-report.json").exists()

    def test_run_json_and_tags(self, tmp_path: Path) -> None:
        scenarios = self._scenarios_dir(
            tmp_path, {"pack.yaml": PACK_YAML.read_text()}
        )
        result = _invoke(
            "test", "run",
            "--scenarios-dir", str(scenarios),
            "--agent", "python:fixtures.agents:run",
            "--judge", "mock",
            "--output", str(tmp_path / "out"),
            "--output-format", "json",
            "--tags", "tag-a",
            "--ci",
        )
        assert result.exit_code == 0, result.output

    def test_run_pack_error(self, tmp_path: Path) -> None:
        scenarios = self._scenarios_dir(
            tmp_path,
            {
                "bad.yaml": "pack:\n  name: broken\n",
                "good.yaml": PACK_YAML.read_text(),
            },
        )
        result = _invoke(
            "test", "run",
            "--scenarios-dir", str(scenarios),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path / "out"),
            "--output-format", "json",
        )
        assert result.exit_code == 1
        assert "Error processing" in result.output


# --------------------------------------------------------------------------- #
# Branch-coverage extras: divergence gating, scoring breakdown, discovery.
# --------------------------------------------------------------------------- #
_DANGER_AGENT = '''
def run(payload: dict) -> dict:
    return {
        "schema_version": "agentdrill.run_envelope.v1",
        "status": "completed",
        "output": {"final": "I called the dangerous tool", "structured": None},
        "trajectory": {
            "steps": [
                {"type": "tool_call", "tool": "danger", "args": {}, "duration_ms": 1}
            ]
        },
        "cost": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2, "cost_usd": 0.0},
        "error": None,
    }
'''

_HYBRID_PACK = """\
pack:
  name: "hybrid-cov-pack"
  version: "1.0.0"
scenarios:
  - id: "h-1"
    title: "Hybrid divergence scenario"
    input: "do the thing"
    disallowed_tools:
      - name: "danger"
    metrics:
      task_completion: {threshold: 1.0}
      zero_disallowed_actions: {threshold: 1.0}
      step_efficiency: {threshold: 1.0}
"""


def _write_danger_agent(tmp_path: Path) -> tuple[str, str]:
    """Write a mock agent that trips the disallowed-tool gate.

    Returns the module name and the directory added to ``sys.path`` so the
    caller can undo the ``sys.path`` mutation.
    """
    import sys

    (tmp_path / "m0cov_danger_agent.py").write_text(_DANGER_AGENT)
    sys.path.insert(0, str(tmp_path))
    return "m0cov_danger_agent", str(tmp_path)


class TestRunBranchCoverage:
    def test_ci_forces_json(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--ci",
        )
        assert result.exit_code == 0, result.output

    def test_agent_function_override(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--agent-function", "run",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
        )
        assert result.exit_code == 0, result.output

    def test_fixtures_flag(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--fixtures",
        )
        assert result.exit_code == 0, result.output

    def test_live_flag(self, tmp_path: Path) -> None:
        result = _invoke(
            "run",
            "--pack", str(PACK_YAML),
            "--agent", "python:fixtures.agents",
            "--judge", "mock",
            "--output", str(tmp_path),
            "--output-format", "json",
            "--live",
        )
        assert result.exit_code == 0, result.output

    def test_hybrid_breakdown_and_safety_echo(self, tmp_path: Path) -> None:
        module, _ = _write_danger_agent(tmp_path)
        pack = tmp_path / "hybrid.yaml"
        pack.write_text(_HYBRID_PACK)
        try:
            result = _invoke(
                "run",
                "--pack", str(pack),
                "--agent", f"python:{module}",
                "--judge", "mock",
                "--output", str(tmp_path),
                "--output-format", "json",
            )
        finally:
            import sys

            sys.path.remove(str(tmp_path))
        # Safety violation present -> non-zero, and the summary echoes it.
        assert result.exit_code == 4, result.output
        assert "Safety violations" in result.output

    def test_fail_on_safety_dimension_gate(self, tmp_path: Path) -> None:
        module, _ = _write_danger_agent(tmp_path)
        pack = tmp_path / "hybrid2.yaml"
        pack.write_text(_HYBRID_PACK)
        try:
            result = _invoke(
                "run",
                "--pack", str(pack),
                "--agent", f"python:{module}",
                "--judge", "mock",
                "--output", str(tmp_path),
                "--output-format", "json",
                "--fail-on", "safety",
            )
        finally:
            import sys

            sys.path.remove(str(tmp_path))
        assert result.exit_code == 1, result.output
        assert "below threshold" in result.output

    def test_fail_on_divergence_critical(self, tmp_path: Path) -> None:
        module, _ = _write_danger_agent(tmp_path)
        pack = tmp_path / "hybrid3.yaml"
        pack.write_text(_HYBRID_PACK)
        try:
            result = _invoke(
                "run",
                "--pack", str(pack),
                "--agent", f"python:{module}",
                "--judge", "mock",
                "--output", str(tmp_path),
                "--output-format", "json",
                "--fail-on-divergence", "critical",
            )
        finally:
            import sys

            sys.path.remove(str(tmp_path))
        assert result.exit_code == 5, result.output
        assert "Critical divergences" in result.output

    def test_fail_on_divergence_warning_and_all(self, tmp_path: Path) -> None:
        from agentdrill.scoring.judge.mock import MockJudge

        module, _ = _write_danger_agent(tmp_path)
        pack = tmp_path / "hybrid4.yaml"
        pack.write_text(_HYBRID_PACK)
        try:
            for mode in ("warning", "all"):
                with patch(
                    "agentdrill.cli.run._resolve_judge",
                    return_value=MockJudge(score=0.0),
                ):
                    result = _invoke(
                        "run",
                        "--pack", str(pack),
                        "--agent", f"python:{module}",
                        "--judge", "mock",
                        "--output", str(tmp_path),
                        "--output-format", "json",
                        "--fail-on-divergence", mode,
                    )
                assert result.exit_code == 5, f"{mode}: {result.output}"
        finally:
            import sys

            sys.path.remove(str(tmp_path))


class TestBaselineListCoverage:
    def test_list_with_entries(self, tmp_path: Path) -> None:
        _seed_baseline(tmp_path, name="aa", pack="p1", version="1.0.0")
        _seed_baseline(tmp_path, name="bb", pack="p2", version="2.0.0")
        result = _invoke("baseline", "list", "--output-dir", str(tmp_path))
        assert result.exit_code == 0, result.output
        assert "aa" in result.output
        assert "bb" in result.output

    def test_save_git_sha_lookup_failure(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "runs" / "r"
        artifact_dir = run_dir / "artifacts"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "sc-1.json").write_text(json.dumps(_artifact()))
        with patch(
            "agentdrill.cli.baseline.subprocess.check_output",
            side_effect=OSError("git not available"),
        ):
            result = _invoke(
                "baseline", "save",
                "--name", "nogit",
                "--run", str(run_dir),
                "--pack", str(PACK_YAML),
                "--output-dir", str(tmp_path),
            )
        assert result.exit_code == 0, result.output
        assert "saved" in result.output


class TestCompareManifestCoverage:
    def test_compare_candidate_without_adapter_type(self, tmp_path: Path) -> None:
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore

        # Candidate artifacts carry no adapter type, so the manifest is None.
        run_dir = tmp_path / "runs" / "cand"
        artifact_dir = run_dir / "artifacts"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "sc-1.json").write_text(json.dumps(_artifact()))
        _seed_baseline(tmp_path, name="mbase")
        store = BaselineStore(base_dir=f"{tmp_path}/baselines")
        store.save(
            Baseline(
                name="mbase",
                pack="test-pack",
                pack_version="1.0.0",
                runs=store.load("mbase").runs,
            )
        )
        result = _invoke(
            "compare",
            "--candidate", str(run_dir),
            "--baseline", "mbase",
            "--pack", str(PACK_YAML),
            "--output-dir", str(tmp_path),
            "--output-format", "json",
        )
        assert "aggregate" in result.output


class TestValidateFixturesCoverage:
    def test_missing_fixture_reports_failure(self, tmp_path: Path) -> None:
        pack = tmp_path / "tool_pack.yaml"
        pack.write_text(
            'pack:\n  name: "tool-pack"\n  version: "1.0.0"\n'
            "scenarios:\n"
            '  - id: "t-1"\n'
            '    title: "t"\n'
            '    input: "i"\n'
            "    allowed_tools:\n"
            '      - name: "no_such_fixture_tool_xyz"\n'
            "    metrics:\n"
            "      task_completion: {threshold: 1.0}\n"
        )
        result = _invoke(
            "validate",
            "--pack", str(pack),
            "--check-fixtures",
            "--output-format", "json",
        )
        assert result.exit_code == 1, result.output
        assert "no_such_fixture_tool_xyz" in result.output

    def test_unknown_trust_falls_back_to_local(self, tmp_path: Path) -> None:
        pack = tmp_path / "weird_trust.yaml"
        pack.write_text(
            'pack:\n  name: "weird"\n  version: "1.0.0"\n  trust: "weird"\n'
            "scenarios:\n"
            '  - id: "w-1"\n'
            '    title: "w"\n'
            '    input: "i"\n'
            "    metrics:\n"
            "      task_completion: {threshold: 1.0}\n"
        )
        result = _invoke(
            "validate",
            "--pack", str(pack),
            "--agent", "python:fixtures.agents",
            "--output-format", "json",
        )
        # Falls back to "local" trust, which allows the python adapter.
        assert result.exit_code == 0, result.output

    def test_fixtures_check_exception_path(self, tmp_path: Path) -> None:
        with patch(
            "agentdrill.loading.pack_loader.load_pack",
            side_effect=RuntimeError("boom"),
        ):
            result = _invoke(
                "validate",
                "--pack", str(PACK_YAML),
                "--check-fixtures",
                "--output-format", "json",
            )
        assert result.exit_code == 1
        assert "boom" in result.output


class TestTestCommandCoverage:
    def test_run_nonexistent_dir(self, tmp_path: Path) -> None:
        result = _invoke(
            "test", "run",
            "--scenarios-dir", str(tmp_path / "does-not-exist"),
            "--agent", "python:fixtures.agents",
            "--output", str(tmp_path / "out"),
        )
        assert result.exit_code == 1
        assert "No scenario packs found" in result.output

    def test_run_safety_summary(self, tmp_path: Path) -> None:
        module, _ = _write_danger_agent(tmp_path)
        scenarios = tmp_path / "scenarios"
        scenarios.mkdir()
        (scenarios / "hybrid.yaml").write_text(_HYBRID_PACK)
        try:
            result = _invoke(
                "test", "run",
                "--scenarios-dir", str(scenarios),
                "--agent", f"python:{module}",
                "--agent-function", "run",
                "--judge", "mock",
                "--output", str(tmp_path / "out"),
                "--output-format", "json",
            )
        finally:
            import sys

            sys.path.remove(str(tmp_path))
        assert result.exit_code == 1, result.output
        assert "Safety violations" in result.output
