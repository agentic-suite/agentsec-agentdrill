"""M26 26.3 — OCSF/ECS + OSCAL + STIX emitters (RED → GREEN).

SIEM/lake events (OCSF detection finding + ECS), OSCAL assessment-results and
POA&M, and STIX 2.1 bundles (adversary card + findings). Each emitter ships a
validator that fails loudly on a malformed document.
"""

from __future__ import annotations

import pytest

from agentdrill.integrations import (
    ECS_VERSION,
    OCSF_VERSION,
    OSCAL_VERSION,
    STIX_VERSION,
    ECSValidationError,
    IntegrationFinding,
    OCSFValidationError,
    OSCALValidationError,
    STIXValidationError,
    to_ecs_events,
    to_ocsf_findings,
    to_oscal_assessment_results,
    to_oscal_poam,
    to_stix_bundle,
    validate_ecs,
    validate_ocsf,
    validate_oscal,
    validate_stix,
)
from agentdrill.interop.profiles import AdversaryProfile


def _findings() -> list[IntegrationFinding]:
    return [
        IntegrationFinding(
            case_id="destructive-fs-wipe",
            pack="incidents-core@1.0.0+deadbeef",
            outcome="missed",
            severity="critical",
            tier="T1",
            witness_ref="witness:fs-canary-1",
            tags=["ATLAS-AML.T0053", "OWASP-A08"],
            rationale="un-blocked destructive delete",
        ),
        IntegrationFinding(
            case_id="exfil-secret",
            pack="incidents-core@1.0.0+deadbeef",
            outcome="blocked",
            severity="low",
            tags=["ATLAS-AML.T0048", "OWASP-A01"],
        ),
    ]


def test_ocsf_detection_findings_are_valid() -> None:
    events = to_ocsf_findings(_findings(), timestamp_ms=1730000000000)
    validate_ocsf(events)
    first = events[0]
    assert first["class_uid"] == 2004
    assert first["category_uid"] == 2
    assert first["metadata"]["version"] == OCSF_VERSION
    assert first["time"] == 1730000000000
    assert first["severity_id"] == 5  # critical
    assert first["finding_info"]["uid"] == "destructive-fs-wipe"
    assert first["attacks"][0]["technique"]["uid"] == "AML.T0053"


def test_ocsf_waived_finding_is_suppressed() -> None:
    waived = IntegrationFinding(
        case_id="c", outcome="blocked", waived=True, waiver_reason="accepted"
    )
    (event,) = to_ocsf_findings([waived])
    validate_ocsf([event])
    assert event["status_id"] == 3  # Suppressed


def test_ocsf_fails_loudly() -> None:
    with pytest.raises(OCSFValidationError):
        validate_ocsf([{"class_uid": 2004}])  # missing required fields


def test_ecs_events_are_valid() -> None:
    events = to_ecs_events(_findings())
    validate_ecs(events)
    assert events[0]["event"]["kind"] == "alert"
    assert events[0]["event"]["outcome"] == "failure"  # missed
    assert ECS_VERSION.startswith("8.")


def test_ecs_fails_loudly() -> None:
    with pytest.raises(ECSValidationError):
        validate_ecs([{"event": {"kind": "alert"}}])


def test_oscal_assessment_results_are_valid() -> None:
    doc = to_oscal_assessment_results(
        _findings(), title="drill", start="2026-10-24T00:00:00Z", end="2026-10-24T00:01:00Z"
    )
    validate_oscal(doc)
    result = doc["assessment-results"]
    assert result["metadata"]["oscal-version"] == OSCAL_VERSION
    assert result["results"][0]["findings"][0]["target"]["target-id"] == "destructive-fs-wipe"


def test_oscal_poam_lists_open_findings() -> None:
    doc = to_oscal_poam(_findings(), title="drill")
    validate_oscal(doc)
    items = doc["plan-of-action-and-milestones"]["poam-items"]
    assert [i["title"] for i in items] == ["destructive-fs-wipe"]


def test_oscal_fails_loudly() -> None:
    with pytest.raises(OSCALValidationError):
        validate_oscal({"assessment-results": {}})


def test_stix_bundle_is_valid_with_adversary_card() -> None:
    profile = AdversaryProfile(
        who="APT-X", what="data theft", source="intel feed", objective="exfiltrate secrets"
    )
    bundle = to_stix_bundle(_findings(), profile=profile)
    validate_stix(bundle)
    assert bundle["type"] == "bundle"
    assert bundle["spec_version"] == STIX_VERSION
    types = [o["type"] for o in bundle["objects"]]
    assert "threat-actor" in types
    assert "identity" in types
    assert "vulnerability" in types
    threat = next(o for o in bundle["objects"] if o["type"] == "threat-actor")
    assert threat["name"] == "APT-X"


