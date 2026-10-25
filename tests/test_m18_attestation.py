"""M18 18.4 — target attestation, F63 (RED → GREEN).

`live` / `fixture` / `mock` per component; a result is labeled at the **weakest
link**, and a `mock`-attested result can never publish.
"""

from __future__ import annotations

import pytest

from agentdrill.lifecycle import (
    AttestationError,
    can_publish,
    require_publishable,
    result_attestation,
)


def test_result_is_labeled_at_the_weakest_link() -> None:
    assert result_attestation(["live", "fixture"]) == "fixture"
    assert result_attestation(["live", "live"]) == "live"
    assert result_attestation(["live", "mock"]) == "mock"


def test_an_empty_chain_is_mock() -> None:
    assert result_attestation([]) == "mock"


def test_mock_attested_result_cannot_publish() -> None:
    assert can_publish("mock") is False
    with pytest.raises(AttestationError, match="mock"):
        require_publishable("mock")


def test_live_and_fixture_can_publish() -> None:
    assert can_publish("live") is True
    assert can_publish("fixture") is True
    require_publishable("fixture")  # no raise
