"""M29 29.7 — frontier classes 2 (browser), 3 (multimodal) & 8 (AP2 stub).

Class 2 (ASI01/02/05) needs a sandbox + domain allowlist + form-fill guard; class
3 (ASI01) needs ≥12 payload carriers; class 8 is the **spec-gated** AP2 payments
stub (never claimed as implemented).
"""

from __future__ import annotations

import pytest

from agentdrill.frontier import (
    FRONTIER_CLASSES,
    FrontierError,
    require_browser_guards,
    require_carriers,
    require_spec_gated,
)


def test_registry_knows_classes_two_three_and_eight() -> None:
    assert FRONTIER_CLASSES[2].asi == ["ASI01", "ASI02", "ASI05"]
    assert "browser" in FRONTIER_CLASSES[2].name.lower()
    assert FRONTIER_CLASSES[3].asi == ["ASI01"]
    assert "multimodal" in FRONTIER_CLASSES[3].name.lower()
    assert FRONTIER_CLASSES[8].spec_gated is True


def test_carriers_are_at_least_twelve() -> None:
    require_carriers(FRONTIER_CLASSES[3].carriers)  # the registry meets the bar
    require_carriers(12)
    with pytest.raises(FrontierError):
        require_carriers(11)


def test_browser_guards_are_required() -> None:
    require_browser_guards(sandbox=True, allowlist=True, form_fill_guard=True)
    with pytest.raises(FrontierError):
        require_browser_guards(sandbox=False, allowlist=True, form_fill_guard=True)
    with pytest.raises(FrontierError):
        require_browser_guards(sandbox=True, allowlist=False, form_fill_guard=True)
    with pytest.raises(FrontierError):
        require_browser_guards(sandbox=True, allowlist=True, form_fill_guard=False)


def test_the_ap2_stub_is_always_marked_spec_gated() -> None:
    require_spec_gated(FRONTIER_CLASSES[8])
    with pytest.raises(FrontierError):
        require_spec_gated(FRONTIER_CLASSES[8].model_copy(update={"spec_gated": False}))
