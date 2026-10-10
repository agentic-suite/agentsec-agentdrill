"""Targeted coverage tests for M0 core/scoring modules.

This module exercises the core entry point and a handful of foundational
modules (plugins, judge clients/scorers, pack loading, provenance, scenario
registry, determinism, baselines, classification, grounding) to raise line
coverage. Every test is deterministic and fully offline — external HTTP is
mocked and no real model/server is ever contacted.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _artifact(
    output: str = "ok",
    trajectory: list | None = None,
):
    from agentdrill.models.artifact import Cost, RunArtifact, RunOutput, RunTimestamps

    return RunArtifact(
        id="r1",
        scenario_id="sc-1",
        timestamp=RunTimestamps(start="x", end="y", duration_ms=0),
        output=RunOutput(final=output, structured=None),
        trajectory=trajectory or [],
        cost=Cost(),
        status="completed",
        error=None,
        agent={},
    )


def _scenario(
    goal: str | None = "Do the thing",
    input_text: str = "in",
    expected=None,
    allowed_tools: list | None = None,
):
    from agentdrill.models.pack import Budget, Scenario, Tool

    return Scenario(
        id="sc-1",
        title="T",
        goal=goal,
        input=input_text,
        allowed_tools=[Tool(name=t) for t in (allowed_tools or [])],
        budget=Budget(max_steps=5),
        expected=expected,
    )


# ===========================================================================
# agentdrill/__init__.py — evaluate() entry point and _resolve_judge
# ===========================================================================


class TestEvaluateEntryPoint:
    def test_evaluate_basic_offline(self, tmp_path: Path) -> None:
        import agentdrill

        score = agentdrill.evaluate(
            pack=FIXTURES / "valid_pack.yaml",
            agent="python:fixtures.agents",
            output_dir=str(tmp_path),
        )
        assert set(score.scenario_scores) == {"sc-1", "sc-2"}

    def test_evaluate_with_mock_judge_and_string_tags(self, tmp_path: Path) -> None:
        import agentdrill

        score = agentdrill.evaluate(
            pack=FIXTURES / "valid_pack.yaml",
            agent="python:fixtures.agents",
            judge="mock",
            model="whatever",
            tags="tag-a",
            workers=1,
            timeout=30,
            output_dir=str(tmp_path / "judged"),
        )
        assert "sc-1" in score.scenario_scores

    def test_evaluate_with_baseline(self, tmp_path: Path) -> None:
        import agentdrill
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore
        from agentdrill.runner import Runner

        out = tmp_path / "baseline-run"
        runner = Runner(
            agent_config={
                "type": "python",
                "module": "fixtures.agents",
                "timeout_seconds": 30,
            },
            output_dir=str(out),
        )
        runner.load_pack(FIXTURES / "valid_pack.yaml")
        artifacts = runner.run_all()

        store = BaselineStore(base_dir=f"{tmp_path}/baselines")
        store.save(
            Baseline(
                name="base",
                pack="test-pack",
                pack_version="1.0.0",
                runs=artifacts,
            )
        )

        score = agentdrill.evaluate(
            pack=FIXTURES / "valid_pack.yaml",
            agent="python:fixtures.agents",
            baseline="base",
            output_dir=str(tmp_path),
        )
        assert "sc-1" in score.scenario_scores

    def test_resolve_judge_openai(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill import _resolve_judge

        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        client = _resolve_judge("openai", "gpt-4o")
        assert client.name == "openai"
        assert client.model == "gpt-4o"

    def test_resolve_judge_anthropic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill import _resolve_judge

        monkeypatch.setenv("ANTHROPIC_API_KEY", "ak-test")
        client = _resolve_judge("anthropic")
        assert client.name == "anthropic"

    def test_resolve_judge_ollama(self) -> None:
        from agentdrill import _resolve_judge

        client = _resolve_judge("ollama", "llama3")
        assert client.name == "ollama"

    def test_resolve_judge_mlx(self) -> None:
        from agentdrill import _resolve_judge

        client = _resolve_judge("mlx")
        assert client.name == "mlx"

    def test_resolve_judge_mock(self) -> None:
        from agentdrill import _resolve_judge

        client = _resolve_judge("mock")
        assert client.name == "mock"

    def test_resolve_judge_unknown_raises(self) -> None:
        from agentdrill import _resolve_judge

        with pytest.raises(ValueError, match="unknown judge provider"):
            _resolve_judge("does-not-exist")


# ===========================================================================
# plugins/manager.py
# ===========================================================================


class _FakeDist:
    def __init__(self, version: str, author: str = "") -> None:
        self.version = version
        self.metadata = {"Author": author}


class _FakeEP:
    def __init__(self, name: str, value: str, dist: object = None) -> None:
        self.name = name
        self.value = value
        self.dist = dist

    def load(self):
        return SimpleNamespace(loaded_name=self.name)


class TestPluginManagerCoverage:
    def test_discover_entry_points_handles_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.plugins import manager

        monkeypatch.setattr(
            manager, "entry_points", lambda **kw: (_ for _ in ()).throw(RuntimeError("boom"))
        )
        mgr = manager.PluginManager()
        mgr.discover_entry_points()
        assert mgr.list_plugins() == []

    def test_discover_entry_points_registers_metadata(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.plugins import manager

        eps = [
            _FakeEP("ep_with_dist", "m:Cls", _FakeDist("1.2.3", "Tester")),
            _FakeEP("ep_no_dist", "m:Cls2", None),
        ]
        monkeypatch.setattr(manager, "entry_points", lambda **kw: list(eps))
        mgr = manager.PluginManager()
        mgr.discover_entry_points()

        with_dist = mgr.get_plugin("ep_with_dist")
        assert with_dist is not None
        assert with_dist.version == "1.2.3"
        assert with_dist.author == "Tester"

        no_dist = mgr.get_plugin("ep_no_dist")
        assert no_dist is not None
        assert no_dist.version == "0.0.0"
        assert no_dist.author == ""

    def test_load_plugin_success_and_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.plugins import manager

        eps = [_FakeEP("loadable", "m:Cls", _FakeDist("1.0.0"))]
        monkeypatch.setattr(manager, "entry_points", lambda **kw: list(eps))
        mgr = manager.PluginManager()
        mgr.discover_entry_points()
        obj = mgr.load_plugin("loadable")
        assert obj.loaded_name == "loadable"

        # No matching entry point -> ImportError.
        monkeypatch.setattr(manager, "entry_points", lambda **kw: [])
        with pytest.raises(ImportError, match="entry point not resolvable"):
            mgr.load_plugin("loadable")

    def test_load_plugin_entry_points_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.plugins import manager

        eps = [_FakeEP("x", "m:Cls", _FakeDist("1.0.0"))]
        monkeypatch.setattr(manager, "entry_points", lambda **kw: list(eps))
        mgr = manager.PluginManager()
        mgr.discover_entry_points()

        monkeypatch.setattr(
            manager, "entry_points", lambda **kw: (_ for _ in ()).throw(RuntimeError())
        )
        with pytest.raises(ImportError):
            mgr.load_plugin("x")

    def test_load_plugin_unknown_raises(self) -> None:
        from agentdrill.plugins.manager import PluginManager

        with pytest.raises(KeyError, match="Plugin not found"):
            PluginManager().load_plugin("nope")

    def test_discover_directory_skips_underscore_files(self, tmp_path: Path) -> None:
        from agentdrill.plugins.manager import PluginManager

        _write(
            tmp_path / "_skip.py",
            "raise RuntimeError('underscore files must not be imported')\n",
        )
        _write(
            tmp_path / "good_plugin.py",
            "from agentdrill.plugins.manager import PluginInfo\n"
            "PLUGIN_INFO = PluginInfo(name='good', version='1', type='scorer',"
            " entry_point='g:S')\n"
            "class ScorerPlugin:\n    def score(self, *a, **k):\n        return {}\n",
        )
        mgr = PluginManager()
        mgr.discover_directory(str(tmp_path))
        names = [p.name for p in mgr.list_plugins()]
        assert "good" in names

    def test_load_plugin_file_spec_none(self, tmp_path: Path) -> None:
        from agentdrill.plugins.manager import PluginManager

        orig = importlib.util.spec_from_file_location

        def _none(*a, **k):
            return None

        try:
            importlib.util.spec_from_file_location = _none  # type: ignore[assignment]
            mgr = PluginManager()
            mgr._load_plugin_file(tmp_path / "anything.py")
        finally:
            importlib.util.spec_from_file_location = orig  # type: ignore[assignment]

    def test_load_plugin_file_without_plugin_info(self, tmp_path: Path) -> None:
        from agentdrill.plugins.manager import PluginManager

        f = _write(tmp_path / "noinfo.py", "X = 1\n")
        mgr = PluginManager()
        mgr._load_plugin_file(f)
        assert mgr.list_plugins() == []

    def test_register_module_objects_all_types(self, tmp_path: Path) -> None:
        from agentdrill.plugins.manager import PluginManager

        _write(
            tmp_path / "p_scorer.py",
            "from agentdrill.plugins.manager import PluginInfo\n"
            "PLUGIN_INFO = PluginInfo(name='c_scorer', version='1', type='scorer',"
            " entry_point='s:S')\n"
            "class ScorerPlugin:\n    def score(self, *a, **k):\n        return {}\n",
        )
        _write(
            tmp_path / "p_adapter.py",
            "from agentdrill.plugins.manager import PluginInfo\n"
            "PLUGIN_INFO = PluginInfo(name='c_adapter', version='1', type='adapter',"
            " entry_point='a:A')\n"
            "class AdapterPlugin:\n    def run(self, *a, **k):\n        return {}\n",
        )
        _write(
            tmp_path / "p_judge.py",
            "from agentdrill.plugins.manager import PluginInfo\n"
            "PLUGIN_INFO = PluginInfo(name='c_judge', version='1', type='judge',"
            " entry_point='j:J')\n"
            "class JudgePlugin:\n    def evaluate(self, *a, **k):\n        return {}\n",
        )
        _write(
            tmp_path / "p_benchmark.py",
            "from agentdrill.plugins.manager import PluginInfo\n"
            "PLUGIN_INFO = PluginInfo(name='c_bench', version='1', type='benchmark',"
            " entry_point='b:L')\n"
            "def load_benchmark():\n    return []\n",
        )
        mgr = PluginManager()
        mgr.discover_directory(str(tmp_path))
        reg = mgr.registry
        assert reg.get_scorer("c_scorer") is not None
        assert reg.get_adapter("c_adapter") is not None
        assert reg.get_judge("c_judge") is not None
        assert reg.get_benchmark_loader("c_bench") is not None

    def test_validate_empty_version_and_entry_point(self) -> None:
        from agentdrill.plugins.manager import PluginInfo, PluginManager

        mgr = PluginManager()
        info = PluginInfo(name="x", version="", type="scorer", entry_point="pkg:x")
        errors = mgr.validate_plugin(info)
        assert "Plugin version is empty" in errors

        info2 = PluginInfo(name="y", version="1.0", type="scorer", entry_point="")
        errors2 = mgr.validate_plugin(info2)
        assert "Plugin entry point is empty" in errors2

    def test_registry_duplicates_and_misc(self) -> None:
        from agentdrill.plugins.manager import PluginInfo, PluginRegistry

        reg = PluginRegistry()
        reg.register_scorer("s", object)
        with pytest.raises(ValueError, match="Duplicate scorer"):
            reg.register_scorer("s", object)
        reg.register_adapter("a", object)
        with pytest.raises(ValueError, match="Duplicate adapter"):
            reg.register_adapter("a", object)
        reg.register_judge("j", object)
        with pytest.raises(ValueError, match="Duplicate judge"):
            reg.register_judge("j", object)
        reg.register_benchmark_loader("b", object)
        with pytest.raises(ValueError, match="Duplicate benchmark"):
            reg.register_benchmark_loader("b", object)

        assert reg.list_plugins() == []
        reg._register_info(PluginInfo(name="s", version="1", type="scorer", entry_point="x"))
        with pytest.raises(ValueError, match="Duplicate plugin info"):
            reg._register_info(
                PluginInfo(name="s", version="1", type="scorer", entry_point="x")
            )
        reg._register_info(PluginInfo(name="a", version="1", type="adapter", entry_point="x"))
        assert len(reg.list_plugins("scorer")) == 1
        assert len(reg.list_plugins("adapter")) == 1
        assert reg.list_plugins(None) != []

    def test_validate_empty_name_and_unknown_type(self) -> None:
        from agentdrill.plugins.manager import PluginInfo, PluginManager

        mgr = PluginManager()
        assert "Plugin name is empty" in mgr.validate_plugin(
            PluginInfo(name="   ", version="1", type="scorer", entry_point="x")
        )
        unknown = mgr.validate_plugin(
            PluginInfo(name="u", version="1", type="weird", entry_point="x")
        )
        assert any("Unknown plugin type" in e for e in unknown)

    def test_validate_missing_required_methods(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.plugins.manager import PluginInfo, PluginManager

        mgr = PluginManager()
        for ptype, method in (
            ("scorer", "score"),
            ("adapter", "_invoke"),
            ("judge", "evaluate"),
            ("benchmark", "load"),
        ):
            info = PluginInfo(name=f"bad_{ptype}", version="1", type=ptype, entry_point="x")
            monkeypatch.setattr(mgr, "load_plugin", lambda name: object())
            errors = mgr.validate_plugin(info)
            assert any(f"missing required method: {method}" in e for e in errors)

    def test_discover_plugins_convenience(self) -> None:
        from agentdrill.plugins.manager import PluginManager, discover_plugins

        assert isinstance(discover_plugins(), PluginManager)

    def test_discover_directory_not_a_directory(self, tmp_path: Path) -> None:
        from agentdrill.plugins.manager import PluginManager

        with pytest.raises(ValueError, match="Not a directory"):
            PluginManager().discover_directory(str(tmp_path / "nope"))

    def test_install_plugin_existing_dir(self, tmp_path: Path) -> None:
        from agentdrill.plugins.manager import PluginManager

        mgr = PluginManager()
        mgr.install_plugin(str(tmp_path))
        assert mgr.list_plugins() == []

    def test_install_plugin_via_pip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.plugins.manager import PluginManager

        calls: list[list[str]] = []

        def _fake_check_call(cmd, *a, **k):
            calls.append(list(cmd))

        monkeypatch.setattr(subprocess, "check_call", _fake_check_call)
        PluginManager().install_plugin("some-nonexistent-package-xyz")
        assert calls and calls[0][-1] == "some-nonexistent-package-xyz"


# ===========================================================================
# scoring/judge/openai.py
# ===========================================================================


class _FakeResponse:
    def __init__(self, status_code: int, payload=None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


class TestOpenAIJudge:
    def test_judge_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.scoring.judge import openai as mod

        payload = {"choices": [{"message": {"content": '{"score": 0.7, "rationale": "ok"}'}}]}
        monkeypatch.setattr(mod.httpx, "post", lambda *a, **k: _FakeResponse(200, payload))
        client = mod.OpenAIClient(api_key="k")
        verdict = client.judge("prompt")
        assert verdict.score == 0.7
        assert verdict.rationale == "ok"

    def test_judge_http_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.models.errors import JudgeError
        from agentdrill.scoring.judge import openai as mod

        monkeypatch.setattr(
            mod.httpx, "post", lambda *a, **k: _FakeResponse(500, None, text="boom")
        )
        client = mod.OpenAIClient(api_key="k", base_url="http://localhost:1234/v1/")
        assert client.base_url == "http://localhost:1234/v1"
        with pytest.raises(JudgeError, match="500"):
            client.judge("p")

    def test_parse_verdict_malformed(self) -> None:
        from agentdrill.models.errors import JudgeError
        from agentdrill.scoring.judge.openai import _parse_verdict

        with pytest.raises(JudgeError, match="malformed verdict JSON"):
            _parse_verdict("not json {")

    def test_parse_verdict_single_number_list(self) -> None:
        from agentdrill.scoring.judge.openai import _parse_verdict

        v = _parse_verdict("[0.9]")
        assert v.score == 0.9

    def test_parse_verdict_single_dict_list(self) -> None:
        from agentdrill.scoring.judge.openai import _parse_verdict

        v = _parse_verdict('[{"score": 0.4, "rationale": "x"}]')
        assert v.score == 0.4
        assert v.rationale == "x"

    def test_parse_verdict_non_object_scalar(self) -> None:
        from agentdrill.models.errors import JudgeError
        from agentdrill.scoring.judge.openai import _parse_verdict

        with pytest.raises(JudgeError, match="expected JSON object"):
            _parse_verdict('"just a string"')

    def test_parse_verdict_multi_element_list(self) -> None:
        from agentdrill.models.errors import JudgeError
        from agentdrill.scoring.judge.openai import _parse_verdict

        with pytest.raises(JudgeError, match="expected JSON object"):
            _parse_verdict("[1, 2]")

    def test_parse_verdict_defaults_and_clamping(self) -> None:
        from agentdrill.scoring.judge.openai import _parse_verdict

        assert _parse_verdict("{}").score == 0.0
        assert _parse_verdict('{"score": 2}').score == 1.0
        assert _parse_verdict('{"score": -1}').score == 0.0

    def test_parse_verdict_non_numeric_score(self) -> None:
        from agentdrill.models.errors import JudgeError
        from agentdrill.scoring.judge.openai import _parse_verdict

        with pytest.raises(JudgeError, match="must be numeric"):
            _parse_verdict('{"score": "high"}')

    def test_parse_verdict_output_wrapper_dict(self) -> None:
        from agentdrill.scoring.judge.openai import _parse_verdict

        v = _parse_verdict('{"output": {"score": 0.3, "rationale": "inner"}}')
        assert v.score == 0.3
        assert v.rationale == "inner"

    def test_parse_verdict_output_wrapper_json_string(self) -> None:
        from agentdrill.scoring.judge.openai import _parse_verdict

        v = _parse_verdict('{"output": "{\\"score\\": 0.6, \\"rationale\\": \\"s\\"}"}')
        assert v.score == 0.6
        assert v.rationale == "s"

    def test_parse_verdict_output_wrapper_bad_string(self) -> None:
        from agentdrill.scoring.judge.openai import _parse_verdict

        # Inner string is not JSON -> wrapper ignored, top-level score kept.
        v = _parse_verdict('{"output": "nope", "score": 0.2}')
        assert v.score == 0.2


# ===========================================================================
# scoring/judge/scorers.py
# ===========================================================================


class TestJudgeScorers:
    def test_normalize_verdict_branches(self) -> None:
        from agentdrill.scoring.judge.scorers import _normalize_verdict
        from agentdrill.scoring.result import JudgeVerdict

        original = JudgeVerdict(score=0.5, rationale="orig")
        assert _normalize_verdict(original) is original

        assert _normalize_verdict({"score": 0.2, "rationale": "d"}).score == 0.2
        assert _normalize_verdict([]).score == 0.0
        assert _normalize_verdict([{"score": 0.8, "rationale": "r"}]).score == 0.8
        assert _normalize_verdict([0.3]).score == 0.3
        assert _normalize_verdict(0.9).score == 0.9
        fallback = _normalize_verdict(None)
        assert fallback.score == 0.0

    def test_build_prompt_expected_and_trajectory_branches(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.models.pack import Expected
        from agentdrill.scoring.judge.scorers import _build_prompt

        art = _artifact(
            output="final answer",
            trajectory=[
                TrajectoryStep(type="tool_call", tool="t", args={}),
                TrajectoryStep(type="tool_result", tool="t", result="r"),
                TrajectoryStep(type="note", content="n", error="boom"),
            ],
        )

        # expected value + criteria + trajectory with errors
        sc = _scenario(
            expected=Expected(type="rubric", value="expected", criteria=["one", "two"])
        )
        prompt = _build_prompt(sc, art, "criterion-here")
        assert "### Expected Answer" in prompt
        assert "### Rubric Criteria" in prompt
        assert "### Agent Trajectory" in prompt
        assert "Errors:" in prompt
        assert "criterion-here" in prompt

        # No expected block at all -> else branch (empty expected_section)
        sc_none = _scenario(expected=None)
        prompt2 = _build_prompt(sc_none, _artifact(output="x"), "c")
        assert "### Expected Answer" not in prompt2
        assert "### Agent Trajectory" not in prompt2

    def test_score_via_judge_with_and_without_judge(self) -> None:
        from agentdrill.scoring.judge.mock import MockJudge
        from agentdrill.scoring.judge.scorers import TaskCompletionScorer

        scorer = TaskCompletionScorer()
        no_judge = scorer.score(_artifact(), _scenario(), {"threshold": 0.8})
        assert no_judge.error == "judge not configured"

        scorer.judge = MockJudge(score=0.9, rationale="great")
        ok = scorer.score(_artifact(), _scenario(), {"threshold": 0.8})
        assert ok.score == 0.9
        assert ok.passed is True
        assert ok.error is None

        scorer.judge = MockJudge(score=0.1)
        failed = scorer.score(_artifact(), _scenario(), {"threshold": 0.8})
        assert failed.passed is False

    def test_score_via_judge_exception(self) -> None:
        from agentdrill.scoring.judge.scorers import TaskCompletionScorer

        class _BoomJudge:
            name = "boom"
            model = "m"
            base_url = None

            def judge(self, prompt, **kwargs):
                raise RuntimeError("judge exploded")

        scorer = TaskCompletionScorer()
        scorer.judge = _BoomJudge()
        result = scorer.score(_artifact(), _scenario(), {"threshold": 0.8})
        assert result.error is not None
        assert "judge call failed" in result.error


# ===========================================================================
# loading/pack_loader.py
# ===========================================================================


_PACK_HEADER = 'pack:\n  name: "p"\n  version: "1.0"\n'


class TestPackLoaderCoverage:
    def test_top_level_not_mapping(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "list.yaml", "- a\n- b\n")
        with pytest.raises(PackParseError, match="must be a mapping"):
            load_pack(f)

    def test_missing_pack_metadata(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "nopack.yaml", "scenarios: []\n")
        with pytest.raises(PackParseError, match="missing required `pack`"):
            load_pack(f)

    def test_pack_missing_name(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "noname.yaml", 'pack:\n  version: "1"\nscenarios: []\n')
        with pytest.raises(PackParseError, match="missing required field: name"):
            load_pack(f)

    def test_scenarios_not_list(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "nolist.yaml", _PACK_HEADER + "scenarios: nope\n")
        with pytest.raises(PackParseError, match="missing required `scenarios`"):
            load_pack(f)

    def test_scenario_not_mapping(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "badscen.yaml", _PACK_HEADER + 'scenarios:\n  - "str"\n')
        with pytest.raises(PackParseError, match="must be a mapping"):
            load_pack(f)

    def test_metrics_not_mapping(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(
            tmp_path / "badmetrics.yaml",
            _PACK_HEADER
            + "scenarios:\n  - id: s\n    title: t\n    input: i\n    metrics: nope\n",
        )
        with pytest.raises(PackParseError, match="metrics must be a mapping"):
            load_pack(f)

    def test_metric_entry_not_mapping(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(
            tmp_path / "badmetric.yaml",
            _PACK_HEADER
            + "scenarios:\n  - id: s\n    title: t\n    input: i\n"
            + "    metrics:\n      task_completion: nope\n",
        )
        with pytest.raises(PackParseError, match="must be a mapping"):
            load_pack(f)

    def test_pydantic_validation_error(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        # `version` present (structural pass) but wrong type for pydantic (int).
        f = _write(
            tmp_path / "badtype.yaml",
            'pack:\n  name: "p"\n  version: 123\nscenarios: []\n',
        )
        with pytest.raises(PackParseError, match="invalid pack structure"):
            load_pack(f)

    def test_oserror_on_read(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.loading import pack_loader
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "readerr.yaml", _PACK_HEADER + "scenarios: []\n")

        def _raise(self, *a, **k):
            raise OSError("cannot read")

        monkeypatch.setattr(Path, "read_text", _raise)
        with pytest.raises(PackParseError, match="could not read pack"):
            pack_loader.load_pack(f)

    def test_malformed_json(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "bad.json", "{not valid json")
        with pytest.raises(PackParseError, match="malformed JSON"):
            load_pack(f)

    def test_json_cache_fast_path(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack

        data = {
            "pack": {"name": "jp", "version": "1.0"},
            "scenarios": [{"id": "s", "title": "t", "input": "i"}],
        }
        f = tmp_path / "cached.json"
        f.write_text(json.dumps(data), encoding="utf-8")
        first = load_pack(f)
        second = load_pack(f)  # cache hit -> JSON fast path
        assert first.pack.name == second.pack.name == "jp"

    def test_fast_path_validation_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from pydantic import ValidationError

        from agentdrill.loading import pack_loader
        from agentdrill.models.errors import PackParseError
        from agentdrill.models.pack import ScenarioPack

        data = {
            "pack": {"name": "jp2", "version": "1.0"},
            "scenarios": [{"id": "s", "title": "t", "input": "i"}],
        }
        f = tmp_path / "cached2.json"
        f.write_text(json.dumps(data), encoding="utf-8")
        pack_loader.load_pack(f)  # prime the cache

        try:
            ScenarioPack(pack={"name": "x"}, scenarios="bad")
        except ValidationError as exc:  # pragma: no cover - defensive
            captured = exc

        def _boom(cls, payload):
            raise captured

        monkeypatch.setattr(ScenarioPack, "model_validate", classmethod(_boom))
        with pytest.raises(PackParseError, match="invalid pack structure"):
            pack_loader.load_pack(f)

    def test_missing_file(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        with pytest.raises(PackParseError, match="not found"):
            load_pack(tmp_path / "nope.yaml")

    def test_malformed_yaml_with_line(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(tmp_path / "malformed.yaml", "pack: [unclosed\n")
        with pytest.raises(PackParseError) as excinfo:
            load_pack(f)
        assert excinfo.value.line is not None

    def test_missing_scenario_field(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(
            tmp_path / "miss.yaml",
            _PACK_HEADER + "scenarios:\n  - id: s\n    title: t\n",
        )
        with pytest.raises(PackParseError, match="missing required field: input"):
            load_pack(f)

    def test_duplicate_scenario_id(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(
            tmp_path / "dup.yaml",
            _PACK_HEADER
            + "scenarios:\n"
            + "  - {id: s, title: t, input: i}\n"
            + "  - {id: s, title: t2, input: i2}\n",
        )
        with pytest.raises(PackParseError, match="duplicate scenario id"):
            load_pack(f)

    def test_unknown_metric(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        f = _write(
            tmp_path / "unknown.yaml",
            _PACK_HEADER
            + "scenarios:\n  - {id: s, title: t, input: i, metrics: {not_a_metric: {}}}\n",
        )
        with pytest.raises(PackParseError, match="unknown metric"):
            load_pack(f)

    def test_threshold_type_and_range(self, tmp_path: Path) -> None:
        from agentdrill.loading.pack_loader import load_pack
        from agentdrill.models.errors import PackParseError

        bad_type = _write(
            tmp_path / "thresh_type.yaml",
            _PACK_HEADER
            + "scenarios:\n  - {id: s, title: t, input: i,"
            + " metrics: {task_completion: {threshold: high}}}\n",
        )
        with pytest.raises(PackParseError, match="threshold must be a number"):
            load_pack(bad_type)

        bad_range = _write(
            tmp_path / "thresh_range.yaml",
            _PACK_HEADER
            + "scenarios:\n  - {id: s, title: t, input: i,"
            + " metrics: {task_completion: {threshold: 2.5}}}\n",
        )
        with pytest.raises(PackParseError, match="threshold out of range"):
            load_pack(bad_range)

    def test_warn_orphaned_import_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.loading import pack_loader

        monkeypatch.setattr(pack_loader, "_known_metrics_warned", False)
        monkeypatch.setitem(sys.modules, "agentdrill.scoring.registry", None)

        f = _write(
            tmp_path / "warned.yaml",
            _PACK_HEADER + "scenarios:\n  - id: s\n    title: t\n    input: i\n",
        )
        pack = pack_loader.load_pack(f)
        assert pack.pack.name == "p"


# ===========================================================================
# provenance/tracker.py
# ===========================================================================


class TestProvenanceTrackerCoverage:
    def test_capture_pack_unparseable_yaml(self, tmp_path: Path) -> None:
        from agentdrill.provenance.tracker import ProvenanceTracker

        f = _write(tmp_path / "broken.yaml", "pack: [unclosed\n")
        info = ProvenanceTracker().capture_pack(str(f))
        assert info.pack_hash != ""
        assert info.pack_version == ""

    def test_capture_agent_colon_spec_with_file(self, tmp_path: Path) -> None:
        from agentdrill.provenance.tracker import ProvenanceTracker

        agent_file = _write(tmp_path / "agent.py", "def run(): pass\n")
        info = ProvenanceTracker().capture_agent(f"python:{agent_file}")
        assert info.agent_source == f"python:{agent_file}"
        assert len(info.agent_hash) == 64

    def test_capture_pack_valid_yaml_version(self, tmp_path: Path) -> None:
        from agentdrill.provenance.tracker import ProvenanceTracker

        f = _write(tmp_path / "ok.yaml", "pack:\n  name: x\n  version: '3.0'\n")
        info = ProvenanceTracker().capture_pack(str(f))
        assert info.pack_version == "3.0"

    def test_capture_agent_direct_file(self, tmp_path: Path) -> None:
        from agentdrill.provenance.tracker import ProvenanceTracker

        agent_file = _write(tmp_path / "a.py", "x = 1\n")
        info = ProvenanceTracker().capture_agent(str(agent_file))
        assert len(info.agent_hash) == 64

    def test_to_artifact_metadata(self) -> None:
        from agentdrill.provenance.tracker import ProvenanceTracker

        meta = ProvenanceTracker().to_artifact_metadata()
        assert "provenance" in meta
        assert "python_version" in meta["provenance"]

    def test_compute_content_hash_str_and_bytes(self) -> None:
        from agentdrill.provenance.tracker import ProvenanceTracker

        assert (
            ProvenanceTracker.compute_content_hash("abc")
            == ProvenanceTracker.compute_content_hash(b"abc")
        )

    def test_verify_all_paths(self, tmp_path: Path) -> None:
        from agentdrill.provenance.tracker import ProvenanceInfo, ProvenanceTracker

        tracker = ProvenanceTracker()
        assert tracker.verify(ProvenanceInfo(agentdrill_version="0.1")) == []

        issues = tracker.verify(
            ProvenanceInfo(
                timestamp="bad",
                agentdrill_version="",
                pack_uri="/p.yaml",
                agent_source="python:a",
            )
        )
        assert any("timestamp" in i for i in issues)
        assert any("agentdrill_version" in i for i in issues)
        assert any("pack_hash" in i for i in issues)
        assert any("agent_hash" in i for i in issues)

        f = _write(tmp_path / "p.yaml", "pack:\n  name: x\n")
        mismatch = tracker.verify(
            ProvenanceInfo(
                pack_uri=str(f),
                pack_hash="0" * 64,
                agentdrill_version="0.1",
            )
        )
        assert any("mismatch" in i for i in mismatch)

    def test_get_agentdrill_version_fallback(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import agentdrill
        from agentdrill.provenance.tracker import _get_agentdrill_version

        monkeypatch.delattr(agentdrill, "__version__", raising=False)
        assert _get_agentdrill_version() == "unknown"

    def test_get_dependencies_exception(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import importlib.metadata as md

        from agentdrill.provenance.tracker import _get_dependencies

        monkeypatch.setattr(
            md, "packages_distributions", lambda: (_ for _ in ()).throw(RuntimeError())
        )
        assert _get_dependencies() == {}

    def test_get_dependencies_per_package_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import importlib.metadata as md

        from agentdrill.provenance.tracker import _get_dependencies

        monkeypatch.setattr(md, "packages_distributions", lambda: {"pkg": ["distx"]})
        monkeypatch.setattr(
            md, "version", lambda name: (_ for _ in ()).throw(RuntimeError())
        )
        assert _get_dependencies() == {}

    def test_get_git_sha_failure_and_nonzero(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.provenance.tracker import _get_git_sha

        monkeypatch.setattr(
            subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(OSError("no git"))
        )
        assert _get_git_sha() == ""

        monkeypatch.setattr(
            subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="")
        )
        assert _get_git_sha() == ""


# ===========================================================================
# scenarios/registry.py
# ===========================================================================


class TestScenarioRegistryCoverage:
    def test_discover_default_missing_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        monkeypatch.chdir(tmp_path)
        assert ScenarioRegistry().discover() == []

    def test_read_oserror_returns_none(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        assert ScenarioRegistry().add(tmp_path) is None

    def test_read_bad_json(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        f = _write(tmp_path / "bad.json", "{not json")
        assert ScenarioRegistry().add(f) is None

    def test_data_not_a_dict(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        f = _write(tmp_path / "list.yaml", "- a\n- b\n")
        assert ScenarioRegistry().add(f) is None

    def test_read_bad_yaml(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        f = _write(tmp_path / "bad.yaml", "pack: [unclosed\n")
        assert ScenarioRegistry().add(f) is None

    def test_yaml_module_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.scenarios import registry

        monkeypatch.setattr(registry, "yaml", None)
        f = _write(tmp_path / "p.yaml", "pack:\n  name: x\n")
        assert registry.ScenarioRegistry().add(f) is None

    def test_pack_not_dict(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        f = _write(tmp_path / "p.yaml", "pack: 5\n")
        assert ScenarioRegistry().add(f) is None

    def test_name_not_string(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        f = _write(tmp_path / "p.yaml", "pack:\n  name: 123\n")
        assert ScenarioRegistry().add(f) is None

    def test_name_empty(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        f = _write(tmp_path / "p.yaml", 'pack:\n  name: ""\n')
        assert ScenarioRegistry().add(f) is None

    def test_version_and_description_not_string(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        f = _write(
            tmp_path / "p.yaml",
            "pack:\n  name: good\n  version: 123\n  description: [1, 2]\n"
            "scenarios:\n  - id: s\n",
        )
        info = ScenarioRegistry().add(f)
        assert info is not None
        assert info.version == "unknown"
        assert info.description == ""
        assert info.scenario_count == 1

    def test_discover_and_lookup(self, tmp_path: Path) -> None:
        from agentdrill.scenarios.registry import ScenarioRegistry

        _write(
            tmp_path / "pack.json",
            json.dumps(
                {
                    "pack": {"name": "json-pack", "version": "2.0", "description": "d"},
                    "scenarios": [{"id": "a"}, {"id": "b"}],
                }
            ),
        )
        reg = ScenarioRegistry()
        discovered = reg.discover([str(tmp_path)])
        assert len(discovered) == 1
        assert reg.find("json-pack") is not None
        assert [p.name for p in reg.list()] == ["json-pack"]


# ===========================================================================
# determinism/reproducibility.py
# ===========================================================================


class TestReproducibilityCoverage:
    def test_too_few_runs(self) -> None:
        from agentdrill.determinism.reproducibility import ReproducibilityChecker

        report = ReproducibilityChecker().check([])
        assert report.runs == 0
        assert "need at least 2 runs" in report.recommendations[0]

    def test_score_variance_recommendation(self) -> None:
        from agentdrill.determinism.reproducibility import ReproducibilityChecker
        from agentdrill.scoring.result import RunScore, ScenarioScore, ScoreResult

        def _run(score: float) -> RunScore:
            return RunScore(
                scenario_scores={
                    "sc": ScenarioScore(
                        scenario_id="sc",
                        metric_results={
                            "m": ScoreResult(
                                metric="m",
                                score=score,
                                threshold=0.5,
                                passed=True,
                                category="correctness",
                                blocking=False,
                                detail={},
                                source="deterministic",
                                error=None,
                            )
                        },
                        status="passed",
                        safety_violations=[],
                    )
                },
                totals={"passed": 1, "warned": 0, "failed": 0},
                safety_violations=[],
                exit_code=0,
            )

        report = ReproducibilityChecker().check([_run(1.0), _run(0.2)])
        assert report.consistent_scores is False
        assert any("Score variance" in r for r in report.recommendations)

    def test_trajectory_only_variance(self) -> None:
        from agentdrill.determinism.reproducibility import ReproducibilityChecker
        from agentdrill.scoring.result import RunScore, ScenarioScore, ScoreResult

        def _metric(score: float) -> ScoreResult:
            return ScoreResult(
                metric="m",
                score=score,
                threshold=0.5,
                passed=True,
                category="correctness",
                blocking=False,
                detail={},
                source="deterministic",
                error=None,
            )

        run1 = RunScore(
            scenario_scores={
                "sc": ScenarioScore(
                    scenario_id="sc",
                    metric_results={"a": _metric(0.5), "b": _metric(0.5)},
                    status="passed",
                    safety_violations=[],
                )
            },
            totals={"passed": 1, "warned": 0, "failed": 0},
            safety_violations=[],
            exit_code=0,
        )
        run2 = RunScore(
            scenario_scores={
                "sc": ScenarioScore(
                    scenario_id="sc",
                    metric_results={"a": _metric(1.0)},
                    status="passed",
                    safety_violations=[],
                )
            },
            totals={"passed": 1, "warned": 0, "failed": 0},
            safety_violations=[],
            exit_code=0,
        )
        report = ReproducibilityChecker().check([run1, run2])
        # Scores identical (both total 1.0) but trajectory lengths differ.
        assert report.consistent_scores is False
        assert any("Trajectory variance" in r for r in report.recommendations)

    def test_check_single_with_fakes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from agentdrill.determinism import reproducibility

        class _FakeRunner:
            def __init__(self, *a, **k) -> None:
                self.pack = object()

            def load_pack(self, path: str) -> None:
                return None

            def run_all(self):
                return [object()]

        class _FakeEngine:
            def __init__(self, *a, **k) -> None:
                pass

            def score_run(self, artifacts, *a, **k):
                # A RunScore-like object (check() reads .scenario_scores).
                return SimpleNamespace(scenario_scores={})

        monkeypatch.setattr("agentdrill.runner.Runner", _FakeRunner)
        monkeypatch.setattr("agentdrill.scoring.engine.ScoringEngine", _FakeEngine)

        report = reproducibility.ReproducibilityChecker().check_single(
            "pack.yaml", "python:agent", runs=3
        )
        assert report.runs == 3
        assert report.consistent_scores is True


# ===========================================================================
# baselines/store.py
# ===========================================================================


class TestBaselineStoreCoverage:
    def test_list_missing_dir(self, tmp_path: Path) -> None:
        from agentdrill.baselines.store import BaselineStore

        assert BaselineStore(base_dir=str(tmp_path / "missing")).list() == []

    def test_load_missing_raises(self, tmp_path: Path) -> None:
        from agentdrill.baselines.store import BaselineStore

        with pytest.raises(FileNotFoundError, match="missing"):
            BaselineStore(base_dir=str(tmp_path)).load("missing")

    def test_list_existing_and_validate_version_mismatch(self, tmp_path: Path) -> None:
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore

        store = BaselineStore(base_dir=str(tmp_path))
        store.save(Baseline(name="v1", pack="core", pack_version="2.0", runs=[_artifact()]))
        assert store.list() == ["v1"]
        msg = store.validate("v1", pack_version="1.0")
        assert "version mismatch" in msg

    def test_describe_int_scores(self, tmp_path: Path) -> None:
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore

        store = BaselineStore(base_dir=str(tmp_path))
        store.save(
            Baseline(
                name="b",
                pack="core",
                pack_version="1.0",
                runs=[_artifact()],
                score_snapshot={"scenario_scores": {"sc-1": 0.8, "sc-2": 0.6}},
            )
        )
        assert store.describe("b")["avg_score"] == pytest.approx(0.7)

    def test_tag_annotate_delete(self, tmp_path: Path) -> None:
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore

        store = BaselineStore(base_dir=str(tmp_path))
        store.save(Baseline(name="v1", pack="core", pack_version="1.0", runs=[_artifact()]))
        assert store.tag("v1", ["golden"]).tags == ["golden"]
        assert store.annotate("v1", "note").notes == "note"
        store.delete("v1")
        assert store.list() == []
        with pytest.raises(FileNotFoundError):
            store.delete("v1")

    def test_validate_adapter_digest_mismatch(self, tmp_path: Path) -> None:
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore

        store = BaselineStore(base_dir=str(tmp_path))
        store.save(
            Baseline(
                name="b",
                pack="core",
                pack_version="1.0",
                runs=[_artifact()],
                adapter_manifest={"digest": "abcdef1234567890"},
            )
        )
        msg = store.validate(
            "b", pack_version="1.0", adapter_manifest={"digest": "9999999999999999"}
        )
        assert "adapter digest mismatch" in msg

        ok = store.validate(
            "b", pack_version="1.0", adapter_manifest={"digest": "abcdef1234567890"}
        )
        assert ok == ""

    def test_describe_with_nested_metric_scores(self, tmp_path: Path) -> None:
        from agentdrill.baselines.model import Baseline
        from agentdrill.baselines.store import BaselineStore

        store = BaselineStore(base_dir=str(tmp_path))
        store.save(
            Baseline(
                name="b",
                pack="core",
                pack_version="1.0",
                runs=[_artifact()],
                score_snapshot={
                    "scenario_scores": {
                        "sc-1": {"metrics": {"m": {"score": 0.5}}},
                        "sc-2": {"metrics": {"m": {"score": 0.7}}},
                    }
                },
            )
        )
        info = store.describe("b")
        assert info["avg_score"] == pytest.approx(0.6)


# ===========================================================================
# classification.py
# ===========================================================================


class TestClassificationCoverage:
    def test_classify_api_key_and_network(self) -> None:
        from agentdrill.classification import AgentClassifier, InfraTags

        tags = AgentClassifier.classify({"env": {"API_KEY": "x"}, "mod": "requests"})
        assert InfraTags.NEEDS_API_KEY in tags
        assert InfraTags.NETWORK_ACCESS in tags
        assert InfraTags.NEEDS_GATEWAY in tags

    def test_classify_all_categories(self) -> None:
        from agentdrill.classification import AgentClassifier, InfraTags

        fs = AgentClassifier.classify({"code": "Path('/etc/cfg').write_text('x')"})
        assert InfraTags.FILESYSTEM_WRITE in fs
        assert InfraTags.WRITES_ROOT in fs

        db = AgentClassifier.classify({"db": "sqlite://"})
        assert InfraTags.NEEDS_DB in db

        gpu = AgentClassifier.classify({"gpu": "torch.cuda"})
        assert InfraTags.NEEDS_GPU in gpu

        side = AgentClassifier.classify({"x": "os.environ"})
        assert InfraTags.IMPORT_SIDE_EFFECTS in side

    def test_from_source_all_categories(self) -> None:
        from agentdrill.classification import AgentClassifier, InfraTags

        tags = AgentClassifier.from_source(
            "import requests\n"
            "open('f', 'w')\n"
            "import sqlite3\n"
            "torch.cuda.is_available()\n"
            "os.environ['X']\n"
            "TOKEN = 'abc'\n"
        )
        assert InfraTags.NEEDS_API_KEY in tags
        assert InfraTags.NETWORK_ACCESS in tags
        assert InfraTags.FILESYSTEM_WRITE in tags
        assert InfraTags.NEEDS_DB in tags
        assert InfraTags.NEEDS_GPU in tags
        assert InfraTags.IMPORT_SIDE_EFFECTS in tags


# ===========================================================================
# scoring/deterministic/grounding.py
# ===========================================================================


class TestGroundingCoverage:
    def test_extract_tool_names_empty_output(self) -> None:
        from agentdrill.scoring.deterministic.grounding import (
            _extract_tool_names_from_output,
        )

        assert _extract_tool_names_from_output("") == set()

    def test_factual_consistency_no_content_words(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import FactualConsistencyScorer

        art = _artifact(
            output="a b c d e f g h",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="anything")],
        )
        result = FactualConsistencyScorer().score(art, _scenario(), {})
        assert result.score == 0.0

    def test_factual_consistency_ungrounded(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import FactualConsistencyScorer

        art = _artifact(
            output="Zebras migrate across savannah grasslands annually.",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="unrelated")],
        )
        result = FactualConsistencyScorer().score(art, _scenario(), {"threshold": 0.5})
        assert result.score == 0.0
        assert result.detail["sentences_ungrounded"] == 1

    def test_factual_consistency_grounded(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import FactualConsistencyScorer

        art = _artifact(
            output="The server is healthy and serving traffic.",
            trajectory=[
                TrajectoryStep(type="tool_result", tool="t", result="server healthy serving")
            ],
        )
        result = FactualConsistencyScorer().score(art, _scenario(), {"threshold": 0.5})
        assert result.score == 1.0

    def test_source_citation_empty_output(self) -> None:
        from agentdrill.scoring.deterministic.grounding import SourceCitationScorer

        result = SourceCitationScorer().score(_artifact(output=""), _scenario(), {})
        assert result.score == 1.0

    def test_source_citation_no_references(self) -> None:
        from agentdrill.scoring.deterministic.grounding import SourceCitationScorer

        art = _artifact(output="Nothing to cite here at all.")
        result = SourceCitationScorer().score(art, _scenario(), {})
        assert result.score == 0.5

    def test_source_citation_valid_and_invalid(self) -> None:
        from agentdrill.scoring.deterministic.grounding import SourceCitationScorer

        art = _artifact(output="Used `search` and `bogus_tool` to answer.")
        sc = _scenario(allowed_tools=["search"])
        result = SourceCitationScorer().score(art, sc, {"threshold": 0.5})
        assert result.score == pytest.approx(0.5)
        assert result.detail["invalid_citations"] == ["bogus_tool"]

    def test_output_grounding_empty_output(self) -> None:
        from agentdrill.scoring.deterministic.grounding import OutputGroundingScorer

        result = OutputGroundingScorer().score(_artifact(output=""), _scenario(), {})
        assert result.score == 1.0

    def test_output_grounding_no_evaluable_sentences(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import OutputGroundingScorer

        art = _artifact(
            output="hi.",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="x")],
        )
        result = OutputGroundingScorer().score(art, _scenario(), {})
        assert result.score == 1.0

    def test_output_grounding_no_content_words(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import OutputGroundingScorer

        art = _artifact(
            output="a b c d e f g h",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="x")],
        )
        result = OutputGroundingScorer().score(art, _scenario(), {})
        assert result.score == 1.0

    def test_output_grounding_grounded_sentence(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import OutputGroundingScorer

        art = _artifact(
            output="The server is healthy and serving traffic.",
            trajectory=[
                TrajectoryStep(type="tool_result", tool="t", result="server healthy serving")
            ],
        )
        result = OutputGroundingScorer().score(art, _scenario(), {"threshold": 0.6})
        assert result.score == 1.0

    def test_output_grounding_ungrounded_sentence(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import OutputGroundingScorer

        art = _artifact(
            output="Zebras migrate across savannah grasslands annually.",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="unrelated")],
        )
        result = OutputGroundingScorer().score(art, _scenario(), {"threshold": 0.6})
        assert result.score == 0.0
        assert result.detail["sentences_ungrounded"] == 1

    def test_insufficient_data_branches(self) -> None:
        from agentdrill.scoring.deterministic.grounding import (
            ContradictionDetectionScorer,
            FactualConsistencyScorer,
            OutputGroundingScorer,
        )

        assert FactualConsistencyScorer().score(_artifact(output=""), _scenario(), {}).score == 1.0
        assert OutputGroundingScorer().score(
            _artifact(output="Some real output here"), _scenario(), {}
        ).score == 0.0
        assert ContradictionDetectionScorer().score(
            _artifact(output=""), _scenario(), {}
        ).score == 1.0

    def test_contradiction_none_detected(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import (
            ContradictionDetectionScorer,
        )

        art = _artifact(
            output="The system is healthy.",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="healthy")],
        )
        result = ContradictionDetectionScorer().score(art, _scenario(), {})
        assert result.score == 1.0
        assert result.detail["contradictions_found"] == 0

    def test_contradiction_detected(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import (
            ContradictionDetectionScorer,
        )

        art = _artifact(
            output="Yes, everything is fine.",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="no errors found")],
        )
        result = ContradictionDetectionScorer().score(art, _scenario(), {})
        assert result.score < 1.0
        assert result.detail["contradictions_found"] >= 1

    def test_contradiction_reversed(self) -> None:
        from agentdrill.models.artifact import TrajectoryStep
        from agentdrill.scoring.deterministic.grounding import (
            ContradictionDetectionScorer,
        )

        art = _artifact(
            output="No, it did not pass.",
            trajectory=[TrajectoryStep(type="tool_result", tool="t", result="yes it passed")],
        )
        result = ContradictionDetectionScorer().score(art, _scenario(), {})
        assert result.score < 1.0
