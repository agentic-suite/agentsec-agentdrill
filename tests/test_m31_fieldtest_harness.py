"""M31 field-test harness regression tests (one behavior per defect I-1..I-11).

The v0.1.0 field test found eleven harness defects (the product had zero). Each
test here pins the behavior that the matching defect violated, so the same
defect cannot come back silently. None of these need Docker, oMLX, or a network:
they exercise the harness as a unit.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]
FT = REPO / "scripts" / "fieldtest"
REGISTRY: list[dict[str, Any]] = json.loads((FT / "cases" / "registry.json").read_text("utf-8"))


def _load(path: Path, name: str) -> Any:
    """Import a stand-alone script by path (they are not installed packages)."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- I-1: run-ft-all.sh listed stale suite names (every suite "no cases found") ---
def test_suite_list_matches_registry() -> None:
    text = (FT / "run-ft-all.sh").read_text(encoding="utf-8")
    match = re.search(r"ALL=\(([^)]*)\)", text)
    assert match, "run-ft-all.sh must declare ALL=(...) suites"
    listed = set(match.group(1).split())
    declared = {str(case["suite"]) for case in REGISTRY}
    assert listed == declared


# --- I-2: FT-A-CORE referenced tests/test_m11_gate.py, which does not exist ---
def test_every_step_test_ref_exists() -> None:
    refs: set[str] = set()
    for case in REGISTRY:
        refs.update(re.findall(r"tests/[\w./-]+\.py", str(case["steps"])))
    assert refs, "registry should reference shipped tests"
    missing = sorted(ref for ref in refs if not (REPO / ref).exists())
    assert not missing, f"step scripts reference missing test files: {missing}"


# --- I-3: the field runner's `uv run pytest` resolved a Python without agentdrill ---
def test_field_runner_uses_project_env_pytest() -> None:
    text = (REPO / "field" / "run-local.sh").read_text(encoding="utf-8")
    assert "python -m pytest" in text, "must run pytest as a module in the project env"
    assert "uv run" in text and "--extra" in text, "must run under uv with the framework extras"


# --- I-4: Track B demanded every scenario pass, ignoring acceptance.minimum_pass_rate ---
def _agent_summary(results: Path, passed: int, failed: int, skipped: int) -> None:
    (results / "summary.json").write_text(
        json.dumps({"passed": passed, "failed": failed, "skipped": skipped}), encoding="utf-8"
    )


def _agent_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, min_rate: float) -> Any:
    mod = _load(FT / "run_agent.py", "run_agent_ut")
    repo = tmp_path / "repo"
    results = repo / "field" / "results"
    (repo / "field" / "config").mkdir(parents=True)
    results.mkdir(parents=True)
    (repo / "field" / "config" / "pai.json").write_text(
        json.dumps({"acceptance": {"minimum_pass_rate": min_rate}}), encoding="utf-8"
    )
    monkeypatch.setattr(mod, "REPO", repo)
    monkeypatch.setattr(mod, "RESULTS", results)
    return mod


def test_acceptance_uses_configured_minimum_pass_rate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _agent_env(tmp_path, monkeypatch, min_rate=0.5)
    _agent_summary(mod.RESULTS, passed=5, failed=2, skipped=0)  # 5/7 = 0.71 >= 0.5
    assert mod.main(["pai", "--skip-setup"]) == 0


def test_acceptance_below_minimum_pass_rate_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _agent_env(tmp_path, monkeypatch, min_rate=0.5)
    _agent_summary(mod.RESULTS, passed=1, failed=6, skipped=0)  # 1/7 = 0.14 < 0.5
    assert mod.main(["pai", "--skip-setup"]) == 1


def test_acceptance_requires_at_least_one_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _agent_env(tmp_path, monkeypatch, min_rate=0.0)
    _agent_summary(mod.RESULTS, passed=0, failed=0, skipped=7)  # a sweep of skips is not a pass
    assert mod.main(["pai", "--skip-setup"]) == 1


# --- I-5: LlamaIndex's OpenAI class rejected the custom local model name ---
@pytest.mark.parametrize("wrapper", ["li-official_wrapper.py", "li-azure_wrapper.py"])
def test_llamaindex_wrappers_accept_custom_model_names(wrapper: str) -> None:
    text = (REPO / "field" / "config" / wrapper).read_text(encoding="utf-8")
    assert "OpenAILike" in text
    assert "from llama_index.llms.openai import OpenAI" not in text


# --- I-6: smolagents pinned mcp 1.x while the agent code needed the 2.x API ---
def test_mcp_extra_supports_2x() -> None:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    assert "mcp>=2.3" in text


# --- I-7: the LlamaIndex adapter could not read trajectories/outputs ---
def test_llamaindex_extraction_helpers() -> None:
    sys.path.insert(0, str(REPO / "src"))
    import agentdrill.adapters.llamaindex as li

    call = SimpleNamespace(tool_name="search", tool_kwargs={"q": "weather"})
    assert li._tool_name_of(call) == "search"
    assert li._tool_args_of(call) == {"q": "weather"}
    assert li._tool_name_of({"name": "finish"}) == "finish"
    assert li._tool_args_of({"arguments": {"x": 1}}) == {"x": 1}
    assert li._message_text("done") == "done"
    assert li._message_text({"content": "hello"}) == "hello"
    assert li._message_text(None) is None


# --- I-8: the model pin leaked (the field runner defaulted to the old model) ---
def test_field_runner_pin_is_single_source() -> None:
    text = (REPO / "field" / "run-local.sh").read_text(encoding="utf-8")
    assert "AGENTDRILL_FIELD_MODEL" in text and "FT_LLM_MODEL" in text


