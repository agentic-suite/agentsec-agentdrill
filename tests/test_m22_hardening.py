"""M22 22.3 — untrusted-pack hardening (RED → GREEN).

An OS-level sandbox (`--network none`, read-only root, resource caps) is
required for `external` trust; the audit log is hash-chained so tamper is
detected (G4).
"""

from __future__ import annotations

import pytest

from agentdrill.hardening import (
    AuditChain,
    SandboxError,
    SandboxSpec,
    require_sandbox,
    sandbox_spec_for,
)


def test_external_requires_an_isolated_sandbox() -> None:
    spec = sandbox_spec_for("external")
    assert isinstance(spec, SandboxSpec)
    assert spec.network == "none"
    assert spec.read_only_root is True
    assert spec.memory_limit
    require_sandbox("external", spec)  # no raise


def test_external_with_network_is_rejected() -> None:
    spec = sandbox_spec_for("external").model_copy(update={"network": "bridge"})
    with pytest.raises(SandboxError, match="network"):
        require_sandbox("external", spec)


def test_audit_chain_detects_tamper() -> None:
    chain = AuditChain()
    chain.add("run_start")
    chain.add("case_blocked")
    assert chain.verify() is True
    chain.entries[0].payload = "tampered"
    assert chain.verify() is False


def test_unmodified_audit_verifies() -> None:
    chain = AuditChain()
    for i in range(3):
        chain.add(f"event-{i}")
    assert chain.verify() is True
    assert chain.head
