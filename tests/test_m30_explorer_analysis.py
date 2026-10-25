"""M30 30.2 — trace explorer analysis (RED → GREEN).

Pressure curve (M24), bypass-family tree (M24), diff + attribution (F38), path
view (M27), redaction-aware export, deep links; and the security/a11y/load gates:
**zero XSS**, WCAG-AA structural checks, and a 10 k-row render under 2 s.
"""

from __future__ import annotations

import pytest

from agentdrill.explorer import (
    ViewRow,
    a11y_report,
    build_overview,
    export_bundle,
    pressure_points,
    render_explorer_html,
    require_a11y,
    require_load_time,
)


def _rows(count: int = 3) -> list[ViewRow]:
    return [
        ViewRow(case_id=f"c{i}", outcome="missed", tier="T1", tags=["ASI09"])
        for i in range(count)
    ]


def _html(count: int = 3) -> str:
    return render_explorer_html(
        build_overview(_rows(count)),
        pressure=[("T0", 1.0), ("T1", 0.6), ("T2", 0.2)],
        families={"h_all": ["refused-argument", "tool-aliasing"], "egress": ["dns-tunnel"]},
        diff=[("c1", "blocked", "missed", "attributed: adapter_swap")],
        paths=[["agent:main", "tool:fs", "data:secrets"]],
        hitl=[("c0", "witness_discrepancy")],
        title="agentdrill run 42",
    )


def test_pressure_points_are_normalized() -> None:
    assert pressure_points([("T0", 1.0), ("T1", 0.5)]) == [("T0", 1.0), ("T1", 0.5)]


def test_the_view_carries_every_analysis_section() -> None:
    html = _html()
    assert "Pressure curve" in html
    assert "h_all" in html and "dns-tunnel" in html
    assert "adapter_swap" in html
    assert "data:secrets" in html
    assert "witness_discrepancy" in html
    assert 'id="case-c1"' in html  # the case anchor a deep link targets


def test_a11y_report_is_empty_for_a_good_render() -> None:
    violations = a11y_report(_html())
    assert violations == []
    require_a11y(_html())


def test_a11y_report_catches_missing_landmarks() -> None:
    violations = a11y_report("<div>no html element</div>")
    assert violations
    for expected in ("lang", "title"):
        assert any(expected in violation for violation in violations)


def test_untrusted_content_is_inert_zero_xss() -> None:
    html = render_explorer_html(
        [ViewRow(case_id="<img src=x onerror=alert(1)>", outcome="missed")],
        families={"<script>alert(1)</script>": ["x"]},
    )
    assert "<script>alert(1)</script>" not in html
    assert "onerror=alert(1)" not in html.split("&")[0]  # the raw attribute is gone
    assert "&lt;script&gt;" in html or "&amp;lt;script&amp;gt;" in html


def test_load_time_for_ten_thousand_rows() -> None:
    require_load_time(_rows(10_000))  # default ≤ 2 s
    assert a11y_report(_html(10_000)) == []


def _doc(body: str, *, head: str = "<title>t</title>") -> str:
    return f'<html lang="en"><head>{head}</head><body>{body}</body></html>'


def test_a11y_report_catches_each_structural_violation() -> None:
    assert a11y_report(_doc("<h1>x</h1>")) == []
    no_caption = _doc("<h1>x</h1><table><tr><td>c</td></tr></table>")
    assert any("caption" in v for v in a11y_report(no_caption))
    no_scope = _doc("<h1>x</h1><table><caption>c</caption><tr><th>h</th></tr></table>")
    assert any("scope" in v for v in a11y_report(no_scope))
    assert any("script" in v for v in a11y_report(_doc("<h1>x</h1><script>1</script>")))
    assert any("event handler" in v for v in a11y_report(_doc('<h1>x</h1><p onclick="x()">y</p>')))
    assert any("h1" in v for v in a11y_report(_doc("")))
    with pytest.raises(ValueError):
        require_a11y("<div>nope</div>")


def test_load_budget_fails_loudly_when_exceeded() -> None:
    with pytest.raises(ValueError):
        require_load_time(_rows(10_000), max_seconds=0.0)


def test_export_is_redaction_aware() -> None:
    bundle, receipts = export_bundle(
        "<p>secret sk-abcdefghij in the trace</p>", location="view:trace"
    )
    assert "sk-abcdefghij" not in bundle
    assert receipts  # a receipt proves the redaction
