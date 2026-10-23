"""M9 9.4 — attribution, F38 / CUJ-14 (RED → GREEN).

Correlate a blocked→missed flip with the target-config diff / pin change /
adapter change that caused it. Emit `attributed_to` + stage/mechanism +
confidence; an unattributable flip is honestly `unknown`, never guessed. A
flip can also be bisected across intermediate configs.
"""

from __future__ import annotations

from agentdrill.comparison import (
    Attribution,
    RunChange,
    attribute_flip,
    bisect_flip,
)
from agentdrill.comparison.attack_engine import CaseDelta
from agentdrill.comparison.change_detection import ChangeReport


def _flip() -> CaseDelta:
    return CaseDelta(
        case_id="c1",
        golden_outcome="blocked",
        candidate_outcome="missed",
        changed=True,
        direction="regressed",
    )


def _report(**flags: bool) -> ChangeReport:
    changes = []
    if flags.get("adapter"):
        changes.append(RunChange(kind="adapter_changed", detail="driver digest differs"))
    if flags.get("model"):
        changes.append(RunChange(kind="model_changed", detail="model pin differs"))
    if flags.get("oracle"):
        changes.append(RunChange(kind="oracle_changed", detail="oracle versions differ"))
    return ChangeReport(
        adapter_changed=bool(flags.get("adapter")),
        model_changed=bool(flags.get("model")),
        oracle_changed=bool(flags.get("oracle")),
        changes=changes,
    )


def test_flip_with_adapter_change_attributes_to_adapter() -> None:
    result = attribute_flip(_flip(), _report(adapter=True))
    assert isinstance(result, Attribution)
    assert result.attributed_to == "adapter"
    assert result.stage == "delivery"
    assert result.mechanism
    assert result.confidence > 0.0


def test_flip_with_model_change_attributes_to_model() -> None:
    result = attribute_flip(_flip(), _report(model=True))
    assert result.attributed_to == "model"
    assert result.stage in ("judge", "model")


def test_flip_with_oracle_change_attributes_to_oracle() -> None:
    result = attribute_flip(_flip(), _report(oracle=True))
    assert result.attributed_to == "oracle"
    assert result.stage == "oracle"


def test_flip_with_target_config_diff_attributes_to_target_config() -> None:
    result = attribute_flip(_flip(), _report(), config_diffs={"policy": "deny -> audit"})
    assert result.attributed_to == "target_config"
    assert result.stage == "enforcement"


def test_unattributable_flip_is_unknown_never_guessed() -> None:
    result = attribute_flip(_flip(), _report())
    assert result.attributed_to == "unknown"
    assert result.confidence == 0.0
    assert result.mechanism == "unattributed"


def test_confidence_lower_when_multiple_changes_compete() -> None:
    single = attribute_flip(_flip(), _report(adapter=True))
    multiple = attribute_flip(_flip(), _report(adapter=True, model=True))
    assert multiple.confidence < single.confidence


def test_bisect_finds_the_first_flip() -> None:
    observations = ["unchanged", "unchanged", "regressed", "regressed"]
    assert bisect_flip(observations) == 2
    assert bisect_flip(["unchanged", "improved"]) is None
