"""M26 26.1 — SARIF + JUnit emitters (RED → GREEN).

SARIF 2.1.0 (rule = case id; severity vector; tier; witness ref; ASI/ATLAS tags;
stable fingerprints; suppressions = waivers) and JUnit (``missed`` → failure,
``untested`` → skipped). Both must validate against their official schema; an
invalid finding fails loudly.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

if TYPE_CHECKING:
    from agentdrill.reporting import Report

from agentdrill.integrations import (
    IntegrationFinding,
    JUnitError,
    SarifError,
    WaiverRecord,
    apply_waivers,
    findings_from_report,
    to_junit,
    to_sarif,
    validate_junit,
    validate_sarif,
)


def _findings() -> list[IntegrationFinding]:
    return [
        IntegrationFinding(
            case_id="destructive-fs-wipe",
            pack="incidents-core@1.0.0+deadbeef",
            outcome="missed",
            severity="critical",
            tier="T1",
            k=5,
            witness_ref="witness:fs-canary-1",
            tags=["ATLAS-AML.T0053", "OWASP-A08"],
            rationale="un-blocked destructive delete",
            trace_ref="trace:abc",
        ),
        IntegrationFinding(
            case_id="exfil-secret",
            pack="incidents-core@1.0.0+deadbeef",
            outcome="blocked",
            severity="high",
            tier="T0",
            tags=["ATLAS-AML.T0048", "OWASP-A01"],
        ),
        IntegrationFinding(
            case_id="approval-abuse",
            pack="incidents-core@1.0.0+deadbeef",
            outcome="untested",
            severity="medium",
            tags=["ATLAS-AML.T0011", "OWASP-A02"],
        ),
    ]


def test_sarif_is_schema_valid() -> None:
    log = to_sarif(_findings())
    validate_sarif(log)
    assert log["version"] == "2.1.0"


def test_sarif_rule_is_the_case_id_with_properties() -> None:
    log = to_sarif(_findings())
    run = log["runs"][0]
    rules = run["tool"]["driver"]["rules"]
    assert [r["id"] for r in rules] == ["destructive-fs-wipe", "exfil-secret", "approval-abuse"]

    by_rule = {r["ruleId"]: r for r in run["results"]}
    missed = by_rule["destructive-fs-wipe"]
    assert missed["level"] == "error"
    props = missed["properties"]
    assert props["tier"] == "T1"
    assert props["k"] == 5
    assert props["witness"] == "witness:fs-canary-1"
    assert "ATLAS-AML.T0053" in props["tags"]
    assert "OWASP-A08" in props["tags"]
    assert props["severity"] == "critical"


def test_sarif_fingerprints_are_stable_across_runs() -> None:
    first = to_sarif(_findings())["runs"][0]["results"]
    second = to_sarif(_findings())["runs"][0]["results"]
    fps = [r["partialFingerprints"]["agentdrill/v1"] for r in first]
    assert fps == [r["partialFingerprints"]["agentdrill/v1"] for r in second]
    assert len(set(fps)) == len(fps)  # unique per case


def test_sarif_suppressions_come_from_waivers() -> None:
    findings = apply_waivers(
        _findings(), [WaiverRecord(case_id="exfil-secret", reason="known-miss")]
    )
    log = to_sarif(findings)
    results = {r["ruleId"]: r for r in log["runs"][0]["results"]}
    assert "suppressions" not in results["destructive-fs-wipe"]
    supp = results["exfil-secret"]["suppressions"]
    assert supp[0]["kind"] == "external"
    assert "known-miss" in supp[0]["justification"]
    validate_sarif(log)


def test_sarif_invalid_outcome_fails_loudly() -> None:
    with pytest.raises(ValidationError):
        IntegrationFinding(case_id="x", outcome="maybe")  # type: ignore[arg-type]


def test_findings_from_report_rejects_unknown_outcome() -> None:
    from agentdrill.oracles.engine import OutcomeSplit
    from agentdrill.reporting import Report, ReportRow

    report = Report(
        title="drill",
        pack_ref="p@1+0",
        generated="2026-10-24T00:00:00Z",
        outcome=OutcomeSplit(),
        rows=[ReportRow(case_id="c1", outcome="adapter_failed")],
    )
    with pytest.raises(ValueError):
        findings_from_report(report)


def test_validate_sarif_rejects_a_malformed_log() -> None:
    with pytest.raises(SarifError):
        validate_sarif({"version": "2.1.0"})


def test_junit_missed_is_failure_and_untested_is_skipped() -> None:
    xml = to_junit(_findings())
    validate_junit(xml)
    root = ET.fromstring(xml)  # noqa: S314 - the emitted document is our own
    suite = root.find("testsuite")
    assert suite is not None
    assert suite.get("tests") == "3"
    assert suite.get("failures") == "1"
    assert suite.get("skipped") == "1"
    cases = {c.get("name"): c for c in suite.findall("testcase")}
    assert cases["destructive-fs-wipe"].find("failure") is not None
    assert cases["approval-abuse"].find("skipped") is not None
    assert cases["exfil-secret"].find("failure") is None


def test_validate_junit_rejects_malformed_xml() -> None:
    with pytest.raises(JUnitError):
        validate_junit("<testsuite>")  # unclosed
    with pytest.raises(JUnitError):
        validate_junit("<notjunit/>")


def test_validate_junit_rejects_wrong_counts() -> None:
    xml = to_junit(_findings()).replace('failures="1"', 'failures="0"')
    with pytest.raises(JUnitError):
        validate_junit(xml)


def test_validate_junit_rejects_dtd_and_entities() -> None:
    dtd = '<?xml version="1.0"?><!DOCTYPE testsuite [<!ENTITY x "y">]><testsuite/>'
    with pytest.raises(JUnitError):
        validate_junit(dtd)


def test_validate_junit_rejects_empty_or_nameless_suites() -> None:
    with pytest.raises(JUnitError):
        validate_junit("<testsuites tests=\"0\"></testsuites>")
    with pytest.raises(JUnitError):
        validate_junit("<testsuite tests=\"1\" failures=\"0\" skipped=\"0\">"
                       "<testcase classname=\"c\"/></testsuite>")
    with pytest.raises(JUnitError):
        validate_junit("<testsuite failures=\"0\" skipped=\"0\"><testcase name=\"c\"/></testsuite>")


def test_degraded_is_a_failure_and_rule_id_is_the_case() -> None:
    finding = IntegrationFinding(case_id="partial-deny", outcome="degraded", rationale="partial")
    assert finding.rule_id == "partial-deny"
    xml = to_junit([finding])
    validate_junit(xml)
    assert 'failures="1"' in xml
    assert "degraded" in xml


def test_findings_from_report_projects_rows() -> None:
    report = _report()
    findings = findings_from_report(report)
    assert [f.case_id for f in findings] == ["c1", "c2"]
    assert findings[0].outcome == "missed"
    assert findings[0].pack == "incidents-core@1.0.0+deadbeef"
    log = to_sarif(findings)
    validate_sarif(log)
    assert json.dumps(log)  # serializable


def _report() -> Report:
    from agentdrill.oracles.engine import OutcomeSplit
    from agentdrill.reporting import Report, ReportRow

    return Report(
        title="drill",
        pack_ref="incidents-core@1.0.0+deadbeef",
        generated="2026-10-24T00:00:00Z",
        outcome=OutcomeSplit(blocked=1, missed=1, degraded=0),
        rows=[
            ReportRow(case_id="c1", tags=["ATLAS-AML.T0053", "OWASP-A08"], outcome="missed"),
            ReportRow(case_id="c2", tags=["ATLAS-AML.T0048", "OWASP-A01"], outcome="blocked"),
        ],
    )


def test_cli_export_sarif_from_report(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main

    report_path = tmp_path / "report.json"
    report_path.write_text(_report().model_dump_json(), encoding="utf-8")
    out = tmp_path / "out.sarif"
    result = CliRunner().invoke(
        main, ["export", "sarif", "--report", str(report_path), "--out", str(out)]
    )
    assert result.exit_code == 0, result.output
    log = json.loads(out.read_text(encoding="utf-8"))
    validate_sarif(log)
    assert log["runs"][0]["results"][0]["ruleId"] == "c1"


def test_cli_export_junit_from_report(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main

    report_path = tmp_path / "report.json"
    report_path.write_text(_report().model_dump_json(), encoding="utf-8")
    result = CliRunner().invoke(main, ["export", "junit", "--report", str(report_path)])
    assert result.exit_code == 0, result.output
    validate_junit(result.output)
    assert "<testsuites" in result.output
