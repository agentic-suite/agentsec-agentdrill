"""Expected-telemetry validation (M7 work item 7.3, F52).

A case declares the agentwatch events a **true block** must produce. A ``blocked``
verdict without them is a ``telemetry_gap`` finding
(design/evidence-integration.md rule 3).
"""

from __future__ import annotations

from agentdrill.evidence.schema import AgentWatchEvent
from agentdrill.models.attack_pack import AttackCase
from agentdrill.oracles.base import Finding, Verdict


def validate_expected_telemetry(
    case: AttackCase, verdict: Verdict, events: list[AgentWatchEvent]
) -> Finding | None:
    """Flag a ``blocked`` verdict that lacks its expected telemetry.

    Only ``blocked`` verdicts require the declared ``expect_telemetry`` events;
    a ``missed``/``degraded`` case does not. No declared events ⇒ no requirement.

    Returns:
        A ``telemetry_gap`` :class:`Finding`, or ``None`` when satisfied.
    """
    if verdict.outcome != "blocked":
        return None
    expected = set(case.oracle.expect_telemetry)
    if not expected:
        return None
    present = {event.event for event in events}
    missing = expected - present
    if not missing:
        return None
    return Finding(
        case_id=case.id,
        type="telemetry_gap",
        severity="warning",
        detail=f"blocked without expected telemetry: {sorted(missing)}",
    )
