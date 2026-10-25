"""Driver base + invocation contract (M4 work item 4.1).

A :class:`Driver` builds a **restricted** invocation payload and delivers it to a
harness, returning a normalized :class:`CaseOutcome`. The invariant (DD-03): the
expected outcome — ``oracle``/``expect``, dimensions, telemetry, kill-time,
thresholds, benign twins — **never** reaches the driver.

Design: ``docs/design/adapter-contract.md`` (the design calls the return a
``RunArtifact``; the M3 spine defines it as ``CaseOutcome``, which the runner
wraps into a ``CaseArtifact``).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from agentdrill.attack_runner import CaseOutcome
from agentdrill.models.artifact import Cost, RunOutput, TrajectoryStep
from agentdrill.models.attack_pack import AttackCase
from agentdrill.models.errors import AdapterError


def normalize_envelope(raw: Any) -> CaseOutcome:
    """Normalize a raw driver return into a :class:`CaseOutcome`.

    A ``str`` is treated as raw stdout (text output, empty trajectory); a
    ``dict`` is a run envelope (``agentdrill.run_envelope.v1``); anything else
    is a loud :class:`AdapterError`.

    Args:
        raw: The value a driver returned from ``_invoke``.

    Returns:
        The normalized outcome.

    Raises:
        AdapterError: If ``raw`` is neither a ``str`` nor a ``dict``.
    """
    if isinstance(raw, str):
        return CaseOutcome(output=RunOutput(final=raw))
    if isinstance(raw, dict):
        return _envelope_to_outcome(raw)
    raise AdapterError(f"driver returned unsupported type: {type(raw).__name__}")


def _envelope_to_outcome(raw: dict[str, Any]) -> CaseOutcome:
    """Parse a run-envelope dict into a :class:`CaseOutcome`."""
    output_raw = raw.get("output")
    if isinstance(output_raw, dict):
        output = RunOutput.model_validate(output_raw)
    elif output_raw is None:
        output = RunOutput()
    else:
        output = RunOutput(final=str(output_raw))

    trajectory_raw = raw.get("trajectory")
    steps_raw = (
        trajectory_raw.get("steps") if isinstance(trajectory_raw, dict) else trajectory_raw
    )
    steps = (
        [TrajectoryStep.model_validate(step) for step in steps_raw]
        if isinstance(steps_raw, list)
        else []
    )
    cost = Cost.model_validate(raw.get("cost") or {})
    return CaseOutcome(output=output, trajectory=steps, cost=cost)


class Driver(ABC):
    """Base class for attack drivers (the delivery layer).

    Subclasses set :attr:`name` (matching ``case.driver.type``) and implement
    :meth:`_invoke`. The base builds the restricted payload and normalizes the
    result; the runner (M3) owns timing, timeouts, status and artifact writing.
    """

    #: Registered driver type; matches ``case.driver.type``.
    name: ClassVar[str] = ""

    def build_payload(self, case: AttackCase) -> dict[str, Any]:
        """Build the restricted invocation payload for ``case``.

        Carries the case id, goal, target and attack steps (plus budget when
        set) and **never** the expected outcome — the no-leakage boundary.
        """
        payload: dict[str, Any] = {
            "case_id": case.id,
            "goal": case.goal,
            "target": {"type": case.target.type, "config": case.target.config},
            "attack": {
                "steps": [
                    {"tool": step.tool, "args": step.args} for step in case.attack.steps
                ]
            },
        }
        if case.budget is not None:
            payload["budget"] = case.budget.model_dump(exclude_none=True)
        return payload

    @abstractmethod
    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> Any:
        """Deliver ``payload`` to the harness and return a raw result.

        Returns a run-envelope ``dict`` or raw text (``str``). Raise
        :class:`~agentdrill.models.errors.AgentTimeoutError` on timeout and
        :class:`~agentdrill.models.errors.AdapterError` on any other failure.
        """

    def run(self, case: AttackCase, config: dict[str, Any]) -> CaseOutcome:
        """Build the payload, deliver it, and normalize the outcome."""
        return normalize_envelope(self._invoke(self.build_payload(case), config))

    def __call__(self, case: AttackCase) -> CaseOutcome:
        """Let a driver be used directly as an ``AttackRunner`` driver callable."""
        return self.run(case, case.driver.config)
