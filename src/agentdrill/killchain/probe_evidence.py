"""Evidence for the cessation probe (M12 12.6).

The re-attempt is recorded in the evidence bundle — **what** was re-attempted,
**when**, and the **result** — so the probe is auditable. Design:
``docs/design/killchain.md``.
"""

from __future__ import annotations

from agentdrill.killchain.probe import ProbeResult
from agentdrill.models.evidence import Evidence


def probe_evidence(result: ProbeResult, *, at: str) -> Evidence:
    """An evidence event recording the cessation probe re-attempt.

    Args:
        result: The probe result to record.
        at: The ISO-8601 timestamp of the re-attempt (the "when").
    """
    outcome = "still acting" if result.action_succeeded else "ceased"
    return Evidence(
        event="cease-probe",
        summary=f"re-attempt at {at}: {outcome} ({result.detail})",
        ref=result.case_id,
    )
