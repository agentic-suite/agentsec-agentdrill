"""M18 18.6 — evidence privacy, F65 (RED → GREEN).

Redaction-before-bundling with **receipts** (class, count, location); the
verifier checks the receipts, so a bundle redacts and proves it.
"""

from __future__ import annotations

from agentdrill.lifecycle import Receipt, RedactionResult, redact, verify_receipts

SAMPLE_KEY = "sk-abcdef123456"
EMAIL = "analyst@example.com"


def test_bundle_redacts_and_proves_it() -> None:
    result = redact(f"token={SAMPLE_KEY}", location="artifacts/c1.json")
    assert isinstance(result, RedactionResult)
    assert SAMPLE_KEY not in result.redacted
    assert "[REDACTED:secret]" in result.redacted
    assert result.receipts[0].klass == "secret"
    assert result.receipts[0].count == 1


def test_multiple_classes_produce_receipts() -> None:
    result = redact(f"{SAMPLE_KEY} {EMAIL}", location="run.json")
    classes = {r.klass for r in result.receipts}
    assert classes == {"secret", "email"}


def test_receipt_carries_location() -> None:
    result = redact(SAMPLE_KEY, location="artifacts/c9.json")
    assert result.receipts[0].location == "artifacts/c9.json"


def test_verify_receipts_accepts_a_redacted_bundle() -> None:
    result = redact(SAMPLE_KEY, location="run.json")
    assert verify_receipts(result.redacted, result.receipts) is True


def test_verify_receipts_rejects_an_unredacted_secret() -> None:
    receipts = [Receipt(klass="secret", count=0, location="run.json")]
    assert verify_receipts(f"token={SAMPLE_KEY}", receipts) is False
