"""M16 16.3 — trust levels (RED → GREEN).

`built-in` / `local` / `external` enforced at load/run: an `external` pack must
use a sandboxed subprocess only, and is never benchmark-published.
"""

from __future__ import annotations

import pytest

from agentdrill.registry import (
    TrustError,
    enforce_trust,
    is_benchmark_publishable,
    is_sandbox_required,
    normalize_trust,
)


def test_external_requires_subprocess_and_sandbox() -> None:
    with pytest.raises(TrustError):
        enforce_trust("external", adapter_type="python", sandbox=True)
    with pytest.raises(TrustError):
        enforce_trust("external", adapter_type="subprocess", sandbox=False)
    enforce_trust("external", adapter_type="subprocess", sandbox=True)  # no raise


def test_external_is_never_benchmark_publishable() -> None:
    assert is_benchmark_publishable("external") is False
    assert is_benchmark_publishable("local") is True
    assert is_benchmark_publishable("built-in") is True


def test_local_and_builtin_packs_are_allowed() -> None:
    enforce_trust("local", adapter_type="python", sandbox=False)
    enforce_trust("built-in", adapter_type="subprocess", sandbox=False)


def test_sandbox_is_required_for_external_only() -> None:
    assert is_sandbox_required("external") is True
    assert is_sandbox_required("local") is False


def test_unknown_trust_fails_loudly() -> None:
    with pytest.raises(TrustError, match="unknown"):
        normalize_trust("cosmic")


def test_the_builtin_label_is_normalized() -> None:
    assert normalize_trust("built-in") == normalize_trust("builtin")
