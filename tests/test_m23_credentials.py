"""M23 23.3 — credential + process witnesses, F87 (RED → GREEN).

Honey credentials / canary tokens (use observed by the verifier) and a
process/syscall witness; credential use and exec are detected.
"""

from __future__ import annotations

from agentdrill.witness import HoneyCredential, ProcessWitness


def test_honey_credential_use_is_observed() -> None:
    cred = HoneyCredential(name="aws-key", token="canary-token-1")  # noqa: S106 - fixture
    assert cred.used is False
    cred.observe_use()
    assert cred.used is True


def test_process_exec_is_detected() -> None:
    witness = ProcessWitness()
    assert witness.detected is False
    witness.observe_exec("rm -rf /tmp/canary")
    assert witness.detected is True
    assert witness.execs == ["rm -rf /tmp/canary"]


def test_process_witness_ignores_benign_commands() -> None:
    witness = ProcessWitness()
    witness.observe_exec("echo hi", benign=True)
    assert witness.detected is False
