"""Trace explorer - analysis (M30 30.2, F102).

The analysis half of the view: the **pressure curve** (M24), the **bypass-family
tree** (M24), the **diff + attribution** (F38), the **attack-path view** (M27),
the **HITL queue**, a **redaction-aware export** (F27/F65), deep links -- and the
gates that make the viewer safe to ship: **zero XSS** (all untrusted content is
escaped and inert), WCAG 2.2 **AA** structural checks, and a 10 k-row render
budget. Design: ``docs/design/trace-explorer-and-platform-standards.md``; PRD 40
(R76).
"""

from __future__ import annotations

import re
import time
from collections.abc import Mapping, Sequence

from agentdrill.explorer.view import ViewRow, escape
from agentdrill.lifecycle.privacy import Receipt, redact

#: The default render budget for a 10 k-row view, in seconds.
DEFAULT_LOAD_SECONDS = 2.0

#: Inline event-handler attributes that must never appear in the view.
_EVENT_HANDLER = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)


def pressure_points(curve: Sequence[tuple[str, float]]) -> list[tuple[str, float]]:
    """Normalize an M24 pressure curve into ``(tier, hold_ratio)`` points."""
    return [(tier, ratio) for tier, ratio in curve]


def _table(rows: Sequence[ViewRow]) -> str:
    body = "\n".join(
        f'<tr id="case-{escape(row.case_id)}"><td>{escape(row.case_id)}</td>'
        f"<td>{escape(row.outcome)}</td><td>{escape(row.tier or '')}</td></tr>"
        for row in rows
    )
    return (
        "<table>\n<caption>Run overview</caption>\n"
        '<thead><tr><th scope="col">Case</th><th scope="col">Outcome</th>'
        '<th scope="col">Tier</th></tr></thead>\n'
        f"<tbody>\n{body}\n</tbody>\n</table>"
    )


def _pressure_section(points: Sequence[tuple[str, float]]) -> str:
    items = "".join(f"<li>Hold@{escape(tier)}: {ratio:.0%}</li>" for tier, ratio in points)
    return (
        '<section aria-labelledby="pressure"><h2 id="pressure">Pressure curve</h2>'
        f"<ul>{items}</ul></section>"
    )


def _family_section(families: Mapping[str, Sequence[str]]) -> str:
    groups = "".join(
        f"<li>{escape(family)}<ul>"
        + "".join(f"<li>{escape(route)}</li>" for route in routes)
        + "</ul></li>"
        for family, routes in families.items()
    )
    return (
        '<section aria-labelledby="families"><h2 id="families">Bypass families</h2>'
        f"<ul>{groups}</ul></section>"
    )


def _diff_section(changes: Sequence[tuple[str, str, str, str]]) -> str:
    items = "".join(
        f"<li>{escape(case_id)}: {escape(before)} -> {escape(after)} "
        f"({escape(attribution)})</li>"
        for case_id, before, after, attribution in changes
    )
    return (
        '<section aria-labelledby="diff"><h2 id="diff">Diff &amp; attribution</h2>'
        f"<ul>{items}</ul></section>"
    )


def _path_section(paths: Sequence[Sequence[str]]) -> str:
    items = "".join(
        f"<li>{' &rarr; '.join(escape(node) for node in path)}</li>" for path in paths
    )
    return (
        '<section aria-labelledby="paths"><h2 id="paths">Attack paths</h2>'
        f"<ul>{items}</ul></section>"
    )


def _hitl_section(queue: Sequence[tuple[str, str]]) -> str:
    items = "".join(
        f"<li>{escape(case_id)}: {escape(reason)}</li>" for case_id, reason in queue
    )
    return (
        '<section aria-labelledby="hitl"><h2 id="hitl">HITL queue</h2>'
        f"<ul>{items}</ul></section>"
    )


def render_explorer_html(
    rows: Sequence[ViewRow],
    *,
    pressure: Sequence[tuple[str, float]] = (),
    families: Mapping[str, Sequence[str]] | None = None,
    diff: Sequence[tuple[str, str, str, str]] = (),
    paths: Sequence[Sequence[str]] = (),
    hitl: Sequence[tuple[str, str]] = (),
    title: str = "agentdrill run",
) -> str:
    """Render the full, inert, accessible explorer view (no scripts, no network)."""
    sections = [
        _pressure_section(pressure),
        _family_section(families or {}),
        _diff_section(diff),
        _path_section(paths),
        _hitl_section(hitl),
    ]
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n</head>\n<body>\n"
        f"<main>\n<h1>{escape(title)}</h1>\n"
        f"{_table(rows)}\n"
        f"{''.join(sections)}\n"
        "</main>\n</body>\n</html>\n"
    )


def a11y_report(html: str) -> list[str]:
    """Structural WCAG 2.2 AA checks; the empty list means the view passes."""
    violations: list[str] = []
    if 'lang="' not in html:
        violations.append("missing <html lang>")
    if "<title>" not in html:
        violations.append("missing <title>")
    if html.count("<h1") != 1:
        violations.append("must have exactly one <h1>")
    if "<table>" in html and "<caption>" not in html:
        violations.append("every <table> needs a <caption>")
    if "<th" in html and 'scope="' not in html:
        violations.append("<th> needs a scope attribute")
    if "<script" in html.lower():
        violations.append("no <script> is allowed (inert rendering)")
    if _EVENT_HANDLER.search(html):
        violations.append("no inline event handler is allowed (inert rendering)")
    return violations


def require_a11y(html: str) -> None:
    """Fail loudly unless the view passes the a11y/inert checks.

    Raises:
        ValueError: One or more a11y/inert violations were found.
    """
    violations = a11y_report(html)
    if violations:
        raise ValueError(f"view failed the a11y/inert checks: {violations}")


def require_load_time(
    rows: Sequence[ViewRow], *, max_seconds: float = DEFAULT_LOAD_SECONDS
) -> None:
    """Fail loudly unless rendering ``rows`` stays within the budget.

    Raises:
        ValueError: The render exceeded ``max_seconds``.
    """
    start = time.perf_counter()
    render_explorer_html(rows)
    elapsed = time.perf_counter() - start
    if elapsed > max_seconds:
        raise ValueError(
            f"view render took {elapsed:.2f}s for {len(rows)} rows "
            f"(budget {max_seconds}s)"
        )


def export_bundle(content: str, *, location: str) -> tuple[str, list[Receipt]]:
    """Redact ``content`` for sharing; return the bundle and its receipts (F27/F65)."""
    result = redact(content, location=location)
    return result.redacted, result.receipts
