"""M23 23.8 — lab isolation + ground truth, F88 (RED → GREEN).

Loopback-only enforcement (egress allowlist); a ground-truth event log; the lab
version pinned in the manifest — zero non-loopback egress.
"""

from __future__ import annotations

import pytest

from agentdrill.lab import (
    EgressViolation,
    LabIsolation,
    build_lab,
    enforce_loopback,
    event_log,
    pin_lab,
)


def test_loopback_is_allowed() -> None:
    isolation = LabIsolation()
    for host in ("127.0.0.1", "::1", "localhost"):
        assert isolation.is_allowed(host) is True
        enforce_loopback(isolation, host)  # no raise


def test_non_loopback_is_a_violation() -> None:
    isolation = LabIsolation()
    assert isolation.is_allowed("evil.example") is False
    with pytest.raises(EgressViolation, match=r"evil\.example"):
        enforce_loopback(isolation, "evil.example")


def test_lab_version_is_pinned_in_the_manifest() -> None:
    manifest = pin_lab({}, version="0.3.0")
    assert manifest["lab"]["version"] == "0.3.0"


def test_ground_truth_log_records_events() -> None:
    lab = build_lab(version="0.3.0", seed=1)
    lab.serve_mcp("poisoning")
    assert event_log(lab) == [(0, "evil-mcp", "poisoning")]
