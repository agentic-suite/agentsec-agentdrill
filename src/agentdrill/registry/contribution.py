"""Contribution flow (M16 16.4).

``init`` scaffold → ``pack lint`` → independent review → ``pack publish`` →
``pack verify``. The lint gates schema, tags, ``incident_ref``, oracle,
fixtures and methodology; an **unreviewed** (or external) pack cannot be
benchmark-published. Design: ``docs/prd/17-pack-registry-and-governance.md``.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, Field

from agentdrill.interop.tagging import untagged_cases
from agentdrill.loading.attack_catalog import missing_fixtures
from agentdrill.loading.attack_registry import ORACLE_EXPECTATIONS
from agentdrill.models.attack_pack import AttackPack
from agentdrill.registry.trust import is_benchmark_publishable


class ContributionError(ValueError):
    """Raised when a pack is not publishable (unreviewed, external, or lint-failing)."""


class LintFinding(BaseModel):
    """One lint check result."""

    check: str
    ok: bool
    detail: str = ""


class LintResult(BaseModel):
    """The full lint result for a pack."""

    findings: list[LintFinding] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether every lint check passed."""
        return all(finding.ok for finding in self.findings)


class ReviewDecision(BaseModel):
    """An independent review decision for a pack ref."""

    pack_ref: str
    reviewer: str
    approved: bool = False


def lint_pack(
    pack: AttackPack,
    *,
    fixtures_dir: str | Path,
    methodology: str | None,
) -> LintResult:
    """Lint a contribution: schema, tags, incident_ref, oracle, fixtures, methodology."""
    findings: list[LintFinding] = []

    findings.append(
        LintFinding(
            check="schema",
            ok=bool(pack.pack.name and pack.pack.version),
            detail="pack name + version present",
        )
    )

    missing_incident = [c.id for c in pack.cases if not c.incident_ref]
    findings.append(
        LintFinding(
            check="incident_ref",
            ok=not missing_incident,
            detail=f"cases missing incident_ref: {missing_incident}",
        )
    )

    missing_tags = [c.id for c in pack.cases if not c.tags]
    findings.append(
        LintFinding(
            check="tags",
            ok=not missing_tags,
            detail=f"cases missing tags: {missing_tags}",
        )
    )

    bad_oracles = [c.id for c in pack.cases if c.oracle.expect not in ORACLE_EXPECTATIONS]
    findings.append(
        LintFinding(
            check="oracle",
            ok=not bad_oracles,
            detail=f"cases with an unknown oracle expectation: {bad_oracles}",
        )
    )

    missing = missing_fixtures(pack, fixtures_dir)
    findings.append(
        LintFinding(
            check="fixtures",
            ok=not missing,
            detail=f"tools without fixtures: {sorted(missing)}",
        )
    )

    untagged = untagged_cases(pack)
    findings.append(
        LintFinding(
            check="standards",
            ok=not untagged,
            detail=f"cases missing ATLAS/OWASP tags: {untagged}",
        )
    )

    findings.append(
        LintFinding(
            check="methodology",
            ok=bool(methodology),
            detail="methodology path present" if methodology else "no methodology supplied",
        )
    )

    return LintResult(findings=findings)


def require_publishable(
    pack_ref: str,
    *,
    trust: str,
    decisions: Iterable[ReviewDecision],
) -> None:
    """Fail loudly unless ``pack_ref`` is approved and benchmark-publishable.

    Raises:
        ContributionError: The pack is external, or has no approved review.
    """
    if not is_benchmark_publishable(trust):
        raise ContributionError(f"pack {pack_ref}: an external pack cannot be benchmark-published")
    approved = anyone_approved(pack_ref, decisions)
    if not approved:
        raise ContributionError(
            f"pack {pack_ref}: no approved independent review — cannot be benchmark-published"
        )


def anyone_approved(pack_ref: str, decisions: Iterable[ReviewDecision]) -> bool:
    """Whether ``pack_ref`` has an approved review decision."""
    return any(d.pack_ref == pack_ref and d.approved for d in decisions)
