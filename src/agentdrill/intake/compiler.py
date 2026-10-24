"""Incident-to-pack compiler (M27 27.6, F94).

Turn a fresh advisory into a reviewed pack fast: **dedup** intake feeds, filter by
**relevance** against the capability inventory, build a **cite-or-drop** incident
brief (uncited facts are dropped, never kept), draft a pack with a benign twin, a
cleanup step, declared **witness effects** (M23) and a **preregistered outcome**,
run the **dual-use screen**, then gate the draft behind **HITL** review
(reviewer ≠ drafter). Intake content is untrusted — the draft is a product of the
cited facts, never of invented payloads. Design:
``docs/design/backtest-path-intake.md``; PRD 32 (R68).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.models.attack_pack import AttackPack
from agentdrill.witness.effects import Effect, EffectDeclaration

#: The default pack trust for an intake draft (unreviewed).
DRAFT_TRUST = "local"

#: The default port for a compiled draft.
DRAFT_TARGET = "policyweave-output"


class IntakeError(ValueError):
    """Raised when an advisory cannot be compiled, or a draft ships unreviewed."""


class Fact(BaseModel):
    """One fact from an advisory, with its citation and (optional) capability."""

    text: str
    citation: str | None = None
    tool: str | None = None


class IntakeItem(BaseModel):
    """One advisory / intake feed record."""

    source: str
    external_id: str
    title: str
    summary: str = ""
    facts: list[Fact] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class IncidentBrief(BaseModel):
    """A cite-or-drop brief: only cited facts survive."""

    source: str
    external_id: str
    title: str
    cited_facts: list[Fact] = Field(default_factory=list)
    dropped_facts: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class DualUseScreen(BaseModel):
    """The dual-use screen result for a draft."""

    flags: list[str] = Field(default_factory=list)
    clean: bool


class DraftPack(BaseModel):
    """A compiled draft pack, gated behind HITL review."""

    pack: AttackPack
    brief: IncidentBrief
    effects: EffectDeclaration
    dual_use: DualUseScreen
    approved: bool = False
    reviewer: str | None = None
    drafter: str = "agentdrill"


def dedup(items: Sequence[IntakeItem]) -> list[IntakeItem]:
    """Deduplicate advisories by ``(source, external_id)``, preserving order."""
    seen: set[tuple[str, str]] = set()
    unique: list[IntakeItem] = []
    for item in items:
        key = (item.source, item.external_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def relevance(item: IntakeItem, inventory: Sequence[str]) -> int:
    """How many inventory capabilities the advisory mentions (case-insensitive)."""
    haystack = " ".join([item.title, item.summary, *(fact.text for fact in item.facts)]).lower()
    return sum(1 for capability in inventory if capability.lower() in haystack)


def build_brief(item: IntakeItem) -> IncidentBrief:
    """Build a cite-or-drop brief (uncited facts are dropped, and listed)."""
    cited = [fact for fact in item.facts if fact.citation]
    dropped = [fact.text for fact in item.facts if not fact.citation]
    citations = sorted({*item.references, *(fact.citation for fact in cited if fact.citation)})
    return IncidentBrief(
        source=item.source,
        external_id=item.external_id,
        title=item.title,
        cited_facts=cited,
        dropped_facts=dropped,
        citations=list(citations),
    )


def require_all_facts_cited(brief: IncidentBrief) -> None:
    """Fail loudly unless every fact that survived the brief carries a citation.

    Raises:
        IntakeError: A surviving fact has no citation (100 % facts cited).
    """
    uncited = [fact.text for fact in brief.cited_facts if not fact.citation]
    if uncited:
        raise IntakeError(f"brief {brief.external_id} kept uncited facts: {uncited}")


def screen_dual_use(
    brief: IncidentBrief, pack: AttackPack, inventory: Sequence[str]
) -> DualUseScreen:
    """Flag a draft whose steps are off-inventory or unattested by the brief."""
    flags: list[str] = []
    if not brief.cited_facts:
        flags.append("no_cited_facts")
    attested = {fact.tool for fact in brief.cited_facts if fact.tool}
    allowed = set(inventory)
    for case in pack.cases:
        for step in case.attack.steps:
            if step.tool not in allowed:
                flags.append(f"off_inventory_step: {step.tool}")
            if step.tool not in attested:
                flags.append(f"uncited_step: {step.tool}")
    return DualUseScreen(flags=flags, clean=not flags)


def compile_incident(
    item: IntakeItem,
    *,
    inventory: Sequence[str],
    case_id: str,
    twin_id: str | None = None,
    cleanup_cmd: str = "run-cleanup",
    effects: EffectDeclaration | None = None,
) -> DraftPack:
    """Compile an advisory into a draft pack.

    Raises:
        IntakeError: No cited fact references the capability inventory (an
            irrelevant advisory must not become a pack).
    """
    brief = build_brief(item)
    allowed = set(inventory)
    relevant = [fact for fact in brief.cited_facts if fact.tool and fact.tool in allowed]
    if not relevant:
        raise IntakeError(
            f"{item.source}:{item.external_id} has no cited fact referencing the inventory"
        )
    steps: list[dict[str, Any]] = [{"tool": fact.tool, "args": {}} for fact in relevant]
    if effects is None:
        effects = EffectDeclaration(
            case_id=case_id,
            forbidden=[Effect(kind="unauthorized_action", target=relevant[0].tool or "")],
        )
    pack = AttackPack.model_validate(
        {
            "pack": {
                "name": f"intake-{item.external_id}",
                "version": "1.0.0",
                "description": item.title,
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": DRAFT_TRUST,
            },
            "cases": [
                {
                    "id": case_id,
                    "title": item.title,
                    "goal": "Verify the deployed stack stops the ingested incident",
                    "incident_ref": f"{item.source}:{item.external_id}",
                    "target": {"type": DRAFT_TARGET},
                    "driver": {"type": "subprocess"},
                    "attack": {"steps": steps},
                    "oracle": {"expect": "blocked"},
                    "benign_twin": twin_id,
                    "cleanup": [{"cmd": cleanup_cmd}],
                    "tags": ["intake", item.source, f"origin:{item.source}"],
                }
            ],
        }
    )
    return DraftPack(
        pack=pack,
        brief=brief,
        effects=effects,
        dual_use=screen_dual_use(brief, pack, inventory),
    )


def require_dual_use_clean(draft: DraftPack) -> None:
    """Fail loudly unless the dual-use screen is clean.

    Raises:
        IntakeError: The screen flagged the draft.
    """
    if not draft.dual_use.clean:
        raise IntakeError(
            f"draft {draft.pack.cases[0].id!r} failed the dual-use screen: "
            f"{draft.dual_use.flags}"
        )


def approve_draft(
    draft: DraftPack, *, reviewer: str, drafter: str = "agentdrill"
) -> DraftPack:
    """Approve a compiled draft (HITL).

    Raises:
        IntakeError: The reviewer is the drafter (independent review required).
    """
    if reviewer == drafter:
        raise IntakeError("HITL review requires a reviewer independent of the drafter")
    return draft.model_copy(update={"approved": True, "reviewer": reviewer})


def require_approved(draft: DraftPack) -> None:
    """Fail loudly unless the draft was approved by a reviewer.

    Raises:
        IntakeError: The draft is unreviewed.
    """
    if not draft.approved:
        raise IntakeError(
            f"draft {draft.pack.cases[0].id!r} is unreviewed; "
            "HITL review is required before it ships"
        )
