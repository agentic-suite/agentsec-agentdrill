"""M10 10.6 — coverage heat-map, F53 (RED → GREEN).

A pack/tag x control matrix with cells blocked / partial / missed / untested,
plus a delta against a previous release.
"""

from __future__ import annotations

from agentdrill.reporting import HeatMap, HeatMapDelta, Report, ReportRow, build_heatmap


def _report(*rows: ReportRow) -> Report:
    return Report(
        title="t",
        pack_ref="p@1.0.0+deadbeef",
        generated="2026-10-23T00:00:00Z",
        rows=list(rows),
    )


def _row(case_id: str, outcome: str, tags: list[str], pack: str = "p") -> ReportRow:
    return ReportRow(case_id=case_id, outcome=outcome, tags=tags, pack=pack)


def test_all_blocked_cell_is_blocked() -> None:
    hm = build_heatmap(
        _report(_row("c1", "blocked", ["destructive"]), _row("c2", "blocked", ["destructive"]))
    )
    assert isinstance(hm, HeatMap)
    assert hm.status("p", "destructive") == "blocked"


def test_mixed_cell_is_partial() -> None:
    hm = build_heatmap(
        _report(_row("c1", "blocked", ["destructive"]), _row("c2", "missed", ["destructive"]))
    )
    assert hm.status("p", "destructive") == "partial"


def test_all_missed_cell_is_missed() -> None:
    hm = build_heatmap(
        _report(_row("c1", "missed", ["secret"]), _row("c2", "degraded", ["secret"]))
    )
    assert hm.status("p", "secret") == "missed"


def test_absent_cell_is_untested() -> None:
    hm = build_heatmap(_report(_row("c1", "blocked", ["destructive"])))
    assert hm.status("p", "nope") == "untested"


def test_delta_reports_a_status_change() -> None:
    before = build_heatmap(_report(_row("c1", "blocked", ["destructive"])))
    after = build_heatmap(_report(_row("c1", "missed", ["destructive"])))
    delta = before.delta(after)
    assert len(delta) == 1
    assert isinstance(delta[0], HeatMapDelta)
    assert delta[0].pack == "p"
    assert delta[0].control == "destructive"
    assert delta[0].previous == "blocked"
    assert delta[0].current == "missed"


def test_delta_is_empty_when_nothing_changed() -> None:
    report = _report(_row("c1", "blocked", ["destructive"]))
    assert build_heatmap(report).delta(build_heatmap(report)) == []
