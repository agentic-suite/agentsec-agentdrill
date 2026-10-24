"""Lab isolation + ground truth (M23 23.8, F88).

Loopback-only enforcement (an egress allowlist), a ground-truth event log and
the lab version pinned in the manifest — **zero non-loopback egress**. Design:
``docs/prd/27-adversary-lab.md``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

#: Hosts the lab may reach (loopback only).
LOOPBACK_HOSTS: tuple[str, ...] = ("127.0.0.1", "::1", "localhost")


class EgressViolation(ValueError):
    """Raised when the lab would reach a non-loopback host."""


class LabIsolation(BaseModel):
    """Loopback-only egress enforcement for the lab."""

    egress_allowlist: list[str] = Field(default_factory=lambda: list(LOOPBACK_HOSTS))

    def is_allowed(self, host: str) -> bool:
        """Whether ``host`` is on the loopback allowlist."""
        return host in self.egress_allowlist


def enforce_loopback(isolation: LabIsolation, host: str) -> None:
    """Fail loudly if the lab would reach a non-loopback host.

    Raises:
        EgressViolation: ``host`` is not loopback.
    """
    if not isolation.is_allowed(host):
        raise EgressViolation(
            f"non-loopback egress blocked: {host!r} (allowlist {isolation.egress_allowlist})"
        )


def pin_lab(manifest: dict[str, Any], *, version: str) -> dict[str, Any]:
    """Pin the lab version into the run manifest."""
    manifest["lab"] = {"version": version}
    return manifest
