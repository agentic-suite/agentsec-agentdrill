"""M27 27.6 — incident-to-pack compiler (RED → GREEN).

Turn an advisory into a reviewed pack fast: dedup feeds, filter by inventory
relevance, build a **cite-or-drop** brief (uncited facts dropped), draft a pack
with a twin + cleanup + witness effects + a preregistered outcome, run the
dual-use screen, and gate the draft behind HITL review.
"""

from __future__ import annotations

import pytest

from agentdrill.intake import (
    DraftPack,
    DualUseScreen,
    Fact,
    IncidentBrief,
    IntakeError,
    IntakeItem,
    approve_draft,
    build_brief,
    compile_incident,
    dedup,
    relevance,
    require_all_facts_cited,
    require_approved,
    require_dual_use_clean,
    screen_dual_use,
)
from agentdrill.witness import require_effects


def _item() -> IntakeItem:
    return IntakeItem(
        source="GHSA",
        external_id="GHSA-xxxx-yyyy",
        title="MCP filesystem write bypass",
        summary="an advisory touching the filesystem tool",
        facts=[
            Fact(
                text="filesystem tool can write",
                citation="https://ghsa.example/1",
                tool="filesystem",
            ),
            Fact(text="uncited rumor of a wider bypass"),  # no citation → dropped
        ],
        references=["https://ghsa.example/1"],
    )


def test_dedup_keeps_one_of_each_advisory() -> None:
    assert dedup([_item(), _item()]) == [_item()]
    other = _item().model_copy(update={"external_id": "GHSA-zzzz"})
    assert len(dedup([_item(), other])) == 2


def test_relevance_scores_against_inventory() -> None:
    inventory = ["filesystem", "mcp_server", "secrets"]
    assert relevance(_item(), inventory) >= 1
    assert relevance(_item(), ["unrelated-capability"]) == 0


def test_brief_is_cite_or_drop() -> None:
    brief = build_brief(_item())
    assert [f.text for f in brief.cited_facts] == ["filesystem tool can write"]
    assert brief.dropped_facts == ["uncited rumor of a wider bypass"]
    require_all_facts_cited(brief)
    assert "https://ghsa.example/1" in brief.citations


def test_compile_produces_a_draft_with_twin_cleanup_effects_and_outcome() -> None:
    draft = compile_incident(
        _item(), inventory=["filesystem", "mcp_server"], case_id="c1", twin_id="t1"
    )
    assert isinstance(draft, DraftPack)
    case = draft.pack.cases[0]
    assert case.id == "c1"
    assert case.benign_twin == "t1"
    assert case.cleanup and case.cleanup[0].cmd
    assert case.oracle.expect == "blocked"  # preregistered outcome
    assert draft.effects.case_id == "c1"
    require_effects(draft.effects)  # the witness effects are declared
    assert draft.dual_use.clean is True
    require_dual_use_clean(draft)
    assert draft.approved is False


def test_compile_refuses_an_irrelevant_advisory() -> None:
    with pytest.raises(IntakeError):
        compile_incident(_item(), inventory=["unrelated-capability"], case_id="c1")


def test_dual_use_screen_flags_an_off_inventory_step() -> None:
    draft = compile_incident(_item(), inventory=["filesystem"], case_id="c1")
    screen = screen_dual_use(draft.brief, draft.pack, ["unrelated-capability"])
    assert screen.clean is False
    assert any("filesystem" in flag for flag in screen.flags)


def test_dual_use_screen_and_defensive_gates() -> None:
    draft = compile_incident(_item(), inventory=["filesystem"], case_id="c1")

    empty = draft.brief.model_copy(update={"cited_facts": []})
    assert "no_cited_facts" in screen_dual_use(empty, draft.pack, ["filesystem"]).flags

    unattested = draft.brief.model_copy(
        update={"cited_facts": [Fact(text="other", citation="u", tool="other")]}
    )
    flags = screen_dual_use(unattested, draft.pack, ["filesystem", "other"]).flags
    assert any("uncited_step" in flag for flag in flags)

    dirty = draft.model_copy(update={"dual_use": DualUseScreen(flags=["x"], clean=False)})
    with pytest.raises(IntakeError):
        require_dual_use_clean(dirty)

    # defensive invariant: a surviving fact without a citation is refused
    brief = IncidentBrief(source="s", external_id="e", title="t", cited_facts=[Fact(text="x")])
    with pytest.raises(IntakeError):
        require_all_facts_cited(brief)


def test_hitl_gate() -> None:
    draft = compile_incident(_item(), inventory=["filesystem"], case_id="c1")
    with pytest.raises(IntakeError):
        require_approved(draft)
    with pytest.raises(IntakeError):
        approve_draft(draft, reviewer="agentdrill", drafter="agentdrill")
    approved = approve_draft(draft, reviewer="alice@example.com")
    assert approved.approved is True
    require_approved(approved)
