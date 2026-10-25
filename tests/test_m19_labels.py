"""M19 19.6 — oracle honesty labels, F84 (RED → GREEN).

`calibrated` / `reviewed` / `experimental` per oracle on every result; an
`experimental` oracle cannot gate CI.
"""

from __future__ import annotations

import pytest

from agentdrill.credibility import (
    LabelError,
    OracleLabel,
    can_gate_ci,
    label_result,
    require_gate_capable,
)


def test_experimental_oracle_cannot_gate() -> None:
    assert can_gate_ci("experimental") is False
    with pytest.raises(LabelError, match="experimental"):
        require_gate_capable("experimental")


def test_calibrated_and_reviewed_can_gate() -> None:
    assert can_gate_ci("calibrated") is True
    assert can_gate_ci("reviewed") is True
    require_gate_capable("calibrated")  # no raise


def test_labels_attached_per_oracle_on_a_result() -> None:
    labels = label_result(
        [
            OracleLabel(oracle="deny", label="calibrated"),
            OracleLabel(oracle="judge", label="experimental"),
        ]
    )
    assert labels == {"deny": "calibrated", "judge": "experimental"}