def test_stix_fails_loudly_on_a_bad_id() -> None:
    bundle = to_stix_bundle(_findings())
    bundle["objects"][0]["id"] = "wrong--123"
    with pytest.raises(STIXValidationError):
        validate_stix(bundle)


def test_cli_export_ocsf_oscal_stix(tmp_path) -> None:
    import json

    from click.testing import CliRunner

    from agentdrill.cli.__main__ import main
    from agentdrill.oracles.engine import OutcomeSplit
    from agentdrill.reporting import Report, ReportRow

    report = Report(
        title="drill",
        pack_ref="incidents-core@1.0.0+deadbeef",
        generated="2026-10-24T00:00:00Z",
        outcome=OutcomeSplit(missed=1),
        rows=[ReportRow(case_id="c1", tags=["ATLAS-AML.T0053"], outcome="missed")],
    )
    report_path = tmp_path / "report.json"
    report_path.write_text(report.model_dump_json(), encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(main, ["export", "ocsf", "--report", str(report_path)])
    assert result.exit_code == 0, result.output
    validate_ocsf(json.loads(result.output))

    result = runner.invoke(main, ["export", "oscal", "--report", str(report_path)])
    assert result.exit_code == 0, result.output
    validate_oscal(json.loads(result.output))

    result = runner.invoke(main, ["export", "stix", "--report", str(report_path)])
    assert result.exit_code == 0, result.output
    validate_stix(json.loads(result.output))


def test_ocsf_validator_rejects_each_bad_field() -> None:
    def bad(**overrides: object) -> list[dict]:
        event = to_ocsf_findings(_findings()[:1], timestamp_ms=1)[0]
        event.update(overrides)
        return [event]

    for overrides in (
        {"class_uid": 1},
        {"category_uid": 9},
        {"severity_id": 99},
        {"severity_id": "high"},
        {"time": "now"},
        {"metadata": {}},
        {"finding_info": {"uid": "", "title": ""}},
    ):
        with pytest.raises(OCSFValidationError):
            validate_ocsf(bad(**overrides))


def test_ecs_validator_rejects_each_bad_field() -> None:
    def bad(mutate) -> list[dict]:
        event = to_ecs_events(_findings()[:1])[0]
        mutate(event)
        return [event]

    with pytest.raises(ECSValidationError):
        validate_ecs([{"event": {"kind": "alert"}}])  # missing @timestamp
    with pytest.raises(ECSValidationError):
        validate_ecs([{"@timestamp": "t", "event": "nope"}])
    for mutate in (
        lambda e: e["event"].pop("action"),
        lambda e: e["event"].__setitem__("kind", "event"),
        lambda e: e["event"].__setitem__("category", []),
        lambda e: e["event"].__setitem__("outcome", "maybe"),
    ):
        with pytest.raises(ECSValidationError):
            validate_ecs(bad(mutate))


def test_stix_validator_rejects_each_bad_field() -> None:
    def bad(mutate) -> dict:
        bundle = to_stix_bundle(_findings())
        mutate(bundle)
        return bundle

    for mutate in (
        lambda b: b.__setitem__("type", "not-bundle"),
        lambda b: b.__setitem__("spec_version", "2.0"),
        lambda b: b.__setitem__("id", "bundle--123"),
        lambda b: b.__setitem__("objects", "nope"),
        lambda b: b["objects"][0].pop("created"),
        lambda b: b["objects"][0].__setitem__("spec_version", "2.0"),
        lambda b: b["objects"][0].__setitem__("name", ""),
        lambda b: next(o for o in b["objects"] if o["type"] == "relationship").pop(
            "relationship_type"
        ),
    ):
        with pytest.raises(STIXValidationError):
            validate_stix(bad(mutate))


def test_oscal_validator_rejects_each_bad_field() -> None:
    with pytest.raises(OSCALValidationError):
        validate_oscal({"assessment-results": {}})
    with pytest.raises(OSCALValidationError):
        validate_oscal({"unknown-model": {}})

    document = to_oscal_assessment_results(_findings(), title="drill")
    document["assessment-results"]["metadata"]["oscal-version"] = "0.0"
    with pytest.raises(OSCALValidationError):
        validate_oscal(document)

    document = to_oscal_assessment_results(_findings(), title="drill")
    document["assessment-results"]["results"][0].pop("findings")
    with pytest.raises(OSCALValidationError):
        validate_oscal(document)

    document = to_oscal_assessment_results(_findings(), title="drill")
    document["assessment-results"]["results"] = "nope"
    with pytest.raises(OSCALValidationError):
        validate_oscal(document)

    poam = to_oscal_poam(_findings(), title="drill")
    poam["plan-of-action-and-milestones"]["poam-items"][0].pop("title")
    with pytest.raises(OSCALValidationError):
        validate_oscal(poam)

    poam = to_oscal_poam(_findings(), title="drill")
    poam["plan-of-action-and-milestones"]["poam-items"] = "nope"
    with pytest.raises(OSCALValidationError):
        validate_oscal(poam)
