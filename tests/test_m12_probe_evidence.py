"""M12 12.6 — evidence for the cessation probe (RED → GREEN).

The re-attempt is recorded in the evidence bundle (what, when, result), so the
probe is auditable.
"""

from __future__ import annotations

from agentdrill.killchain import probe_evidence, run_cessation_probe
from agentdrill.models.evidence import Evidence


def _still_acting():  # the guarded action still succeeds after revoke
    return run_cessation_probe(
        "c1", revoke=lambda: None, reattempt=lambda: True, action="drop database prod"
    )


def test_probe_records_a_reproof_evidence_event() -> None:
    evidence = probe_evidence(_still_acting(), at="2026-10-23T00:00:01Z")
    assert isinstance(evidence, Evidence)
    assert evidence.event == "cease-probe"


def test_evidence_names_what_when_and_result() -> None:
    evidence = probe_evidence(_still_acting(), at="2026-10-23T00:00:01Z")
    assert "drop database prod" in evidence.summary  # what
    assert "2026-10-23T00:00:01Z" in evidence.summary  # when
    assert "still acting" in evidence.summary  # result


def test_evidence_ref_points_at_the_case() -> None:
    assert probe_evidence(_still_acting(), at="t").ref == "c1"


def test_a_ceased_probe_records_ceased() -> None:
    ceased = run_cessation_probe("c2", revoke=lambda: None, reattempt=lambda: False)
    assert "ceased" in probe_evidence(ceased, at="t").summary


def test_probe_evidence_attaches_to_a_bundle() -> None:
    bundle: list[Evidence] = []
    bundle.append(probe_evidence(_still_acting(), at="t"))
    assert bundle[0].event == "cease-probe"
