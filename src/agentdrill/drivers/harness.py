"""Per-harness drivers (M4 work item 4.5).

``claude-code`` and ``cursor`` deliver the attack through their harness surface.
They reuse the subprocess delivery contract (stdin JSON payload → stdout run
envelope) with harness-specific defaults and an ``AGENTDRILL_HARNESS`` marker in
the child environment.
"""

from __future__ import annotations

from typing import Any, ClassVar

from agentdrill.drivers.subprocess_driver import SubprocessDriver


class HarnessDriver(SubprocessDriver):
    """Base for harness-surface drivers; sets the harness marker + default argv.

    Config keys are those of :class:`SubprocessDriver`; ``command`` defaults to
    :attr:`default_command` when not supplied.
    """

    #: Harness identifier, exported to the child as ``AGENTDRILL_HARNESS``.
    harness: ClassVar[str] = ""

    #: Default argv when ``config["command"]`` is not set.
    default_command: ClassVar[tuple[str, ...]] = ()

    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> Any:
        merged: dict[str, Any] = dict(config)
        if "command" not in merged and self.default_command:
            merged["command"] = list(self.default_command)
        env = dict(merged.get("env") or {})
        env.setdefault("AGENTDRILL_HARNESS", self.harness)
        merged["env"] = env
        return super()._invoke(payload, merged)


class ClaudeCodeDriver(HarnessDriver):
    """Deliver the attack through Claude Code (Tier-1 harness)."""

    name = "claude-code"
    harness = "claude-code"
    default_command = ("claude", "-p")


class CursorDriver(HarnessDriver):
    """Deliver the attack through Cursor (Tier-1 harness)."""

    name = "cursor"
    harness = "cursor"
    default_command = ("cursor-agent", "-p")
