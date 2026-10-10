"""Extra offline coverage tests for adapter modules (M0 adapter sweep).

These tests exercise happy and edge/failure paths of the framework adapters,
the base adapter contract, and the subprocess/isolation plumbing. They are
fully deterministic and offline: framework builders are injected as synthetic
modules via ``sys.modules`` and HTTP / subprocess calls are monkeypatched.
"""

from __future__ import annotations

import asyncio
import sys
import types
from typing import Any

import pytest

from agentdrill.models.errors import AdapterError, AgentTimeoutError
from agentdrill.models.pack import Scenario


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _scenario(mode: str = "x", input_: str = "hello") -> Scenario:
    return Scenario(id="sc-1", title="T", input=input_, context={"mode": mode})


def _install(monkeypatch: pytest.MonkeyPatch, name: str, **attrs: Any) -> str:
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    monkeypatch.setitem(sys.modules, name, mod)
    return name


# --------------------------------------------------------------------------- #
# base.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters.base import (  # noqa: E402
    Adapter,
    _artifact_for_error,
    _inject_fixtures,
    build_invocation_payload,
    parse_agent_stdout,
)


class _IntAdapter(Adapter):
    name = "int"

    def _invoke(self, payload: dict, config: dict) -> Any:  # type: ignore[override]
        return 123


class _RaisingAdapter(Adapter):
    name = "raise"

    def _invoke(self, payload: dict, config: dict) -> Any:  # type: ignore[override]
        raise ValueError("boom")


def test_parse_agent_stdout_non_object_json() -> None:
    out = parse_agent_stdout("[1, 2]")
    assert out["status"] == "completed"
    with pytest.raises(AdapterError):
        parse_agent_stdout("[1, 2]", strict=True)


def test_run_unexpected_return_type() -> None:
    art = _IntAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "unexpected type" in (art.error or "")


def test_run_generic_exception_normalized() -> None:
    art = _RaisingAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "boom" in (art.error or "")


def test_get_manifest_default() -> None:
    manifest = _IntAdapter().get_manifest()
    assert manifest["name"] == "int"
    assert "version" in manifest
    assert manifest["capabilities"] == ["stdin_stdout"]


def test_get_manifest_version_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.metadata as _md

    def _boom(_name: str) -> str:
        raise _md.PackageNotFoundError("nope")

    monkeypatch.setattr(_md, "version", _boom)
    assert _IntAdapter().get_manifest()["version"] == "0.0.0"


def test_malformed_trajectory_steps_skipped() -> None:
    # non-dict step and a step that fails TrajectoryStep validation are dropped
    adapter = _RawEnvelope(
        {
            "status": "completed",
            "output": {"final": "hi"},
            "trajectory": {"steps": [1, {"type": "bogus"}, {"type": "response", "content": "x"}]},
        }
    )
    art = adapter.run(_scenario(), {"run_id": "r"})
    assert art.status == "completed"
    assert len(art.trajectory) == 1


class _RawEnvelope(Adapter):
    name = "rawenv"

    def __init__(self, envelope: dict) -> None:
        self._envelope = envelope

    def _invoke(self, payload: dict, config: dict) -> dict:  # type: ignore[override]
        return self._envelope


def test_inject_fixtures_sets_metadata() -> None:
    payload: dict[str, Any] = {}
    _inject_fixtures(payload, {"fixtures": True, "fixtures_dir": "d"})
    assert payload["_fixture_mode"] is True
    assert payload["_fixtures_dir"] == "d"
    other: dict[str, Any] = {}
    _inject_fixtures(other, {})
    assert other == {}


def test_inject_fixtures_default_dir() -> None:
    payload: dict[str, Any] = {}
    _inject_fixtures(payload, {"fixtures": True})
    assert payload["_fixtures_dir"] == "scenarios/fixtures"


def test_build_invocation_payload_budget_none() -> None:
    payload = build_invocation_payload(_scenario(), "r")
    assert payload["budget"] == {}


def test_artifact_for_error_explicit_trace_diff() -> None:
    art = _artifact_for_error(
        _scenario(),
        "r",
        "error",
        "m",
        {"type": "custom"},
        "2020-01-01T00:00:00Z",
        0,
        trace_diff={"some": "diff"},
    )
    assert art.trace_diff == {"some": "diff"}
    assert art.error_category is not None


# --------------------------------------------------------------------------- #
# _model_patch.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import _model_patch as mp  # noqa: E402


class _Fake:
    def __init__(self, *a: Any, **kw: Any) -> None:
        self.kw = kw


def _prep_fake() -> type:
    fake = type("Fake", (_Fake,), {})
    return fake


def test_patch_langchain_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    import langchain_openai

    fake = _prep_fake()
    monkeypatch.setattr(langchain_openai, "ChatOpenAI", fake)
    monkeypatch.setattr(mp, "_FORCE", False)
    monkeypatch.setattr(mp, "_MODEL", "M")
    langchain_openai.ChatOpenAI = fake
    mp._patch_langchain_openai()
    assert fake._agentdrill_patched is True
    assert fake().kw["model"] == "M"
    assert "model" not in fake(model_name="x").kw
    monkeypatch.setattr(mp, "_FORCE", True)
    assert fake(model_name="x").kw["model"] == "M"
    mp._patch_langchain_openai()  # idempotent


def test_patch_langchain_openai_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import langchain_openai

    monkeypatch.delattr(langchain_openai, "ChatOpenAI")
    mp._patch_langchain_openai()  # swallowed


def test_patch_smolagents(monkeypatch: pytest.MonkeyPatch) -> None:
    import smolagents.models as sm

    fake = _prep_fake()
    monkeypatch.setattr(sm, "LiteLLMModel", fake)
    monkeypatch.setattr(mp, "_FORCE", False)
    monkeypatch.setattr(mp, "_MODEL", "M")
    mp._patch_smolagents()
    assert fake().kw["model_id"] == "openai/M"
    assert fake(model="x").kw == {"model": "x"}
    monkeypatch.setattr(mp, "_FORCE", True)
    assert fake(model="x").kw["model_id"] == "openai/M"
    mp._patch_smolagents()


def test_patch_smolagents_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import smolagents.models as sm

    monkeypatch.delattr(sm, "LiteLLMModel")
    mp._patch_smolagents()


def test_patch_autogen(monkeypatch: pytest.MonkeyPatch) -> None:
    import autogen_ext.models.openai as ao

    fake = _prep_fake()
    monkeypatch.setattr(ao, "OpenAIChatCompletionClient", fake)
    monkeypatch.setattr(mp, "_FORCE", False)
    monkeypatch.setattr(mp, "_MODEL", "M")
    mp._patch_autogen()
    assert fake().kw["model"] == "M"
    assert fake(model="x").kw == {"model": "x"}
    monkeypatch.setattr(mp, "_FORCE", True)
    assert fake(model="x").kw["model"] == "M"
    mp._patch_autogen()


def test_patch_autogen_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import autogen_ext.models.openai as ao

    monkeypatch.delattr(ao, "OpenAIChatCompletionClient")
    mp._patch_autogen()


def test_patch_llamaindex(monkeypatch: pytest.MonkeyPatch) -> None:
    import llama_index.llms.openai as lo

    fake = _prep_fake()
    monkeypatch.setattr(lo, "OpenAI", fake)
    monkeypatch.setattr(mp, "_FORCE", False)
    monkeypatch.setattr(mp, "_MODEL", "M")
    mp._patch_llamaindex()
    assert fake().kw["model"] == "M"
    assert fake(model="x").kw == {"model": "x"}
    monkeypatch.setattr(mp, "_FORCE", True)
    assert fake(model="x").kw["model"] == "M"
    mp._patch_llamaindex()


def test_patch_llamaindex_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import llama_index.llms.openai as lo

    monkeypatch.delattr(lo, "OpenAI")
    mp._patch_llamaindex()


def test_patch_adk(monkeypatch: pytest.MonkeyPatch) -> None:
    import google.adk.models.lite_llm as ll

    fake = _prep_fake()
    monkeypatch.setattr(ll, "LiteLlm", fake)
    monkeypatch.setattr(mp, "_FORCE", False)
    monkeypatch.setattr(mp, "_MODEL", "M")
    mp._patch_adk()
    assert fake().kw["model"] == "M"
    assert fake(model="x").kw == {"model": "x"}
    monkeypatch.setattr(mp, "_FORCE", True)
    assert fake(model="x").kw["model"] == "M"
    mp._patch_adk()


def test_patch_adk_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import google.adk.models.lite_llm as ll

    monkeypatch.delattr(ll, "LiteLlm")
    mp._patch_adk()


def test_patch_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    import claude_agent_sdk
    import claude_agent_sdk.client as cc

    class _Opts:
        def __init__(self, *a: Any, **kw: Any) -> None:
            self.kw = kw
            self.model = kw.get("model")

    class _Client:
        def __init__(self, *a: Any, **kw: Any) -> None:
            self.kw = kw

    monkeypatch.setattr(claude_agent_sdk, "ClaudeAgentOptions", _Opts)
    monkeypatch.setattr(cc, "ClaudeSDKClient", _Client)
    monkeypatch.setattr(mp, "_FORCE", False)
    monkeypatch.setattr(mp, "_MODEL", "M")
    mp._patch_claude()
    opt = _Opts(model="orig")
    _Client(options=opt)  # force False -> unchanged
    assert opt.model == "orig"
    assert "options" not in _Client().kw
    # force True
    monkeypatch.setattr(mp, "_FORCE", True)
    opt2 = _Opts(model="orig")
    _Client(options=opt2)
    assert opt2.model == "M"
    assert _Client().kw["options"].model == "M"
    mp._patch_claude()


