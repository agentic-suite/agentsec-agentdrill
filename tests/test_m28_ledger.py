"""M28 28.1 — finding lifecycle + exposure ledger (RED → GREEN).

The lifecycle ``open → triaged → fix_in_progress → fixed → verified_fixed →
decayed`` plus side states (`accepted_risk`/`false_positive`/`wont_fix`); a
per-finding CVSS v4.0 + AIVSS vector that is **never aggregated**; and an
immutable honest outcome so a miss stays a miss.
"""

from __future__ import annotations

import pytest

from agentdrill.ledger import (
    SIDE_STATES,
    Finding,
    Ledger,
    LedgerError,
    SeverityVector,
    composite_score,
    is_integrity,
    open_finding,
    transition,
)


def _finding(**overrides: object) -> Finding:
    base = dict(
        id="f1",
        case_id="destructive-fs-wipe",
        pack="incidents-core@1.0.0+deadbeef",
        outcome="missed",
        dimension="enforcement",
        title="un-blocked destructive delete",
        severity=SeverityVector(
            cvss="CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H", aivss="AIVSS:4.0/..."
        ),
    )
    base.update(overrides)
    return Finding.model_validate(base)


def test_side_states_are_the_documented_three() -> None:
    assert SIDE_STATES == ("accepted_risk", "false_positive", "wont_fix")


def test_open_and_forward_lifecycle() -> None:
    entry = open_finding(_finding())
    assert entry.finding.status == "open"
    for nxt in ("triaged", "fix_in_progress", "fixed"):
        entry = transition(entry, nxt, actor="alice", reason="working")
    assert entry.finding.status == "fixed"
    assert [t.to_status for t in entry.history] == [
        "open",
        "triaged",
        "fix_in_progress",
        "fixed",
    ]


def test_illegal_transition_fails_loudly() -> None:
    entry = open_finding(_finding())
    with pytest.raises(LedgerError):
        transition(entry, "fixed", actor="alice")  # open → fixed is not allowed


def test_verified_fixed_requires_verification() -> None:
    entry = open_finding(_finding())
    entry = transition(entry, "triaged", actor="a")
    entry = transition(entry, "fix_in_progress", actor="a")
    entry = transition(entry, "fixed", actor="a")
    with pytest.raises(LedgerError):
        transition(entry, "verified_fixed", actor="a")  # unverified ⇒ refused
    entry = transition(entry, "verified_fixed", actor="a", fix_verified=True)
    assert entry.finding.status == "verified_fixed"


def test_decay_and_reopen() -> None:
    entry = open_finding(_finding())
    entry = transition(entry, "triaged", actor="a")
    entry = transition(entry, "fix_in_progress", actor="a")
    entry = transition(entry, "fixed", actor="a")
    entry = transition(entry, "verified_fixed", actor="a", fix_verified=True)
    entry = transition(entry, "decayed", actor="a", reason="fix stopped holding")
    assert entry.finding.status == "decayed"
    entry = transition(entry, "open", actor="a", reason="reopened")
    assert entry.finding.status == "open"


def test_a_miss_stays_a_miss_through_every_transition() -> None:
    entry = open_finding(_finding())
    entry = transition(entry, "accepted_risk", actor="a", reason="signed off")
    assert entry.finding.outcome == "missed"  # the label never changes
    assert entry.finding.status == "accepted_risk"


def test_integrity_findings_are_recognized() -> None:
    assert is_integrity(_finding(dimension="integrity")) is True
    assert is_integrity(_finding()) is False


def test_no_composite_score_is_ever_produced() -> None:
    with pytest.raises(LedgerError):
        composite_score([_finding()])


def test_ledger_never_hides_a_finding() -> None:
    ledger = Ledger()
    ledger.record(open_finding(_finding()))
    ledger.record(open_finding(_finding(id="f2", outcome="blocked")))
    assert len(ledger.all()) == 2
    assert {e.finding.id for e in ledger.all()} == {"f1", "f2"}
    assert ledger.get("f1").finding.id == "f1"
    with pytest.raises(LedgerError):
        ledger.get("nope")


def test_unknown_status_transition_fails_loudly() -> None:
    entry = open_finding(_finding())
    with pytest.raises(LedgerError):
        transition(entry, "bogus", actor="a")
