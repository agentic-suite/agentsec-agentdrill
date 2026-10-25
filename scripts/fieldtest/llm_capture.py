#!/usr/bin/env python3
"""Make one real LLM call and record the request/response pair (field-test must).

Every LLM-backed field-test case captures the full request/response pair(s) it
made — that capture is the evidence behind the case's verdict. This driver:

  1. sends a minimal chat completion to the pinned OpenAI-compatible endpoint,
  2. writes ``<out>/<name>-request.json`` and ``<out>/<name>-response.json``,
  3. **sanitizes** both before writing (secrets masked, never persisted), and
  4. exits non-zero if no response was captured (fail-closed, never a silent OK).

Usage::

    python3 llm_capture.py --out DIR --name llm [--prompt "..."] \
        [--base-url URL] [--model M] [--api-key K]

Env fallbacks: AGENTDRILL_FIELD_ENDPOINT / LLM_BASE_URL / OPENAI_BASE_URL,
AGENTDRILL_FIELD_MODEL / LLM_MODEL / OPENAI_MODEL, OPENAI_API_KEY.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Fallback redaction if agentdrill.security.sanitize is not importable.
_SECRET_RES = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)(api[_-]?key\"?\s*[:=]\s*\"?)[A-Za-z0-9._-]{16,}"),
]


def sanitize(text: str) -> str:
    try:
        from agentdrill.security.sanitize import sanitize_output  # type: ignore

        return sanitize_output(text)
    except Exception:
        for pattern in _SECRET_RES:
            text = pattern.sub("[REDACTED]", text)
        return text


def _endpoint(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if not base.endswith("/v1"):
        base += "/v1"
    return f"{base}/chat/completions"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="directory for the captured pair")
    ap.add_argument("--name", default="llm", help="pair name (files: <name>-request/-response.json)")
    ap.add_argument("--prompt", default="Reply with the single word: ok")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--timeout", type=float, default=120.0)
    args = ap.parse_args(argv)

    # Prefer the namespaced FT_LLM_* vars (and the explicit --base-url from
    # ft_llm_probe). The ambient OPENAI_*/LLM_* env is deliberately ignored.
    base = (
        args.base_url
        or os.environ.get("FT_LLM_HOST_URL")
        or os.environ.get("FT_LLM_BASE_URL")
        or os.environ.get("AGENTDRILL_FIELD_ENDPOINT")
        or "http://127.0.0.1:8000/v1"  # local oMLX (OpenAI-compatible)
    )
    model = (
        args.model
        or os.environ.get("FT_LLM_MODEL")
        or os.environ.get("AGENTDRILL_FIELD_MODEL")
        or "Qwen3.5-4B-4bit"
    )
    # Never send the ambient OPENAI_API_KEY (a real key from the surrounding
    # environment); oMLX accepts any key.
    api_key = args.api_key or os.environ.get("LLM_API_KEY") or "omlx-test"

    url = _endpoint(base)
    request_body = {
        "model": model,
        "messages": [{"role": "user", "content": args.prompt}],
        "temperature": 0,
        "max_tokens": 16,
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.name}-request.json").write_text(
        sanitize(
            json.dumps(
                {
                    "method": "POST",
                    "url": url,
                    "headers": {"content-type": "application/json", "authorization": "Bearer [REDACTED]"},
                    "json": request_body,
                    "meta": {"model": model, "endpoint": url},
                },
                indent=2,
            )
        ),
        encoding="utf-8",
    )

    data = json.dumps(request_body).encode()
    req = urllib.request.Request(  # noqa: S310 - pinned, operator-provided endpoint
        url,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:  # noqa: S310
            status = resp.status
            raw = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        (out / f"{args.name}-response.json").write_text(
            sanitize(json.dumps({"status_code": 0, "error": str(exc)}, indent=2)),
            encoding="utf-8",
        )
        print(f"fail: no LLM response from {url}: {exc}", file=sys.stderr)
        return 1

    captured_model = None
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            captured_model = parsed.get("model") or parsed.get("id")
    except json.JSONDecodeError:
        parsed = None

    (out / f"{args.name}-response.json").write_text(
        sanitize(
            json.dumps(
                {
                    "status_code": status,
                    "body": raw,
                    "meta": {"model": captured_model or model, "endpoint": url},
                },
                indent=2,
            )
        ),
        encoding="utf-8",
    )
    print(f"ok: captured LLM request/response pair for {model} from {url} (HTTP {status})")
    return 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