def test_patch_claude_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import claude_agent_sdk

    monkeypatch.delattr(claude_agent_sdk, "ClaudeAgentOptions")
    mp._patch_claude()


def test_apply_model_patch_sets_env(monkeypatch: pytest.MonkeyPatch) -> None:
    mp.apply_model_patch()
    assert mp.apply_model_patch() is None


# --------------------------------------------------------------------------- #
# http.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import http as http_mod  # noqa: E402
from agentdrill.adapters.http import HttpAdapter, _check_egress, _parse_hostnames  # noqa: E402


class _Egress:
    def __init__(self, allow: bool = True) -> None:
        self.allow = allow
        self.logged: list[tuple[str, str, str]] = []

    def check_request(self, method: str, url: str, headers: Any) -> tuple[bool, str]:
        return (self.allow, "policy says no")

    def log_request(self, method: str, url: str, status: str) -> None:
        self.logged.append((method, url, status))


class _Resp:
    def __init__(self, status: int = 200, text: str = "") -> None:
        self.status_code = status
        self.text = text


def test_parse_hostnames() -> None:
    hosts = _parse_hostnames({"http://a.com:80/x", "not a url", "http://b.com"})
    assert hosts == {"a.com", "b.com"}


def test_check_egress_allowed_and_blocked() -> None:
    ok = _Egress(allow=True)
    _check_egress("http://x", ok)
    assert ok.logged == [("POST", "http://x", "allowed")]
    blocked = _Egress(allow=False)
    with pytest.raises(AdapterError):
        _check_egress("http://x", blocked)
    assert blocked.logged == [("POST", "http://x", "blocked")]


def test_http_missing_url() -> None:
    art = HttpAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "url" in (art.error or "")


def test_http_egress_blocked() -> None:
    art = HttpAdapter().run(
        _scenario(), {"url": "http://x", "run_id": "r", "egress_controller": _Egress(False)}
    )
    assert art.status == "error"


def test_http_egress_allowed_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    egress = _Egress(True)
    monkeypatch.setattr(
        http_mod.httpx,
        "post",
        lambda *a, **k: _Resp(200, '{"status": "completed", "output": {"final": "ok"}}'),
    )
    art = HttpAdapter().run(
        _scenario(), {"url": "http://x", "run_id": "r", "egress_controller": egress}
    )
    assert art.status == "completed"
    assert egress.logged[-1] == ("POST", "http://x", "allowed")


def test_http_sandbox_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(http_mod.httpx, "post", lambda *a, **k: _Resp())
    with pytest.raises(AdapterError):
        HttpAdapter()._invoke(
            {},
            {
                "url": "http://evil.com/x",
                "sandbox": True,
                "sandbox_denied_urls": {"http://evil.com"},
            },
        )


def test_http_sandbox_not_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(http_mod.httpx, "post", lambda *a, **k: _Resp())
    with pytest.raises(AdapterError):
        HttpAdapter()._invoke({}, {"url": "http://other.com/x", "sandbox": True})


def test_http_sandbox_bad_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(http_mod.httpx, "post", lambda *a, **k: _Resp())
    with pytest.raises(AdapterError):
        HttpAdapter()._invoke({}, {"url": "http://", "sandbox": True})


def test_http_sandbox_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(http_mod.httpx, "post", lambda *a, **k: _Resp(200, "hi"))
    out = HttpAdapter()._invoke(
        {}, {"url": "http://ok.com/x", "sandbox": True, "sandbox_allowed_urls": {"http://ok.com"}}
    )
    assert out == "hi"


def test_http_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    egress = _Egress(True)

    def _boom(*a: Any, **k: Any) -> Any:
        raise http_mod.httpx.TimeoutException("t")

    monkeypatch.setattr(http_mod.httpx, "post", _boom)
    art = HttpAdapter().run(
        _scenario(), {"url": "http://x", "run_id": "r", "egress_controller": egress}
    )
    assert art.status == "timeout"
    assert ("POST", "http://x", "timeout") in egress.logged


def test_http_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    egress = _Egress(True)

    def _boom(*a: Any, **k: Any) -> Any:
        raise http_mod.httpx.ConnectError("c")

    monkeypatch.setattr(http_mod.httpx, "post", _boom)
    art = HttpAdapter().run(
        _scenario(), {"url": "http://x", "run_id": "r", "egress_controller": egress}
    )
    assert art.status == "error"
    assert ("POST", "http://x", "error") in egress.logged


def test_http_non_200_with_egress(monkeypatch: pytest.MonkeyPatch) -> None:
    egress = _Egress(True)
    monkeypatch.setattr(http_mod.httpx, "post", lambda *a, **k: _Resp(503, "nope"))
    art = HttpAdapter().run(
        _scenario(), {"url": "http://x", "run_id": "r", "egress_controller": egress}
    )
    assert art.status == "error"
    assert ("POST", "http://x", "status_503") in egress.logged


# --------------------------------------------------------------------------- #
# subprocess_runner.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import subprocess_runner as sr  # noqa: E402


class _CP:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_find_agentdrill_path() -> None:
    assert isinstance(sr._find_agentdrill_path(), str)


def test_subprocess_runner_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sr, "run_in_container", lambda *a, **k: _CP(0, "OUT"))
    out = sr.run_agent_in_subprocess(
        {"a": 1}, ["echo"], {"container_runtime": "docker", "timeout_seconds": 5}
    )
    assert out == "OUT"


def test_subprocess_runner_docker_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sr, "run_in_container", lambda *a, **k: _CP(1, "", "boom"))
    with pytest.raises(AdapterError):
        sr.run_agent_in_subprocess({}, ["echo"], {"container_runtime": "docker"})


def test_subprocess_runner_fixtures_env(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def _fake(**kw: Any) -> _CP:
        captured.update(kw)
        return _CP(0, "ok")

    monkeypatch.setattr(sr, "sandboxed_run", _fake)
    out = sr.run_agent_in_subprocess(
        {},
        ["echo"],
        {"fixtures": True, "fixtures_dir": "d", "env": {"PYTHONPATH": "/x"}},
    )
    assert out == "ok"
    assert captured["env"]["AGENTDRILL_FIXTURES"] == "1"
    assert captured["env"]["AGENTDRILL_FIXTURES_DIR"] == "d"
    assert "/x" in captured["env"]["PYTHONPATH"]


def test_subprocess_runner_fixtures_no_existing_pythonpath(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(sr, "sandboxed_run", lambda **kw: (captured.update(kw), _CP(0, "ok"))[1])
    sr.run_agent_in_subprocess({}, ["echo"], {"fixtures": True})
    assert ":" not in captured["env"]["PYTHONPATH"]


# --------------------------------------------------------------------------- #
# isolated.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import isolated as iso  # noqa: E402
from agentdrill.adapters.isolated import IsolatedAdapter, _run_worker  # noqa: E402


def test_isolated_unsupported_adapter_type() -> None:
    art = IsolatedAdapter().run(_scenario(), {"adapter_type": "nope", "module": "m", "run_id": "r"})
    assert art.status == "error"
    assert "unsupported" in (art.error or "")


def test_isolated_run_worker_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iso, "sandboxed_run", lambda **kw: (_ for _ in ()).throw(OSError("no")))
    with pytest.raises(AdapterError):
        _run_worker(["x"], {}, 1.0, {})


def test_isolated_run_worker_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iso, "sandboxed_run", lambda **kw: _CP(2, "", "err"))
    with pytest.raises(AdapterError):
        _run_worker(["x"], {}, 1.0, {})


def test_isolated_run_worker_no_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iso, "sandboxed_run", lambda **kw: _CP(0, "  "))
    with pytest.raises(AdapterError):
        _run_worker(["x"], {}, 1.0, {})


def test_isolated_run_worker_bad_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iso, "sandboxed_run", lambda **kw: _CP(0, "not json"))
    with pytest.raises(AdapterError):
        _run_worker(["x"], {}, 1.0, {})


def test_isolated_run_worker_non_object(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iso, "sandboxed_run", lambda **kw: _CP(0, "[1, 2]"))
    with pytest.raises(AdapterError):
        _run_worker(["x"], {}, 1.0, {})


def test_isolated_run_worker_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iso, "sandboxed_run", lambda **kw: _CP(0, '{"status": "completed"}'))
    assert _run_worker(["x"], {}, 1.0, {}) == {"status": "completed"}


# --------------------------------------------------------------------------- #
# python_import.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import python_import as pi  # noqa: E402
from agentdrill.adapters.python_import import PythonImportAdapter, _agent_worker  # noqa: E402


class _Queue:
    def __init__(self, items: list | None = None, raise_get: bool = False) -> None:
        self.items = list(items or [])
        self.raise_get = raise_get

    def put(self, item: Any) -> None:
        self.items.append(item)

    def get(self, timeout: float | None = None) -> Any:
        if self.raise_get or not self.items:
            raise RuntimeError("empty")
        return self.items.pop(0)


def test_agent_worker_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, "cov_pi_mod", run=lambda p: {"status": "completed"})
    q = _Queue()
    _agent_worker("cov_pi_mod", "run", {}, q)
    assert q.items[0] == ("ok", {"status": "completed"})


def test_agent_worker_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(_p: Any) -> Any:
        raise ValueError("bad")

    _install(monkeypatch, "cov_pi_mod2", run=_boom)
    q = _Queue()
    _agent_worker("cov_pi_mod2", "run", {}, q)
    assert q.items[0][0] == "error"
    assert "ValueError" in q.items[0][1]


def test_agent_worker_fixture_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    def _run(p: dict) -> dict:
        return {"has_stub": p.get("_tool_stub") is not None}

    _install(monkeypatch, "cov_pi_mod3", run=_run)
    q = _Queue()
    _agent_worker("cov_pi_mod3", "run", {"_fixture_mode": True, "_fixtures_dir": str(tmp_path)}, q)
    assert q.items[0][1]["has_stub"] is True


