"""M30 30.6 — standards master table + pins + evidence index (RED -> GREEN).

A master standards table with version pins and a **drift watcher** (pins updated
<= 30 d); ASI coverage incl. `untested`; an **ATLAS-mitigation** mapping; and a
per-framework evidence index that lists `not covered` **explicitly** (a silent
"fully covered" claim is refused).
"""

from __future__ import annotations

import pytest

from agentdrill.standards import (
    EvidenceIndexEntry,
    StandardPin,
    StandardsError,
    asi_coverage_table,
    atlas_mitigation_mapping,
    build_evidence_index,
    detect_drift,
    require_explicit_gaps,
    require_no_drift,
    require_pins_current,
)


def _pins() -> list[StandardPin]:
    return [
        StandardPin(name="MITRE ATLAS", version="2026.01", updated="2026-01-10"),
        StandardPin(name="OWASP ASI", version="2025.11", updated="2026-01-10"),
    ]


def test_drift_is_detected_and_gated() -> None:
    published = {"MITRE ATLAS": "2026.01", "OWASP ASI": "2026.02"}
    drift = detect_drift(_pins(), published)
    assert len(drift) == 1
    assert drift[0].standard == "OWASP ASI"
    assert drift[0].pinned == "2025.11" and drift[0].published == "2026.02"
    with pytest.raises(StandardsError):
        require_no_drift(_pins(), published)
    require_no_drift(_pins(), {"MITRE ATLAS": "2026.01", "OWASP ASI": "2025.11"})


def test_pins_must_be_current_within_thirty_days() -> None:
    require_pins_current(_pins(), now="2026-02-01")  # 22 days
    with pytest.raises(StandardsError):
        require_pins_current(_pins(), now="2026-03-15")  # > 30 days


def test_asi_coverage_marks_untested() -> None:
    table = asi_coverage_table(["ASI01", "ASI03"])
    assert table["ASI01"] == "verified"
    assert table["ASI06"] == "untested"
    assert len(table) == 10


def test_atlas_mitigation_mapping_is_populated() -> None:
    mapping = atlas_mitigation_mapping()
    assert mapping
    assert all(technique.startswith("ATLAS-") for technique in mapping)
    assert all(mitigation for mitigation in mapping.values())


def test_evidence_index_lists_explicit_gaps() -> None:
    index = build_evidence_index(
        {
            "EU AI Act Art.12": (["logging"], ["human oversight"]),
            "NIST AI RMF": (["govern"], []),
        }
    )
    assert isinstance(index[0], EvidenceIndexEntry)
    assert index[0].not_covered == ["human oversight"]
    with pytest.raises(StandardsError):
        require_explicit_gaps(index)  # NIST has no gaps and no explicit "fully covered"

    declared = build_evidence_index(
        {"NIST AI RMF": (["govern"], [])}, fully_covered=["NIST AI RMF"]
    )
    require_explicit_gaps(declared)
