"""Three-way outcome classification (M9 9.5).

Classify a case to the layer that failed — ``adapter_failed`` /
``agent_crashed`` / ``scenario_failed`` — alongside the oracle ``outcome``
(``blocked`` / ``missed`` / ``degraded``), so a comparison names *where* a
failure happened. Design: ``docs/design/comparison.md``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from agentdrill.models.attack_run import CaseArtifact
from agentdrill.oracles.base import Outcome

#: The layer a case result is classified into.
Classification = Literal["adapter_failed", "agent_crashed", "scenario_failed", "passed"]

#: Substrings that mark a delivery/observation-layer (adapter) failure.
_ADAPTER_MARKERS = (
    "adaptererror",
    "configerror",
    "adapter",
    "driver",
    "target",
    "unsupported type",
)


class OutcomeClassification(BaseModel):
    """A case's three-way layer classification plus its oracle outcome."""

    case_id: str
    outcome: Outcome | None
    classification: Classification
    detail: str = ""


def classify_outcome(artifact: CaseArtifact, *, outcome: Outcome | None) -> OutcomeClassification:
    """Classify ``artifact`` into a failure layer.

    - ``timeout`` → ``agent_crashed`` (no result inside the bound).
    - ``error`` → ``adapter_failed`` when the traceback names the adapter/
      driver/target layer, else ``agent_crashed``.
    - ``aborted`` → ``adapter_failed`` (a run-level governor stopped it).
    - ``completed`` → ``passed`` when the oracle outcome is ``blocked``, else
      ``scenario_failed``.

    Args:
        artifact: The case artifact to classify.
        outcome: The oracle outcome for the case, when evaluated.
    """
    if artifact.status == "timeout":
        return _result(artifact, outcome, "agent_crashed", "case exceeded its time bound")
    if artifact.status == "aborted":
        reason = artifact.error or "aborted"
        return _result(
            artifact, outcome, "adapter_failed", f"run stopped before the agent ran ({reason})"
        )
    if artifact.status == "error":
        error = (artifact.error or "").lower()
        if any(marker in error for marker in _ADAPTER_MARKERS):
            return _result(artifact, outcome, "adapter_failed", "delivery/observation layer raised")
        return _result(artifact, outcome, "agent_crashed", "the agent raised")
    # completed
    if outcome == "blocked":
        return _result(artifact, outcome, "passed", "defense held")
    if outcome is None:
        return _result(artifact, outcome, "scenario_failed", "completed with no oracle outcome")
    return _result(artifact, outcome, "scenario_failed", f"agent ran but the result was {outcome}")


def _result(
    artifact: CaseArtifact,
    outcome: Outcome | None,
    classification: Classification,
    detail: str,
) -> OutcomeClassification:
    return OutcomeClassification(
        case_id=artifact.case_id,
        outcome=outcome,
        classification=classification,
        detail=detail,
    )
