"""Reporting package (M10) — honest, multi-format run reports.

The reporter renders one run to JSON / Markdown / GitHub-Actions / self-contained
HTML / PDF (M10 10.1), enforcing the honesty rules: misses mandatory,
multi-seed numbers, bootstrap CIs, no composite score. Design:
``docs/design/reporting.md``.
"""

from agentdrill.reporting.model import Report, ReportRow
from agentdrill.reporting.render import (
    Format,
    render,
    render_github_actions,
    render_html,
    render_json,
    render_markdown,
    render_pdf,
)

__all__ = [
    "Format",
    "Report",
    "ReportRow",
    "render",
    "render_github_actions",
    "render_html",
    "render_json",
    "render_markdown",
    "render_pdf",
]
