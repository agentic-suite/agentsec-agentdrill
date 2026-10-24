"""Incident-to-pack compiler (M27, F94).

Dedup intake feeds, filter by inventory relevance, build a cite-or-drop brief,
and compile a reviewed draft pack (twin + cleanup + witness effects +
preregistered outcome, dual-use screened, HITL-gated). Design:
``docs/design/backtest-path-intake.md``; PRD 32 (R68).
"""

from agentdrill.intake.compiler import (
    DRAFT_TARGET,
    DRAFT_TRUST,
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

__all__ = [
    "DRAFT_TARGET",
    "DRAFT_TRUST",
    "DraftPack",
    "DualUseScreen",
    "Fact",
    "IncidentBrief",
    "IntakeError",
    "IntakeItem",
    "approve_draft",
    "build_brief",
    "compile_incident",
    "dedup",
    "relevance",
    "require_all_facts_cited",
    "require_approved",
    "require_dual_use_clean",
    "screen_dual_use",
]
