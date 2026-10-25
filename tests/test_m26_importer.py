"""M26 26.5 — inbound import (RED → GREEN).

Normalize external results from **Inspect / promptfoo / garak / AgentDojo /
PyRIT** into imported findings (marked ``imported``, lower trust), plus an
inventory import. 5/5 sources must map ≥ 95 % of their records; an unknown
source or a below-threshold mapping fails loudly.
"""

from __future__ import annotations

import pytest

from agentdrill.integrations import (
    IMPORTED_SOURCES,
    IMPORTED_TRUST,
    ImportedResult,
    IngestError,
    import_results,
    mapping_report,
    parse_inventory,
    require_mapping,
    to_imported_findings,
)

_FIXTURES = {
    "inspect": {"samples": [{"id": "s1", "scores": {"blocked": 1}}, {"id": "s2", "scores": {}}]},
    "promptfoo": {"results": {"results": [{"vars": {"case_id": "p1"}, "success": False}]}},
    "garak": {
        "results": [
            {"probe": "probe.A", "passed": False},
            {"probe": "probe.B", "passed": True},
        ]
    },
    "agentdojo": {
        "results": [
            {"task_id": "t1", "security": False},
            {"task_id": "t2", "security": True},
        ]
    },
    "pyrit": {"results": [{"objective": "o1", "score": 0.9}, {"objective": "o2", "score": 0.0}]},
}


def test_five_sources_are_supported() -> None:
    assert IMPORTED_SOURCES == ("inspect", "promptfoo", "garak", "agentdojo", "pyrit")


def test_every_source_maps_its_records() -> None:
    for source, data in _FIXTURES.items():
        results = import_results(data, source)
        assert results, source
        assert all(isinstance(r, ImportedResult) for r in results)
        assert all(r.source == source for r in results)
        assert all(r.trust == IMPORTED_TRUST for r in results)


def test_mapping_coverage_is_five_of_five_above_threshold() -> None:
    for source, data in _FIXTURES.items():
        mapped, total, coverage = mapping_report(data, source)
        assert mapped == total, source
        assert coverage >= 0.95
        require_mapping(data, source)


def test_findings_are_marked_imported() -> None:
    findings = to_imported_findings(import_results(_FIXTURES["garak"], "garak"))
    assert findings
    assert all("imported" in f.tags for f in findings)
    assert findings[0].case_id == "probe.A"


def test_unknown_source_fails_loudly() -> None:
    with pytest.raises(IngestError):
        import_results({"results": []}, "myspace")


def test_unmappable_records_lower_coverage_and_fail_the_gate() -> None:
    data = {"results": [{"probe": "ok", "passed": True}, {"nope": 1}]}
    mapped, total, coverage = mapping_report(data, "garak")
    assert (mapped, total) == (1, 2)
    assert coverage == 0.5
    with pytest.raises(IngestError):
        require_mapping(data, "garak")


def test_imported_result_normalizes_the_outcome() -> None:
    results = import_results(_FIXTURES["promptfoo"], "promptfoo")
    assert results[0].outcome == "missed"  # success=False ⇒ the external tool did not block
    assert results[0].case_id == "p1"


def test_inventory_import() -> None:
    items = parse_inventory({"inventory": [{"id": "mcp.fs", "kind": "tool", "name": "filesystem"}]})
    assert items[0].id == "mcp.fs"
    assert items[0].kind == "tool"


def test_importer_tolerates_odd_shapes_and_fails_loudly() -> None:
    with pytest.raises(IngestError):
        import_results(42, "garak")
    with pytest.raises(IngestError):
        mapping_report({"results": []}, "myspace")

    # Non-dict records and a missing identity are skipped, not mis-mapped.
    assert import_results([1, 2], "garak") == []

    # A non-numeric score reports an unreported outcome, not a guess.
    result = import_results([{"id": "x", "score": "abc"}], "pyrit")[0]
    assert result.outcome == "untested"
    assert result.blocked is None

    # Inventory ignores non-dict entries.
    assert parse_inventory([1, 2]) == []
    assert require_mapping({"results": [{"probe": "ok"}]}, "garak") is None
    assert mapping_report({"results": []}, "garak") == (0, 0, 1.0)
