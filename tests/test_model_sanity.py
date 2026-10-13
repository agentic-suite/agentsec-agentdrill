"""M5 5.5 — model/target sanity (RED → GREEN).

A run declares `model`/`base_url`; recon fails **loudly** on an unreachable model
surface *before* any case runs — an opaque 404 becomes a clear failure (G12).
"""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.errors import ConfigError
from agentdrill.recon import ModelSurface, check_model_surface, recon


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/models":
            self._respond(200, json.dumps({"data": [{"id": "gpt"}]}))
        else:
            self._respond(404, "not found")

    def _respond(self, code: int, body: str) -> None:
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args: Any) -> None:
        return


@pytest.fixture
def server() -> Iterator[str]:
    httpd = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    host, port = httpd.server_address[:2]
    yield f"http://{host}:{port}"
    httpd.shutdown()


def _pack() -> AttackPack:
    return AttackPack.model_validate(
        {
            "pack": {
                "name": "p",
                "version": "1.0.0",
                "description": "d",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
                "hash": "deadbeef",
            },
            "cases": [
                {
                    "id": "c1",
                    "title": "t",
                    "goal": "g",
                    "incident_ref": "incident-register#1",
                    "target": {"type": "policyweave-output"},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": [{"tool": "shell"}]},
                    "oracle": {"expect": "blocked"},
                    "tags": [],
                }
            ],
        }
    )


INVENTORY = {"tools": ["shell"], "mcp_servers": [], "capabilities": []}


def test_reachable_model_surface_passes(server: str) -> None:
    check_model_surface(ModelSurface(model="gpt", base_url=server))


def test_opaque_404_becomes_clear_failure(server: str) -> None:
    with pytest.raises(ConfigError, match="gpt"):
        check_model_surface(ModelSurface(model="gpt", base_url=f"{server}/nope"))


def test_unreachable_model_surface_fails() -> None:
    with pytest.raises(ConfigError):
        check_model_surface(ModelSurface(model="gpt", base_url="http://127.0.0.1:9"))


def test_recon_checks_model_before_binding(server: str) -> None:
    with pytest.raises(ConfigError):
        recon(
            _pack(),
            inventory=INVENTORY,
            model=ModelSurface(model="gpt", base_url=f"{server}/nope"),
        )


def test_recon_ok_with_reachable_model(server: str) -> None:
    snapshot = recon(
        _pack(), inventory=INVENTORY, model=ModelSurface(model="gpt", base_url=server)
    )
    assert snapshot.case_bindings["c1"] == ["shell"]
