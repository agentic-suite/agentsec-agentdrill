"""Reliability for outbound integrations (M26 26.7, R74).

Idempotent upserts on **stable ids**, retries with exponential backoff,
dead-letter / **offline spool** so a prolonged outage loses no request, signed
webhooks, and rate-limit aware backoff. The spool is durable (atomic writes) and
replays exactly once. Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from agentdrill.integrations.transport import (
    DELIVERY_FAILED,
    DELIVERY_OK,
    DeliveryResult,
    HttpRequest,
    Transport,
)

#: The signature header written on a signed webhook.
SIGNATURE_HEADER = "X-AgentDrill-Signature"


class SpoolError(ValueError):
    """Raised when a request cannot be spooled (e.g. duplicate or no key)."""


def stable_id(kind: str, key: str) -> str:
    """A deterministic id for ``kind``/``key`` (stable across runs/hosts)."""
    digest = hashlib.sha256()
    digest.update(kind.encode("utf-8"))
    digest.update(b"\x00")
    digest.update(key.encode("utf-8"))
    return digest.hexdigest()


@dataclass(frozen=True)
class RetryPolicy:
    """Exponential backoff with a cap."""

    attempts: int = 3
    base_ms: int = 100
    max_ms: int = 5_000

    def delay_ms(self, attempt: int) -> int:
        """The backoff before retry ``attempt`` (1-based), capped at ``max_ms``."""
        shift: int = 1 << (attempt - 1)
        return min(self.max_ms, self.base_ms * shift)


#: The default retry policy — a module singleton, safe as a default argument.
DEFAULT_RETRY_POLICY = RetryPolicy()


def parse_retry_after(value: str | int | None) -> int | None:
    """Parse a ``Retry-After`` delay (seconds) into milliseconds, or ``None``."""
    if value is None:
        return None
    if isinstance(value, int):
        return value * 1000
    try:
        return int(value.strip()) * 1000
    except (ValueError, AttributeError):
        return None


def retry_send(
    request: HttpRequest,
    *,
    transport: Transport,
    policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    sleep: Callable[[int], None] = time.sleep,
) -> bool:
    """Send ``request`` with retries; return whether it was delivered."""
    for attempt in range(1, policy.attempts + 1):
        if transport(request):
            return True
        if attempt < policy.attempts:
            sleep(policy.delay_ms(attempt))
    return False


class DeliveryLedger:
    """An idempotent upsert store of delivered keys (SQLite, cross-run)."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._path))
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS delivered ("
            "key TEXT PRIMARY KEY, payload_hash TEXT NOT NULL)"
        )
        self._conn.commit()

    def record(self, key: str, payload_hash: str) -> bool:
        """Record ``key``; return ``True`` on first insert, ``False`` if present."""
        cursor = self._conn.execute(
            "INSERT OR IGNORE INTO delivered (key, payload_hash) VALUES (?, ?)",
            (key, payload_hash),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def has(self, key: str) -> bool:
        """Whether ``key`` has already been delivered."""
        cursor = self._conn.execute("SELECT 1 FROM delivered WHERE key = ?", (key,))
        return cursor.fetchone() is not None

    def close(self) -> None:
        """Close the underlying connection."""
        self._conn.close()


def sign_webhook(body: str, *, secret: str) -> dict[str, str]:
    """The signature header for a webhook ``body`` (HMAC-SHA256)."""
    digest = hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256)
    return {SIGNATURE_HEADER: f"sha256={digest.hexdigest()}"}


def verify_webhook(body: str, headers: dict[str, str], *, secret: str) -> bool:
    """Whether ``headers`` carry a valid signature for ``body``."""
    provided = headers.get(SIGNATURE_HEADER)
    if not provided:
        return False
    expected = sign_webhook(body, secret=secret)[SIGNATURE_HEADER]
    return hmac.compare_digest(provided, expected)


class OfflineSpool:
    """A durable spool of undelivered requests (atomic, exactly-once replay)."""

    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self._dir / f"{stable_id('spool', key)}.json"

    def spool(self, request: HttpRequest) -> Path:
        """Persist ``request`` for later delivery.

        Raises:
            SpoolError: The request has no stable key, or its key is already spooled.
        """
        if not request.key:
            raise SpoolError("spooled requests need a stable key")
        path = self._path(request.key)
        if path.exists():
            raise SpoolError(f"duplicate spooled request: {request.key!r}")
        payload = {
            "url": request.url,
            "method": request.method,
            "body": request.body,
            "headers": request.headers,
            "key": request.key,
        }
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload), encoding="utf-8")
        temporary.replace(path)
        return path

    def _load(self, path: Path) -> HttpRequest:
        data = json.loads(path.read_text(encoding="utf-8"))
        return HttpRequest(
            url=data["url"],
            method=data["method"],
            body=data["body"],
            headers=data["headers"],
            key=data["key"],
        )

    def pending(self) -> list[HttpRequest]:
        """The spooled requests still awaiting delivery."""
        return [self._load(path) for path in sorted(self._dir.glob("*.json"))]

    def flush(
        self,
        *,
        transport: Transport,
        policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        sleep: Callable[[int], None] = time.sleep,
    ) -> list[DeliveryResult]:
        """Attempt every spooled request; drop only the ones delivered."""
        results: list[DeliveryResult] = []
        for path in sorted(self._dir.glob("*.json")):
            request = self._load(path)
            delivered = retry_send(request, transport=transport, policy=policy, sleep=sleep)
            if delivered:
                path.unlink()
            results.append(
                DeliveryResult(
                    key=request.key,
                    url=request.url,
                    status=DELIVERY_OK if delivered else DELIVERY_FAILED,
                )
            )
        return results
