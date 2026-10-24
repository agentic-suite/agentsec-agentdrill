"""M22 22.4 — portability (RED → GREEN).

Python 3.10+; macOS/Linux; local-first (no service required for core function).
"""

from __future__ import annotations

import pytest

from agentdrill.hardening import (
    MIN_PYTHON,
    SUPPORTED_OS,
    PortabilityError,
    PortabilityReport,
    check_portability,
    require_portable,
)


def test_supported_python_and_os() -> None:
    report = check_portability(python_version=(3, 12), system="Darwin")
    assert isinstance(report, PortabilityReport)
    assert report.python_ok is True
    assert report.os_ok is True
    assert report.local_first is True
    assert MIN_PYTHON == (3, 10)
    assert set(SUPPORTED_OS) == {"Darwin", "Linux"}


def test_old_python_is_rejected() -> None:
    report = check_portability(python_version=(3, 9), system="Linux")
    assert report.python_ok is False
    with pytest.raises(PortabilityError, match=r"3\.10"):
        require_portable(report)


def test_unsupported_os_is_rejected() -> None:
    report = check_portability(python_version=(3, 12), system="Windows")
    assert report.os_ok is False
    with pytest.raises(PortabilityError, match="Windows"):
        require_portable(report)
