"""Trace explorer (M30, F102).

A local, offline run view with the defense-vs-witness panel. Design:
``docs/design/trace-explorer-and-platform-standards.md``; PRD 40 (R76).
"""

from agentdrill.explorer.analysis import (
    DEFAULT_LOAD_SECONDS,
    a11y_report,
    export_bundle,
    pressure_points,
    render_explorer_html,
    require_a11y,
    require_load_time,
)
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
    "DEFAULT_LOAD_SECONDS",
    "CaseView",
    "DefenseWitnessPanel",
    "HitlQueueItem",
    "ViewRow",
    "a11y_report",
    "build_case_view",
    "build_overview",
    "deep_link",
    "escape",
    "export_bundle",
    "filter_rows",
    "hitl_queue",
    "pressure_points",
    "render_explorer_html",
    "render_view_html",
    "require_a11y",
    "require_load_time",
]
