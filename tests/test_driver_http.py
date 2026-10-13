"""M4 4.4 — http driver (RED → GREEN).

POST the payload; handle connection / timeout / non-200 by normalizing them to
typed errors (the runner maps these to `status`).
"""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from agentdrill.drivers.http_driver import HttpDriver
from agentdrill.models.attack_pack import (
    Attack,
    AttackCase,
    AttackStep,
    AttackTarget,
    Oracle,
)
from agentdrill.models.attack_pack import (
    Driver as DriverCfg,
)
from agentdrill.models.errors import AdapterError, AgentTimeoutError, ConfigError


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        if self.path == "/ok":
            self._respond(200, json.dumps({"output": {"final": "ok " + payload["case_id"]}}))
        elif self.path == "/raw":
            self._respond(200, "plain text output", content_type="text/plain")
        elif self.path == "/slow":
            time.sleep(2)
            self._respond(200, "{}")
        else:
            self._respond(500, "boom")

    def _respond(self, code: int, body: str, content_type: str = "application/json") -> None:
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args: Any) -> None:  # silence the server
        return


@pytest.fixture
def server() -> Iterator[str]:
    httpd = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    yield f"http://{host}:{port}"
    httpd.shutdown()


def _case() -> AttackCase:
    return AttackCase(
        id="c1",
        title="t",
        goal="g",
        incident_ref="incident-register#1",
        target=AttackTarget(type="policyweave-output"),
        driver=DriverCfg(type="http"),
        attack=Attack(steps=[AttackStep(tool="shell")]),
        oracle=Oracle(expect="blocked"),
    )


def test_ok_envelope(server: str) -> None:
    outcome = HttpDriver().run(_case(), {"url": f"{server}/ok"})
    assert outcome.output.final == "ok c1"


def test_raw_text_body(server: str) -> None:
    outcome = HttpDriver().run(_case(), {"url": f"{server}/raw"})
    assert outcome.output.final == "plain text output"


def test_non_200_raises_adapter_error(server: str) -> None:
    with pytest.raises(AdapterError, match="500"):
        HttpDriver().run(_case(), {"url": f"{server}/nope"})


def test_timeout_raises_agent_timeout_error(server: str) -> None:
    with pytest.raises(AgentTimeoutError):
        HttpDriver().run(_case(), {"url": f"{server}/slow", "timeout_seconds": 0.5})


def test_connection_error_raises_adapter_error() -> None:
    # port 9 (discard) is not listening → connection refused
    with pytest.raises(AdapterError):
        HttpDriver().run(_case(), {"url": "http://127.0.0.1:9", "timeout_seconds": 1})


def test_missing_url_is_config_error() -> None:
    with pytest.raises(ConfigError):
        HttpDriver().run(_case(), {})
