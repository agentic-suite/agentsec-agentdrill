"""Injected HTTP transport + delivery (M26 26.4).

Integrations never own a network client: they build an :class:`HttpRequest` and
hand it to an injected :data:`Transport`. That keeps tests offline, keeps
credentials out of the library, and lets 26.7 add retries/DLQ/offline spool
around the same seam. :func:`deliver_tickets` dedups by request key so a repeat
batch cannot open duplicate tickets.
Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

#: Delivery outcome markers.
DELIVERY_OK = "delivered"
DELIVERY_DUPLICATE = "duplicate"
DELIVERY_FAILED = "failed"


@dataclass(frozen=True)
class HttpRequest:
    """A prepared outbound request (no client, no credentials baked in)."""

    url: str
    method: str
    body: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    #: A stable identity for dedup; when empty, method+url+body is used.
    key: str = ""


@dataclass(frozen=True)
class DeliveryResult:
    """The outcome of one delivery attempt."""

    key: str
    url: str
    status: str
    detail: str = ""


#: A transport returns ``True`` on success, ``False`` on failure.
Transport = Callable[[HttpRequest], bool]


def _request_key(request: HttpRequest) -> str:
    """The dedup key for a request (stable across runs)."""
    return request.key or f"{request.method} {request.url}\n{request.body}"


def deliver_tickets(
    requests: Sequence[HttpRequest], *, transport: Transport
) -> list[DeliveryResult]:
    """Deliver ``requests``, deduplicating identical tickets within the batch.

    A duplicate is reported as :data:`DELIVERY_DUPLICATE` and is not re-sent.
    """
    seen: set[str] = set()
    results: list[DeliveryResult] = []
    for request in requests:
        key = _request_key(request)
        if key in seen:
            results.append(DeliveryResult(key=key, url=request.url, status=DELIVERY_DUPLICATE))
            continue
        seen.add(key)
        delivered = transport(request)
        results.append(
            DeliveryResult(
                key=key,
                url=request.url,
                status=DELIVERY_OK if delivered else DELIVERY_FAILED,
            )
        )
    return results
