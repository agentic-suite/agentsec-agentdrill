"""M28 28.5 — freshness + consumers (RED → GREEN).

Auto-invalidate a drill attestation on: config-digest change, security-deprecated
pack, a relevant new incident, an oracle major bump, a waiver expiry — and on its
own expiry. Model the ≥4 reference consumers (CLI, GitHub Action, K8s admission,
agentgate) and keep ``mock``/``fixture`` as **non-evidence**.
"""

from __future__ import annotations

import pytest

from agentdrill.attestations import (
    CONSUMERS,
    AttestationError,
    DrillClaim,
    FreshnessContext,
    OutcomeCI,
    assess,
    attest,
    check_freshness,
    require_fresh,
)

_KEY = "s3cret"


def _claim(**over: object) -> DrillClaim:
    base = dict(
        config_digest="sha256:abc",
        packs=["incidents-core@1.0.0+deadbeef"],
        tiers=["T0"],
        k=5,
        outcomes={"missed": OutcomeCI(point=0.1, low=0.0, high=0.2, n=10)},
        witness_coverage=0.97,
        realness="live",
        oracle_versions={"deny": "1.2.0"},
        waivers=["w3"],
        issued="2026-02-01",
        expires="2026-05-01",
        not_drilled=["browser class"],
    )
    base.update(over)
    return DrillClaim.model_validate(base)


def _context(**over: object) -> FreshnessContext:
    base: dict[str, object] = {"config_digest": "sha256:abc"}
    base.update(over)
    return FreshnessContext.model_validate(base)


def test_four_reference_consumers_are_modelled() -> None:
    assert set(CONSUMERS) == {"cli", "github-action", "k8s-admission", "agentgate"}


def test_fresh_when_nothing_changed() -> None:
    invalidity = check_freshness(_claim(), _context(), now="2026-03-01")
    assert invalidity.stale is False
    assert invalidity.reasons == []
    require_fresh(invalidity)


def test_each_invalidation_trigger_fires() -> None:
    cases = {
        "config_changed": (_claim(), _context(config_digest="sha256:different"), "2026-03-01"),
        "pack_deprecated": (
            _claim(),
            _context(deprecated_packs=["incidents-core@1.0.0+deadbeef"]),
            "2026-03-01",
        ),
        "new_incident": (_claim(), _context(new_incidents=["GHSA-1"]), "2026-03-01"),
        "oracle_major_bump": (
            _claim(),
            _context(oracle_versions={"deny": "2.0.0"}),
            "2026-03-01",
        ),
        "waiver_expired": (_claim(), _context(expired_waivers=["w3"]), "2026-03-01"),
        "attestation_expired": (_claim(), _context(), "2026-06-01"),
    }
    for expected, (claim, context, now) in cases.items():
        invalidity = check_freshness(claim, context, now=now)
        assert invalidity.stale is True, expected
        assert expected in invalidity.reasons, expected
        with pytest.raises(AttestationError):
            require_fresh(invalidity)


def test_patch_level_oracle_bump_does_not_invalidate() -> None:
    invalidity = check_freshness(
        _claim(), _context(oracle_versions={"deny": "1.4.0"}), now="2026-03-01"
    )
    assert invalidity.stale is False


def test_assess_verifies_and_serves_every_consumer() -> None:
    signed = attest(_claim(), keyid="k1", secret=_KEY)
    good = assess(signed, _context(), now="2026-03-01", secret=_KEY)
    assert good.valid is True
    assert good.fresh is True
    assert good.evidence is True
    assert len(good.consumers) == 4
    assert all(verdict.accept for verdict in good.consumers)

    stale = assess(signed, _context(config_digest="sha256:x"), now="2026-03-01", secret=_KEY)
    assert stale.fresh is False
    assert all(not verdict.accept for verdict in stale.consumers)


def test_forged_or_mock_attestations_are_rejected_by_consumers() -> None:
    signed = attest(_claim(), keyid="k1", secret=_KEY)
    forged = assess(signed, _context(), now="2026-03-01", secret="wrong")  # noqa: S106
    assert forged.valid is False
    assert all(not verdict.accept for verdict in forged.consumers)

    mock = attest(_claim(realness="live"), keyid="k1", secret=_KEY)
    mock = mock.model_copy(
        update={"statement": mock.statement.model_copy(
            update={"predicate": mock.statement.predicate.model_copy(update={"realness": "mock"})}
        )}
    )
    assessed = assess(mock, _context(), now="2026-03-01", secret=_KEY)
    assert assessed.evidence is False
    assert all(not verdict.accept for verdict in assessed.consumers)
