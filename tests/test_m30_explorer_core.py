"""M30 30.1 - trace explorer core (RED → GREEN).

A local, offline run view: overview (outcome x tier x witness; `untested` always
visible; filters), case step-through with a **defense-vs-witness** panel
(`witness_discrepancy` highlighted), a stage timeline, and a HITL queue.
"""

from __future__ import annotations

from agentdrill.explorer import (
    CaseView,
    DefenseWitnessPanel,
    HitlQueueItem,
    ViewRow,
    build_case_view,
    build_overview,
    deep_link,
    filter_rows,
    hitl_queue,
    render_view_html,
)


def _rows() -> list[ViewRow]:
    return [
        ViewRow(
            case_id="wipe",
            outcome="missed",
            tier="T1",
            witness="witness:fs-canary",
            tags=["ATLAS-AML.T0053"],
            severity="critical",
            defense_decision="allowed",
            witness_effect="file-deleted",
            witness_discrepancy=True,
        ),
        ViewRow(case_id="exfil", outcome="blocked", tier="T0", tags=["ATLAS-AML.T0048"]),
        ViewRow(case_id="approval", outcome="untested", tier="T2", tags=["ASI09"]),
    ]


def test_overview_never_hides_untested() -> None:
    overview = build_overview(_rows())
    assert [row.case_id for row in overview] == ["wipe", "exfil", "approval"]
    assert any(row.outcome == "untested" for row in overview)


def test_filters_by_outcome_tier_and_tag() -> None:
    rows = _rows()
    assert [r.case_id for r in filter_rows(rows, outcome="missed")] == ["wipe"]
    assert [r.case_id for r in filter_rows(rows, tier="T0")] == ["exfil"]
    assert [r.case_id for r in filter_rows(rows, tag="ASI09")] == ["approval"]
    assert filter_rows(rows, outcome="nope") == []


def test_case_view_has_steps_stages_and_a_defense_vs_witness_panel() -> None:
    view = build_case_view(
        _rows()[0],
        steps=["read", "write /etc/hosts", "delete /var/data"],
        stages=[("detect", 12.5), ("decide", 4.0), ("halt", 900.0)],
    )
    assert isinstance(view, CaseView)
    panel = view.panel
    assert isinstance(panel, DefenseWitnessPanel)
    assert panel.decision == "allowed"
    assert panel.effect == "file-deleted"
    assert panel.discrepancy is True
    assert [stage for stage, _ in view.stages] == ["detect", "decide", "halt"]


def test_hitl_queue_lists_discrepancies_and_degraded() -> None:
    rows = [*_rows(), ViewRow(case_id="slow", outcome="degraded")]
    queue = hitl_queue(rows)
    assert all(isinstance(item, HitlQueueItem) for item in queue)
    assert [item.case_id for item in queue] == ["wipe", "slow"]


def test_deep_links() -> None:
    assert deep_link("wipe") == "#case-wipe"
    assert deep_link("wipe", base="view.html") == "view.html#case-wipe"


def test_html_escapes_untrusted_content() -> None:
    evil = ViewRow(
        case_id="<script>alert(1)</script>", outcome="missed", defense_decision="<b>x</b>"
    )
    html = render_view_html([evil], cases=[build_case_view(evil, steps=["<img src=x onerror=1>"])])
    assert "&lt;script&gt;" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;b&gt;" in html
