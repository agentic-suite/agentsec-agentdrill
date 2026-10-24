"""M28 28.2 — time-boxed waivers (RED → GREEN).

Waivers carry scope/tier/reason/**drilled compensating control**/approvers/
**expiry**/drift trigger/residual risk; they **annotate, never relabel** (the miss
stays visible), **auto-reopen** on expiry, are signed + verifier-checked, gate
against a **known-miss budget**, and **integrity findings are not waivable**.
"""

from __future__ import annotations

import pytest

from agentdrill.ledger import (
    Finding,
    Ledger,
    SeverityVector,
    Waiver,
    WaiverError,
    active_waivers,
    create_waiver,
    is_active,
    open_finding,
    require_known_miss_budget,
    require_waivable,
    sign_waiver,
    sync_waivers,
    verify_waiver,
)


def _finding(**overrides: object) -> Finding:
    base = dict(
        id="f1",
        case_id="c1",
        pack="p@1.0.0+dead",
        outcome="missed",
        dimension="enforcement",
        title="miss",
        severity=SeverityVector(cvss="CVSS:4.0/..."),
        severity_level="high",
    )
    base.update(overrides)
    return Finding.model_validate(base)


def _waiver(**overrides: object) -> Waiver:
    finding = _finding()
    waiver = create_waiver(
        finding,
        waiver_id="w1",
        reason="accepted risk",
        compensating_control="network egress blocked",
        approvers=["ciso@example.com"],
        now="2026-01-01",
    )
    return waiver.model_copy(update=overrides) if overrides else waiver


def test_default_expiry_is_ninety_days_critical_is_thirty() -> None:
    assert _waiver().expires == "2026-04-01"
    critical = create_waiver(
        _finding(severity_level="critical"),
        waiver_id="w2",
        reason="r",
        compensating_control="c",
        approvers=["a"],
        now="2026-01-01",
        critical=True,
    )
    assert critical.expires == "2026-01-31"


def test_integrity_findings_are_not_waivable() -> None:
    integrity = _finding(dimension="integrity")
    with pytest.raises(WaiverError):
        require_waivable(integrity)
    with pytest.raises(WaiverError):
        create_waiver(
            integrity,
            waiver_id="w3",
            reason="r",
            compensating_control="c",
            approvers=["a"],
            now="2026-01-01",
        )


def test_a_waiver_annotates_never_relabels() -> None:
    ledger = Ledger()
    entry = ledger.record(open_finding(_finding()))
    ledger = sync_waivers(ledger, [_waiver()], now="2026-01-01")
    synced = ledger.get("f1")
    assert synced.finding.outcome == "missed"  # the label never changes
    assert synced.finding.waivers == ["waived:w1"]
    assert len(ledger.all()) == 1  # visibility never drops
    assert entry.finding.outcome == "missed"


def test_expired_waiver_is_inactive_and_reopens() -> None:
    ledger = Ledger()
    entry = open_finding(_finding())
    accepted = entry.finding.model_copy(update={"status": "accepted_risk"})
    ledger.record(entry.model_copy(update={"finding": accepted}))

    ledger = sync_waivers(ledger, [_waiver()], now="2026-01-01")
    assert active_waivers(ledger.get("f1"), [_waiver()], now="2026-01-01") != []
    assert ledger.get("f1").finding.waivers == ["waived:w1"]

    # after expiry the waiver no longer suppresses and the finding reopens
    assert is_active(_waiver(), now="2026-06-01") is False
    reopened = sync_waivers(ledger, [_waiver()], now="2026-06-01").get("f1")
    assert reopened.finding.waivers == []
    assert reopened.finding.status == "open"


def test_known_miss_budget_gate() -> None:
    ledger = Ledger()
    ledger.record(open_finding(_finding(id="f1")))
    ledger.record(open_finding(_finding(id="f2", case_id="c2")))

    with pytest.raises(WaiverError):
        require_known_miss_budget(ledger, budget=1)  # 2 unwaived misses

    ledger = sync_waivers(ledger, [_waiver()], now="2026-01-01")
    require_known_miss_budget(ledger, budget=1)  # one is waived ⇒ 1 unwaived miss
    with pytest.raises(WaiverError):
        require_known_miss_budget(ledger, budget=0)


def test_waivers_are_signed_and_verifier_checked() -> None:
    signed = sign_waiver(_waiver(), secret="s3cret")  # noqa: S106 - a fake secret in a test
    assert verify_waiver(signed, secret="s3cret") is True  # noqa: S106
    assert verify_waiver(signed, secret="wrong") is False  # noqa: S106
    assert verify_waiver(_waiver(), secret="s3cret") is False  # noqa: S106 - unsigned
    tampered = signed.model_copy(update={"reason": "changed"})
    assert verify_waiver(tampered, secret="s3cret") is False  # noqa: S106


def test_pack_and_class_scoped_waivers_match() -> None:
    ledger = Ledger()
    ledger.record(open_finding(_finding()))
    pack_scoped = _waiver(id="wp", scope="pack").model_copy(update={"finding_id": "p@1.0.0+dead"})
    class_scoped = _waiver(id="wc", scope="class").model_copy(update={"finding_id": "enforcement"})
    synced = sync_waivers(ledger, [pack_scoped, class_scoped], now="2026-01-01")
    assert synced.get("f1").finding.waivers == ["waived:wp", "waived:wc"]
