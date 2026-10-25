"""M17 17.4 — compliance-mapped reporting, F24 (RED → GREEN).

Findings mapped to EU AI Act Art. 12, NIST AI RMF and ISO 42001; an evidence
export to agentcomply generates offline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdrill.interop import (
    FRAMEWORKS,
    ComplianceError,
    ComplianceReport,
    build_compliance_report,
    export_agentcomply,
    map_finding,
)


def test_finding_maps_to_three_frameworks() -> None:
    mapping = map_finding("safety_miss")
    assert set(mapping.frameworks) == set(FRAMEWORKS)
    assert mapping.frameworks["eu_ai_act_art12"]


def test_unknown_finding_type_fails_loudly() -> None:
    with pytest.raises(ComplianceError, match="zorp"):
        map_finding("zorp")


def test_compliance_report_generates_offline(tmp_path: Path) -> None:
    report = build_compliance_report(
        [("c1", "safety_miss"), ("c2", "kill_slow")], generated="2026-10-23T00:00:00Z"
    )
    assert isinstance(report, ComplianceReport)
    data = json.loads(report.model_dump_json())
    assert data["rows"][0]["finding_type"] == "safety_miss"
    assert "nist_ai_rmf" in data["rows"][0]["frameworks"]


def test_report_rows_carry_control_ids() -> None:
    report = build_compliance_report([("c1", "safety_miss")], generated="t")
    row = report.rows[0]
    assert row.case_id == "c1"
    assert row.frameworks["iso_42001"]


def test_export_to_agentcomply_writes_a_file(tmp_path: Path) -> None:
    report = build_compliance_report([("c1", "safety_miss")], generated="t")
    path = export_agentcomply(report, tmp_path / "compliance")
    assert path.exists()
    assert "safety_miss" in path.read_text(encoding="utf-8")
