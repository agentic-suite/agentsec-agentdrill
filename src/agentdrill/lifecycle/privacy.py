"""Evidence privacy (M18 18.6, F65).

**Redaction before bundling** with receipts: each redaction records its class,
count and location, and the verifier checks the receipts — a bundle redacts and
proves it. Design: ``docs/prd/20-efficacy-freshness-lifecycle.md``.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

#: Redaction patterns by class.
PATTERNS: dict[str, re.Pattern[str]] = {
    "secret": re.compile(r"sk-[A-Za-z0-9]{6,}|AKIA[0-9A-Z]{8,}"),
    "token": re.compile(r"ghp_[A-Za-z0-9]{10,}"),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
}


class Receipt(BaseModel):
    """A redaction receipt: what class, how many, and where."""

    klass: str
    count: int
    location: str


class RedactionResult(BaseModel):
    """The redacted content and the receipts that prove it."""

    redacted: str
    receipts: list[Receipt] = Field(default_factory=list)


def redact(content: str, *, location: str) -> RedactionResult:
    """Redact every known class in ``content``; return the result + receipts."""
    redacted = content
    receipts: list[Receipt] = []
    for klass, pattern in PATTERNS.items():
        matches = pattern.findall(redacted)
        if matches:
            redacted = pattern.sub(f"[REDACTED:{klass}]", redacted)
            receipts.append(Receipt(klass=klass, count=len(matches), location=location))
    return RedactionResult(redacted=redacted, receipts=receipts)


def verify_receipts(content: str, receipts: list[Receipt]) -> bool:
    """Whether ``content`` is redacted and ``receipts`` validly account for it.

    Fails when any known class still appears (an unredacted secret) or a
    receipt is malformed (no location, non-positive count).
    """
    for pattern in PATTERNS.values():
        if pattern.search(content):
            return False
    return all(receipt.count >= 1 and bool(receipt.location) for receipt in receipts)
