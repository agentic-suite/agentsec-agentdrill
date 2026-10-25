"""M18 18.3 — seam probing, F62 (RED → GREEN).

Denied-then-retried + multi-enforcer composition cases; `seam_gap` names **both**
controls involved in the composition gap.
"""

from __future__ import annotations

from agentdrill.lifecycle import SEAM_GAP, SeamFinding, probe_seam


def test_denied_then_retried_through_is_a_seam_gap() -> None:
    finding = probe_seam(
        "c1",
        first_control="policyweave-output",
        second_control="agentgate",
        first_denied=True,
        second_allowed=True,
    )
    assert isinstance(finding, SeamFinding)
    assert finding.gap == SEAM_GAP
    assert set(finding.controls) == {"policyweave-output", "agentgate"}


def test_the_gap_names_both_controls() -> None:
    finding = probe_seam(
        "c1",
        first_control="policyweave-output",
        second_control="agenthalt",
        first_denied=True,
        second_allowed=True,
    )
    assert "policyweave-output" in finding.detail
    assert "agenthalt" in finding.detail


def test_no_gap_when_the_retry_is_also_denied() -> None:
    assert (
        probe_seam(
            "c1",
            first_control="a",
            second_control="b",
            first_denied=True,
            second_allowed=False,
        )
        is None
    )


def test_no_gap_when_the_first_control_did_not_deny() -> None:
    assert (
        probe_seam(
            "c1",
            first_control="a",
            second_control="b",
            first_denied=False,
            second_allowed=True,
        )
        is None
    )
