"""Target adapter base + contract (M5 work item 5.1).

A :class:`Target` drives a **deployed-stack component** into an attack posture
and reads back its decision + evidence: ``drive(case)`` →
``read_decision()`` / ``read_evidence()``. Targets own the real enforcement path;
agentdrill owns **no** enforcement (ADR-0003). A case bound to a nonexistent
surface must fail loudly (never silently pass).

Design: ``docs/design/adapter-contract.md``.
"""

from __future__ import annotations

import json
import subprocess
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Literal

from pydantic import BaseModel

from agentdrill.models.attack_pack import AttackCase
from agentdrill.models.errors import AdapterError, ConfigError
from agentdrill.models.evidence import Evidence as Evidence

#: What the target decided about the attempted attack.
DecisionOutcome = Literal["allow", "deny", "ask", "unknown"]


class Decision(BaseModel):
    """A target's decision about an attempted attack."""

    decision: DecisionOutcome = "unknown"
    rationale: str = ""
    source: str = ""


class Target(ABC):
    """Base class for target adapters (the deployed-stack layer).

    Subclasses set :attr:`component` (matching ``case.target.type``) and implement
    :meth:`drive`, :meth:`read_decision` and :meth:`read_evidence`.
    """

    #: Registered component name; matches ``case.target.type``.
    component: ClassVar[str] = ""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config: dict[str, Any] = dict(config or {})

    def build_payload(self, case: AttackCase) -> dict[str, Any]:
        """Build the restricted attack payload (no ground truth)."""
        return {
            "case_id": case.id,
            "attack": {
                "steps": [
                    {"tool": step.tool, "args": step.args} for step in case.attack.steps
                ]
            },
            "target": {"type": case.target.type, "config": case.target.config},
        }

    @abstractmethod
    def drive(self, case: AttackCase) -> None:
        """Deliver the attack to the component."""

    @abstractmethod
    def read_decision(self) -> Decision:
        """Return the component's decision for the most recent drive."""

    @abstractmethod
    def read_evidence(self) -> list[Evidence]:
        """Return the evidence the component emitted for the most recent drive."""


class CommandTarget(Target):
    """Drive a component through a command; parse its decision + evidence.

    Config keys:

    - ``command`` (required) — the argv list to run; the attack payload is fed on
      stdin and a ``{"decision": {...}, "evidence": [...]}`` envelope read from stdout.
    - ``timeout_seconds`` — child timeout (expiry → :class:`AdapterError`).
    - ``attestation`` — ``live`` / ``fixture`` / ``mock`` (default ``mock``).
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self.attestation: str = str(self.config.get("attestation", "mock"))
        self._decision = Decision()
        self._evidence: list[Evidence] = []

    def drive(self, case: AttackCase) -> None:
        command = self.config.get("command")
        if not isinstance(command, list) or not command:
            raise ConfigError("target requires config.command (a non-empty list)")
        try:
            proc = subprocess.run(  # noqa: S603 - command comes from trusted target config
                command,
                input=json.dumps(self.build_payload(case)),
                capture_output=True,
                text=True,
                timeout=self.config.get("timeout_seconds"),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise AdapterError("target command timed out") from exc
        except OSError as exc:
            raise AdapterError(f"target command failed to start: {exc}") from exc
        if proc.returncode != 0:
            raise AdapterError(f"target exited {proc.returncode}: {proc.stderr.strip()}")
        try:
            data = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise AdapterError("target output is not a decision envelope") from exc
        decision_raw = data.get("decision", {})
        self._decision = (
            Decision.model_validate(decision_raw)
            if isinstance(decision_raw, dict)
            else Decision()
        )
        raw_evidence = data.get("evidence", [])
        self._evidence = [
            Evidence.model_validate(item)
            for item in raw_evidence
            if isinstance(item, dict)
        ]

    def read_decision(self) -> Decision:
        return self._decision

    def read_evidence(self) -> list[Evidence]:
        return list(self._evidence)
