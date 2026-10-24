"""M28 28.4 — drill attestation (RED → GREEN).

The claim model + the in-toto ``agentdrill/drill-result/v1`` predicate: the
statement binds ``config_digest`` and carries packs@ver/hash, tiers/k,
outcomes+CIs, witness coverage, live/fixture/mock, oracle versions, known
misses/waivers, lab, standards pins, issued/expires — and always lists what was
**NOT** drilled. Signing is verified (forgery rejected) and ``mock``/``fixture``
are **non-evidence**.
"""

from __future__ import annotations

import time

import pytest

from agentdrill.attestations import (
    PREDICATE_KIND,
    AttestationError,
    DrillClaim,
    OutcomeCI,
    SignedAttestation,
    attest,
    build_statement,
    is_evidence,
    require_evidence,
    sign_statement,
    verify_statement,
)

#: A fake key for the tests.
_KEY = "s3cret"


def _claim(**over: object) -> DrillClaim:
    base = dict(
        config_digest="sha256:abc",
        packs=["incidents-core@1.0.0+deadbeef"],
        tiers=["T0", "T1"],
        k=5,
        outcomes={"missed": OutcomeCI(point=0.12, low=0.05, high=0.22, n=40)},
        witness_coverage=0.97,
        realness="live",
        oracle_versions={"deny": "1.2.0"},
        known_misses=["c-miss"],
        waivers=["w3"],
        lab="lab@1.0.0",
        standards_pins={"atlas": "2026.01"},
        issued="2026-02-01",
        expires="2026-05-01",
        not_drilled=["wallet class", "browser class"],
    )
    base.update(over)
    return DrillClaim.model_validate(base)


def test_statement_uses_the_intoto_predicate_and_binds_the_config_digest() -> None:
    statement = build_statement(_claim())
    assert statement.predicateType == PREDICATE_KIND == "agentdrill/drill-result/v1"
    assert statement.subject[0].digest == {"sha256": "sha256:abc"}
    assert statement.predicate.k == 5
    assert statement.predicate.not_drilled == ["wallet class", "browser class"]


def test_signing_verifies_and_rejects_forgery() -> None:
    signed = sign_statement(build_statement(_claim()), keyid="k1", secret=_KEY)
    assert isinstance(signed, SignedAttestation)
    assert verify_statement(signed, secret=_KEY) is True
    assert verify_statement(signed, secret="wrong") is False  # noqa: S106 - a fake secret

    forged = signed.model_copy(
        update={"statement": signed.statement.model_copy(update={"predicateType": "evil/v1"})}
    )
    assert verify_statement(forged, secret=_KEY) is False


def test_verification_is_fast() -> None:
    signed = attest(_claim(), keyid="k1", secret=_KEY)
    start = time.perf_counter()
    assert verify_statement(signed, secret=_KEY) is True
    assert time.perf_counter() - start < 2.0


def test_mock_and_fixture_are_non_evidence() -> None:
    assert is_evidence("live") is True
    assert is_evidence("mock") is False
    assert is_evidence("fixture") is False
    require_evidence("live")
    with pytest.raises(AttestationError):
        require_evidence("mock")


def test_missing_not_drilled_list_fails_loudly() -> None:
    with pytest.raises(AttestationError):
        build_statement(_claim(not_drilled=[]))
    with pytest.raises(AttestationError):
        build_statement(_claim(realness="mock"))


def test_an_unsigned_attestation_never_verifies() -> None:
    statement = build_statement(_claim())
    unsigned = SignedAttestation(statement=statement)
    assert verify_statement(unsigned, secret=_KEY) is False
