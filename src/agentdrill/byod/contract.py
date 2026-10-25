"""Defense Contract + SDK (M25 25.1, F90).

An open contract any defense implements — decision points, I/O shape, evidence,
a **config digest**, fail-mode, version and ToS notes — plus an SDK so a
request/response defense adapts quickly. Design:
``docs/prd/29-bring-your-own-defense.md``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field


class DefenseContract(BaseModel):
    """The contract every defense implements."""

    name: str
    decision_points: list[str] = Field(default_factory=list)
    io_shape: str = "request/response"
    evidence: list[str] = Field(default_factory=list)
    config_digest: str = ""
    fail_mode: str = "closed"
    version: str = "0.1.0"
    tos_notes: str = ""


class DefenseSDK:
    """Adapts a request/response defense to the contract.

    Args:
        contract: The defense's contract.
        decide: Maps a request dict to a response dict (e.g. ``{"decision": "deny"}``).
    """

    def __init__(
        self, contract: DefenseContract, *, decide: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> None:
        self.contract = contract
        self._decide = decide

    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a request against the wrapped defense."""
        return self._decide(request)


def config_digest(config: dict[str, Any]) -> str:
    """The SHA-256 of a defense's canonical config (bound into head-to-head cells)."""
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_contract(
    *,
    name: str,
    decision_points: list[str],
    io_shape: str,
    evidence: list[str],
    config: dict[str, Any],
    fail_mode: str,
    version: str,
    tos_notes: str = "",
) -> DefenseContract:
    """Build a defense contract with its config digest."""
    return DefenseContract(
        name=name,
        decision_points=list(decision_points),
        io_shape=io_shape,
        evidence=list(evidence),
        config_digest=config_digest(config),
        fail_mode=fail_mode,
        version=version,
        tos_notes=tos_notes,
    )
