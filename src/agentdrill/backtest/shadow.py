"""Shadow mode (M27 27.2, F92).

Run a candidate policy **log-only** beside the enforced one and report the
divergence rate, cluster the candidate's **false blocks** on benign calls, and
gate on the policy's declared **false-block budget** (with a bootstrap CI). The
shadow must be **provably side-effect free** — the M23 witness supplies the
side-effect list; a non-empty list fails the gate.
Design: ``docs/design/backtest-path-intake.md``; PRD 30 (R66).
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentdrill.reporting.ci import DEFAULT_LEVEL, bootstrap_ci

#: The default false-block budget (0.5 % of benign calls).
DEFAULT_FALSE_BLOCK_BUDGET = 0.005


class ShadowError(ValueError):
    """Raised when a shadow run violates its budget or is not side-effect free."""


class ShadowDecision(BaseModel):
    """One observed call, decided by both the enforced and candidate policies.

    ``enforced_allowed`` / ``candidate_allowed`` are ``True`` when the policy
    allows the call. ``benign`` marks a call that was benign in production.
    """

    action: str
    enforced_allowed: bool
    candidate_allowed: bool
    benign: bool = True


class ShadowReport(BaseModel):
    """The result of a log-only shadow run."""

    total: int
    divergent: int
    divergence_rate: float
    clusters: dict[str, int] = Field(default_factory=dict)
    benign_total: int
    false_block_count: int
    false_block_rate: float
    false_block_ci: tuple[float, float]
    side_effects: list[str] = Field(default_factory=list)
    side_effect_free: bool


def _is_false_block(decision: ShadowDecision) -> bool:
    """A benign call the enforced policy allowed and the candidate blocks."""
    return decision.benign and decision.enforced_allowed and not decision.candidate_allowed


def run_shadow(
    decisions: Sequence[ShadowDecision],
    *,
    side_effects: Sequence[str] | None = None,
    seed: int = 0,
    level: float = DEFAULT_LEVEL,
) -> ShadowReport:
    """Compare enforced vs. candidate decisions (log-only) over ``decisions``."""
    divergent = sum(
        1 for decision in decisions if decision.enforced_allowed != decision.candidate_allowed
    )
    clusters: dict[str, int] = {}
    for decision in decisions:
        if _is_false_block(decision):
            clusters[decision.action] = clusters.get(decision.action, 0) + 1

    benign = [d for d in decisions if d.benign and d.enforced_allowed]
    false_blocks = sum(1 for d in benign if not d.candidate_allowed)
    rate = 0.0 if not benign else false_blocks / len(benign)
    samples = [1.0 if not d.candidate_allowed else 0.0 for d in benign]
    ci = bootstrap_ci(samples, seed=seed, level=level)

    effects = list(side_effects or [])
    total = len(decisions)
    return ShadowReport(
        total=total,
        divergent=divergent,
        divergence_rate=0.0 if total == 0 else divergent / total,
        clusters=clusters,
        benign_total=len(benign),
        false_block_count=false_blocks,
        false_block_rate=rate,
        false_block_ci=ci,
        side_effects=effects,
        side_effect_free=not effects,
    )


def false_block_rate(report: ShadowReport) -> float:
    """The candidate's false-block rate over benign calls."""
    return report.false_block_rate


def require_false_block_budget(
    report: ShadowReport, *, budget: float = DEFAULT_FALSE_BLOCK_BUDGET
) -> None:
    """Fail loudly unless the false-block rate is within ``budget``.

    Raises:
        ShadowError: The rate exceeds the budget.
    """
    if report.false_block_rate > budget:
        low, high = report.false_block_ci
        raise ShadowError(
            f"false-block rate {report.false_block_rate:.2%} [{low:.2%}, {high:.2%}] "
            f"exceeds the budget {budget:.2%} "
            f"({report.false_block_count}/{report.benign_total} benign calls); "
            f"clusters: {report.clusters}"
        )


def require_side_effect_free(report: ShadowReport) -> None:
    """Fail loudly unless the shadow recorded no side effects.

    Raises:
        ShadowError: The shadow produced side effects.
    """
    if not report.side_effect_free:
        raise ShadowError(f"shadow produced side effects (not log-only): {report.side_effects}")
