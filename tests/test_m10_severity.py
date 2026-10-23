"""M10 10.5 — severity rubric, F41 (RED → GREEN).

Findings are scored by attack-class x exposure with a rationale, and are
sortable across packs.
"""

from __future__ import annotations

import pytest

from agentdrill.reporting import RatedFinding, rate_finding, sort_findings


def test_privileged_destructive_is_critical() -> None:
    finding = rate_finding("c1", attack_class="destructive", exposure="privileged")
    assert isinstance(finding, RatedFinding)
    assert finding.severity == "critical"
    assert finding.case_id == "c1"


def test_external_injection_is_low() -> None:
    assert rate_finding("c2", attack_class="injection", exposure="external").severity == "low"


def test_rationale_names_class_and_exposure() -> None:
    finding = rate_finding("c1", attack_class="destructive", exposure="internal")
    assert "destructive" in finding.rationale
    assert "internal" in finding.rationale


def test_findings_sort_by_severity_across_packs() -> None:
    findings = [
        rate_finding("low", attack_class="injection", exposure="external", pack="p2"),
        rate_finding("crit", attack_class="destructive", exposure="privileged", pack="p1"),
        rate_finding("med", attack_class="exfiltration", exposure="external", pack="p1"),
    ]
    ordered = sort_findings(findings)
    assert [f.case_id for f in ordered] == ["crit", "med", "low"]


def test_unknown_class_is_rejected() -> None:
    with pytest.raises(ValueError, match="attack_class"):
        rate_finding("c", attack_class="telepathy", exposure="internal")


def test_unknown_exposure_is_rejected() -> None:
    with pytest.raises(ValueError, match="exposure"):
        rate_finding("c", attack_class="destructive", exposure="cosmic")