# --- I-9: the capture hooked request(), so agent calls via send() were invisible ---
def test_http_capture_hooks_send_not_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import httpx

    monkeypatch.setenv("AGENTDRILL_FIELD_OUTPUT_DIR", str(tmp_path))
    orig_client_send = httpx.Client.send
    orig_async_send = httpx.AsyncClient.send
    mod = _load(REPO / "field" / "test_field_agent.py", "field_agent_ut")
    try:
        mod._install_http_capture()
        assert getattr(httpx.Client.send, "_agentdrill_field_patched", False)
        assert getattr(httpx.AsyncClient.send, "_agentdrill_field_patched", False)
        # The OpenAI SDK sends via send(); hooking request() would miss it.
        assert not getattr(httpx.Client.request, "_agentdrill_field_patched", False)
        first = httpx.Client.send
        mod._install_http_capture()  # idempotent: no double wrap
        assert httpx.Client.send is first
    finally:
        httpx.Client.send = orig_client_send
        httpx.AsyncClient.send = orig_async_send


# --- I-10: a PASS with no grounded assertion is over-claimed ---
def _verdict_tree(tmp_path: Path, grounded: bool, cmd: str) -> Path:
    case = tmp_path / "track-a" / "cases" / "FT-A-CORE"
    case.mkdir(parents=True)
    (case / "verdict.json").write_text(
        json.dumps({"id": "FT-A-CORE", "status": "pass"}), encoding="utf-8"
    )
    (case / "assertions.ndjson").write_text(
        json.dumps({"name": "check", "ok": True, "grounded": grounded, "cmd": cmd}) + "\n",
        encoding="utf-8",
    )
    return tmp_path


def test_grounding_gate_flags_unbacked_pass(tmp_path: Path) -> None:
    results = _verdict_tree(tmp_path, grounded=False, cmd="run_pytest tests/test_m1.py")
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(FT / "check_grounding.py"), str(results)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "over-claimed" in (proc.stdout + proc.stderr)


def test_grounding_gate_accepts_grounded_pass(tmp_path: Path) -> None:
    results = _verdict_tree(tmp_path, grounded=True, cmd="run_pytest tests/test_m1.py")
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(FT / "check_grounding.py"), str(results)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


# --- I-11: a direct case run defaulted to results/all/ (a duplicate evidence tree) ---
def test_lib_refuses_unset_run_id() -> None:
    env = {k: v for k, v in os.environ.items() if k != "FT_RUN_ID"}
    env["FT_VERSION"] = "v0.1.0"
    proc = subprocess.run(
        ["bash", "-c", "source scripts/fieldtest/lib.sh"],  # noqa: S607
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "FATAL" in proc.stderr


# --- FT-E25: the cross-OS parity battery (pure, deterministic, two-host) ---
def _parity_doc(os_name: str, outcomes: dict[str, Any]) -> dict[str, Any]:
    return {
        "platform": {"os": os_name, "machine": "arm64", "python": "3.11.17"},
        "scorers": ["scorer"],
        "outcomes": outcomes,
    }


def test_parity_battery_is_pure() -> None:
    sys.path.insert(0, str(FT))
    pp = _load(FT / "parity_probe.py", "parity_probe_ut")
    scorers = pp._deterministic_scorers()
    battery = pp._fixture_battery()
    assert len(scorers) >= 10
    assert len(battery) == 11
    # running the battery twice yields byte-identical outcomes (no clock/network)
    import tempfile

    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        pa, pb = Path(a) / "a.json", Path(b) / "b.json"
        assert pp.cmd_run(str(pa)) == 0
        assert pp.cmd_run(str(pb)) == 0
        da = json.loads(pa.read_text("utf-8"))
        db = json.loads(pb.read_text("utf-8"))
        assert da["outcomes"] == db["outcomes"]


def test_parity_compare_refuses_same_os(tmp_path: Path) -> None:
    sys.path.insert(0, str(FT))
    pp = _load(FT / "parity_probe.py", "parity_probe_ut")
    outcomes = {"scorer/x": {"passed": True, "score": 1.0}}
    h = tmp_path / "h.json"
    lin = tmp_path / "l.json"
    h.write_text(json.dumps(_parity_doc("Darwin", outcomes)), encoding="utf-8")
    lin.write_text(json.dumps(_parity_doc("Darwin", outcomes)), encoding="utf-8")
    assert pp.cmd_compare(str(h), str(lin), 0.995, None) == 3


def test_parity_compare_math(tmp_path: Path) -> None:
    sys.path.insert(0, str(FT))
    pp = _load(FT / "parity_probe.py", "parity_probe_ut")
    good = {f"scorer/{i}": {"passed": True, "score": 1.0} for i in range(100)}
    h = tmp_path / "h.json"
    lin = tmp_path / "l.json"
    h.write_text(json.dumps(_parity_doc("Darwin", good)), encoding="utf-8")

    # identical -> 100% -> pass
    lin.write_text(json.dumps(_parity_doc("Linux", good)), encoding="utf-8")
    report = tmp_path / "r.json"
    assert pp.cmd_compare(str(h), str(lin), 0.995, str(report)) == 0
    assert json.loads(report.read_text("utf-8"))["parity"] == 1.0

    # one mismatch -> 0.99 < 0.995 -> fail
    one_off = dict(good)
    one_off["scorer/0"] = {"passed": False, "score": 0.0}
    lin.write_text(json.dumps(_parity_doc("Linux", one_off)), encoding="utf-8")
    assert pp.cmd_compare(str(h), str(lin), 0.995, None) == 1
