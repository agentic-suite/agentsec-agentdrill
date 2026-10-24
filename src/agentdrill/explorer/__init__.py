"""Trace explorer (M30, F102).

A local, offline run view with the defense-vs-witness panel. Design:
``docs/design/trace-explorer-and-platform-standards.md``; PRD 40 (R76).
"""

from agentdrill.explorer.view import (
    CaseView,
    DefenseWitnessPanel,
    HitlQueueItem,
    ViewRow,
    build_case_view,
    build_overview,
    deep_link,
    escape,
    filter_rows,
    hitl_queue,
    render_view_html,
)

__all__ = [
    "CaseView",
    "DefenseWitnessPanel",
    "HitlQueueItem",
    "ViewRow",
    "build_case_view",
    "build_overview",
    "deep_link",
    "escape",
    "filter_rows",
    "hitl_queue",
    "render_view_html",
]
