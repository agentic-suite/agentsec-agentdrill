"""M29 29.2 — Break-It program (RED → GREEN).

A pinned reference range + a structured proof-of-bypass **auto-verified by the
witness**; triage SLA + severity; coordinated disclosure (fix window, embargo,
CVE/CWE); and conversion of an accepted bypass into a permanent regression (F61)
plus the route-family catalogue.
"""

from __future__ import annotations

import pytest

from agentdrill.breakit import (
    BreakItError,
    BypassSubmission,
    auto_verified_rate,
    convert_to_regression,
    dedup_families,
    family_catalogue,
    require_auto_verified,
    require_disclosure_timeline,
    require_triage_sla,
    triage,
    verify_proof,
)


def _submission(**over: object) -> BypassSubmission:
    base = dict(id="b1", route="refused-argument:h_all", effect_goal="forbidden_write")
    base.update(over)
    return BypassSubmission.model_validate(base)


def test_proof_is_auto_verified_by_the_witness() -> None:
    verified = verify_proof(_submission(), witness_effect="forbidden_write")
    assert verified.proof is not None
    assert verified.proof.verified is True
    assert verified.proof.witness_effect == "forbidden_write"

    unverified = verify_proof(_submission(), witness_effect="something-else")
    assert unverified.proof is not None
    assert unverified.proof.verified is False


def test_triage_accepts_only_a_verified_bypass() -> None:
    accepted = triage(
        _submission(), witness_effect="forbidden_write", ack_hours=6, now="2026-02-01"
    )
    assert accepted.accepted is True
    assert accepted.timeline is not None
    require_disclosure_timeline(accepted.timeline)

    refused = triage(_submission(), witness_effect="nope", ack_hours=6, now="2026-02-01")
    assert refused.accepted is False
    assert refused.timeline is None


def test_triage_sla_and_disclosure_window() -> None:
    require_triage_sla(ack_hours=12)
    with pytest.raises(BreakItError):
        require_triage_sla(ack_hours=48)  # ack ≤ 24 h

    timeline = triage(
        _submission(), witness_effect="forbidden_write", ack_hours=1, now="2026-02-01"
    ).timeline
    assert timeline is not None
    with pytest.raises(BreakItError):
        require_disclosure_timeline(timeline.model_copy(update={"fix_window_days": 5}))
    with pytest.raises(BreakItError):
        require_disclosure_timeline(timeline.model_copy(update={"embargo_days": 10}))


def test_auto_verified_rate_gate_and_family_catalogue() -> None:
    good = [
        triage(
            _submission(id=f"b{i}"),
            witness_effect="forbidden_write",
            ack_hours=1,
            now="2026-02-01",
        )
        for i in range(5)
    ]
    bad = [triage(_submission(id="bx"), witness_effect="nope", ack_hours=1, now="2026-02-01")]
    submissions = [*good, *bad]
    assert auto_verified_rate(submissions) == pytest.approx(5 / 6)
    require_auto_verified(submissions)  # ≥80%
    with pytest.raises(BreakItError):
        require_auto_verified(bad)

    catalogue = family_catalogue(
        [*good, _submission(id="b9", route="tool-aliasing:h_all")]
    )
    assert catalogue["h_all"] == 6
    assert sum(catalogue.values()) == 6
    # family-level dedup keeps one representative route per family
    assert dedup_families([*good, _submission(id="b9", route="tool-aliasing:h_all")]) == [
        "refused-argument:h_all"
    ]


def test_an_empty_program_is_fully_verified() -> None:
    assert auto_verified_rate([]) == 1.0


def test_accepted_bypass_converts_to_a_permanent_regression() -> None:
    accepted = triage(
        _submission(), witness_effect="forbidden_write", ack_hours=1, now="2026-02-01"
    )
    case = convert_to_regression(accepted, fix_commit="deadbeef")
    assert case.pinned is True
    assert case.fix_commit == "deadbeef"
    assert case.case_id == "bypass-forbidden_write"
    with pytest.raises(BreakItError):
        convert_to_regression(
            triage(_submission(), witness_effect="nope", ack_hours=1, now="2026-02-01"),
            fix_commit="deadbeef",
        )
