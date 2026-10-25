"""Trust-level enforcement (M16 16.3).

``built-in`` / ``local`` / ``external`` are enforced at load/run: an
``external`` (untrusted) pack must use a **sandboxed subprocess** only and is
**never benchmark-published**. Design:
``docs/prd/17-pack-registry-and-governance.md``.
"""

from __future__ import annotations

from agentdrill.security.policy import TrustPolicy

#: Canonical trust labels.
TRUST_LEVELS: tuple[str, ...] = ("builtin", "local", "external")


class TrustError(ValueError):
    """Raised when a pack's trust level forbids the requested execution."""


def normalize_trust(trust: str) -> str:
    """Normalize a trust label to the policy vocabulary (``builtin``/``local``/``external``).

    Accepts ``built-in`` as an alias for ``builtin``.

    Raises:
        TrustError: The label is not a known trust level.
    """
    normalized = "builtin" if trust == "built-in" else trust
    if normalized not in TRUST_LEVELS:
        raise TrustError(f"unknown trust level: {trust!r}; known: {list(TRUST_LEVELS)}")
    return normalized


def is_sandbox_required(trust: str) -> bool:
    """Whether a pack at ``trust`` requires sandboxed execution."""
    return normalize_trust(trust) == "external"


def is_benchmark_publishable(trust: str) -> bool:
    """Whether a pack at ``trust`` may be benchmark-published (external never may)."""
    return normalize_trust(trust) != "external"


def enforce_trust(trust: str, *, adapter_type: str, sandbox: bool) -> None:
    """Enforce the trust/adapter/sandbox matrix for a pack.

    Raises:
        TrustError: The trust/adapter/sandbox combination is not allowed (e.g.
            an external pack with a non-subprocess adapter, or without sandbox).
    """
    normalized = normalize_trust(trust)
    allowed, reason = TrustPolicy(
        trust=normalized,  # type: ignore[arg-type]
        adapter_type=adapter_type,
        sandbox=sandbox,
    ).allowed()
    if not allowed:
        raise TrustError(f"trust {trust!r} forbids this execution: {reason}")