def test_python_import_manifest() -> None:
    m = PythonImportAdapter().get_manifest()
    assert m["name"] == "python_import"


def test_python_import_missing_module() -> None:
    art = PythonImportAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_python_import_sandbox(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sr,
        "run_agent_in_subprocess",
        lambda *a, **k: '{"status": "completed", "output": {"final": "sandboxed"}}',
    )
    art = PythonImportAdapter().run(_scenario(), {"module": "m", "run_id": "r", "sandbox": True})
    assert art.status == "completed"
    assert art.output.final == "sandboxed"


def test_python_import_process_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Boom:
        def __init__(self, *a: Any, **k: Any) -> None:
            raise pi.multiprocessing.ProcessError("boom")

    monkeypatch.setattr(pi.multiprocessing, "Process", _Boom)
    art = PythonImportAdapter().run(
        _scenario(), {"module": "fixtures.agents", "function": "run", "run_id": "r"}
    )
    assert art.status == "error"


def test_python_import_queue_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Proc:
        exitcode = 0

        def __init__(self, *a: Any, **k: Any) -> None:
            pass

        def start(self) -> None:
            pass

        def join(self, timeout: float | None = None) -> None:
            pass

        def is_alive(self) -> bool:
            return False

        def terminate(self) -> None:
            pass

    monkeypatch.setattr(pi.multiprocessing, "Process", _Proc)
    monkeypatch.setattr(pi.multiprocessing, "Queue", lambda: _Queue(raise_get=True))
    art = PythonImportAdapter().run(
        _scenario(), {"module": "fixtures.agents", "function": "run", "run_id": "r"}
    )
    assert art.status == "error"
    assert "no result" in (art.error or "")


@pytest.mark.parametrize(
    ("ret", "expect_status", "expect_final"),
    [
        ({"status": "completed", "output": {"final": "d"}}, "completed", "d"),
        ("raw text", "completed", "raw text"),
    ],
)
def test_python_import_result_shapes(
    monkeypatch: pytest.MonkeyPatch, ret: Any, expect_status: str, expect_final: str
) -> None:
    class _Proc:
        exitcode = 0

        def __init__(self, *a: Any, **k: Any) -> None:
            self._args = k.get("args") or (a[0] if a else ())

        def start(self) -> None:
            pass

        def join(self, timeout: float | None = None) -> None:
            pass

        def is_alive(self) -> bool:
            return False

        def terminate(self) -> None:
            pass

    monkeypatch.setattr(pi.multiprocessing, "Process", _Proc)
    monkeypatch.setattr(pi.multiprocessing, "Queue", lambda: _Queue([("ok", ret)]))
    art = PythonImportAdapter().run(
        _scenario(), {"module": "fixtures.agents", "function": "run", "run_id": "r"}
    )
    assert art.status == expect_status
    assert art.output.final == expect_final


