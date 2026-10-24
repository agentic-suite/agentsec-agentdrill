"""Trace backtest (M27 27.1, F92).

Replay **redacted** agentwatch sessions against a candidate policy, offline, and
classify every session: ``unchanged``, ``newly_blocked`` (a candidate false-block,
clustered), ``regression`` (the candidate allowed what production denied), or
``un_replayable`` (itemized — never silently ignored). The replay **fidelity** —
the share of sessions that could be replayed — is gated, so a backtest on thin
data cannot masquerade as complete.
Design: ``docs/design/backtest-path-intake.md``; PRD 30 (R66).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from agentdrill.evidence import AgentWatchEvent

#: The replay classification of one recorded session.
ReplayLabel = Literal["unchanged", "newly_blocked", "regression", "un_replayable"]

#: The minimum share of sessions that must be replayable.
DEFAULT_MIN_FIDELITY = 0.99

#: The agentwatch event that means production blocked the action.
_DENIED = "denied"


class BacktestError(ValueError):
    """Raised when a backtest cannot be trusted (e.g. fidelity below the gate)."""


class RecordedSession(BaseModel):
    """A redacted production session (agentwatch events) to replay.

    Attributes:
        session_id: The session identity.
        events: The recorded agentwatch events, in order.
        replayable: False when the session cannot be replayed offline.
        un_replayable_reason: Why (required when ``replayable`` is False).
        redacted: Whether the session was redacted (F65).
        receipts: Redaction receipts (F65), when redacted.
    """

    session_id: str
    events: list[AgentWatchEvent] = Field(default_factory=list)
    replayable: bool = True
    un_replayable_reason: str | None = None
    redacted: bool = True
    receipts: list[str] = Field(default_factory=list)


class ReplayPolicy(Protocol):
    """A candidate policy: ``True`` allows the event, ``False`` blocks it."""

    def decide(self, event: AgentWatchEvent) -> bool:
        """The candidate's decision for one recorded event."""
        ...


class SessionVerdict(BaseModel):
    """The backtest verdict for one session."""

    session_id: str
    label: ReplayLabel
    detail: str = ""


class BacktestReport(BaseModel):
    """The result of replaying a session corpus against a candidate policy."""

    total: int
    replayable: int
    fidelity: float
    unchanged: int
    newly_blocked: int
    regressions: int
    un_replayable: int
    clusters: dict[str, int] = Field(default_factory=dict)
    verdicts: list[SessionVerdict] = Field(default_factory=list)
    un_replayable_sessions: list[str] = Field(default_factory=list)


def _cluster_key(event: AgentWatchEvent) -> str:
    """The cluster label for a divergence (the action reference, else the event)."""
    return event.ref or event.event


def _production_allowed(event: AgentWatchEvent) -> bool:
    """Whether production allowed the action (only ``denied`` means blocked)."""
    return event.event != _DENIED


def backtest(sessions: Sequence[RecordedSession], policy: ReplayPolicy) -> BacktestReport:
    """Replay ``sessions`` against ``policy`` and classify each session."""
    verdicts: list[SessionVerdict] = []
    clusters: dict[str, int] = {}
    un_replayable_sessions: list[str] = []
    unchanged = newly_blocked = regressions = un_replayable = 0

    for session in sessions:
        if not session.replayable:
            label: ReplayLabel = "un_replayable"
            detail = session.un_replayable_reason or "not replayable"
            un_replayable += 1
            un_replayable_sessions.append(session.session_id)
        else:
            regression: str | None = None
            newly: str | None = None
            for event in session.events:
                allowed_by_candidate = policy.decide(event)
                if not _production_allowed(event) and allowed_by_candidate:
                    regression = _cluster_key(event)
                elif _production_allowed(event) and not allowed_by_candidate and newly is None:
                    newly = _cluster_key(event)
            if regression is not None:
                label = "regression"
                detail = f"regression: {regression}"
                regressions += 1
            elif newly is not None:
                label = "newly_blocked"
                detail = f"newly blocked: {newly}"
                newly_blocked += 1
                clusters[newly] = clusters.get(newly, 0) + 1
            else:
                label = "unchanged"
                detail = ""
                unchanged += 1
        verdicts.append(SessionVerdict(session_id=session.session_id, label=label, detail=detail))

    total = len(sessions)
    replayable = total - un_replayable
    return BacktestReport(
        total=total,
        replayable=replayable,
        fidelity=1.0 if total == 0 else replayable / total,
        unchanged=unchanged,
        newly_blocked=newly_blocked,
        regressions=regressions,
        un_replayable=un_replayable,
        clusters=clusters,
        verdicts=verdicts,
        un_replayable_sessions=un_replayable_sessions,
    )


def require_fidelity(report: BacktestReport, *, minimum: float = DEFAULT_MIN_FIDELITY) -> None:
    """Fail loudly unless the replay fidelity is at least ``minimum``.

    Raises:
        BacktestError: The fidelity is below ``minimum``.
    """
    if report.fidelity < minimum:
        raise BacktestError(
            f"replay fidelity {report.fidelity:.1%} is below the required {minimum:.1%} "
            f"({report.un_replayable}/{report.total} sessions un-replayable)"
        )
