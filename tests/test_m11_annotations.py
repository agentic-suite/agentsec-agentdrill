"""M11 11.7 — PR annotations + alerts, F47 (RED → GREEN).

Annotate the PR with case/stage/evidence/attribution; a regression annotates
the right file; a gate failure posts an alert (Slack/webhook).
"""

from __future__ import annotations

import json
from typing import Any

from agentdrill.ci import (
    Annotation,
    GateFailure,
    annotate,
    build_alert,
    github_annotation,
    notify,
)
from agentdrill.comparison import Attribution
from agentdrill.comparison.attack_engine import CaseDelta


def _regression() -> CaseDelta:
    return CaseDelta(
        case_id="c1",
        golden_outcome="blocked",
        candidate_outcome="missed",
        changed=True,
        direction="regressed",
    )


def _attribution() -> Attribution:
    return Attribution(
        case_id="c1",
        direction="regressed",
        attributed_to="target_config",
        stage="enforcement",
        mechanism="target_config_changed",
        confidence=0.9,
    )


def test_regression_annotates_the_right_file() -> None:
    annotation = annotate(
        _regression(),
        file="policies/policyweave.yaml",
        line=12,
        stage="enforcement",
        evidence=["policy-fired"],
        attribution=_attribution(),
    )
    assert isinstance(annotation, Annotation)
    assert annotation.file == "policies/policyweave.yaml"
    assert annotation.line == 12
    assert annotation.level == "error"


def test_annotation_message_names_case_stage_evidence_attribution() -> None:
    annotation = annotate(
        _regression(),
        file="policies/policyweave.yaml",
        stage="enforcement",
        evidence=["policy-fired"],
        attribution=_attribution(),
    )
    assert "c1" in annotation.message
    assert "enforcement" in annotation.message
    assert "policy-fired" in annotation.message
    assert "target_config" in annotation.message


def test_github_annotation_format() -> None:
    line = github_annotation(
        annotate(_regression(), file="policies/policyweave.yaml", line=12, stage="enforcement")
    )
    assert line.startswith("::error file=policies/policyweave.yaml,line=12::")


def test_alert_payload_on_gate_failure() -> None:
    payload = build_alert(4, [GateFailure(kind="dimension", dimension="enforcement")])
    assert payload["exit_code"] == 4
    assert payload["failures"][0]["dimension"] == "enforcement"


def test_notify_posts_to_webhook() -> None:
    calls: list[tuple[str, Any]] = []

    def stub_post(url: str, payload: dict[str, Any]) -> None:
        calls.append((url, payload))

    payload = build_alert(4, [])
    notify("https://hooks.example/x", payload, poster=stub_post)
    assert calls == [("https://hooks.example/x", payload)]
    assert json.dumps(payload)  # payload is JSON-serializable


def test_notification_is_skipped_without_a_webhook() -> None:
    calls: list[Any] = []
    notify(None, {"exit_code": 4}, poster=lambda u, p: calls.append((u, p)))
    assert calls == []
