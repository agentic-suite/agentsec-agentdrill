"""Dry-run & explain (M20 20.2, F69).

``run --dry-run`` prints the bound cases, their targets, expected verdicts and
evidence; ``--explain`` annotates why each case exists. A dry-run performs
**zero** executions. Design: ``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentdrill.models.attack_pack import AttackPack


class DryRunCase(BaseModel):
    """One planned case in a dry-run."""

    case_id: str
    target: str
    expected: str
    evidence: list[str] = Field(default_factory=list)
    exists_because: str = ""


class DryRunPlan(BaseModel):
    """A dry-run plan (never executes anything)."""

    cases: list[DryRunCase] = Field(default_factory=list)
    executions: int = 0


def dry_run(pack: AttackPack, *, explain: bool = False) -> DryRunPlan:
    """Build a dry-run plan for ``pack`` (no executions)."""
    cases = [
        DryRunCase(
            case_id=case.id,
            target=case.target.type,
            expected=case.oracle.expect,
            evidence=list(case.oracle.expect_telemetry),
            exists_because=case.incident_ref if explain else "",
        )
        for case in pack.cases
    ]
    return DryRunPlan(cases=cases, executions=0)


def render_dry_run(plan: DryRunPlan) -> str:
    """Render a dry-run plan as text."""
    lines = [f"dry-run: {len(plan.cases)} case(s) (executions: {plan.executions})"]
    for case in plan.cases:
        detail = f"- {case.case_id} -> {case.target}: expect {case.expected}"
        if case.evidence:
            detail += f" [{', '.join(case.evidence)}]"
        if case.exists_because:
            detail += f" (because: {case.exists_because})"
        lines.append(detail)
    return "\n".join(lines) + "\n"
