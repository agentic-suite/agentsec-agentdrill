"""Kill-chain timeline findings (M12 12.4).

Name the bottleneck in a kill-chain timeline: ``kill_slow``, ``detect_gap``,
``decision_gap``, ``halt_gap`` and ``cease_gap`` (revoked but still acting —
highest severity). Design: ``docs/design/killchain.md``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from agentdrill.killchain.model import KillChainTimeline
from agentdrill.killchain.timing import stage_durations, total_duration

#: The typed kill-chain findings.
KillChainFindingType = Literal["kill_slow", "detect_gap", "decision_gap", "halt_gap", "cease_gap"]

#: A dominant segment → (finding type, severity).
_SEGMENT_FINDING: dict[str, tuple[str, str]] = {
    "delivered->detected": ("detect_gap", "warning"),
    "detected->decided": ("decision_gap", "warning"),
    "decided->halted": ("halt_gap", "warning"),
    "revoked->ceased": ("cease_gap", "critical"),
}

#: Default minimum duration (seconds) for a segment to be "dominant".
DEFAULT_MIN_GAP_SECONDS = 0.5


class KillChainFinding(BaseModel):
    """A typed finding about a kill-chain timeline."""

    case_id: str
    type: KillChainFindingType
    severity: str
    stage: str | None = None
    detail: str = ""


def analyze_timeline(
    timeline: KillChainTimeline,
    *,
    max_seconds: float | None = None,
    min_gap_seconds: float = DEFAULT_MIN_GAP_SECONDS,
) -> list[KillChainFinding]:
    """Findings for one timeline.

    A ``cease_gap`` (critical) fires when the target was revoked but never
    ceased (still acting), or when ``revoked -> ceased`` is the dominant
    segment. Otherwise the dominant segment names its gap. ``kill_slow`` fires
    when the total exceeds ``max_seconds``.
    """
    findings: list[KillChainFinding] = []
    stages = timeline.stages

    if stages.get("revoked") is not None and stages.get("ceased") is None:
        findings.append(
            KillChainFinding(
                case_id=timeline.case_id,
                type="cease_gap",
                severity="critical",
                stage="ceased",
                detail="revoked but never ceased (the target is still acting)",
            )
        )
    else:
        durations = stage_durations(timeline)
        if durations:
            dominant = max(durations, key=lambda name: durations[name])
            if durations[dominant] >= min_gap_seconds and dominant in _SEGMENT_FINDING:
                finding_type, severity = _SEGMENT_FINDING[dominant]
                findings.append(
                    KillChainFinding(
                        case_id=timeline.case_id,
                        type=finding_type,  # type: ignore[arg-type]
                        severity=severity,
                        stage=dominant,
                        detail=f"{dominant} dominant ({durations[dominant]:.2f}s)",
                    )
                )

    if max_seconds is not None:
        total = total_duration(timeline)
        if total is not None and total > max_seconds:
            findings.append(
                KillChainFinding(
                    case_id=timeline.case_id,
                    type="kill_slow",
                    severity="warning",
                    detail=f"total {total:.2f}s exceeds the {max_seconds:.2f}s budget",
                )
            )
    return findings
