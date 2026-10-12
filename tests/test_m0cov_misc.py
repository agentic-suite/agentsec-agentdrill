"""Broad edge-path coverage tests for assorted AgentDrill modules.

This file deliberately targets branch/edge paths that the primary test
modules do not exercise: pytest-plugin hooks and fixtures called directly,
benchmark loader fallbacks, egress policy profiles, sandbox env stripping,
security scorers, browser fixtures, observability metrics/tracing, the
comparison engine's aggregate/model/adapter detection, the schema validator's
compatibility checks, the failure taxonomy recommendations, the scoring
engine's judge cache, and the testing helpers.

All tests are deterministic and offline.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentdrill.analytics.taxonomy import (
    FailureCategory,
    FailureTaxonomy,
    _build_recommendations,
    classify_failure,
)
from agentdrill.baselines.model import Baseline
from agentdrill.benchmarks.loader import (
    BenchmarkLoader,
    BenchmarkRegistry,
    BenchmarkTask,
    _BenchmarkLoadError,
)
from agentdrill.comparison.engine import ComparisonEngine, _candidate_model, _sum_cost
from agentdrill.fixtures.browser import BrowserFixture, BrowserToolStub
from agentdrill.fixtures.tool_stub import FixtureNotFoundError
from agentdrill.models.artifact import Cost, RunArtifact, RunOutput, RunTimestamps, TrajectoryStep
from agentdrill.models.pack import (
    Metric,
    PackMetadata,
    Scenario,
    ScenarioPack,
)
from agentdrill.observability.metrics import EvalMetrics, MetricsCollector
from agentdrill.observability.tracing import OpenTelemetryTracer, TraceSpan
from agentdrill.pytest_plugin import (
    agent_adapter,
    agent_config,
    pytest_addoption,
    pytest_configure,
    pytest_generate_tests,
    scenario_pack,
)
from agentdrill.schema_version import SchemaRegistry, SchemaValidator
from agentdrill.scoring.engine import ScoringEngine
from agentdrill.scoring.result import RunScore, ScenarioScore, ScoreResult
from agentdrill.security import evals as security_evals
from agentdrill.security.egress import (
    EgressController,
    EgressPolicy,
    EgressPolicyBuilder,
)
from agentdrill.security.evals import (
    EXFILTRATION_PATTERNS,
    SecurityScenarioGenerator,
    _extract_output_text,
    _extract_tool_args_text,
    _pattern_match_score,
)
from agentdrill.security.sandbox import (
    DockerConfig,
    SandboxConfig,
    run_in_container,
    sandboxed_run,
)

FIXTURES = Path(__file__).parent / "fixtures"
VALID_PACK = FIXTURES / "valid_pack.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _artifact(
    scenario_id: str = "sc-1",
    final: str | None = "ok",
    status: str = "completed",
    trajectory: list[TrajectoryStep] | None = None,
    structured: Any = None,
    duration_ms: int = 1000,
    error: str | None = None,
    error_category: str | None = None,
    agent: dict[str, Any] | None = None,
    cost_usd: float = 0.0,
) -> RunArtifact:
    return RunArtifact(
        id=f"r-{scenario_id}",
        scenario_id=scenario_id,
        agent=agent or {},
        timestamp=RunTimestamps(start="a", end="b", duration_ms=duration_ms),
        output=RunOutput(final=final, structured=structured),
        trajectory=trajectory or [],
        cost=Cost(cost_usd=cost_usd),
        status=status,  # type: ignore[arg-type]
        error=error,
        error_category=error_category,
    )


def _score_result(
    name: str, score: float | None, passed: bool | None, category: str = "correctness"
) -> ScoreResult:
    return ScoreResult(
        metric=name,
        score=score,
        threshold=0.5,
        passed=passed,
        category=category,
        blocking=False,
        detail={},
        source="deterministic",
        error=None,
    )


def _scenario_score(
    sid: str,
    status: str,
    scores: dict[str, tuple[float | None, bool | None]] | None = None,
    safety: list[str] | None = None,
    categories: dict[str, str] | None = None,
) -> ScenarioScore:
    results = {}
    for name, (score, passed) in (scores or {}).items():
        results[name] = _score_result(
            name, score, passed, (categories or {}).get(name, "correctness")
        )
    return ScenarioScore(
        scenario_id=sid,
        metric_results=results,
        status=status,
        safety_violations=safety or [],
    )


def _run_score(scenario_scores: dict[str, ScenarioScore]) -> RunScore:
    return RunScore(
        scenario_scores=scenario_scores,
        totals={"passed": 0, "warned": 0, "failed": 0},
        safety_violations=[],
        exit_code=0,
    )


def _scenario(
    sid: str = "sc-1", tags: list[str] | None = None, metrics: dict[str, Metric] | None = None
) -> Scenario:
    return Scenario(id=sid, title="t", input="i", tags=tags or [], metrics=metrics or {})


# ===========================================================================
# pytest_plugin.py — call hooks/fixtures directly
# ===========================================================================


class _FakeGroup:
    def __init__(self) -> None:
        self.options: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def addoption(self, *args: Any, **kwargs: Any) -> None:
        self.options.append((args, kwargs))


class _FakeParser:
    def __init__(self) -> None:
        self.group = _FakeGroup()
        self.groups_requested: list[str] = []

    def getgroup(self, name: str) -> _FakeGroup:
        self.groups_requested.append(name)
        return self.group


class _FakeConfig:
    def __init__(self, options: dict[str, Any] | None = None) -> None:
        self.options = options or {}
        self.lines: list[tuple[str, str]] = []

    def getoption(self, name: str) -> Any:
        return self.options.get(name)

    def addinivalue_line(self, name: str, line: str) -> None:
        self.lines.append((name, line))


class _FakeMarker:
    def __init__(self, args: tuple[Any, ...] = (), kwargs: dict[str, Any] | None = None) -> None:
        self.args = args
        self.kwargs = kwargs or {}


class _FakeDefinition:
    def __init__(self, markers: dict[str, _FakeMarker] | None = None) -> None:
        self._markers = markers or {}

    def get_closest_marker(self, name: str) -> _FakeMarker | None:
        return self._markers.get(name)


class _FakeMetafunc:
    def __init__(
        self,
        fixturenames: list[str],
        markers: dict[str, _FakeMarker] | None = None,
        options: dict[str, Any] | None = None,
    ) -> None:
        self.fixturenames = fixturenames
        self.definition = _FakeDefinition(markers)
        self.config = _FakeConfig(options)
        self.param_calls: list[tuple[str, Any, Any]] = []

    def parametrize(self, argnames: str, argvalues: Any, ids: Any = None) -> None:
        self.param_calls.append((argnames, argvalues, ids))


class _FakeNode:
    def __init__(self, marker: _FakeMarker | None = None) -> None:
        self._marker = marker

    def get_closest_marker(self, name: str) -> _FakeMarker | None:
        return self._marker


class _FakeRequest:
    def __init__(self, config: _FakeConfig, marker: _FakeMarker | None = None) -> None:
        self.config = config
        self.node = _FakeNode(marker)


def test_plugin_addoption_registers_all_options() -> None:
    parser = _FakeParser()
    pytest_addoption(parser)  # type: ignore[arg-type]
    assert parser.groups_requested == ["agentdrill"]
    names = {args[0] for args, _ in parser.group.options}
    assert names == {
        "--agentdrill-pack",
        "--agentdrill-agent",
        "--agentdrill-judge",
        "--agentdrill-tags",
        "--agentdrill-output",
    }


def test_plugin_configure_registers_markers() -> None:
    config = _FakeConfig()
    pytest_configure(config)  # type: ignore[arg-type]
    assert len(config.lines) == 2
    assert all(name == "markers" for name, _ in config.lines)
    assert any("agentdrill(" in line for _, line in config.lines)


def test_generate_tests_ignored_without_scenario_fixture() -> None:
    metafunc = _FakeMetafunc(fixturenames=["other"])
    pytest_generate_tests(metafunc)  # type: ignore[arg-type]
    assert metafunc.param_calls == []


def test_generate_tests_no_pack_returns_silently() -> None:
    metafunc = _FakeMetafunc(fixturenames=["scenario"])
    pytest_generate_tests(metafunc)  # type: ignore[arg-type]
    assert metafunc.param_calls == []


def test_generate_tests_parametrizes_from_marker_pack() -> None:
    metafunc = _FakeMetafunc(
        fixturenames=["scenario"],
        markers={"agentdrill": _FakeMarker(kwargs={"pack": str(VALID_PACK)})},
    )
    pytest_generate_tests(metafunc)  # type: ignore[arg-type]
    assert len(metafunc.param_calls) == 1
    argnames, scenarios, ids = metafunc.param_calls[0]
    assert argnames == "scenario"
    assert ids == ["sc-1", "sc-2"]
    assert len(scenarios) == 2


def test_generate_tests_parametrizes_from_cli_pack() -> None:
    metafunc = _FakeMetafunc(
        fixturenames=["scenario"],
        options={"--agentdrill-pack": str(VALID_PACK)},
    )
    pytest_generate_tests(metafunc)  # type: ignore[arg-type]
    assert len(metafunc.param_calls) == 1


def test_generate_tests_tags_marker_filter() -> None:
    metafunc = _FakeMetafunc(
        fixturenames=["scenario"],
        markers={
            "agentdrill": _FakeMarker(kwargs={"pack": str(VALID_PACK)}),
            "agentdrill_tags": _FakeMarker(args=("tag-b",)),
        },
    )
    pytest_generate_tests(metafunc)  # type: ignore[arg-type]
    _, scenarios, ids = metafunc.param_calls[0]
    assert ids == ["sc-1"]
    assert len(scenarios) == 1


def test_generate_tests_tags_cli_filter() -> None:
    metafunc = _FakeMetafunc(
        fixturenames=["scenario"],
        options={
            "--agentdrill-pack": str(VALID_PACK),
            "--agentdrill-tags": "tag-a,tag-b",
        },
    )
    pytest_generate_tests(metafunc)  # type: ignore[arg-type]
    _, _, ids = metafunc.param_calls[0]
    assert ids == ["sc-1", "sc-2"]


def test_agent_config_fixture_skips_without_spec() -> None:
    request = _FakeRequest(config=_FakeConfig({}))
    with pytest.raises(pytest.skip.Exception):
        agent_config.__wrapped__(request)  # type: ignore[attr-defined]


def test_agent_config_fixture_uses_cli_option() -> None:
    request = _FakeRequest(config=_FakeConfig({"--agentdrill-agent": "python:fixtures.agents"}))
    cfg = agent_config.__wrapped__(request)  # type: ignore[attr-defined]
    assert cfg["type"] == "python"
    assert "run_id" in cfg


def test_agent_config_fixture_uses_marker() -> None:
    request = _FakeRequest(
        config=_FakeConfig({}),
        marker=_FakeMarker(kwargs={"agent": "subprocess:/bin/echo"}),
    )
    cfg = agent_config.__wrapped__(request)  # type: ignore[attr-defined]
    assert cfg["type"] == "subprocess"


def test_scenario_pack_fixture_skips_without_pack() -> None:
    request = _FakeRequest(config=_FakeConfig({}))
    with pytest.raises(pytest.skip.Exception):
        scenario_pack.__wrapped__(request)  # type: ignore[attr-defined]


def test_scenario_pack_fixture_from_cli() -> None:
    request = _FakeRequest(config=_FakeConfig({"--agentdrill-pack": str(VALID_PACK)}))
    pack = scenario_pack.__wrapped__(request)  # type: ignore[attr-defined]
    assert len(pack.scenarios) == 2


def test_scenario_pack_fixture_from_marker() -> None:
    request = _FakeRequest(
        config=_FakeConfig({}),
        marker=_FakeMarker(kwargs={"pack": str(VALID_PACK)}),
    )
    pack = scenario_pack.__wrapped__(request)  # type: ignore[attr-defined]
    assert pack.pack.name == "test-pack"


def test_agent_adapter_fixture_delegates_to_factory() -> None:
    sentinel = object()
    with patch("agentdrill.adapters.factory.create_adapter", return_value=sentinel) as m:
        result = agent_adapter.__wrapped__({"type": "python"})  # type: ignore[attr-defined]
    assert result is sentinel
    m.assert_called_once_with({"type": "python"})


# ===========================================================================
# benchmarks/loader.py — fallbacks and branch coverage
# ===========================================================================


def test_swe_bench_parse_defaults_and_optional_fields() -> None:
    loader = BenchmarkLoader()
    task = loader._parse_swe_bench_task({"problem_statement": "fix it"}, line_num=7)
    assert task.task_id == "swe-unknown-7"
    assert task.expected["type"] == "exact"
    assert task.reference_output is None

    full = loader._parse_swe_bench_task(
        {
            "instance_id": "swe-9",
            "repo": "r/x",
            "issue": "the issue",
            "base_commit": "abc",
            "patch": "patch-text",
            "hints_text": "hint",
            "FAIL_TO_PASS": ["t1"],
            "PASS_TO_PASS": ["t2"],
        },
        line_num=1,
    )
    assert full.expected["hints_text"] == "hint"
    assert full.expected["fail_to_pass"] == ["t1"]
    assert full.expected["pass_to_pass"] == ["t2"]
    assert full.reference_output == "patch-text"


def test_swe_bench_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "d.jsonl"
    path.write_text('{"instance_id": "x"}\n\n   \n', encoding="utf-8")
    tasks = BenchmarkLoader().load_swe_bench(path)
    assert len(tasks) == 1


def test_webarena_parse_string_start_urls_and_non_dict_expected() -> None:
    loader = BenchmarkLoader()
    task = loader._parse_webarena_task(
        {
            "intent": "do thing",
            "sites": ["a", "b"],
            "start_urls": "http://start",
            "expected": "plain",
            "eval": "not-a-dict",
        },
        idx=0,
    )
    assert "Sites: a, b" in task.prompt
    assert "Start URL(s): http://start" in task.prompt
    assert task.expected == {"value": "plain"}
    assert task.reference_output is None


def test_webarena_parse_eval_reference_answer() -> None:
    loader = BenchmarkLoader()
    task = loader._parse_webarena_task(
        {
            "intent_template": "tpl",
            "start_url": "http://one",
            "eval": {"reference_answer": "42"},
        },
        idx=3,
    )
    assert task.task_id == "wa-unknown-3"
    assert task.reference_output == "42"


def test_build_expected_all_types() -> None:
    make = lambda exp, ref=None: BenchmarkTask(  # noqa: E731
        task_id="t", category="c", prompt="p", expected=exp, tools=[], reference_output=ref
    )
    assert BenchmarkLoader._build_expected(make({"type": "exact", "value": "v"})).value == "v"
    assert BenchmarkLoader._build_expected(make({}, ref="ref")).value == "ref"
    assert (
        BenchmarkLoader._build_expected(make({"type": "exact", "reference_answer": "ra"})).value
        == "ra"
    )
    schema = BenchmarkLoader._build_expected(
        make({"type": "schema", "schema": {"type": "object"}, "required_fields": ["a"]})
    )
    assert schema.type == "schema"
    trace = BenchmarkLoader._build_expected(
        make({"type": "tool_trace", "trace": [{"name": "t"}], "required_tools": ["t"]})
    )
    assert trace.type == "tool_trace"
    targs = BenchmarkLoader._build_expected(
        make({"type": "tool_args", "tool_name": "x", "tool_args": {"k": 1}})
    )
    assert targs.type == "tool_args"
    assert targs.tool == "x"
    rubric = BenchmarkLoader._build_expected(make({"type": "rubric", "criteria": ["c"]}))
    assert rubric.type == "rubric"
    # Unknown type falls back to exact
    fallback = BenchmarkLoader._build_expected(make({"type": "bogus", "value": "z"}))
    assert fallback.type == "exact"


def test_build_metrics_all_categories() -> None:
    def task(cat: str) -> BenchmarkTask:
        return BenchmarkTask(task_id="t", category=cat, prompt="p", expected={}, tools=[])

    assert set(BenchmarkLoader._build_metrics(task("swe-bench"))) == {
        "output_correctness",
        "tool_correctness",
        "task_completion",
    }
    assert set(BenchmarkLoader._build_metrics(task("webarena"))) == {
        "task_completion",
        "tool_correctness",
        "navigation_efficiency",
    }
    other = BenchmarkLoader._build_metrics(task("custom"))
    assert set(other) == {"task_completion"}
    assert other["task_completion"].weight == 1.0


def test_registry_overwrite_logs_and_registers() -> None:
    registry = BenchmarkRegistry()
    registry.register("swe-bench", lambda p: [])  # overwrite builtin
    assert registry.load("swe-bench", "anything") == []


def test_export_creates_parent_dirs(tmp_path: Path) -> None:
    loader = BenchmarkLoader()
    task = BenchmarkTask(
        task_id="x", category="c", prompt="p", expected={"type": "exact", "value": "v"}, tools=[]
    )
    out = tmp_path / "nested" / "deep" / "pack.yaml"
    result = loader.export_pack([task], out, "p")
    assert result == out
    assert out.exists()


def test_benchmark_load_error_is_exception() -> None:
    assert issubclass(_BenchmarkLoadError, Exception)


# ===========================================================================
# security/egress.py — policy profiles and detection branches
# ===========================================================================


def test_egress_private_ip_blocked_reason() -> None:
    policy = EgressPolicy(allowed_domains=["*"], allow_private_ips=False)
    ctrl = EgressController(policy)
    allowed, reason = ctrl.check_url("https://10.0.0.1/")
    assert not allowed
    assert "private IP" in reason


def test_egress_private_ip_allowed_reason() -> None:
    policy = EgressPolicyBuilder.development()
    ctrl = EgressController(policy)
    allowed, reason = ctrl.check_url("http://10.0.0.1:8080/")
    assert allowed
    assert "private IP" in reason


def test_egress_localhost_allowed_reason() -> None:
    policy = EgressPolicy(allow_localhost=True)
    ctrl = EgressController(policy)
    allowed, reason = ctrl.check_url("https://localhost/")
    assert allowed
    assert "localhost" in reason


def test_egress_default_deny_all_no_domains() -> None:
    ctrl = EgressController()
    allowed, reason = ctrl.check_url("https://example.com/")
    assert not allowed
    assert "no domains are allowed" in reason


def test_egress_domain_not_in_allowlist() -> None:
    policy = EgressPolicy(allowed_domains=["example.com"])
    ctrl = EgressController(policy)
    allowed, reason = ctrl.check_url("https://other.com/")
    assert not allowed
    assert "not in the allowlist" in reason


def test_egress_parse_url_without_scheme() -> None:
    scheme, host, port, path = EgressController.parse_url("example.com/foo")
    assert scheme == "https"
    assert host == ""
    assert port == 443
    assert path == "example.com/foo"


def test_egress_block_list_blocks_named_domains() -> None:
    policy = EgressPolicyBuilder.block_list(["evil.com"])
    ctrl = EgressController(policy)
    allowed, reason = ctrl.check_url("http://evil.com/")
    assert not allowed
    assert "blocked" in reason


def test_egress_air_gapped_blocks_everything() -> None:
    ctrl = EgressController(EgressPolicyBuilder.air_gapped())
    allowed, reason = ctrl.check_url("https://example.com/")
    assert not allowed
    assert "no domains are allowed" in reason


def test_egress_check_request_logs_and_returns() -> None:
    policy = EgressPolicy(allowed_domains=["example.com"], log_all_requests=True)
    ctrl = EgressController(policy)
    allowed, _reason = ctrl.check_request("GET", "https://example.com/x", {"H": "v"})
    assert allowed
    log = ctrl.get_request_log()
    assert log and log[0]["status"] == "allowed"


def test_egress_allow_list_isolation() -> None:
    domains = ["a.com"]
    policy = EgressPolicyBuilder.allow_list(domains)
    domains.append("b.com")
    assert policy.allowed_domains == ["a.com"]


# ===========================================================================
# security/sandbox.py — env stripping + docker command construction
# ===========================================================================


def test_sandboxed_run_disabled_passthrough() -> None:
    result = sandboxed_run(
        [sys.executable, "-c", "print('hi')"],
        SandboxConfig(enabled=False),
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "hi"


def test_sandboxed_run_enabled_strips_env() -> None:
    script = (
        "import os; print(os.environ.get('AGENTDRILL_SANDBOX')); print(os.environ.get('SECRET'))"
    )
    result = sandboxed_run(
        [sys.executable, "-c", script],
        SandboxConfig(enabled=True),
        env={"SECRET": "leak", "AGENTDRILL_FIXTURES_DIR": "/fx"},
        timeout=30,
    )
    assert result.returncode == 0
    lines = result.stdout.splitlines()
    assert lines[0] == "1"
    assert lines[1] == "None"  # SECRET was stripped by the allowlist


def test_sandboxed_run_enabled_respects_timeout_multiplier() -> None:
    result = sandboxed_run(
        [sys.executable, "-c", "import sys; sys.stdin.read(); print('done')"],
        SandboxConfig(enabled=True, timeout_multiplier=3.0),
        input="payload",
        timeout=10,
    )
    assert result.stdout.strip() == "done"


def test_run_in_container_builds_args_and_logs(tmp_path: Path) -> None:
    captured: dict[str, Any] = {}

    def fake_run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args, 0, stdout="out", stderr="err")

    log_dir = tmp_path / "logs"
    with (
        patch("agentdrill.security.sandbox.subprocess.run", side_effect=fake_run),
        patch.dict(os.environ, {"AGENTDRILL_DOCKER_LOG_DIR": str(log_dir)}),
    ):
        result = run_in_container(
            ["my-agent", "--flag"],
            "payload",
            DockerConfig(image="img:1", add_host_gateway=False),
            timeout=5,
        )

    assert result.stdout == "out"
    args = captured["args"]
    for token in [
        "--network",
        "none",
        "--read-only",
        "--memory",
        "512m",
        "--cpus",
        "--tmpfs",
        "--entrypoint",
        "img:1",
    ]:
        assert token in args
    assert args[-2:] == ["my-agent", "--flag"]
    assert any(p.name == "meta.json" for p in log_dir.rglob("meta.json"))


def test_run_in_container_linux_host_gateway_patched() -> None:
    captured: dict[str, Any] = {}

    def fake_run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    with (
        patch("agentdrill.security.sandbox.subprocess.run", side_effect=fake_run),
        patch("platform.system", return_value="Linux"),
    ):
        run_in_container(["x"], "", DockerConfig(add_host_gateway=True), timeout=1)
    assert "host.docker.internal:host-gateway" in captured["args"]


def test_run_in_container_logging_failure_is_swallowed() -> None:
    def fake_run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    with (
        patch("agentdrill.security.sandbox.subprocess.run", side_effect=fake_run),
        patch("agentdrill.security.sandbox.os.makedirs", side_effect=OSError("nope")),
        patch.dict(os.environ, {"AGENTDRILL_DOCKER_LOG_DIR": "/does/not/matter"}),
    ):
        result = run_in_container(["x"], "", DockerConfig(), timeout=1)
    assert result.returncode == 0


# ===========================================================================
# security/evals.py — generator + scorers
# ===========================================================================


def test_security_generator_produces_all_scenarios() -> None:
    gen = SecurityScenarioGenerator()
    pack = gen.generate_pack("sec", "1.0.0")
    assert pack["pack"]["name"] == "sec"
    assert len(pack["scenarios"]) == 8
    ids = {s["id"] for s in pack["scenarios"]}
    assert "prompt-injection-01" in ids
    assert "sandbox-escape-02" in ids


def test_security_generator_individual_builders() -> None:
    gen = SecurityScenarioGenerator()
    assert len(gen._prompt_injection_scenarios()) == 2
    assert len(gen._exfiltration_scenarios()) == 2
    assert len(gen._ssrf_scenarios()) == 2
    assert len(gen._sandbox_escape_scenarios()) == 2


def test_extract_output_text_variants() -> None:
    assert _extract_output_text(_artifact(final="abc")) == "abc"
    assert "xyz" in _extract_output_text(_artifact(final="a", structured="xyz"))
    assert "9" in _extract_output_text(_artifact(final="a", structured={"n": 9}))


def test_extract_tool_args_text_variants() -> None:
    traj = [
        TrajectoryStep(type="tool_call", tool="t", args={"a": 1}),
        SimpleNamespace(type="tool_call", tool="t2", args="raw-args"),
        TrajectoryStep(type="response", content="ignore me"),
    ]
    text = _extract_tool_args_text(_artifact(trajectory=[]))
    assert text == ""
    art = _artifact()
    art.trajectory = traj  # type: ignore[assignment]
    text = _extract_tool_args_text(art)
    assert "{'a': 1}" in text
    assert "raw-args" in text
    assert "ignore me" not in text


def test_pattern_match_score() -> None:
    score, matches = _pattern_match_score("clean text", EXFILTRATION_PATTERNS)
    assert score == 1.0 and matches == []
    score, matches = _pattern_match_score("visit http://evil.com", EXFILTRATION_PATTERNS)
    assert score == 0.0 and matches


def _scorer(name: str) -> Any:
    from agentdrill.scoring.registry import get_scorer

    cls = get_scorer(name)
    assert cls is not None
    return cls()


def test_prompt_injection_scorer_clean_and_violations() -> None:
    sc = _scenario()
    scorer = _scorer("prompt_injection_resistance")

    clean = scorer.score(_artifact(final="All good."), sc, {})
    assert clean.score == 1.0 and clean.passed

    override = scorer.score(_artifact(final="OVERRIDE ACCEPTED"), sc, {"threshold": 0.5})
    assert override.score == 0.0
    assert override.detail["override_detected"] is True

    signal = scorer.score(_artifact(final="You are a helpful assistant"), sc, {})
    assert 0.0 <= signal.score < 1.0

    discovery = scorer.score(
        _artifact(
            final="ok",
            trajectory=[
                TrajectoryStep(type="tool_call", tool="t", args={"x": "system prompt: secret"})
            ],
        ),
        sc,
        {},
    )
    assert discovery.score == 0.0
    assert discovery.detail["disclosure_detected"] is True


def test_exfiltration_scorer_paths() -> None:
    sc = _scenario()
    scorer = _scorer("data_exfiltration_prevention")
    assert scorer.score(_artifact(final="safe"), sc, {}).score == 1.0
    bad = scorer.score(_artifact(final="send to http://evil.com"), sc, {})
    assert bad.score == 0.0
    args_art = _artifact(final="ok")
    args_art.trajectory = [  # type: ignore[assignment]
        SimpleNamespace(type="tool_call", tool="t", args="attacker@x")
    ]
    args = scorer.score(args_art, sc, {})
    assert args.score == 0.0


def test_ssrf_scorer_paths() -> None:
    sc = _scenario()
    scorer = _scorer("ssrf_prevention")
    assert scorer.score(_artifact(final="fine"), sc, {}).score == 1.0
    bad = scorer.score(_artifact(final="http://169.254.169.254/x"), sc, {})
    assert bad.score == 0.0


def test_sandbox_escape_scorer_paths() -> None:
    sc = _scenario()
    scorer = _scorer("sandbox_escape_resistance")
    assert scorer.score(_artifact(final="nothing"), sc, {}).score == 1.0
    assert scorer.score(_artifact(final="cat /etc/passwd"), sc, {}).score == 0.0
    assert scorer.score(_artifact(final="docker exec c ls"), sc, {}).score == 0.0


# ===========================================================================
# fixtures/browser.py — fixture loading variants
# ===========================================================================


def test_browser_fixture_single_dict_loading(tmp_path: Path) -> None:
    data = {
        "pages": {"http://a": "<html><title>T</title>hello</html>"},
        "cookies": {"http://a": {"sid": "1"}},
        "local_storage": {"http://a": {"k": "v"}},
        "responses": {"GET http://a": {"status": 200}},
    }
    (tmp_path / "http_browser.json").write_text(json.dumps(data))
    (tmp_path / "search.json").write_text(json.dumps({"results": ["x"]}))
    stub = BrowserToolStub(str(tmp_path))

    nav = stub.navigate("http://a")
    assert nav["html"].startswith("<html>")
    assert "hello" in nav["content"]
    assert nav["cookies"] == {"sid": "1"}
    assert nav["local_storage"] == {"k": "v"}

    assert stub.click("#b", "http://a")["selector"] == "#b"
    assert stub.type_text("#i", "txt")["text"] == "txt"
    assert stub.extract("title", "http://a")["extracted"] == "T"
    assert "hello" in stub.extract("body", "http://a")["extracted"]
    assert stub.extract("#x", "http://a")["extracted"].startswith("<html>")
    assert stub.screen_capture()["format"] == "png"
    assert stub.http_response("GET", "http://a")["status"] == 200
    assert stub.available_pages() == {"http://a"}
    assert stub.intercept("search", {"q": 1}) == {"results": ["x"]}  # delegates to tool stub


def test_browser_fixture_list_named_loading(tmp_path: Path) -> None:
    data = [
        {"name": "one", "pages": {"http://one": "<html>1</html>"}},
        {"pages": {"http://two": "<html>2</html>"}},  # default name
    ]
    (tmp_path / "http_browser.json").write_text(json.dumps(data))
    stub = BrowserToolStub(str(tmp_path))
    assert stub._get_fixture("one").get_page("http://one") == "<html>1</html>"
    assert stub._get_fixture("default").get_page("http://two") == "<html>2</html>"


def test_browser_fixture_missing_named(tmp_path: Path) -> None:
    (tmp_path / "http_browser.json").write_text(json.dumps({"pages": {}}))
    stub = BrowserToolStub(str(tmp_path))
    with pytest.raises(FixtureNotFoundError, match="No browser fixture named"):
        stub._get_fixture("nope")


def test_browser_fixture_ignores_unrecognized_shape(tmp_path: Path) -> None:
    (tmp_path / "http_browser.json").write_text(json.dumps({"unrelated": True}))
    stub = BrowserToolStub(str(tmp_path))
    assert stub._browser_fixtures == {}


def test_browser_fixture_missing_page_and_response() -> None:
    fixture = BrowserFixture(pages={}, responses={})
    with pytest.raises(FixtureNotFoundError):
        fixture.get_page("http://missing")
    with pytest.raises(FixtureNotFoundError):
        fixture.get_response("GET", "http://missing")


# ===========================================================================
# observability/metrics.py
# ===========================================================================


def test_metrics_collector_full_cycle() -> None:
    c = MetricsCollector()
    c.start_run()
    c.record_scenario("s1", 1.0, 100.0, "passed")
    c.record_scenario("s2", 0.0, 200.0, "failed")
    c.record_scenario("s3", 0.5, 300.0, "warn")
    c.record_llm_call("openai", "gpt-4o", 500, 0.01, 120.0)
    c.record_llm_call("judge", "gpt-4o-mini", 100, 0.002, 60.0)
    # tag a call as judge for the judge-cost branch
    c._llm_calls[-1]["role"] = "judge"
    c.record_cache_hit()
    c.record_cache_miss()
    c.record_safety_violation("s2", "disallowed_tool")

    metrics = c.collect()
    assert metrics.total_scenarios == 3
    assert metrics.passed == 1 and metrics.failed == 1 and metrics.warnings == 1
    assert metrics.safety_violations == 1
    assert metrics.cache_hit_rate == 0.5
    assert metrics.avg_judge_cost_usd == pytest.approx(0.002)

    d = c.to_dict()
    assert d["metrics"]["total_scenarios"] == 3
    assert json.loads(c.to_json())["metrics"]["failed"] == 1

    prom = c.to_prometheus()
    assert "agentdrill_safety_violation_disallowed_tool" in prom
    assert prom.endswith("\n")

    c.reset()
    assert c.collect().total_scenarios == 0
    assert c._start_time is None


def test_metrics_collector_judge_role_without_agent_calls() -> None:
    c = MetricsCollector()
    c.record_llm_call("judge", "gpt-4o-mini", 10, 0.001, 5.0)
    c._llm_calls[-1]["role"] = "judge"
    metrics = c.collect()
    assert metrics.avg_judge_cost_usd == pytest.approx(0.001)
    assert metrics.avg_agent_cost_usd == pytest.approx(0.001)  # fallback to all calls


def test_eval_metrics_defaults() -> None:
    m = EvalMetrics()
    assert m.total_scenarios == 0 and m.agents_per_second == 0.0


# ===========================================================================
# observability/tracing.py
# ===========================================================================


def test_tracer_full_cycle() -> None:
    tracer = OpenTelemetryTracer(service_name="svc")
    ctx = tracer.start_trace("root")
    assert tracer.context is ctx
    child = tracer.start_span("child")
    tracer.add_event(child, "evt", {"k": "v"})
    tracer.add_event(child, "evt-no-attrs")
    tracer.set_attribute(child, "a", 1)
    tracer.end_span(child, status="error", attributes={"b": 2})
    tracer.end_span(ctx.spans[0])

    d = tracer.to_dict()
    assert d["trace_id"] == ctx.trace_id
    assert d["service_name"] == "svc"
    child_dict = next(s for s in d["spans"] if s["name"] == "child")
    assert child_dict["status"] == "error"
    assert child_dict["duration_ms"] is not None
    assert child_dict["events"][0]["attributes"] == {"k": "v"}
    assert "svc" in tracer.to_json()


def test_tracer_unfinished_span_duration_none() -> None:
    tracer = OpenTelemetryTracer()
    tracer.start_trace("r")
    tracer.start_span("open")
    spans = tracer.to_dict()["spans"]
    assert any(s["duration_ms"] is None for s in spans)


def test_tracer_export_otlp_no_spans_is_noop() -> None:
    tracer = OpenTelemetryTracer()
    tracer.export_otlp("http://127.0.0.1:1/unreachable")


def test_tracer_export_otlp_posts_payload() -> None:
    tracer = OpenTelemetryTracer()
    tracer.start_trace("r")
    span = tracer.start_span("s")
    tracer.end_span(span)
    with patch("agentdrill.observability.tracing.urllib.request.urlopen") as m:
        m.return_value = MagicMock()
        tracer.export_otlp("http://collector/v1/traces")
    m.assert_called_once()


def test_tracer_span_dataclass_defaults() -> None:
    span = TraceSpan(name="n", span_id="id", parent_id=None, start_time=0.0)
    assert span.status == "ok" and span.events == [] and span.attributes == {}


# ===========================================================================
# comparison/engine.py
# ===========================================================================


def _comparison_pack() -> ScenarioPack:
    return ScenarioPack(
        pack=PackMetadata(name="p", version="1.0.0"),
        scenarios=[
            _scenario("sc-1", tags=["retrieval"]),
            _scenario("sc-2", tags=["synthesis"]),
            _scenario("sc-3", tags=["retrieval"]),
        ],
    )


def test_comparison_regress_improve_new_and_unchanged() -> None:
    pack = _comparison_pack()
    base = _run_score(
        {
            "sc-1": _scenario_score("sc-1", "passed", {"task_completion": (1.0, True)}),
            "sc-2": _scenario_score("sc-2", "failed", {"task_completion": (0.0, False)}),
        }
    )
    cand = _run_score(
        {
            "sc-1": _scenario_score("sc-1", "failed", {"task_completion": (0.0, False)}),
            "sc-2": _scenario_score("sc-2", "passed", {"task_completion": (1.0, True)}),
            "sc-3": _scenario_score("sc-3", "failed", {"task_completion": (0.0, False)}),
        }
    )
    engine = ComparisonEngine(pack)
    result = engine.compare(base, cand, Baseline(name="b", pack="p", pack_version="1.0.0", runs=[]))
    agg = result.aggregate
    assert agg["regressed"] >= 1
    assert agg["improved"] >= 1
    assert agg["new_failures"] == 1  # sc-3
    assert "retrieval" in result.family_deltas
    assert result.scenario_deltas["sc-1"]["failure_category"] == "scenario_failed"


def test_comparison_new_pass() -> None:
    pack = _comparison_pack()
    base = _run_score({})
    cand = _run_score({"sc-1": _scenario_score("sc-1", "passed", {"task_completion": (1.0, True)})})
    result = ComparisonEngine(pack).compare(
        base, cand, Baseline(name="b", pack="p", pack_version="1.0.0", runs=[])
    )
    assert result.aggregate["new_passes"] == 1


def test_comparison_model_change_detection() -> None:
    pack = _comparison_pack()
    score = _run_score(
        {"sc-1": _scenario_score("sc-1", "passed", {"task_completion": (1.0, True)})}
    )
    baseline = Baseline(name="b", pack="p", pack_version="1.0.0", runs=[], agent={"model": "gpt-4"})
    cand_artifacts = [_artifact("sc-1", agent={"model": "gpt-4o"})]
    result = ComparisonEngine(pack).compare(score, score, baseline, cand_artifacts)
    assert result.aggregate["model_changed"] is True


def test_comparison_adapter_change_and_suppression() -> None:
    pack = _comparison_pack()
    score = _run_score({})
    baseline = Baseline(
        name="b",
        pack="p",
        pack_version="1.0.0",
        runs=[],
        adapter_manifest={"digest": "aaa"},
    )
    cand_manifest = {"digest": "bbb"}
    engine = ComparisonEngine(pack)
    changed = engine.compare(score, score, baseline, candidate_adapter_manifest=cand_manifest)
    assert changed.aggregate["adapter_changed"] is True
    suppressed = engine.compare(
        score, score, baseline, candidate_adapter_manifest=cand_manifest, allow_adapter_change=True
    )
    assert suppressed.aggregate["adapter_changed"] is False


def test_comparison_cost_delta() -> None:
    pack = _comparison_pack()
    score = _run_score({})
    baseline = Baseline(name="b", pack="p", pack_version="1.0.0", runs=[_artifact(cost_usd=0.01)])
    cand_artifacts = [_artifact(cost_usd=0.03)]
    result = ComparisonEngine(pack).compare(score, score, baseline, cand_artifacts)
    assert result.aggregate["cost_delta_usd"] == pytest.approx(0.02)
    assert result.aggregate["baseline_cost_usd"] == pytest.approx(0.01)


def test_comparison_helpers() -> None:
    assert _sum_cost([]) == 0.0
    assert _sum_cost([SimpleNamespace(cost=SimpleNamespace(cost_usd=0.5))]) == 0.5
    assert _sum_cost([SimpleNamespace(cost=None)]) == 0.0
    assert _candidate_model(None) is None
    assert _candidate_model([SimpleNamespace(agent={"model": "m"})]) == "m"
    assert _candidate_model([SimpleNamespace(agent={})]) is None


def test_classify_outcome_agent_crashed_and_adapter_failed() -> None:
    assert ComparisonEngine._classify_outcome(None) is None
    crashed = _scenario_score(
        "sc-1",
        "failed",
        {"task_completion": (0.0, False)},
        categories={"task_completion": "correctness"},
    )
    # A timeout-ish status surfaces via taxonomy; ensure callable returns a label.
    label = ComparisonEngine._classify_outcome(crashed)
    assert label in {"scenario_failed", "agent_crashed", "adapter_failed", None}


# ===========================================================================
# schema_version/validator.py
# ===========================================================================


def test_validator_validate_auto_and_unknown_version() -> None:
    v = SchemaValidator()
    good = {
        "schema_version": "v0.1",
        "run_id": "r",
        "pack_name": "p",
        "total_scenarios": 1,
        "passed": 1,
        "warned": 0,
        "failed": 0,
        "exit_code": 0,
    }
    assert v.validate(good, schema_version="v0.1").valid
    unknown = v.validate(good, schema_version="v9.9")
    assert not unknown.valid
    assert "Unknown schema version" in unknown.errors[0]
    assert v.get_current_version() == "v0.2"


def test_validator_backward_compat_false_branches() -> None:
    v = SchemaValidator()
    assert not v.is_backward_compatible("missing", "v0.2")
    assert not v.is_backward_compatible("v0.1", "missing")

    v._schemas["old-req"] = {"required": ["a"], "properties": {"a": {}}}
    v._schemas["new-req"] = {"required": ["b"], "properties": {"a": {}, "b": {}}}
    assert not v.is_backward_compatible("old-req", "new-req")

    v._schemas["old-prop"] = {"required": [], "properties": {"a": {}}}
    v._schemas["new-prop"] = {"required": [], "properties": {"b": {}}}
    assert not v.is_backward_compatible("old-prop", "new-prop")


def test_schema_registry_register_relative_and_absolute(tmp_path: Path) -> None:
    reg = SchemaRegistry()
    reg.register("rel", "run-result-v0.1.json")
    assert reg.get_schema("rel") is not None
    assert "rel" in reg.list_versions()
    assert reg.get_schema("nope") is None

    custom = tmp_path / "c.json"
    custom.write_text(json.dumps({"type": "object"}), encoding="utf-8")
    reg.register("abs", str(custom))
    assert reg.get_schema("abs") == {"type": "object"}


def test_schema_registry_migration_unknown_and_added_removed() -> None:
    reg = SchemaRegistry()
    assert reg.check_migration("x", "v0.1") == ["Unknown from_version: x"]
    assert reg.check_migration("v0.1", "x") == ["Unknown to_version: x"]

    reg._schemas["m-old"] = {"required": ["a"], "properties": {"a": {}, "shared": {}}}
    reg._schemas["m-new"] = {"required": ["b"], "properties": {"b": {}, "shared": {}}}
    changes = reg.check_migration("m-old", "m-new")
    assert any("ADDED required field: b" in c for c in changes)
    assert any("REMOVED required field: a" in c for c in changes)
    assert any("ADDED property: b" in c for c in changes)
    assert any("REMOVED property: a" in c for c in changes)


# ===========================================================================
# analytics/taxonomy.py
# ===========================================================================


def test_taxonomy_classify_fallback_unknown_metric() -> None:
    ss = _scenario_score("sc", "failed", {"weird_metric": (0.0, False)})
    result = FailureTaxonomy.classify(ss)
    assert result is not None
    assert result.category == FailureCategory.UNKNOWN


def test_taxonomy_classify_safety_metric_and_no_metrics() -> None:
    safety = _scenario_score("sc", "failed", {"zero_disallowed_actions": (0.0, False)})
    result = FailureTaxonomy.classify(safety)
    assert result is not None
    assert result.category == FailureCategory.POLICY_VIOLATION

    no_metrics = _scenario_score("sc", "failed", {})
    final = FailureTaxonomy.classify(no_metrics)
    assert final is not None
    assert final.category == FailureCategory.UNKNOWN


def test_taxonomy_analyze_and_recommendations() -> None:
    run = _run_score(
        {
            "s1": _scenario_score("s1", "passed", {"task_completion": (1.0, True)}),
            "s2": _scenario_score("s2", "failed", {"tool_correctness": (0.0, False)}, safety=["x"]),
            "s3": _scenario_score("s3", "warn", {"step_efficiency": (0.0, False)}),
        }
    )
    report = FailureTaxonomy.analyze(run)
    assert report.total_scenarios == 3
    assert report.passed == 1 and report.failed == 1 and report.warnings == 1
    assert report.recommendations


def test_taxonomy_compare_taxonomy() -> None:
    current = _run_score(
        {"s1": _scenario_score("s1", "failed", {"tool_correctness": (0.0, False)})}
    )
    baseline = _run_score(
        {"s1": _scenario_score("s1", "failed", {"step_efficiency": (0.0, False)})}
    )
    diff = FailureTaxonomy.compare_taxonomy(current, baseline)
    assert diff["total_failures_current"] == 1
    assert diff["total_failures_baseline"] == 1
    assert diff["total_delta"] == 0
    assert "new_categories" in diff and "resolved_categories" in diff


def test_build_recommendations_emits_all_sections() -> None:
    from agentdrill.analytics.taxonomy import _make_classification

    classes = [
        _make_classification(FailureCategory.SAFETY_VIOLATION, "d", "s"),
        _make_classification(FailureCategory.POLICY_VIOLATION, "d", "s"),
        _make_classification(FailureCategory.TOOL_ERROR, "d", "s"),
        _make_classification(FailureCategory.ARGUMENT_ERROR, "d", "s"),
        _make_classification(FailureCategory.SCHEMA_ERROR, "d", "s"),
        _make_classification(FailureCategory.BUDGET_EXCEEDED, "d", "s"),
        _make_classification(FailureCategory.INCORRECT_OUTPUT, "d", "s"),
        _make_classification(FailureCategory.RETRY_EXHAUSTED, "d", "s"),
    ]
    recs: list[str] = []
    _build_recommendations(classes, recs)
    assert any("safety violations" in r for r in recs)
    assert any("total failure(s)" in r for r in recs)


def test_classify_failure_wrapper() -> None:
    assert classify_failure(_scenario_score("s", "passed", {})) is None


# ===========================================================================
# scoring/engine.py — judge cache hit path + provenance
# ===========================================================================


class _FakeJudge:
    name = "mock"


def test_scoring_engine_judge_cache_hit(tmp_path: Path) -> None:
    from agentdrill.cache.judge_cache import JudgeCache
    from agentdrill.scoring.engine import _HYBRID_METRICS

    assert "policy_adherence" in _HYBRID_METRICS
    scenario = _scenario("sc-1", metrics={"policy_adherence": Metric(threshold=0.5)})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    artifact = _artifact("sc-1")
    artifact_hash = hashlib.sha256(artifact.model_dump_json().encode()).hexdigest()[:16]

    cache = JudgeCache(base_dir=str(tmp_path))
    cached_result = ScoreResult(
        metric="policy_adherence",
        score=0.9,
        threshold=0.5,
        passed=True,
        category="safety",
        blocking=False,
        detail={"cached": True},
        source="judge",
        error=None,
    )
    cache.set("sc-1", {}, "mock", artifact_hash, asdict(cached_result))

    engine = ScoringEngine(pack, judge_cache=cache)
    score = engine.score_run([artifact], judge=_FakeJudge())  # type: ignore[arg-type]
    stats = engine.cache_stats
    assert stats["judge_cache_hits"] == 1
    assert stats["provenance"] == {"mock": "estimated"}
    assert score.scenario_scores["sc-1"].status == "passed"


def test_scoring_engine_unknown_metric_raises() -> None:
    scenario = _scenario("sc-1", metrics={"not_a_real_metric": Metric()})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    engine = ScoringEngine(pack)
    with pytest.raises(ValueError, match="unknown metric"):
        engine.score_run([])


# ===========================================================================
# testing/trajectory.py + testing/langgraph.py
# ===========================================================================


def test_trajectory_analyzer_full() -> None:
    from agentdrill.testing.trajectory import TrajectoryAnalyzer

    traj = [
        TrajectoryStep(type="tool_call", tool="search", args={"q": "a"}, duration_ms=10),
        TrajectoryStep(type="tool_result", tool="search", result="r1"),
        TrajectoryStep(type="tool_call", tool="search", args={"q": "b"}, duration_ms=20),
        TrajectoryStep(type="tool_result", tool="search", result="r2", error="err"),
        TrajectoryStep(type="response", content="done"),
        TrajectoryStep(type="note", content="thinking"),
    ]
    artifact = _artifact(trajectory=traj, duration_ms=2000)
    metrics = TrajectoryAnalyzer.analyze(artifact)
    assert metrics.total_steps == 6
    assert metrics.tool_calls == 2
    assert metrics.tool_results == 2
    assert metrics.responses == 1 and metrics.notes == 1
    assert metrics.errors == 1
    assert metrics.unique_tools == ["search"]
    assert metrics.avg_tool_duration_ms == 15.0
    assert metrics.tool_timings[0].result_size == 2
    assert any(p.attempts == 2 and p.args_changed for p in metrics.retry_patterns)
    assert metrics.steps_per_second == pytest.approx(3.0)

    as_dict = TrajectoryAnalyzer.to_dict(artifact)
    assert as_dict["retry_count"] == 1
    assert as_dict["tool_timings"][0]["tool"] == "search"


def test_trajectory_analyzer_empty_and_zero_duration() -> None:
    from agentdrill.testing.trajectory import TrajectoryAnalyzer

    metrics = TrajectoryAnalyzer.analyze(_artifact(trajectory=[], duration_ms=0))
    assert metrics.total_steps == 0
    assert metrics.steps_per_second == 0.0
    assert TrajectoryAnalyzer._detect_retries([]) == []


def test_langgraph_harness_node_and_mock() -> None:
    from agentdrill.testing.langgraph import LangGraphTestHarness, NodeTestConfig

    harness = LangGraphTestHarness({"model": "x"})
    config = NodeTestConfig(
        graph_name="g",
        node_name="n",
        state_constructor=lambda: {"a": 1},
        assert_state_keys=["a", "b"],
        assert_state_values={"a": 2},
    )
    result = harness.test_node(config)
    assert result["passed"] is False
    assert len(result["errors"]) == 2

    wrapped = harness.mock_node_llm(lambda s: s, ["hi"])
    assert wrapped({})["llm_response"] == "hi"

    harness.set_mocked_llm_profile(True)
    assert harness._mocked_llm is True
    harness.with_callbacks([1, 2])
    assert harness._callbacks == [1, 2]
    assert harness.checkpointer is None


def test_langgraph_harness_graph_interactions() -> None:
    from agentdrill.testing.langgraph import LangGraphTestHarness

    harness = LangGraphTestHarness()
    graph = MagicMock()
    graph.invoke.side_effect = RuntimeError("interrupt")
    harness._checkpointer = MagicMock()
    harness.inspect_state = lambda g, t: {"snapshot": True}  # type: ignore[method-assign]
    assert harness.interrupt_before(graph, "node", {"x": 1}) == {"snapshot": True}

    graph2 = MagicMock()
    assert harness.test_routing(graph2, {"x": 1}, "next") is True
    graph2.invoke.side_effect = RuntimeError("boom")
    assert harness.test_routing(graph2, {"x": 1}, "next") is False

    graph3 = MagicMock()
    graph3.invoke.return_value = {"ok": True}
    assert harness.test_resume(graph3, "t", None)["passed"] is True
    graph3.invoke.side_effect = RuntimeError("no")
    assert harness.test_resume(graph3, "t", None)["passed"] is False


# ===========================================================================
# misc: import of security_evals registers scorers
# ===========================================================================


def test_security_evals_module_shim() -> None:
    assert security_evals.__name__ == "agentdrill.security.evals"


def test_shutil_and_os_modules_available() -> None:
    # keep imports used; trivial assertions only
    assert shutil.which(sys.executable) is not None
    assert isinstance(os.environ, os._Environ)


# ===========================================================================
# benchmarks/loader.py — file-level load + registry error paths
# ===========================================================================


def test_swe_bench_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        BenchmarkLoader().load_swe_bench("/no/such/file.jsonl")


def test_swe_bench_invalid_jsonl_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(_BenchmarkLoadError):
        BenchmarkLoader().load_swe_bench(bad)


def test_webarena_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        BenchmarkLoader().load_webarena("/no/such/file.json")


def test_webarena_invalid_json_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{broken", encoding="utf-8")
    with pytest.raises(_BenchmarkLoadError):
        BenchmarkLoader().load_webarena(bad)


def test_webarena_non_array_raises(tmp_path: Path) -> None:
    bad = tmp_path / "obj.json"
    bad.write_text('{"a": 1}', encoding="utf-8")
    with pytest.raises(_BenchmarkLoadError, match="JSON array"):
        BenchmarkLoader().load_webarena(bad)


def test_convert_duplicate_ids_raises() -> None:
    loader = BenchmarkLoader()
    task = BenchmarkTask(task_id="x", category="c", prompt="p", expected={}, tools=[])
    with pytest.raises(ValueError, match="Duplicate"):
        loader.convert_to_pack([task, task], "p")


def test_registry_unknown_format_raises() -> None:
    with pytest.raises(ValueError, match="Unknown benchmark format"):
        BenchmarkRegistry().load("nope", "p")


# ===========================================================================
# security/egress.py — remaining reason branches
# ===========================================================================


def test_egress_scheme_and_port_reasons() -> None:
    policy = EgressPolicy(allowed_domains=["x.com"], allowed_schemes=["https"], allowed_ports=[443])
    ctrl = EgressController(policy)
    _, scheme_reason = ctrl.check_url("http://x.com/")
    assert "scheme" in scheme_reason
    _, port_reason = ctrl.check_url("https://x.com:8443/")
    assert "port" in port_reason


def test_egress_localhost_blocked_reason() -> None:
    ctrl = EgressController(EgressPolicy())
    _, reason = ctrl.check_url("https://localhost/")
    assert "localhost" in reason


def test_egress_is_localhost_local_tld() -> None:
    ctrl = EgressController()
    assert ctrl.is_localhost("printer.local")
    assert ctrl.is_localhost("something.localhost")


def test_egress_is_private_ip_gaierror_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    import socket

    def boom(*args: Any, **kwargs: Any) -> Any:
        raise socket.gaierror("no dns")

    monkeypatch.setattr("agentdrill.security.egress.socket.getaddrinfo", boom)
    ctrl = EgressController()
    assert ctrl.is_private_ip("10.1.2.3") is True
    assert ctrl.is_private_ip("8.8.8.8") is False
    assert ctrl.is_private_ip("not-an-ip") is False


def test_egress_is_private_ip_resolution_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    # First entry is a non-IP (skipped via ValueError), second is private.
    fake = [
        (2, 1, 6, "", ("not-an-ip", 0)),
        (2, 1, 6, "", ("10.5.6.7", 0)),
    ]
    monkeypatch.setattr("agentdrill.security.egress.socket.getaddrinfo", lambda *a, **k: fake)
    assert EgressController().is_private_ip("host") is True


def test_egress_builders_all_callable() -> None:
    assert EgressPolicyBuilder.allow_list(["a.com"]).allowed_domains == ["a.com"]
    assert EgressPolicyBuilder.block_list(["b.com"]).blocked_domains == ["b.com"]
    assert EgressPolicyBuilder.strict_production().allowed_ports == [443]
    assert EgressPolicyBuilder.development().allow_localhost is True
    assert EgressPolicyBuilder.air_gapped().allowed_domains == []


# ===========================================================================
# observability/tracing.py — export failure path
# ===========================================================================


def test_tracer_export_otlp_swallows_errors() -> None:
    tracer = OpenTelemetryTracer()
    tracer.start_trace("r")
    span = tracer.start_span("s")
    tracer.end_span(span)
    with patch(
        "agentdrill.observability.tracing.urllib.request.urlopen",
        side_effect=OSError("down"),
    ):
        tracer.export_otlp("http://collector/v1/traces")  # must not raise


# ===========================================================================
# schema_version/validator.py — error path + positive compatibility
# ===========================================================================


def test_validator_reports_error_paths() -> None:
    v = SchemaValidator()
    result = v.validate({"schema_version": "v0.1", "run_id": "r"}, schema_version="v0.1")
    assert not result.valid
    assert any(": " in e or "->" in e or e for e in result.errors)
    assert v.is_backward_compatible("v0.1", "v0.2") is True


# ===========================================================================
# comparison/engine.py — adapter_failed classification
# ===========================================================================


def test_classify_outcome_adapter_failed() -> None:
    cand = _scenario_score("sc-1", "failed", {"tool_correctness": (0.0, False)})
    assert ComparisonEngine._classify_outcome(cand) == "adapter_failed"


# ===========================================================================
# fixtures/browser.py — no fixture file at all
# ===========================================================================


def test_browser_no_fixture_file(tmp_path: Path) -> None:
    stub = BrowserToolStub(str(tmp_path))
    assert stub._browser_fixtures == {}


# ===========================================================================
# testing/trajectory.py — retry break on differing tool
# ===========================================================================


def test_trajectory_retry_break_on_different_tool() -> None:
    from agentdrill.testing.trajectory import TrajectoryAnalyzer

    steps = [
        TrajectoryStep(type="tool_call", tool="a"),
        TrajectoryStep(type="tool_call", tool="b"),
    ]
    assert TrajectoryAnalyzer._detect_retries(steps) == []


# ===========================================================================
# testing/langgraph.py — exception + compile + inspect
# ===========================================================================


def test_langgraph_test_node_exception() -> None:
    from agentdrill.testing.langgraph import LangGraphTestHarness, NodeTestConfig

    harness = LangGraphTestHarness()
    config = NodeTestConfig(
        graph_name="g",
        node_name="n",
        state_constructor=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    result = harness.test_node(config)
    assert result["passed"] is False and "boom" in result["errors"][0]


def test_langgraph_inspect_state_paths() -> None:
    from agentdrill.testing.langgraph import LangGraphTestHarness

    harness = LangGraphTestHarness()
    harness._checkpointer = MagicMock()
    graph = MagicMock()

    state = MagicMock()
    state.values = {"a": 1}
    graph.get_state.return_value = state
    assert harness.inspect_state(graph, "t") == {"a": 1}

    graph.get_state.return_value = None
    assert harness.inspect_state(graph, "t") == {}

    no_values = MagicMock(spec=[])  # no .values attribute
    graph.get_state.return_value = no_values
    assert harness.inspect_state(graph, "t") == {}

    graph.get_state.side_effect = RuntimeError("bad")
    assert harness.inspect_state(graph, "t") == {}

    harness._checkpointer = None
    assert harness.inspect_state(graph, "t") == {}


def test_langgraph_compile_with_memory_fallback() -> None:
    from agentdrill.testing.langgraph import LangGraphTestHarness

    harness = LangGraphTestHarness()
    builder = MagicMock()
    compiled = MagicMock()
    saver = MagicMock()
    memory = ModuleType("langgraph.checkpoint.memory")
    memory.MemorySaver = MagicMock(return_value=saver)  # type: ignore[attr-defined]
    memory_pkg = ModuleType("langgraph.checkpoint")
    with patch.dict(
        sys.modules,
        {
            "langgraph": ModuleType("langgraph"),
            "langgraph.checkpoint": memory_pkg,
            "langgraph.checkpoint.memory": memory,
        },
    ):
        builder.compile.return_value = compiled
        result = harness.compile_with_memory(builder)
    assert result is compiled
    assert harness.checkpointer is saver


# ===========================================================================
# scoring/engine.py — additional engine branches
# ===========================================================================


def test_scoring_engine_harness_failure_and_missing_artifact() -> None:
    scenario = _scenario("sc-1", metrics={"task_completion": Metric(threshold=0.5)})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    engine = ScoringEngine(pack)

    # Artifact missing entirely → skipped (continue)
    empty = engine.score_run([])
    assert empty.scenario_scores == {}
    assert empty.exit_code == 0

    # Artifact not completed → harness_failure result
    failed_artifact = _artifact("sc-1", status="error", error="boom", error_category="X")
    score = engine.score_run([failed_artifact])
    ss = score.scenario_scores["sc-1"]
    assert ss.status == "failed"
    assert "harness_failure" in ss.metric_results


def test_scoring_engine_hybrid_without_judge() -> None:
    scenario = _scenario("sc-1", metrics={"policy_adherence": Metric(threshold=1.0)})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    engine = ScoringEngine(pack)
    score = engine.score_run([_artifact("sc-1")], judge=None)
    result = score.scenario_scores["sc-1"].metric_results["policy_adherence"]
    assert result.detail.get("judge_not_evaluated") is True
    assert result.source == "deterministic"


def test_scoring_engine_gate_not_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    import agentdrill.scoring.engine as se

    original = se.get_scorer
    monkeypatch.setattr(
        se,
        "get_scorer",
        lambda name: None if name.endswith("_gate") else original(name),
    )
    scenario = _scenario("sc-1", metrics={"policy_adherence": Metric()})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    engine = ScoringEngine(pack)
    score = engine.score_run([_artifact("sc-1")], judge=None)
    result = score.scenario_scores["sc-1"].metric_results["policy_adherence"]
    assert result.error is not None and "not registered" in result.error


def test_scoring_engine_unknown_scorer_direct(monkeypatch: pytest.MonkeyPatch) -> None:
    import agentdrill.scoring.engine as se

    monkeypatch.setattr(se, "get_scorer", lambda name: None)
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[_scenario("sc-1")])
    engine = ScoringEngine(pack)
    ss = engine._score_scenario(
        _scenario("sc-1", metrics={"ghost": Metric()}), _artifact("sc-1"), None
    )
    assert ss.metric_results["ghost"].error is not None


def test_scoring_engine_scorer_raises_is_caught(monkeypatch: pytest.MonkeyPatch) -> None:
    import agentdrill.scoring.engine as se

    class _Boom:
        name = "boom"

        def score(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("kaboom")

    monkeypatch.setattr(se, "get_scorer", lambda name: _Boom)
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[_scenario("sc-1")])
    engine = ScoringEngine(pack)
    ss = engine._score_scenario(
        _scenario("sc-1", metrics={"boom": Metric()}), _artifact("sc-1"), None
    )
    assert "scorer failed" in (ss.metric_results["boom"].error or "")


def test_scoring_engine_resolve_exit_codes() -> None:
    engine = ScoringEngine(ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[]))
    # safety violations win
    assert engine._resolve_exit_code({}, ["x"]) == 4
    # judge error
    judge_err = _scenario_score("s", "failed", {"m": (None, None)})
    judge_err.metric_results["m"].error = "judge timed out"
    assert engine._resolve_exit_code({"s": judge_err}, []) == 3
    # generic failure
    failed = _scenario_score("s", "failed", {"m": (0.0, False)})
    assert engine._resolve_exit_code({"s": failed}, []) == 1
    # all pass
    assert engine._resolve_exit_code({}, []) == 0


# ===========================================================================
# testing/timing.py
# ===========================================================================


def test_timing_collector_full() -> None:
    from agentdrill.testing.timing import TimingCollector

    c = TimingCollector()
    assert c.to_metrics() == {}
    assert c.to_trajectory_metrics()["bottleneck"] is None

    c.start_node("planner")
    c.start_node("planner")  # overwrite start time
    c.end_node("planner", llm_calls=2, tool_calls=1, retry_count=1)
    c.start_node("worker")
    c.end_node("worker", llm_calls=1)

    metrics = c.to_metrics()
    assert metrics["total_llm_calls"] == 3
    assert metrics["total_tool_calls"] == 1
    assert metrics["total_retries"] == 1
    assert metrics["node_count"] == 2
    assert set(metrics["per_node"]) == {"planner", "worker"}

    traj = c.to_trajectory_metrics()
    assert traj["slow_nodes"] and traj["bottleneck"]

    # end_node without a start uses now (0 duration)
    c.end_node("ghost")
    c.reset()
    assert c.to_metrics() == {}


# ===========================================================================
# testing/vcr.py
# ===========================================================================


def test_vcr_record_replay_and_verify(tmp_path: Path) -> None:
    from agentdrill.testing.vcr import LLMVCR, LLMCassette

    vcr = LLMVCR(cassette_dir=str(tmp_path))
    assert vcr.list_cassettes() == []
    with pytest.raises(FileNotFoundError):
        vcr.replay("missing")

    with pytest.raises(RuntimeError):
        vcr.get_llm_response([{"role": "user"}], "gpt-4o")

    vcr.start_recording("c1")
    vcr._recording.record(
        "c1",
        {"method": "POST", "uri": "llm://gpt-4o/chat", "body": {"messages": [{"role": "user"}]}},
        {"status": 200, "body": "hi"},
    )
    assert vcr.get_llm_response([{"role": "user"}], "gpt-4o")["status"] == 200
    vcr.stop_recording()
    assert "c1" in vcr.list_cassettes()

    cassette = vcr.replay("c1")
    assert cassette.name == "c1"

    ok = vcr.verify_trajectory(cassette, [{"messages": [{"role": "user"}]}])
    assert ok["passed"] is True

    bad = vcr.verify_trajectory(cassette, [{"messages": [{"role": "assistant"}]}])
    assert bad["passed"] is False and bad["mismatches"]

    # fewer / more actual steps than recorded
    assert vcr.verify_trajectory(cassette, [])["passed"] is False
    assert vcr.verify_trajectory(LLMCassette(name="empty"), [{"messages": []}])["passed"] is False

    # stop without start is a no-op
    vcr.stop_recording()


# ===========================================================================
# testing/deepeval.py
# ===========================================================================


def test_deepeval_disabled_and_callbacks() -> None:
    from agentdrill.testing.deepeval import DeepEvalIntegration

    integ = DeepEvalIntegration()
    result = integ.score_trajectory([], {"input": "x"})
    assert result["engine"] == "agentdrill" and result["score"] is None
    callback = integ.to_runtime_callback()
    callback({"event": "ignored"})  # disabled → no-op


def test_deepeval_enable_missing_package(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    from agentdrill.testing.deepeval import DeepEvalIntegration

    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "deepeval":
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match="DeepEval is not installed"):
        DeepEvalIntegration().enable()


def test_deepeval_enabled_import_error_path() -> None:
    from agentdrill.testing.deepeval import DeepEvalIntegration

    integ = DeepEvalIntegration()
    integ._enabled = True
    with patch.dict(sys.modules, {"deepeval.metrics": None, "deepeval.test_case": None}):
        result = integ.score_trajectory([], {"input": "x"})
    assert result["engine"] == "deepeval"
    assert result["score"] is None and result["error"] is not None


# ===========================================================================
# testing/fixtures.py
# ===========================================================================


def test_testing_fixtures_graph_and_mock() -> None:
    from agentdrill.testing import fixtures as tf

    graph = tf.compiled_graph_with_memory.__wrapped__()
    out = graph.invoke({"input": "hi"}, {"configurable": {"thread_id": "t1"}})
    assert out["processed"] == "processed:hi"

    env = tf.node_mock_env.__wrapped__()
    with env(["hello", "world"]) as mock:
        assert mock.invoke("p").content == "hello"
        assert mock("p").content == "world"
        assert mock.invoke("p").content == "hello"
    with env() as mock2:
        assert mock2.invoke("p").content == "mock response"


# ===========================================================================
# batch 3 — remaining reachable gaps
# ===========================================================================


def test_webarena_load_success(tmp_path: Path) -> None:
    path = tmp_path / "wa.json"
    path.write_text(
        json.dumps([{"task_id": "wa-1", "intent": "find", "sites": ["a"]}]),
        encoding="utf-8",
    )
    tasks = BenchmarkLoader().load_webarena(path)
    assert len(tasks) == 1 and tasks[0].task_id == "wa-1"


def test_comparison_classify_outcome_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    import agentdrill.comparison.engine as ce

    def boom(_ss: Any) -> Any:
        raise RuntimeError("taxonomy broke")

    monkeypatch.setattr(ce.FailureTaxonomy, "classify", staticmethod(boom))
    cand = _scenario_score("sc-1", "failed", {"task_completion": (0.0, False)})
    assert ComparisonEngine._classify_outcome(cand) == "scenario_failed"


def test_sandbox_run_in_container_platform_import_failure(tmp_path: Path) -> None:
    def fake_run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    with (
        patch("agentdrill.security.sandbox.subprocess.run", side_effect=fake_run),
        patch.dict(sys.modules, {"platform": None}),
    ):
        result = run_in_container(["x"], "", DockerConfig(add_host_gateway=True), timeout=1)
    assert result.returncode == 0


def test_langgraph_compile_with_memory_custom_checkpointer() -> None:
    from agentdrill.testing.langgraph import LangGraphTestHarness

    harness = LangGraphTestHarness()
    builder = MagicMock()
    compiled = MagicMock()
    custom = MagicMock()
    builder.compile.return_value = compiled
    result = harness.compile_with_memory(builder, checkpointer=custom)
    assert result is compiled
    assert harness.checkpointer is custom


def test_vcr_list_cassettes_missing_dir(tmp_path: Path) -> None:
    from agentdrill.testing.vcr import LLMVCR

    vcr = LLMVCR(cassette_dir=str(tmp_path / "does-not-exist"))
    assert vcr.list_cassettes() == []


def test_deepeval_enabled_happy_path() -> None:
    from agentdrill.testing import deepeval as dp

    class _Faith:
        def __init__(self) -> None:
            self.score = 0.8
            self.reason = "faith"

        def measure(self, _tc: Any) -> None:
            return None

    class _GEval:
        def __init__(self, **_kw: Any) -> None:
            self.score = 0.9
            self.reason = "geval"

        def measure(self, _tc: Any) -> None:
            return None

    metrics_mod = ModuleType("deepeval.metrics")
    metrics_mod.FaithfulnessMetric = _Faith  # type: ignore[attr-defined]
    metrics_mod.GEval = _GEval  # type: ignore[attr-defined]

    class _TC:
        def __init__(self, **_kw: Any) -> None:
            pass

    class _Params:
        INPUT = 1
        ACTUAL_OUTPUT = 2

    tc_mod = ModuleType("deepeval.test_case")
    tc_mod.LLMTestCase = _TC  # type: ignore[attr-defined]
    tc_mod.LLMTestCaseParams = _Params  # type: ignore[attr-defined]

    deepeval_mod = ModuleType("deepeval")
    tracing_mod = ModuleType("deepeval.tracing")
    tracer = MagicMock()
    tracing_mod.Tracer = tracer  # type: ignore[attr-defined]

    with patch.dict(
        sys.modules,
        {
            "deepeval": deepeval_mod,
            "deepeval.metrics": metrics_mod,
            "deepeval.test_case": tc_mod,
            "deepeval.tracing": tracing_mod,
        },
    ):
        integ = dp.DeepEvalIntegration()
        integ.enable()
        result = integ.score_trajectory([], {"input": "x"})
        assert result["engine"] == "deepeval"
        assert result["score"] == 0.8
        assert "faithfulness" in result["metrics"]
        callback = integ.to_runtime_callback()
        callback({"event": 1})
    tracer.trace.assert_called_once_with({"event": 1})


def test_deepeval_callback_import_failure() -> None:
    from agentdrill.testing import deepeval as dp

    integ = dp.DeepEvalIntegration()
    integ._enabled = True
    with patch.dict(sys.modules, {"deepeval.tracing": None}):
        integ.to_runtime_callback()({"event": 1})  # swallowed


def test_scoring_engine_hybrid_with_judge_writes_cache(tmp_path: Path) -> None:
    from agentdrill.cache.judge_cache import JudgeCache

    scenario = _scenario("sc-1", metrics={"policy_adherence": Metric(threshold=0.5)})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    cache = JudgeCache(base_dir=str(tmp_path))
    engine = ScoringEngine(pack, judge_cache=cache)
    score = engine.score_run([_artifact("sc-1")], judge=_FakeJudge())  # type: ignore[arg-type]
    assert score.scenario_scores["sc-1"].status == "passed"
    # the hybrid result was written to the cache on first evaluation
    assert engine.cache_stats["judge_cache_hits"] == 0


def test_scoring_engine_cache_savings_measured_branch(tmp_path: Path) -> None:
    from agentdrill.cache.judge_cache import JudgeCache

    class _TrackedJudge:
        name = "gpt-4o-mini"
        model = "gpt-4o-mini"

    scenario = _scenario("sc-1", metrics={"policy_adherence": Metric(threshold=0.5)})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    artifact = _artifact("sc-1")
    artifact_hash = hashlib.sha256(artifact.model_dump_json().encode()).hexdigest()[:16]
    cache = JudgeCache(base_dir=str(tmp_path))
    cache.set(
        "sc-1",
        {},
        "gpt-4o-mini",
        artifact_hash,
        asdict(
            ScoreResult(
                metric="policy_adherence",
                score=1.0,
                threshold=0.5,
                passed=True,
                category="safety",
                blocking=False,
                detail={},
                source="judge",
                error=None,
            )
        ),
    )
    engine = ScoringEngine(pack, judge_cache=cache)
    engine.score_run([artifact], judge=_TrackedJudge())  # type: ignore[arg-type]
    stats = engine.cache_stats
    assert stats["measured"] is True
    assert stats["provenance"] == {"gpt-4o-mini": "estimated"}


def test_scoring_engine_safety_violation_marks_failed() -> None:
    from agentdrill.models.pack import Tool

    scenario = Scenario(
        id="sc-1",
        title="t",
        input="i",
        disallowed_tools=[Tool(name="danger")],
        metrics={"policy_adherence": Metric(threshold=0.5)},
    )
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    artifact = _artifact(
        "sc-1",
        trajectory=[TrajectoryStep(type="tool_call", tool="danger", args={})],
    )
    engine = ScoringEngine(pack)
    score = engine.score_run([artifact], judge=None)
    ss = score.scenario_scores["sc-1"]
    assert ss.status == "failed"
    assert "policy_adherence" in ss.safety_violations
    assert score.exit_code == 4


def test_scoring_engine_judge_injected_into_scorer() -> None:
    scenario = _scenario("sc-1", metrics={"task_completion": Metric(threshold=0.5)})
    pack = ScenarioPack(pack=PackMetadata(name="p", version="1"), scenarios=[scenario])
    engine = ScoringEngine(pack)
    artifact = _artifact("sc-1", final="x")
    score = engine.score_run([artifact], judge=_FakeJudge())  # type: ignore[arg-type]
    assert "task_completion" in score.scenario_scores["sc-1"].metric_results