def test_python_import_unexpected_type(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Proc:
        exitcode = 0

        def __init__(self, *a: Any, **k: Any) -> None:
            pass

        def start(self) -> None:
            pass

        def join(self, timeout: float | None = None) -> None:
            pass

        def is_alive(self) -> bool:
            return False

        def terminate(self) -> None:
            pass

    monkeypatch.setattr(pi.multiprocessing, "Process", _Proc)
    monkeypatch.setattr(pi.multiprocessing, "Queue", lambda: _Queue([("ok", 123)]))
    art = PythonImportAdapter().run(
        _scenario(), {"module": "fixtures.agents", "function": "run", "run_id": "r"}
    )
    assert art.status == "error"
    assert "unexpected type" in (art.error or "")


# --------------------------------------------------------------------------- #
# pydantic_ai.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import pydantic_ai as pa  # noqa: E402
from agentdrill.adapters.pydantic_ai import PydanticAIAdapter  # noqa: E402


class _PAResult:
    def __init__(
        self, parts: list, data: Any = None, usage: Any = None, usage_raise: bool = False
    ) -> None:
        self._parts = parts
        self.data = data
        self._usage = usage
        self._usage_raise = usage_raise

    def all_messages(self) -> list:
        return [types.SimpleNamespace(parts=self._parts)]

    def usage(self) -> Any:
        if self._usage_raise:
            raise RuntimeError("no usage")
        return self._usage


class _PAAgent:
    def __init__(self, result: Any) -> None:
        self.result = result
        self.seen: list[Any] = []

    def run_sync(self, user_input: str) -> Any:
        self.seen.append(user_input)
        return self.result


def test_pydantic_missing_module() -> None:
    art = PydanticAIAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_pydantic_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_pa_nofn")
    art = PydanticAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_pydantic_prebuilt_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = _PAAgent(_PAResult([types.SimpleNamespace(part_kind="final", content="done")]))
    name = _install(monkeypatch, "cov_pa_prebuilt", build_agent=agent)
    art = PydanticAIAdapter().run(_scenario(input_="q"), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "done"
    assert agent.seen == ["q"]


def test_pydantic_factory_with_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def build_agent(payload: dict, model: str | None = None) -> Any:
        captured["model"] = model
        captured["payload"] = payload
        return _PAAgent(_PAResult([types.SimpleNamespace(part_kind="final", content="x")]))

    name = _install(monkeypatch, "cov_pa_factory", build_agent=build_agent)
    art = PydanticAIAdapter().run(_scenario(), {"module": name, "run_id": "r", "model": "m1"})
    assert art.status == "completed"
    assert captured["model"] == "m1"


def test_pydantic_factory_no_args(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent() -> Any:
        return _PAAgent(_PAResult([types.SimpleNamespace(part_kind="final", content="x")]))

    name = _install(monkeypatch, "cov_pa_noargs", build_agent=build_agent)
    art = PydanticAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"


def test_pydantic_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent(payload: dict) -> Any:
        raise RuntimeError("nope")

    name = _install(monkeypatch, "cov_pa_fail", build_agent=build_agent)
    art = PydanticAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_pydantic_no_run_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_pa_norun", build_agent=lambda: types.SimpleNamespace())
    art = PydanticAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "run_sync" in (art.error or "")


def test_pydantic_cost_paths() -> None:
    assert pa._extract_cost(types.SimpleNamespace()) is None
    assert pa._extract_cost(_PAResult([], usage_raise=True)) is None
    assert pa._extract_cost(_PAResult([], usage=None)) is None
    cost = pa._extract_cost(
        _PAResult(
            [], usage=types.SimpleNamespace(request_tokens=1, response_tokens=2, total_tokens=3)
        )
    )
    assert cost is not None and cost["total_tokens"] == 3


def test_pydantic_part_kind_variants() -> None:
    assert pa._get_part_kind(types.SimpleNamespace(part_kind="final")) == "final"
    assert pa._get_part_kind(types.SimpleNamespace(kind="text")) == "text"
    assert pa._get_part_kind(types.SimpleNamespace(kind=lambda: "callable")) == "callable"

    def _boom() -> str:
        raise RuntimeError("x")

    assert pa._get_part_kind(types.SimpleNamespace(kind=_boom)) == ""
    assert pa._get_part_kind(types.SimpleNamespace()) == ""


def test_pydantic_trajectory_and_synthetic_tool_call() -> None:
    parts = [
        types.SimpleNamespace(part_kind="tool-return", tool_name="t1", content="r"),
    ]
    steps, final = pa._extract_trajectory([types.SimpleNamespace(parts=parts)])
    assert final is None
    pa._ensure_tool_call_steps(steps)
    assert [s["type"] for s in steps] == ["tool_call", "tool_result"]


def test_pydantic_trajectory_skips_empty_parts() -> None:
    steps, final = pa._extract_trajectory([types.SimpleNamespace(parts=[])])
    assert steps == [] and final is None


def test_pydantic_structured_dict_output(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = _PAAgent(_PAResult([], data={"a": 1}))
    name = _install(monkeypatch, "cov_pa_struct", build_agent=agent)
    art = PydanticAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.structured == {"a": 1}


# --------------------------------------------------------------------------- #
# openai_agents.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import openai_agents as oa  # noqa: E402
from agentdrill.adapters.openai_agents import OpenAIAgentsAdapter  # noqa: E402


class _OAResult:
    def __init__(
        self, new_items: list | None = None, final_output: Any = None, usage: Any = None
    ) -> None:
        self.new_items = new_items or []
        self.final_output = final_output
        self.usage = usage


class _OAAgent:
    def __init__(self, result: Any = None) -> None:
        self.result = result

    def run_sync(self, user_input: str) -> Any:
        return self.result


def test_oa_missing_module() -> None:
    art = OpenAIAgentsAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_oa_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_oa_nofn")
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_oa_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def build_agent(payload: dict, model: str | None = None) -> Any:
        captured["model"] = model
        return _OAAgent(_OAResult(final_output="ok"))

    name = _install(monkeypatch, "cov_oa_model", build_agent=build_agent)
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": name, "run_id": "r", "model": "m"})
    assert art.status == "completed"
    assert captured["model"] == "m"


def test_oa_prebuilt_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(
        monkeypatch, "cov_oa_prebuilt", build_agent=_OAAgent(_OAResult(final_output="hi"))
    )
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "hi"


def test_oa_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent(payload: dict) -> Any:
        raise RuntimeError("x")

    name = _install(monkeypatch, "cov_oa_fail", build_agent=build_agent)
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_oa_runner_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Runner:
        @staticmethod
        def run_sync(agent: Any, inp: str) -> Any:
            return _OAResult(final_output="via-runner")

    _install(monkeypatch, "agents", Runner=_Runner)
    name = _install(monkeypatch, "cov_oa_runner", build_agent=lambda: types.SimpleNamespace())
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "via-runner"


def test_oa_runner_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "agents", None)
    name = _install(monkeypatch, "cov_oa_noagents", build_agent=lambda: types.SimpleNamespace())
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "install" in (art.error or "")


def test_oa_runner_invocation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Runner:
        @staticmethod
        def run_sync(agent: Any, inp: str) -> Any:
            raise RuntimeError("nope")

    _install(monkeypatch, "agents", Runner=_Runner)
    name = _install(monkeypatch, "cov_oa_runerr", build_agent=lambda: types.SimpleNamespace())
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "invocation failed" in (art.error or "")


def test_oa_extract_output_message_fallback() -> None:
    item = types.SimpleNamespace(type="message", text="from-item")
    final, structured = oa._extract_output(_OAResult(new_items=[item]))
    assert final == "from-item"
    assert structured is None


def test_oa_extract_output_dict() -> None:
    _final, structured = oa._extract_output(_OAResult(final_output={"a": 1}))
    assert structured == {"a": 1}


def test_oa_extract_cost_none() -> None:
    assert oa._extract_cost(_OAResult(usage=None)) is None
    cost = oa._extract_cost(
        _OAResult(usage=types.SimpleNamespace(input_tokens=1, output_tokens=2, total_tokens=3))
    )
    assert cost is not None and cost["total_tokens"] == 3


def test_oa_parse_jsonish_failure() -> None:
    assert oa._parse_jsonish("not json") == "not json"


def test_oa_trajectory_tool_items() -> None:
    call = types.SimpleNamespace(
        type="function_call", raw_item=types.SimpleNamespace(name="t", arguments='{"a":1}')
    )
    out = types.SimpleNamespace(
        type="function_call_output", raw_item=types.SimpleNamespace(name="t", output="o")
    )
    steps = oa._extract_trajectory(_OAResult(new_items=[call, out]))
    assert [s["type"] for s in steps] == ["tool_call", "tool_result"]
    assert steps[0]["args"] == {"a": 1}


# --------------------------------------------------------------------------- #
# autogen.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import autogen as ag  # noqa: E402
from agentdrill.adapters.autogen import AutoGenAdapter  # noqa: E402


class _AGAgent:
    def __init__(self, result: Any = None) -> None:
        self.result = result

    def run(self, task: str | None = None) -> Any:
        return self.result


class _AGResult:
    def __init__(self, messages: list) -> None:
        self.messages = messages


def test_autogen_missing_module() -> None:
    art = AutoGenAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_autogen_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_ag_nofn")
    art = AutoGenAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_autogen_prebuilt_and_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    text = types.SimpleNamespace(type="TextMessage", content="hi", tool_calls=[])
    name = _install(monkeypatch, "cov_ag_prebuilt", build_agent=_AGAgent(_AGResult([text])))
    art = AutoGenAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "hi"

    def build_agent(payload: dict) -> Any:
        raise RuntimeError("x")

    name2 = _install(monkeypatch, "cov_ag_fail", build_agent=build_agent)
    art2 = AutoGenAdapter().run(_scenario(), {"module": name2, "run_id": "r"})
    assert art2.status == "error"
    assert "build_agent failed" in (art2.error or "")


def test_autogen_no_run(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_ag_norun", build_agent=lambda: types.SimpleNamespace())
    art = AutoGenAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert ".run()" in (art.error or "")


def test_autogen_run_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Boom:
        def run(self, task: str | None = None) -> Any:
            raise RuntimeError("x")

    name = _install(monkeypatch, "cov_ag_runerr", build_agent=_Boom)
    art = AutoGenAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "agent run failed" in (art.error or "")


def test_autogen_trajectory_content_lists() -> None:
    result_call = types.SimpleNamespace(name="fn", arguments='{"x": 1}')
    result_out = types.SimpleNamespace(call_id="1", name="fn", content="res")
    event1 = types.SimpleNamespace(
        type="ToolCallRequestEvent", content=[result_call], tool_calls=[]
    )
    event2 = types.SimpleNamespace(
        type="ToolCallExecutionEvent", content=[result_out], tool_calls=[]
    )
    steps = ag._extract_trajectory([event1, event2])
    assert [s["type"] for s in steps] == ["tool_call", "tool_result"]


def test_autogen_trajectory_summary_fallback() -> None:
    summary = types.SimpleNamespace(
        type="ToolCallSummaryMessage", content="summary text", tool_calls=[], results=[]
    )
    steps = ag._extract_trajectory([summary])
    assert steps[-1]["type"] == "response"
    assert steps[-1]["content"] == "summary text"


def test_autogen_trajectory_summary_with_calls() -> None:
    call = types.SimpleNamespace(name="t", arguments='{"a": 1}')
    res = types.SimpleNamespace(content='{"ok": true}')
    summary = types.SimpleNamespace(
        type="ToolCallSummaryMessage", content="s", tool_calls=[call], results=[res]
    )
    steps = ag._extract_trajectory([summary])
    assert steps[0]["type"] == "tool_call"
    assert steps[0]["args"] == {"a": 1}
    assert steps[1]["type"] == "tool_result"
    assert steps[1]["result"] == {"ok": True}


def test_autogen_extract_output_fallback() -> None:
    steps = [{"type": "response", "content": "from-step"}]
    final, structured = ag._extract_output([types.SimpleNamespace(type="Other")], steps)
    assert final == "from-step"
    assert structured is None


def test_autogen_extract_cost_none() -> None:
    assert ag._extract_cost([types.SimpleNamespace(type="X")]) is None
    cost = ag._extract_cost(
        [
            types.SimpleNamespace(
                models_usage=types.SimpleNamespace(prompt_tokens=1, completion_tokens=2)
            )
        ]
    )
    assert cost is not None and cost["total_tokens"] == 3


def test_autogen_parse_jsonish_failure() -> None:
    assert ag._parse_jsonish("nope") == "nope"


# --------------------------------------------------------------------------- #
# crewai.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import crewai as ca  # noqa: E402
from agentdrill.adapters.crewai import CrewAIAdapter  # noqa: E402


class _Crew:
    def __init__(self, result: Any = None) -> None:
        self.result = result
        self.inputs: dict[str, Any] = {}

    def kickoff(self, inputs: dict | None = None) -> Any:
        self.inputs = dict(inputs or {})
        return self.result


class _CrewResult:
    def __init__(
        self, raw: Any = None, tasks_output: list | None = None, token_usage: Any = None
    ) -> None:
        self.raw = raw
        self.tasks_output = tasks_output or []
        self.token_usage = token_usage


def test_crewai_missing_module() -> None:
    art = CrewAIAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_crewai_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_ca_nofn")
    art = CrewAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_crewai_model_override_and_prebuilt(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def build_agent(payload: dict, model: str | None = None) -> Any:
        captured["model"] = model
        return _Crew(_CrewResult(raw="done"))

    name = _install(monkeypatch, "cov_ca_model", build_agent=build_agent)
    art = CrewAIAdapter().run(_scenario(), {"module": name, "run_id": "r", "model": "m"})
    assert art.status == "completed"
    assert captured["model"] == "m"

    name2 = _install(monkeypatch, "cov_ca_prebuilt", build_agent=_Crew(_CrewResult(raw="pre")))
    art2 = CrewAIAdapter().run(_scenario(), {"module": name2, "run_id": "r"})
    assert art2.output.final == "pre"


def test_crewai_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent(payload: dict) -> Any:
        raise RuntimeError("x")

    name = _install(monkeypatch, "cov_ca_fail", build_agent=build_agent)
    art = CrewAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_crewai_no_kickoff(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_ca_nokick", build_agent=lambda: types.SimpleNamespace())
    art = CrewAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "kickoff" in (art.error or "")


def test_crewai_inputs_and_kickoff_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    crew = _Crew(_CrewResult(raw="ok"))
    name = _install(monkeypatch, "cov_ca_inputs", build_agent=crew)
    CrewAIAdapter().run(
        _scenario(input_="q"),
        {"module": name, "run_id": "r", "inputs": {"extra": 1, "input": "override"}},
    )
    assert crew.inputs == {"input": "override", "extra": 1}

    class _Boom:
        def kickoff(self, inputs: dict | None = None) -> Any:
            raise RuntimeError("x")

    name2 = _install(monkeypatch, "cov_ca_boom", build_agent=_Boom)
    art = CrewAIAdapter().run(_scenario(), {"module": name2, "run_id": "r"})
    assert art.status == "error"
    assert "kickoff failed" in (art.error or "")


def test_crewai_structured_non_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _CrewResult(raw="r")
    result.json_dict = "not-a-dict"  # type: ignore[attr-defined]
    name = _install(monkeypatch, "cov_ca_struct", build_agent=_Crew(result))
    art = CrewAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.structured is None


def test_crewai_trajectory_and_cost() -> None:
    msg_assistant = {
        "role": "assistant",
        "tool_calls": [{"function": {"name": "t", "arguments": '{"a": 1}'}}],
    }
    msg_tool = {"role": "tool", "name": "t", "content": "out"}
    result = _CrewResult(
        raw="final", tasks_output=[types.SimpleNamespace(messages=[msg_assistant, msg_tool])]
    )
    steps, final = ca._extract_trajectory(result)
    assert [s["type"] for s in steps] == ["tool_call", "tool_result", "response"]
    assert final == "final"
    assert ca._extract_cost(_CrewResult(token_usage=None)) is None
    assert ca._parse_jsonish("nope") == "nope"


def test_crewai_trajectory_object_messages() -> None:
    # object tool_calls inside a dict assistant message
    fn = types.SimpleNamespace(name="t", arguments='{"a": 1}')
    tc = types.SimpleNamespace(function=fn)
    msg_assistant = {"role": "assistant", "tool_calls": [tc]}
    result = _CrewResult(
        raw="final", tasks_output=[types.SimpleNamespace(messages=[msg_assistant])]
    )
    steps, final = ca._extract_trajectory(result)
    assert steps[0]["tool"] == "t"
    assert final == "final"
    # object tool message (non-dict) exercises the getattr branch
    msg_tool = types.SimpleNamespace(role="tool", name="t", content="out")
    result2 = _CrewResult(raw="final", tasks_output=[types.SimpleNamespace(messages=[msg_tool])])
    steps2, _ = ca._extract_trajectory(result2)
    assert steps2[0]["type"] == "tool_result"
    assert steps2[0]["result"] == "out"


# --------------------------------------------------------------------------- #
# langgraph.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import langgraph as lg  # noqa: E402
from agentdrill.adapters.langgraph import LangGraphAdapter  # noqa: E402


class _LGAgent:
    def __init__(self, result: Any = None) -> None:
        self.result = result
        self.calls: list[Any] = []

    def invoke(self, state: Any, config: Any = None) -> Any:
        self.calls.append((state, config))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def test_langgraph_missing_module(monkeypatch: pytest.MonkeyPatch) -> None:
    # neutralize ChatOpenAI patching so it never touches the real class
    import langchain_openai

    monkeypatch.setattr(langchain_openai, "ChatOpenAI", _prep_fake())
    art = LangGraphAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_langgraph_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_lg_nofn")
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_langgraph_prebuilt_invoke(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = _LGAgent(
        {"messages": [types.SimpleNamespace(type="ai", content="hi", tool_calls=None)]}
    )
    name = _install(monkeypatch, "cov_lg_prebuilt", build_agent=agent)
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "hi"


def test_langgraph_compile_path(monkeypatch: pytest.MonkeyPatch) -> None:
    compiled = _LGAgent(
        {"messages": [types.SimpleNamespace(type="ai", content="c", tool_calls=None)]}
    )

    class _Uncompiled:
        def compile(self, checkpointer: Any = None) -> Any:
            compiled.checkpointer = checkpointer
            return compiled

    name = _install(monkeypatch, "cov_lg_compile", build_agent=lambda: _Uncompiled())
    art = LangGraphAdapter().run(
        _scenario(), {"module": name, "run_id": "r", "checkpointer": "memory"}
    )
    assert art.status == "completed"
    assert compiled.checkpointer is not None


def test_langgraph_compile_no_checkpointer(monkeypatch: pytest.MonkeyPatch) -> None:
    compiled = _LGAgent(
        {"messages": [types.SimpleNamespace(type="ai", content="c", tool_calls=None)]}
    )

    class _Uncompiled:
        def compile(self, checkpointer: Any = None) -> Any:
            return compiled

    name = _install(monkeypatch, "cov_lg_compile2", build_agent=lambda: _Uncompiled())
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"


def test_langgraph_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent() -> Any:
        raise RuntimeError("x")

    name = _install(monkeypatch, "cov_lg_fail", build_agent=build_agent)
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_langgraph_no_invoke(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_lg_noinvoke", build_agent=lambda: types.SimpleNamespace())
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert ".invoke()" in (art.error or "")


def test_langgraph_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}
    agent = _LGAgent({"messages": [types.SimpleNamespace(type="ai", content="x", tool_calls=None)]})

    def build_agent(payload: dict, model: str | None = None) -> Any:
        captured["model"] = model
        return agent

    name = _install(monkeypatch, "cov_lg_cfg", build_agent=build_agent)
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r", "model": "m"})
    assert art.status == "completed"
    assert captured["model"] == "m"
    _, invoke_config = agent.calls[0]
    assert "configurable" in invoke_config


def test_langgraph_invoke_config_merging(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = _LGAgent({"messages": [types.SimpleNamespace(type="ai", content="c", tool_calls=None)]})
    name = _install(monkeypatch, "cov_lg_merge", build_agent=agent)
    config = {
        "module": name,
        "run_id": "r",
        "callbacks": ["cb"],
        "interrupt_before": ["n"],
        "invoke_config": {"thread_id": "t"},
    }
    art = LangGraphAdapter().run(_scenario(), config)
    assert art.status == "completed"
    _, invoke_config = agent.calls[0]
    assert invoke_config["callbacks"] == ["cb"]
    assert invoke_config["interrupt_before"] == ["n"]
    assert invoke_config["thread_id"] == "t"


def test_langgraph_invocation_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = _LGAgent(RuntimeError("x"))
    name = _install(monkeypatch, "cov_lg_inverr", build_agent=agent)
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "invocation failed" in (art.error or "")


def test_langgraph_result_missing_messages(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = _LGAgent({"other": []})
    name = _install(monkeypatch, "cov_lg_nomsg", build_agent=agent)
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "messages" in (art.error or "")


def test_langgraph_extract_trajectory_tools() -> None:
    tool_msg = types.SimpleNamespace(
        type="tool", name="t", content="r", tool_calls=None, tool_call_id="1"
    )
    ai_msg = types.SimpleNamespace(
        type="ai", content="final", tool_calls=[{"name": "t", "args": {"a": 1}}]
    )
    ai_plain = types.SimpleNamespace(type="ai", content="final", tool_calls=None)
    steps, final = lg._extract_trajectory([ai_msg, tool_msg, ai_plain])
    assert [s["type"] for s in steps] == ["tool_call", "tool_result", "response"]
    assert final == "final"


# --------------------------------------------------------------------------- #
# smolagents.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import smolagents as sm  # noqa: E402
from agentdrill.adapters.smolagents import SmolagentsAdapter  # noqa: E402


class _SmolAgent:
    def __init__(
        self, result: Any = None, raise_type: bool = False, raise_exc: bool = False
    ) -> None:
        self.result = result
        self.raise_type = raise_type
        self.raise_exc = raise_exc

    def run(self, *args: Any, **kw: Any) -> Any:
        if self.raise_exc:
            raise ValueError("x")
        if self.raise_type and kw:
            raise TypeError("no kw")
        return self.result


def test_smol_missing_module() -> None:
    art = SmolagentsAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_smol_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_smol_nofn")
    art = SmolagentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_smol_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent(payload: dict) -> Any:
        raise RuntimeError("x")

    name = _install(monkeypatch, "cov_smol_fail", build_agent=build_agent)
    art = SmolagentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_smol_no_run(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_smol_norun", build_agent=lambda: types.SimpleNamespace())
    art = SmolagentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert ".run()" in (art.error or "")


def test_smol_typeerror_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    result = types.SimpleNamespace(output="fallback")
    agent = _SmolAgent(result=result, raise_type=True)
    name = _install(monkeypatch, "cov_smol_type", build_agent=agent)
    art = SmolagentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "fallback"


def test_smol_run_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = _SmolAgent(raise_exc=True)
    name = _install(monkeypatch, "cov_smol_exc", build_agent=agent)
    art = SmolagentsAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "agent run failed" in (art.error or "")


def test_smol_get_helper_dict() -> None:
    assert sm._get({"a": 1}, "a") == 1
    assert sm._get({"a": 1}, "b", "d") == "d"
    assert sm._get(types.SimpleNamespace(a=1), "a") == 1


def test_smol_parse_code_action_tools() -> None:
    calls = sm._parse_code_action_tools(
        "get_weather(city='London')\nlen(x)\nobj.method(a=1)\nfn(y)"
    )
    names = [c[0] for c in calls]
    assert "get_weather" in names
    assert "method" in names
    assert "len" not in names
    assert sm._parse_code_action_tools("def (") == []
    assert sm._parse_code_action_tools("") == []
    assert sm._parse_code_action_tools(123) == []
    # non-literal keyword value
    calls2 = sm._parse_code_action_tools("f(a=unknown())")
    assert calls2[0][1]["a"] is None


def test_smol_trajectory_memory_fallback() -> None:
    step = types.SimpleNamespace(
        tool_calls=[{"function": {"name": "t", "arguments": '{"a": 1}'}}], observations="obs"
    )
    memory = types.SimpleNamespace(get_full_steps=lambda: [step])
    result = types.SimpleNamespace(memory=memory)
    steps = sm._extract_trajectory(result)
    assert steps[0]["type"] == "tool_call"
    assert steps[0]["tool"] == "t"


def test_smol_trajectory_skips_task_dict() -> None:
    result = types.SimpleNamespace(steps=[{"task": "x"}])
    assert sm._extract_trajectory(result) == []


def test_smol_trajectory_code_action_branch() -> None:
    step = types.SimpleNamespace(
        code_action="get_weather(city='London')",
        action_output="15C",
        observations="obs-text",
    )
    steps = sm._extract_trajectory(types.SimpleNamespace(steps=[step]))
    types_seen = [s["type"] for s in steps]
    assert types_seen == ["tool_call", "tool_result", "response"]
    assert steps[0]["tool"] == "get_weather"


def test_smol_trajectory_observations_not_list_or_str() -> None:
    step = types.SimpleNamespace(tool_calls=[], observations=123, is_final_answer=False)
    steps = sm._extract_trajectory(types.SimpleNamespace(steps=[step]))
    assert steps == []


def test_smol_trajectory_obj_call_args_and_obs_list() -> None:
    call = types.SimpleNamespace(name="t", arguments={"a": 1})
    step = types.SimpleNamespace(tool_calls=[call], observations=["o1", None])
    steps = sm._extract_trajectory(types.SimpleNamespace(steps=[step]))
    assert steps[0]["type"] == "tool_call"
    assert steps[1]["result"] == "o1"


def test_smol_trajectory_str_observations() -> None:
    call = {"function": {"name": "t", "arguments": "notjson"}}
    step = types.SimpleNamespace(tool_calls=[call], observations="obs")
    steps = sm._extract_trajectory(types.SimpleNamespace(steps=[step]))
    assert steps[1]["result"] == "obs"


def test_smol_extract_output_variants() -> None:
    assert sm._extract_output(types.SimpleNamespace(output={"a": 1}), []) == (
        str({"a": 1}),
        {"a": 1},
    )
    assert sm._extract_output(types.SimpleNamespace(output="hi"), []) == ("hi", None)
    assert sm._extract_output(
        types.SimpleNamespace(output=types.SimpleNamespace(text="T")), []
    ) == ("T", None)
    steps = [{"type": "response", "content": "from-step"}]
    assert sm._extract_output(types.SimpleNamespace(output=None), steps) == ("from-step", None)
    assert sm._extract_output(types.SimpleNamespace(output=None), []) == (None, None)


def test_smol_extract_cost() -> None:
    assert sm._extract_cost(types.SimpleNamespace()) is None
    cost = sm._extract_cost(
        types.SimpleNamespace(token_usage=types.SimpleNamespace(input_tokens=1, output_tokens=2))
    )
    assert cost is not None and cost["total_tokens"] == 3
    cost2 = sm._extract_cost(
        types.SimpleNamespace(
            token_usage=types.SimpleNamespace(input_tokens=1, output_tokens=2, total_tokens=10)
        )
    )
    assert cost2 is not None and cost2["total_tokens"] == 10


# --------------------------------------------------------------------------- #
# llamaindex.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import llamaindex as li  # noqa: E402
from agentdrill.adapters.llamaindex import LlamaIndexAdapter  # noqa: E402


class _ChatSync:
    def __init__(self, result: Any) -> None:
        self.result = result

    def chat(self, user_msg: str) -> Any:
        return self.result


class _ChatAsync:
    def __init__(self, result: Any) -> None:
        self.result = result

    async def chat(self, user_msg: str) -> Any:
        return self.result


class _QueryAgent:
    def __init__(self, result: Any) -> None:
        self.result = result

    def query(self, user_input: str) -> Any:
        return self.result


def test_llama_missing_module() -> None:
    art = LlamaIndexAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_llama_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_li_nofn")
    art = LlamaIndexAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_llama_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent(payload: dict) -> Any:
        raise RuntimeError("x")

    name = _install(monkeypatch, "cov_li_fail", build_agent=build_agent)
    art = LlamaIndexAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_llama_invoke_agent_branches() -> None:
    out = types.SimpleNamespace(response="hi", sources=[])
    assert li._invoke_agent(_ChatSync(out), "q").response == "hi"
    assert li._invoke_agent(_ChatAsync(out), "q").response == "hi"
    assert li._invoke_agent(_QueryAgent(out), "q").response == "hi"
    with pytest.raises(AdapterError):
        li._invoke_agent(types.SimpleNamespace(), "q")


def test_llama_invoke_agent_awaitable_chat() -> None:
    async def _coro() -> Any:
        return types.SimpleNamespace(response="awaited", sources=[])

    class _AwaitableChat:
        def chat(self, user_msg: str) -> Any:
            return _coro()

    result = li._invoke_agent(_AwaitableChat(), "q")
    assert result.response == "awaited"


def test_llama_invoke_agent_run_runtimeerror_workflow() -> None:
    class _Handler:
        async def stream_events(self) -> Any:
            yield "e"

        def __await__(self) -> Any:
            async def _c() -> Any:
                return types.SimpleNamespace(response="wf", sources=[])

            return _c().__await__()

    class _RunAgent:
        def run(self, *a: Any, **kw: Any) -> Any:
            if "user_msg" in kw:
                raise RuntimeError("need loop")
            return _Handler()

    result = li._invoke_agent(_RunAgent(), "q")
    assert result.response == "wf"


def test_llama_run_workflow_context(monkeypatch: pytest.MonkeyPatch) -> None:
    import llama_index.core.workflow as wf

    class _Ctx:
        def __init__(self, agent: Any) -> None:
            self.agent = agent

    monkeypatch.setattr(wf, "Context", _Ctx)

    class _Handler:
        async def stream_events(self) -> Any:
            yield "e"

        def __await__(self) -> Any:
            async def _c() -> Any:
                return "done"

            return _c().__await__()

    class _Agent:
        def run(self, *a: Any, **kw: Any) -> Any:
            assert "ctx" in kw
            return _Handler()

    assert asyncio.run(li._run_workflow(_Agent(), "q")) == "done"


def test_llama_run_workflow_context_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import llama_index.core.workflow as wf

    monkeypatch.delattr(wf, "Context")

    class _Handler:
        async def stream_events(self) -> Any:
            yield "e"

        def __await__(self) -> Any:
            async def _c() -> Any:
                return "done"

            return _c().__await__()

    class _Agent:
        def run(self, *a: Any, **kw: Any) -> Any:
            assert "ctx" not in kw
            return _Handler()

    assert asyncio.run(li._run_workflow(_Agent(), "q")) == "done"


def test_llama_extract_output_variants() -> None:
    result = types.SimpleNamespace(response='{"a": 1}', sources=[])
    text, structured = li._extract_output(result, [])
    assert text == '{"a": 1}' and structured == {"a": 1}
    result2 = types.SimpleNamespace(response="plain", sources=[])
    assert li._extract_output(result2, []) == ("plain", None)
    steps = [{"type": "response", "content": "step"}]
    assert li._extract_output(types.SimpleNamespace(response=None, sources=[]), steps) == (
        "step",
        None,
    )
    assert li._extract_output(types.SimpleNamespace(response=None, sources=[]), []) == (None, None)


def test_llama_extract_trajectory_and_final_append() -> None:
    source = types.SimpleNamespace(tool_name="t", raw_input={"a": 1}, raw_output="r")
    result = types.SimpleNamespace(response="done", sources=[source])
    steps = li._extract_trajectory(result)
    assert [s["type"] for s in steps] == ["tool_call", "tool_result"]
    assert steps[1]["result"] == "r"


def test_llama_parse_jsonish_failure() -> None:
    assert li._parse_jsonish("nope") == "nope"


def test_llama_adapter_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    source = types.SimpleNamespace(tool_name="t", raw_input={"a": 1}, raw_output="r")
    result = types.SimpleNamespace(response="done", sources=[source])
    name = _install(monkeypatch, "cov_li_e2e", build_agent=lambda: _ChatSync(result))
    art = LlamaIndexAdapter().run(_scenario(input_="q"), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "done"


# --------------------------------------------------------------------------- #
# claude.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import claude as cl  # noqa: E402
from agentdrill.adapters.claude import ClaudeAgentSDKAdapter  # noqa: E402


class _ClaudeClient:
    def __init__(self, messages: list) -> None:
        self.messages = messages
        self.prompt: str | None = None

    async def query(self, prompt: str) -> None:
        self.prompt = prompt

    async def receive_response(self) -> Any:
        for m in self.messages:
            yield m


class _ClaudeRunClient:
    def __init__(self, result: Any) -> None:
        self.result = result

    def run(self, prompt: str) -> Any:
        return self.result


def test_claude_missing_module() -> None:
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_claude_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_cl_nofn")
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_claude_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent(payload: dict) -> Any:
        raise RuntimeError("x")

    name = _install(monkeypatch, "cov_cl_fail", build_agent=build_agent)
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_claude_no_query_or_run(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_cl_nomethods", build_agent=lambda: types.SimpleNamespace())
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert ".query()" in (art.error or "")


def test_claude_run_client_query_and_run() -> None:
    msg = types.SimpleNamespace(content=[])
    client = _ClaudeClient([msg])
    messages = asyncio.run(cl._run_client(client, "p"))
    assert messages == [msg]
    assert asyncio.run(cl._run_client(_ClaudeRunClient([msg]), "p")) == [msg]
    assert asyncio.run(cl._run_client(_ClaudeRunClient(msg), "p")) == [msg]

    class _CoroutineRun:
        def run(self, prompt: str) -> Any:
            async def _c() -> Any:
                return [msg]

            return _c()

    assert asyncio.run(cl._run_client(_CoroutineRun(), "p")) == [msg]


def test_claude_run_client_error() -> None:
    with pytest.raises(AdapterError):
        asyncio.run(cl._run_client(types.SimpleNamespace(), "p"))


def test_claude_extract_output_result_message() -> None:
    result_msg = types.SimpleNamespace(subtype="result", structured_output={"a": 1}, result="text")
    _text, structured = cl._extract_output([result_msg], [])
    assert structured == {"a": 1}
    result_msg2 = types.SimpleNamespace(subtype="result", structured_output=None, result='{"b": 2}')
    _text2, structured2 = cl._extract_output([result_msg2], [])
    assert structured2 == {"b": 2}


def test_claude_extract_output_text_fallback() -> None:
    # subtype result but no usable result -> break, then text fallback
    result_msg = types.SimpleNamespace(subtype="result", structured_output=None, result="")
    text_block = types.SimpleNamespace(type="text", text='{"c": 3}')
    msg = types.SimpleNamespace(content=[text_block])
    _text, structured = cl._extract_output([msg, result_msg], [])
    assert structured == {"c": 3}
    plain = types.SimpleNamespace(content=[types.SimpleNamespace(type="text", text="plain")])
    assert cl._extract_output([plain], []) == ("plain", None)


def test_claude_extract_trajectory_and_block_type() -> None:
    tool_use = types.SimpleNamespace(type="tool_use", name="t", id="1", input={"a": 1})
    tool_result = types.SimpleNamespace(type="tool_result", tool_use_id="1", content="r")
    msg = types.SimpleNamespace(content=[tool_use, tool_result])
    steps = cl._extract_trajectory([msg])
    assert steps[0]["type"] == "tool_call"
    assert steps[1]["result"] == "r"
    # block type inference
    assert cl._block_type(types.SimpleNamespace(text="x")) == "text"
    assert cl._block_type(types.SimpleNamespace(name="n", input={})) == "tool_use"
    assert cl._block_type(types.SimpleNamespace(tool_use_id="1")) == "tool_result"
    assert cl._block_type(types.SimpleNamespace(thinking="hmm")) == "thinking"
    assert cl._block_type(types.SimpleNamespace()) == ""


def test_claude_extract_cost() -> None:
    usage = types.SimpleNamespace(inputTokens=1, outputTokens=2, costUSD=0.5)
    msg = types.SimpleNamespace(model_usage={"m": usage})
    cost = cl._extract_cost([msg])
    assert cost is not None and cost["cost_usd"] == 0.5
    assert cl._extract_cost([types.SimpleNamespace(model_usage={})]) is None
    assert cl._extract_cost([types.SimpleNamespace(model_usage="x")]) is None
    assert cl._extract_cost([types.SimpleNamespace()]) is None


def test_claude_parse_jsonish_failure() -> None:
    assert cl._parse_jsonish("nope") == "nope"


def test_claude_adapter_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    text_block = types.SimpleNamespace(type="text", text="final answer")
    msg = types.SimpleNamespace(content=[text_block])
    name = _install(monkeypatch, "cov_cl_e2e", build_agent=lambda: _ClaudeClient([msg]))
    art = ClaudeAgentSDKAdapter().run(_scenario(input_="q"), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "final answer"


# --------------------------------------------------------------------------- #
# adk.py
# --------------------------------------------------------------------------- #
from agentdrill.adapters import adk as adk_mod  # noqa: E402
from agentdrill.adapters.adk import ADKAdapter  # noqa: E402


class _ADKEvent:
    def __init__(self, calls: list, responses: list, final: bool, content: Any = None) -> None:
        self._calls = calls
        self._responses = responses
        self._final = final
        self.content = content

    def get_function_calls(self) -> list:
        return self._calls

    def get_function_responses(self) -> list:
        return self._responses

    def is_final_response(self) -> bool:
        return self._final


class _ADKRunner:
    def __init__(self, events: list) -> None:
        self.events = events

    def run(self, user_id: str, session_id: str, new_message: str) -> list:
        return self.events


def test_adk_missing_module() -> None:
    art = ADKAdapter().run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "")


def test_adk_no_function(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_adk_nofn")
    art = ADKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "no function" in (art.error or "")


def test_adk_build_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def build_agent(payload: dict) -> Any:
        raise RuntimeError("x")

    name = _install(monkeypatch, "cov_adk_fail", build_agent=build_agent)
    art = ADKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "build_agent failed" in (art.error or "")


def test_adk_no_run(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_adk_norun", build_agent=lambda: types.SimpleNamespace())
    art = ADKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert ".run()" in (art.error or "")


def test_adk_run_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Boom:
        def run(self, **kw: Any) -> Any:
            raise RuntimeError("x")

    name = _install(monkeypatch, "cov_adk_runerr", build_agent=_Boom)
    art = ADKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "adk agent failed" in (art.error or "")


def test_adk_walk_events() -> None:
    call = types.SimpleNamespace(name="t", args={"a": 1})
    resp = types.SimpleNamespace(name="t", response="r")
    part = types.SimpleNamespace(text="final text")
    content = types.SimpleNamespace(parts=[part])
    events = [_ADKEvent([call], [resp], True, content)]
    steps, final, _structured = adk_mod._walk_events(events)
    assert steps[0]["type"] == "tool_call"
    assert steps[1]["type"] == "tool_result"
    assert final == "final text"


def test_adk_extract_event_text_none() -> None:
    assert adk_mod._extract_event_text(types.SimpleNamespace(content=None)) is None
    assert (
        adk_mod._extract_event_text(types.SimpleNamespace(content=types.SimpleNamespace(parts=[])))
        is None
    )


def test_adk_walk_events_structured_json() -> None:
    part = types.SimpleNamespace(text='{"a": 1}')
    content = types.SimpleNamespace(parts=[part])
    events = [_ADKEvent([], [], True, content)]
    _steps, _final, structured = adk_mod._walk_events(events)
    assert structured == {"a": 1}


def test_adk_adapter_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    part = types.SimpleNamespace(text="hello")
    content = types.SimpleNamespace(parts=[part])
    events = [_ADKEvent([], [], True, content)]
    name = _install(monkeypatch, "cov_adk_e2e", build_agent=lambda: _ADKRunner(events))
    art = ADKAdapter().run(_scenario(input_="q"), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "hello"


def test_adk_parse_jsonish_failure() -> None:
    assert adk_mod._parse_jsonish("nope") == "nope"


# --------------------------------------------------------------------------- #
# gap-closing tests
# --------------------------------------------------------------------------- #
def _force_import_error(monkeypatch: pytest.MonkeyPatch, module: Any) -> None:
    def _boom(_name: str) -> Any:
        raise ImportError("no module")

    monkeypatch.setattr(module.importlib, "import_module", _boom)


def test_base_parse_strict_invalid_json() -> None:
    with pytest.raises(AdapterError):
        parse_agent_stdout("not json", strict=True)


def test_base_envelope_construction_failure() -> None:
    adapter = _RawEnvelope(
        {
            "status": "completed",
            "output": {"final": "x"},
            "trajectory": {"steps": []},
            "cost": {"input_tokens": "not-an-int"},
        }
    )
    art = adapter.run(_scenario(), {"run_id": "r"})
    assert art.status == "error"


def test_base_blank_completion_inside_envelope() -> None:
    adapter = _RawEnvelope(
        {
            "status": "completed",
            "output": {"final": None, "structured": None},
            "trajectory": {"steps": []},
        }
    )
    art = adapter.run(_scenario(), {"run_id": "r"})
    assert art.status == "error"
    assert "blank completion" in (art.error or "")


def test_adk_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, adk_mod)
    art = ADKAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_adk_prebuilt_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    part = types.SimpleNamespace(text="hi")
    events = [_ADKEvent([], [], True, types.SimpleNamespace(parts=[part]))]
    name = _install(monkeypatch, "cov_adk_prebuilt", build_agent=_ADKRunner(events))
    art = ADKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"


def test_autogen_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, ag)
    art = AutoGenAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_autogen_async_run(monkeypatch: pytest.MonkeyPatch) -> None:
    text = types.SimpleNamespace(type="TextMessage", content="async", tool_calls=[])

    class _AsyncAgent:
        def run(self, task: str | None = None) -> Any:
            async def _c() -> Any:
                return _AGResult([text])

            return _c()

    name = _install(monkeypatch, "cov_ag_async", build_agent=_AsyncAgent)
    art = AutoGenAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "async"


def test_autogen_extract_output_structured() -> None:
    msg = types.SimpleNamespace(type="TextMessage", content='{"a": 1}')
    _final, structured = ag._extract_output([msg], [])
    assert structured == {"a": 1}


def test_crewai_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, ca)
    art = CrewAIAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_crewai_extract_cost_positive() -> None:
    usage = types.SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3)
    cost = ca._extract_cost(_CrewResult(token_usage=usage))
    assert cost is not None and cost["total_tokens"] == 3


def test_isolated_missing_adapter_type() -> None:
    art = IsolatedAdapter().run(_scenario(), {"module": "m", "run_id": "r"})
    assert art.status == "error"
    assert "adapter_type" in (art.error or "").lower()


def test_isolated_invoke_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        iso,
        "sandboxed_run",
        lambda **kw: _CP(0, '{"status": "completed", "output": {"final": "ok"}}'),
    )
    art = IsolatedAdapter().run(
        _scenario(), {"adapter_type": "langgraph", "module": "m", "run_id": "r"}
    )
    assert art.status == "completed"
    assert art.output.final == "ok"


def test_isolated_invoke_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess as _sp

    def _boom(**kw: Any) -> Any:
        raise _sp.TimeoutExpired("x", 1)

    monkeypatch.setattr(iso, "sandboxed_run", _boom)
    art = IsolatedAdapter().run(
        _scenario(), {"adapter_type": "langgraph", "module": "m", "run_id": "r"}
    )
    assert art.status == "timeout"


def test_langgraph_chatopenai_patch_no_force(monkeypatch: pytest.MonkeyPatch) -> None:
    import langchain_openai

    fake = _prep_fake()
    monkeypatch.setattr(langchain_openai, "ChatOpenAI", fake)
    monkeypatch.delenv("EVALFORCE_FORCE_MODEL", raising=False)
    name = _install(
        monkeypatch,
        "cov_lg_patch1",
        build_agent=_LGAgent(
            {"messages": [types.SimpleNamespace(type="ai", content="x", tool_calls=None)]}
        ),
    )
    LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert fake().kw["model"]  # default injected


def test_langgraph_chatopenai_patch_force(monkeypatch: pytest.MonkeyPatch) -> None:
    import langchain_openai

    fake = _prep_fake()
    monkeypatch.setattr(langchain_openai, "ChatOpenAI", fake)
    monkeypatch.setenv("EVALFORCE_FORCE_MODEL", "1")
    monkeypatch.setenv("AGENTDRILL_FIELD_MODEL", "FM")
    name = _install(
        monkeypatch,
        "cov_lg_patch2",
        build_agent=_LGAgent(
            {"messages": [types.SimpleNamespace(type="ai", content="x", tool_calls=None)]}
        ),
    )
    LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert fake(model_name="z").kw["model"] == "FM"


def test_langgraph_chatopenai_patch_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import langchain_openai

    monkeypatch.delattr(langchain_openai, "ChatOpenAI")
    name = _install(
        monkeypatch,
        "cov_lg_patch3",
        build_agent=_LGAgent(
            {"messages": [types.SimpleNamespace(type="ai", content="x", tool_calls=None)]}
        ),
    )
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"


def test_langgraph_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, lg)
    art = LangGraphAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_langgraph_checkpointer_import_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    import langgraph.checkpoint.memory as mem

    compiled = _LGAgent(
        {"messages": [types.SimpleNamespace(type="ai", content="x", tool_calls=None)]}
    )

    class _Uncompiled:
        def compile(self, checkpointer: Any = None) -> Any:
            assert checkpointer is None
            return compiled

    class _BoomSaver:
        def __init__(self) -> None:
            raise RuntimeError("no saver")

    monkeypatch.setattr(mem, "MemorySaver", _BoomSaver)
    name = _install(monkeypatch, "cov_lg_cperr", build_agent=lambda: _Uncompiled())
    art = LangGraphAdapter().run(
        _scenario(), {"module": name, "run_id": "r", "checkpointer": "memory"}
    )
    assert art.status == "completed"


def test_langgraph_compile_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Uncompiled:
        def compile(self, checkpointer: Any = None) -> Any:
            raise RuntimeError("compile boom")

    name = _install(monkeypatch, "cov_lg_comperr", build_agent=lambda: _Uncompiled())
    art = LangGraphAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"  # falls back to built (no invoke)


def test_llamaindex_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, li)
    art = LlamaIndexAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_llamaindex_prebuilt_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    result = types.SimpleNamespace(response="pre", sources=[])
    name = _install(monkeypatch, "cov_li_prebuilt", build_agent=_ChatSync(result))
    art = LlamaIndexAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "pre"


def test_llamaindex_invoke_agent_errors() -> None:
    # AdapterError re-raise path (agent exposes none of the methods)
    with pytest.raises(AdapterError):
        li._invoke_agent(types.SimpleNamespace(), "q")

    class _ValueErr:
        def run(self, user_msg: str) -> Any:
            raise ValueError("boom")

    with pytest.raises(ValueError):
        li._invoke_agent(_ValueErr(), "q")


def test_llamaindex_adapter_agent_error(monkeypatch: pytest.MonkeyPatch) -> None:
    name = _install(monkeypatch, "cov_li_nomethods", build_agent=lambda: types.SimpleNamespace())
    art = LlamaIndexAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"

    class _ValueErr:
        def run(self, user_msg: str) -> Any:
            raise ValueError("boom")

    name2 = _install(monkeypatch, "cov_li_valueerr", build_agent=_ValueErr)
    art2 = LlamaIndexAdapter().run(_scenario(), {"module": name2, "run_id": "r"})
    assert art2.status == "error"
    assert "agent chat failed" in (art2.error or "")


def test_llamaindex_agent_async_run_and_query_awaitable() -> None:
    class _AsyncRun:
        async def run(self, user_input: str) -> Any:
            return types.SimpleNamespace(response="ar", sources=[])

    assert li._invoke_agent(_AsyncRun(), "q").response == "ar"

    class _AwaitableQuery:
        def query(self, user_input: str) -> Any:
            async def _c() -> Any:
                return types.SimpleNamespace(response="aq", sources=[])

            return _c()

    assert li._invoke_agent(_AwaitableQuery(), "q").response == "aq"

    class _AwaitableRun:
        def run(self, user_msg: str) -> Any:
            async def _c() -> Any:
                return types.SimpleNamespace(response="arun", sources=[])

            return _c()

    assert li._invoke_agent(_AwaitableRun(), "q").response == "arun"


def test_llamaindex_run_workflow_stream_events_error() -> None:
    class _Handler:
        async def stream_events(self) -> Any:
            raise RuntimeError("stream boom")
            yield "never"  # pragma: no cover

        def __await__(self) -> Any:
            async def _c() -> Any:
                return "done"

            return _c().__await__()

    class _Agent:
        def run(self, *a: Any, **kw: Any) -> Any:
            return _Handler()

    assert asyncio.run(li._run_workflow(_Agent(), "q")) == "done"


def test_openai_agents_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, oa)
    art = OpenAIAgentsAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_pydantic_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, pa)
    art = PydanticAIAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_pydantic_trajectory_tool_call() -> None:
    parts = [types.SimpleNamespace(part_kind="tool-call", tool_name="t", args={"a": 1})]
    steps, _final = pa._extract_trajectory([types.SimpleNamespace(parts=parts)])
    assert steps[0]["type"] == "tool_call"
    assert steps[0]["args"] == {"a": 1}


def test_pydantic_run_sync_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Boom:
        def run_sync(self, user_input: str) -> Any:
            raise RuntimeError("boom")

    name = _install(monkeypatch, "cov_pa_boom", build_agent=_Boom)
    art = PydanticAIAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "invocation failed" in (art.error or "")


def test_python_import_manifest_version_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.metadata as _md

    def _boom(_name: str) -> str:
        raise _md.PackageNotFoundError("nope")

    monkeypatch.setattr(_md, "version", _boom)
    assert PythonImportAdapter().get_manifest()["version"] == "0.0.0"


class _ProcBase:
    exitcode = 0
    alive = False

    def __init__(self, *a: Any, **k: Any) -> None:
        pass

    def start(self) -> None:
        pass

    def join(self, timeout: float | None = None) -> None:
        pass

    def is_alive(self) -> bool:
        return self.alive

    def terminate(self) -> None:
        pass


def test_python_import_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Proc(_ProcBase):
        alive = True

    monkeypatch.setattr(pi.multiprocessing, "Process", _Proc)
    monkeypatch.setattr(pi.multiprocessing, "Queue", lambda: _Queue())
    art = PythonImportAdapter().run(
        _scenario(), {"module": "m", "function": "r", "run_id": "r", "timeout_seconds": 1}
    )
    assert art.status == "timeout"


def test_python_import_nonzero_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Proc(_ProcBase):
        exitcode = 3

    monkeypatch.setattr(pi.multiprocessing, "Process", _Proc)
    monkeypatch.setattr(pi.multiprocessing, "Queue", lambda: _Queue())
    art = PythonImportAdapter().run(_scenario(), {"module": "m", "function": "r", "run_id": "r"})
    assert art.status == "error"
    assert "exited with code" in (art.error or "")


def test_python_import_status_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pi.multiprocessing, "Process", _ProcBase)
    monkeypatch.setattr(pi.multiprocessing, "Queue", lambda: _Queue([("error", "boom")]))
    art = PythonImportAdapter().run(_scenario(), {"module": "m", "function": "r", "run_id": "r"})
    assert art.status == "error"
    assert "boom" in (art.error or "")


def test_smolagents_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, sm)
    art = SmolagentsAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_smol_trajectory_action_output_without_code() -> None:
    call = {"function": {"name": "t", "arguments": "{}"}}
    step = types.SimpleNamespace(tool_calls=[call], action_output="resp")
    steps = sm._extract_trajectory(types.SimpleNamespace(steps=[step]))
    assert steps[-1]["type"] == "response"
    assert steps[-1]["content"] == "resp"


def test_smol_parse_code_action_edge_cases() -> None:
    # subscript call target and **kwargs splat are skipped
    calls = sm._parse_code_action_tools("d['k']()\nf(**opts)\ng(1)")
    names = [c[0] for c in calls]
    assert names == ["f", "g"]
    assert calls[0][1] == {}


def test_claude_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_import_error(monkeypatch, cl)
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"module": "x", "run_id": "r"})
    assert art.status == "error"


def test_claude_prebuilt_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    text_block = types.SimpleNamespace(type="text", text="prebuilt")
    name = _install(
        monkeypatch,
        "cov_cl_prebuilt",
        build_agent=_ClaudeClient([types.SimpleNamespace(content=[text_block])]),
    )
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "completed"
    assert art.output.final == "prebuilt"


def test_claude_client_missing_receive_response(monkeypatch: pytest.MonkeyPatch) -> None:
    class _QueryOnly:
        async def query(self, prompt: str) -> None:
            return None

    name = _install(monkeypatch, "cov_cl_queryonly", build_agent=_QueryOnly)
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"


def test_claude_client_run_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Boom:
        def run(self, prompt: str) -> Any:
            raise ValueError("boom")

    name = _install(monkeypatch, "cov_cl_boom", build_agent=_Boom)
    art = ClaudeAgentSDKAdapter().run(_scenario(), {"module": name, "run_id": "r"})
    assert art.status == "error"
    assert "claude agent failed" in (art.error or "")


def test_claude_trajectory_non_list_content() -> None:
    assert cl._extract_trajectory([types.SimpleNamespace(content=123)]) == []


def test_claude_extract_output_json_non_dict_result() -> None:
    result_msg = types.SimpleNamespace(subtype="result", structured_output=None, result="123")
    text, structured = cl._extract_output([result_msg], [])
    assert text == "123"
    assert structured is None


def test_isolated_missing_module() -> None:
    art = IsolatedAdapter().run(_scenario(), {"adapter_type": "langgraph", "run_id": "r"})
    assert art.status == "error"
    assert "module" in (art.error or "").lower()


def test_subprocess_runner_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess as _sp

    def _boom(**kw: Any) -> Any:
        raise _sp.TimeoutExpired("x", 1)

    monkeypatch.setattr(sr, "sandboxed_run", _boom)
    with pytest.raises(AgentTimeoutError):
        sr.run_agent_in_subprocess({}, ["echo"], {"timeout_seconds": 1})


def test_subprocess_runner_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(**kw: Any) -> Any:
        raise OSError("nope")

    monkeypatch.setattr(sr, "sandboxed_run", _boom)
    with pytest.raises(AdapterError):
        sr.run_agent_in_subprocess({}, ["echo"], {})


def test_subprocess_runner_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sr, "sandboxed_run", lambda **kw: _CP(1, "", "boom"))
    with pytest.raises(AdapterError):
        sr.run_agent_in_subprocess({}, ["echo"], {})
