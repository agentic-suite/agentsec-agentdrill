"""M28 28.6 — rules of engagement (RED → GREEN).

A signed, versioned RoE (targets+ownership, env class, effect classes,
canary-only, windows, ceilings, caps, tier ceiling, approvers, contacts, aborts);
a **fail-closed preflight** that refuses to fire on any violation; and per-action
**scope receipts** (hash-chained).
"""

from __future__ import annotations

import pytest

from agentdrill.roe import (
    CaseRequest,
    EnvClass,
    PreflightResult,
    RoE,
    RoEError,
    preflight,
    require_allowed,
    require_signed,
    scope_receipt,
    sign_roe,
    verify_receipt_chain,
    verify_roe,
)

_KEY = "s3cret"


def _roe(**over: object) -> RoE:
    base = dict(
        version="1.0",
        targets=["policyweave-output"],
        ownership={"policyweave-output": "team@example.com"},
        env_class="ephemeral",
        allowed_effect_classes=["data_access", "network"],
        canary_only=True,
        windows=["2026-02-01/2026-02-28"],
        rate_ceiling=100,
        cost_ceiling_usd=5.0,
        blast_radius_cap=3,
        tier_ceiling="T2",
        approvers=["ciso@example.com"],
        contacts=["oncall@example.com"],
        abort_conditions=["egress observed"],
    )
    base.update(over)
    return RoE.model_validate(base)


def _request(**over: object) -> CaseRequest:
    base = dict(
        case_id="c1",
        target="policyweave-output",
        effect_class="data_access",
        now="2026-02-10",
        tier="T1",
        canary=True,
        rate=10,
        cost_usd=0.5,
        blast_radius=1,
    )
    base.update(over)
    return CaseRequest.model_validate(base)


def _signed(**over: object) -> RoE:
    return sign_roe(_roe(**over), secret=_KEY)


def test_a_preflight_that_meets_every_rule_is_allowed() -> None:
    result = preflight(_signed(), _request())
    assert isinstance(result, PreflightResult)
    assert result.allowed is True
    assert result.refusals == []
    require_allowed(result)


def test_env_class_vocabulary() -> None:
    assert set(EnvClass.__args__) == {"ephemeral", "purple", "prod"}


def test_each_refusal_is_fail_closed() -> None:
    cases = {
        "roe_unsigned": (preflight(_roe(), _request()),),
        "target_out_of_scope": (preflight(_signed(), _request(target="other")),),
        "ownership_unverified": (preflight(_signed(ownership={}), _request()),),
        "effect_class_not_allowed": (preflight(_signed(), _request(effect_class="destructive")),),
        "canary_required": (preflight(_signed(), _request(canary=False)),),
        "outside_window": (preflight(_signed(), _request(now="2026-03-15")),),
        "rate_ceiling_exceeded": (preflight(_signed(), _request(rate=1000)),),
        "cost_ceiling_exceeded": (preflight(_signed(), _request(cost_usd=99.0)),),
        "blast_radius_cap_exceeded": (preflight(_signed(), _request(blast_radius=9)),),
        "tier_ceiling_exceeded": (preflight(_signed(), _request(tier="T3")),),
        "third_party_hosts_resolvable": (
            preflight(_signed(), _request(third_party_hosts=["evil.example"])),
        ),
        "witness_unhealthy": (preflight(_signed(), _request(witness_healthy=False)),),
        "cleanup_unverified": (preflight(_signed(), _request(cleanup_verified=False)),),
    }
    for expected, (result,) in cases.items():
        assert result.allowed is False, expected
        assert expected in result.refusals, expected
        with pytest.raises(RoEError):
            require_allowed(result)


def test_a_prod_environment_never_permits_destructive_effects() -> None:
    roe = _signed(env_class="prod", allowed_effect_classes=["destructive"])
    result = preflight(roe, _request(effect_class="destructive"))
    assert result.allowed is False
    assert "env_would_not_permit_effect" in result.refusals


def test_roe_is_signed_and_verified() -> None:
    signed = _signed()
    assert verify_roe(signed, secret=_KEY) is True
    assert verify_roe(signed, secret="wrong") is False  # noqa: S106
    require_signed(signed)
    with pytest.raises(RoEError):
        require_signed(_roe())


def test_scope_receipts_are_hash_chained() -> None:
    roe = _signed()
    first = scope_receipt(roe, _request(case_id="c1"))
    second = scope_receipt(roe, _request(case_id="c2"), prev=first)
    assert first.hash_prev == ""
    assert second.hash_prev == first.digest
    assert verify_receipt_chain([first, second]) is True

    tampered = second.model_copy(update={"target": "other"})
    assert verify_receipt_chain([first, tampered]) is False
    assert verify_receipt_chain([second]) is False  # a broken chain head
