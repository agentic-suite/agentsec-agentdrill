"""``http`` driver (M4 work item 4.4).

POSTs the restricted payload to a harness endpoint. A timeout raises
:class:`AgentTimeoutError`; a connection failure or non-200 raises
:class:`AdapterError` — both normalized to ``status`` by the runner.
"""

from __future__ import annotations

from typing import Any

import httpx

from agentdrill.drivers.base import Driver
from agentdrill.models.errors import AdapterError, AgentTimeoutError, ConfigError


class HttpDriver(Driver):
    """Deliver the attack to an HTTP harness.

    Config keys:

    - ``url`` (required) — the endpoint to POST to.
    - ``timeout_seconds`` — request timeout (default 30).
    - ``headers`` — extra request headers.
    """

    name = "http"

    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> Any:
        url = config.get("url")
        if not isinstance(url, str) or not url:
            raise ConfigError("http driver requires config.url")
        timeout = config.get("timeout_seconds", 30)
        headers = config.get("headers")
        try:
            response = httpx.post(
                url,
                json=payload,
                timeout=timeout,
                headers=headers if isinstance(headers, dict) else None,
            )
        except httpx.TimeoutException as exc:
            raise AgentTimeoutError(f"http driver timed out after {timeout}s") from exc
        except httpx.HTTPError as exc:
            raise AdapterError(f"http driver request failed: {exc}") from exc
        if response.status_code != 200:
            raise AdapterError(
                f"http driver: HTTP {response.status_code} from {url}: "
                f"{response.text[:200]}"
            )
        body = response.text.strip()
        if not body:
            return ""
        try:
            return response.json()
        except ValueError:
            return body
