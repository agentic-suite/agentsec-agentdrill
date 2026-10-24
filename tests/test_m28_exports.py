"""M28 28.3 — ledger exports (RED → GREEN).

Export the ledger to OSCAL POA&M / assessment-results and SARIF (waivers →
suppressions), and derive ticket-status updates. The exports reuse the M26
emitters (single source of truth) and validate against their schemas; the M26
``WaiverRecord`` seam is re-pointed at this ledger.
"""

from __future__ import annotations

from agentdrill.integrations import (
    IntegrationFinding,
    WaiverRecord,
    validate_oscal,
    validate_sarif,
)
from agentdrill.ledger import (
    Finding,
    Ledger,
    SeverityVector,
    Waiver,
    create_waiver,
    export_oscal_assessment_results,
    export_oscal_poam,
    export_sarif,
    findings_from_ledger,
    open_finding,
    ticket_updates,
    to_waiver_record,
    transition,
)


def _finding(finding_id: str, case_id: str, outcome: str = "missed", **over: object) -> Finding:
    base = dict(
        id=finding_id,
        case_id=case_id,
        pack="p@1.0.0+dead",
        outcome=outcome,
        dimension="enforcement",
        title=case_id,
        severity=SeverityVector(cvss="CVSS:4.0/..."),
        severity_level="high",
    )
    base.update(over)
    return Finding.model_validate(base)


def _ledger() -> Ledger:
    ledger = Ledger()
    ledger.record(open_finding(_finding("f1", "missed-case")))  # open miss
    fixed = open_finding(_finding("f2", "fixed-case"))
    fixed = transition(fixed, "triaged", actor="a")
    fixed = transition(fixed, "fix_in_progress", actor="a")
    fixed = transition(fixed, "fixed", actor="a")
    fixed = transition(fixed, "verified_fixed", actor="a", fix_verified=True)
    ledger.record(fixed)
    ledger.record(open_finding(_finding("f3", "waived-case")))
    return ledger


def _waivers() -> list[Waiver]:
    return [
        create_waiver(
            _finding("f3", "waived-case"),
            waiver_id="w3",
            reason="accepted risk",
            compensating_control="egress blocked",
            approvers=["ciso@example.com"],
            now="2026-01-01",
        )
    ]


def test_findings_projection_marks_waivers() -> None:
    findings = findings_from_ledger(_ledger(), _waivers(), now="2026-02-01")
    by_case = {f.case_id: f for f in findings}
    assert isinstance(by_case["missed-case"], IntegrationFinding)
    assert by_case["missed-case"].waived is False
    assert by_case["waived-case"].waived is True
    assert by_case["waived-case"].waiver_reason == "accepted risk"
    assert by_case["missed-case"].outcome == "missed"


def test_waiver_record_is_a_projection_of_the_ledger_waiver() -> None:
    waiver = _waivers()[0]
    record = to_waiver_record(waiver)
    assert isinstance(record, WaiverRecord)
    assert record.case_id == "waived-case"
    assert record.reason == "accepted risk"


def test_sarif_export_validates_and_suppresses_the_waiver() -> None:
    log = export_sarif(_ledger(), _waivers(), now="2026-02-01")
    validate_sarif(log)
    results = {r["ruleId"]: r for r in log["runs"][0]["results"]}
    assert results["missed-case"]["level"] == "error"
    assert "suppressions" in results["waived-case"]
    assert "suppressions" not in results["missed-case"]


def test_oscal_exports_validate() -> None:
    poam = export_oscal_poam(_ledger(), _waivers(), title="Q1", now="2026-02-01")
    validate_oscal(poam)
    assert [i["title"] for i in poam["plan-of-action-and-milestones"]["poam-items"]] == [
        "missed-case"
    ]

    results = export_oscal_assessment_results(_ledger(), _waivers(), title="Q1", now="2026-02-01")
    validate_oscal(results)
    assert results["assessment-results"]["results"][0]["findings"]


def test_expired_waiver_is_not_exported_as_a_suppression() -> None:
    log = export_sarif(_ledger(), _waivers(), now="2026-12-01")  # past the waiver expiry
    results = {r["ruleId"]: r for r in log["runs"][0]["results"]}
    assert "suppressions" not in results["waived-case"]


def test_ticket_updates_reflect_status_and_waivers() -> None:
    updates = {u.finding_id: u for u in ticket_updates(_ledger(), _waivers(), now="2026-02-01")}
    assert updates["f1"].state == "open"
    assert updates["f2"].state == "resolved"
    assert updates["f3"].state == "suppressed"
    assert updates["f1"].key == "p@1.0.0+dead:missed-case"


def test_empty_ledger_exports_are_valid() -> None:
    empty = Ledger()
    validate_sarif(export_sarif(empty, [], now="2026-02-01"))
    validate_oscal(export_oscal_poam(empty, [], title="t", now="2026-02-01"))
    validate_oscal(export_oscal_assessment_results(empty, [], title="t", now="2026-02-01"))
    assert ticket_updates(empty, [], now="2026-02-01") == []
    assert findings_from_ledger(empty, [], now="2026-02-01") == []
