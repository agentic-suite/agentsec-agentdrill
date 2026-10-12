"""Tests for the isolated adapter worker (agentdrill.adapters.worker)."""

from __future__ import annotations

import io
import json

import pytest

from agentdrill.adapters import worker


@pytest.fixture(autouse=True)
def _clear_cache():
    worker._CACHE.clear()
    yield
    worker._CACHE.clear()


def test_load_payload_ok(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO('{"a": 1}'))
    assert worker._load_payload() == {"a": 1}


def test_load_payload_not_object(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("[1, 2]"))
    with pytest.raises(RuntimeError):
        worker._load_payload()


def test_try_import_adapter_success() -> None:
    cls = worker._try_import_adapter("agentdrill.adapters.langgraph", "LangGraphAdapter")
    assert cls is not worker._SENTINEL


def test_try_import_adapter_failure() -> None:
    assert worker._try_import_adapter("nope.not_real", "X") is worker._SENTINEL


def test_adapter_for_unknown() -> None:
    assert worker._adapter_for("bogus") is None
    assert worker._adapter_for("bogus") is None  # cached None


def test_adapter_for_known_and_cached() -> None:
    inst = worker._adapter_for("langgraph")
    assert inst is not None
    assert worker._adapter_for("langgraph") is inst


def test_adapter_for_import_failure() -> None:
    worker._ADAPTER_TABLE["bogus2"] = ("nope.not_real", "X")
    try:
        assert worker._adapter_for("bogus2") is None
    finally:
        del worker._ADAPTER_TABLE["bogus2"]


def test_error_envelope() -> None:
    env = worker._error_envelope(ValueError("boom"))
    assert env["status"] == "error"
    assert env["error"] == "boom"
    assert env["output"] == {"final": None, "structured": None}


def test_main_unknown_adapter(monkeypatch, capsys) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"adapter_type": "bogus"})))
    assert worker.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "error"


def test_main_success(monkeypatch, capsys) -> None:
    class Fake:
        def _invoke(self, payload, config):
            return {"status": "ok", "echo": payload}

    monkeypatch.setattr(worker, "_adapter_for", lambda _k: Fake())
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO(json.dumps({"adapter_type": "langgraph", "payload": {"x": 1}})),
    )
    assert worker.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "ok"
    assert out["echo"] == {"x": 1}


def test_main_invoke_raises(monkeypatch, capsys) -> None:
    class Boom:
        def _invoke(self, payload, config):
            raise ValueError("kaboom")

    monkeypatch.setattr(worker, "_adapter_for", lambda _k: Boom())
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"adapter_type": "langgraph"})))
    assert worker.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "error"
    assert "kaboom" in out["error"]
