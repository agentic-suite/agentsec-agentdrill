"""M7 7.2 — evidence binding (RED → GREEN).

Every result references the agentwatch evidence behind it; a result with no
evidence yields an explicit `evidence_gap` finding — never a silent pass.
"""

from __future__ import annotations

from typing import Any

from agentdrill.evidence.binding import EvidenceBinding, bind_all, bind_case, evidence_gap
from agentdrill.evidence.schema import read_events

EVENTS: list[dict[str, Any]] = [
    {"event": "denied", "ref": "evt-1", "case_id": "c1"},
    {"event": "halted", "ref": "evt-2", "case_id": "c1"},
    {"event": "policy-fired", "ref": "evt-3", "case_id": "c2"},
]


def _events() -> Any:
    return read_events(EVENTS)


def test_bind_case_collects_refs() -> None:
    binding = bind_case("c1", _events())
    assert isinstance(binding, EvidenceBinding)
    assert binding.refs == ["evt-1", "evt-2"]
    assert binding.gap is False


def test_bind_case_without_evidence_is_gap() -> None:
    binding = bind_case("c3", _events())
    assert binding.refs == []
    assert binding.gap is True


def test_evidence_gap_finding() -> None:
    binding = bind_case("c3", _events())
    finding = evidence_gap(binding)
    assert finding is not None
    assert finding.type == "evidence_gap"
    assert finding.case_id == "c3"


def test_no_finding_when_evidence_present() -> None:
    assert evidence_gap(bind_case("c1", _events())) is None


def test_bind_all() -> None:
    bindings = bind_all(["c1", "c2", "c3"], _events())
    by_id = {b.case_id: b for b in bindings}
    assert by_id["c1"].gap is False
    assert by_id["c2"].gap is False
    assert by_id["c3"].gap is True
