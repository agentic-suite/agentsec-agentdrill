"""M23 23.5 — two-oracle verdict + integrity, F87 (RED → GREEN).

Compare the defense decision x the witness → blocked / missed / degraded /
blocked_silently / witness_discrepancy; `witness_unavailable`; a live/none
label. Disagreement is a first-class finding.
"""

from __future__ import annotations

from agentdrill.witness import TwoOracleVerdict, two_oracle_verdict


def test_defense_blocked_but_effect_seen_is_a_discrepancy() -> None:
    verdict = two_oracle_verdict("c1", defense="blocked", effect_seen=True)
    assert isinstance(verdict, TwoOracleVerdict)
    assert verdict.verdict == "witness_discrepancy"
    assert verdict.finding == "witness_discrepancy"
    assert verdict.witness_label == "live"


def test_defense_blocked_and_no_effect_is_blocked() -> None:
    assert two_oracle_verdict("c1", defense="blocked", effect_seen=False).verdict == "blocked"


def test_defense_missed_and_effect_seen_is_missed() -> None:
    assert two_oracle_verdict("c1", defense="missed", effect_seen=True).verdict == "missed"


def test_defense_missed_and_no_effect_is_blocked_silently() -> None:
    assert (
        two_oracle_verdict("c1", defense="missed", effect_seen=False).verdict == "blocked_silently"
    )


def test_witness_unavailable_is_labeled() -> None:
    verdict = two_oracle_verdict(
        "c1", defense="blocked", effect_seen=False, witness_available=False
    )
    assert verdict.witness_label == "none"
    assert verdict.finding == "witness_unavailable"
