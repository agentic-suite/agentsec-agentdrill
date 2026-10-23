"""M12 12.2 — cessation probe (RED → GREEN).

Drive the revoke, then **re-attempt the guarded action**: if it still succeeds,
the target is *not* ceased — `ceased` is measured, never believed.
"""

from __future__ import annotations

from agentdrill.killchain import ProbeResult, run_cessation_probe


def test_still_acting_after_revoke_is_not_ceased() -> None:
    calls: list[str] = []
    result = run_cessation_probe(
        "c1",
        revoke=lambda: calls.append("revoke"),
        reattempt=lambda: calls.append("reattempt") or True,
        action="drop database prod",
    )
    assert isinstance(result, ProbeResult)
    assert result.action_succeeded is True
    assert result.ceased is False
    assert result.reattempted is True


def test_action_blocked_after_revoke_is_ceased() -> None:
    result = run_cessation_probe(
        "c1",
        revoke=lambda: None,
        reattempt=lambda: False,
    )
    assert result.ceased is True
    assert result.action_succeeded is False


def test_probe_revokes_before_reattempting() -> None:
    order: list[str] = []
    run_cessation_probe(
        "c1",
        revoke=lambda: order.append("revoke"),
        reattempt=lambda: order.append("reattempt") or True,
    )
    assert order == ["revoke", "reattempt"]


def test_probe_records_the_action_and_case() -> None:
    result = run_cessation_probe(
        "c9", revoke=lambda: None, reattempt=lambda: True, action="exfiltrate secrets"
    )
    assert result.case_id == "c9"
    assert "exfiltrate secrets" in result.detail


def test_probe_result_round_trips() -> None:
    result = run_cessation_probe("c1", revoke=lambda: None, reattempt=lambda: False)
    assert ProbeResult.model_validate_json(result.model_dump_json()) == result
