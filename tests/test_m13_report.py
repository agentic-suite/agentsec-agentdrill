"""M13 13.5 — efficacy report artifact (RED → GREEN).

Efficacy status per case is shipped in the evidence bundle (CUJ-11), so
efficacy is visible per case.
"""

from __future__ import annotations

from agentdrill.efficacy import (
    CaseEfficacy,
    EfficacyReport,
    build_efficacy_report,
    efficacy_evidence,
    run_efficacy,
)
from agentdrill.models.evidence import Evidence


def _verified(case_id: str, guarded: str):
    return run_efficacy(case_id, unguarded=lambda: True, guarded_outcome=guarded)


def _inert(case_id: str):
    return run_efficacy(case_id, unguarded=lambda: False, guarded_outcome="blocked")


def test_report_has_efficacy_status_per_case() -> None:
    report = build_efficacy_report([_verified("c1", "blocked"), _inert("c2")])
    assert isinstance(report, EfficacyReport)
    entry = report.for_case("c1")
    assert isinstance(entry, CaseEfficacy)
    assert entry.efficacy_verified is True
    assert entry.flag is None


def test_inert_case_carries_the_flag() -> None:
    report = build_efficacy_report([_inert("c2")])
    assert report.for_case("c2").flag == "attack_inert"


def test_missing_case_is_absent() -> None:
    assert build_efficacy_report([_verified("c1", "blocked")]).for_case("nope") is None


def test_efficacy_evidence_is_shipped_in_the_bundle() -> None:
    bundle: list[Evidence] = []
    bundle.append(efficacy_evidence(_inert("c2")))
    assert isinstance(bundle[0], Evidence)
    assert bundle[0].event == "efficacy"
    assert "attack_inert" in bundle[0].summary


def test_efficacy_report_round_trips() -> None:
    report = build_efficacy_report([_verified("c1", "blocked")])
    assert EfficacyReport.model_validate_json(report.model_dump_json()) == report
