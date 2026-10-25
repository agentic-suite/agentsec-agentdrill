"""Portability (M22 22.4).

Python 3.10+, macOS/Linux, and **local-first** — no service is required for the
core function. Design: ``docs/prd/13-non-functional-requirements.md``.
"""

from __future__ import annotations

import platform
import sys

from pydantic import BaseModel

#: The minimum supported Python version.
MIN_PYTHON: tuple[int, int] = (3, 10)

#: The supported operating systems.
SUPPORTED_OS: tuple[str, ...] = ("Darwin", "Linux")


class PortabilityError(ValueError):
    """Raised when the environment is not supported (or not local-first)."""


class PortabilityReport(BaseModel):
    """A portability check result."""

    python_ok: bool
    os: str
    os_ok: bool
    local_first: bool = True


def check_portability(
    *,
    python_version: tuple[int, ...] | None = None,
    system: str | None = None,
) -> PortabilityReport:
    """Check the runtime against the portability requirements."""
    version = python_version or (sys.version_info.major, sys.version_info.minor)
    os_name = system or platform.system()
    return PortabilityReport(
        python_ok=version[:2] >= MIN_PYTHON,
        os=os_name,
        os_ok=os_name in SUPPORTED_OS,
        local_first=True,
    )


def require_portable(report: PortabilityReport) -> None:
    """Fail loudly if the runtime is unsupported.

    Raises:
        PortabilityError: The Python version or OS is unsupported.
    """
    if not report.python_ok:
        raise PortabilityError(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required")
    if not report.os_ok:
        raise PortabilityError(f"unsupported OS: {report.os!r}; supported: {list(SUPPORTED_OS)}")
