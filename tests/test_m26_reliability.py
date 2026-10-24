"""M26 26.7 — reliability (RED → GREEN).

Idempotent upserts on stable IDs, retries with exponential backoff, a dead-letter
queue, signed webhooks, rate-limit aware backoff, and an offline spool that loses
**no** request across a prolonged outage.
"""

from __future__ import annotations

import json

import pytest

from agentdrill.integrations import (
    DELIVERY_OK,
    DeliveryLedger,
    HttpRequest,
    OfflineSpool,
    RetryPolicy,
    SpoolError,
    parse_retry_after,
    retry_send,
    sign_webhook,
    stable_id,
    verify_webhook,
)


def _request(key: str) -> HttpRequest:
    return HttpRequest(
        url="https://hooks.example.com/x",
        method="POST",
        body=json.dumps({"ticket": key}),
        key=key,
    )


def test_stable_id_is_deterministic() -> None:
    assert stable_id("ticket", "pack:case") == stable_id("ticket", "pack:case")
    assert stable_id("ticket", "a") != stable_id("ticket", "b")


def test_retry_policy_backoff_is_exponential_and_capped() -> None:
    policy = RetryPolicy(attempts=5, base_ms=100, max_ms=400)
    delays = [policy.delay_ms(attempt) for attempt in range(1, 5)]
    assert delays == [100, 200, 400, 400]


def test_retry_send_retries_then_succeeds() -> None:
    calls = {"n": 0}
    slept: list[int] = []

    def flaky(request: HttpRequest) -> bool:
        calls["n"] += 1
        return calls["n"] >= 3

    ok = retry_send(
        _request("k"),
        transport=flaky,
        policy=RetryPolicy(attempts=5, base_ms=10, max_ms=10),
        sleep=slept.append,
    )
    assert ok is True
    assert calls["n"] == 3
    assert slept == [10, 10]


def test_retry_send_gives_up_and_reports_failure() -> None:
    ok = retry_send(
        _request("k"),
        transport=lambda request: False,
        policy=RetryPolicy(attempts=2, base_ms=5, max_ms=5),
        sleep=lambda ms: None,
    )
    assert ok is False


def test_parse_retry_after() -> None:
    assert parse_retry_after("2") == 2000
    assert parse_retry_after(3) == 3000
    assert parse_retry_after(None) is None
    assert parse_retry_after("garbage") is None


def test_delivery_ledger_is_idempotent_across_runs(tmp_path) -> None:
    ledger = DeliveryLedger(tmp_path / "ledger.sqlite")
    assert ledger.record("k1", "hash") is True  # first insert
    assert ledger.record("k1", "hash") is False  # already delivered
    assert ledger.has("k1") is True
    assert ledger.has("k2") is False


def test_signed_webhook_round_trips_and_rejects_tampering() -> None:
    body = '{"hello":"world"}'
    headers = sign_webhook(body, secret="s3cret")  # noqa: S106 - a fake secret in a test
    assert verify_webhook(body, headers, secret="s3cret") is True  # noqa: S106
    assert verify_webhook(body + " ", headers, secret="s3cret") is False  # noqa: S106
    assert verify_webhook(body, headers, secret="wrong") is False  # noqa: S106
    assert verify_webhook(body, {}, secret="s3cret") is False  # noqa: S106


def test_offline_spool_loses_nothing_across_an_outage(tmp_path) -> None:
    spool = OfflineSpool(tmp_path / "spool")
    for key in ("k1", "k2", "k3"):
        spool.spool(_request(key))
    assert len(spool.pending()) == 3

    # Outage: the transport fails; nothing is dropped.
    def outage(request: HttpRequest) -> bool:
        return False

    results = spool.flush(transport=outage, policy=RetryPolicy(attempts=1))
    assert [r.status for r in results] == ["failed", "failed", "failed"]
    assert len(spool.pending()) == 3  # still spooled, ready for replay

    # Recovery: every spooled request is delivered exactly once.
    delivered: list[str] = []

    def recovered(request: HttpRequest) -> bool:
        delivered.append(request.key)
        return True

    results = spool.flush(transport=recovered, policy=RetryPolicy(attempts=1))
    assert [r.status for r in results] == [DELIVERY_OK, DELIVERY_OK, DELIVERY_OK]
    assert sorted(delivered) == ["k1", "k2", "k3"]
    assert spool.pending() == []


def test_spool_rejects_a_duplicate_key(tmp_path) -> None:
    spool = OfflineSpool(tmp_path / "spool")
    spool.spool(_request("k1"))
    with pytest.raises(SpoolError):
        spool.spool(_request("k1"))
