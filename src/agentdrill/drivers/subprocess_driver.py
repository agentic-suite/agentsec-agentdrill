"""``subprocess`` driver (M4 work item 4.2).

Feeds the restricted JSON payload on the child's **stdin** and reads a run
envelope from its **stdout** (raw-text fallback unless ``strict_output``). Child
logs go to stderr; a non-zero exit is an :class:`AdapterError`, a timeout an
:class:`AgentTimeoutError`.
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from agentdrill.drivers.base import Driver
from agentdrill.models.errors import AdapterError, AgentTimeoutError, ConfigError


class SubprocessDriver(Driver):
    """Deliver the attack to a subprocess harness over stdin/stdout.

    Config keys:

    - ``command`` (required) — the argv list to run.
    - ``strict_output`` — when true, non-envelope stdout is an error.
    - ``timeout_seconds`` — child timeout; expiry raises ``AgentTimeoutError``.
    - ``env`` — extra environment variables for the child.
    """

    name = "subprocess"

    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> Any:
        command = config.get("command")
        if not isinstance(command, list) or not command:
            raise ConfigError(
                "subprocess driver requires config.command (a non-empty list)"
            )
        strict = bool(config.get("strict_output", False))
        timeout = config.get("timeout_seconds")
        env = config.get("env")
        run_env = {**os.environ, **env} if isinstance(env, dict) else None
        try:
            proc = subprocess.run(  # noqa: S603 - command comes from trusted pack config
                command,
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=run_env,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentTimeoutError(
                f"subprocess driver timed out after {timeout}s"
            ) from exc
        except OSError as exc:
            raise AdapterError(f"subprocess driver failed to start: {exc}") from exc
        if proc.returncode != 0:
            raise AdapterError(
                f"subprocess driver exited {proc.returncode}: {proc.stderr.strip()}"
            )
        out = proc.stdout.strip()
        if not out:
            return ""
        try:
            return json.loads(out)
        except json.JSONDecodeError as exc:
            if strict:
                raise AdapterError(
                    "subprocess driver output is not a run envelope (strict_output)"
                ) from exc
            return out
