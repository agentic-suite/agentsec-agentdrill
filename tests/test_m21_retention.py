"""M21 21.4 — predecessor retention plan (RED → GREEN).

Confirm agentdrill is self-contained and record the M32 instruction to make the
predecessor private (never delete).
"""

from __future__ import annotations

from agentdrill.parity import RetentionPlan, build_retention, retention_record


def test_retention_plan_records_make_private_at_m32() -> None:
    plan = build_retention(
        self_contained=True,
        predecessor_repo="agent-exec-trace",
        provenance_ref="THIRD_PARTY_NOTICES.md",
    )
    assert isinstance(plan, RetentionPlan)
    assert plan.self_contained is True
    assert "private" in plan.action_at_m32.lower()
    assert "M32" in plan.action_at_m32


def test_never_delete_is_true() -> None:
    plan = build_retention(
        self_contained=True, predecessor_repo="agent-exec-trace", provenance_ref="x"
    )
    assert plan.never_delete is True


def test_retention_record_is_a_dict() -> None:
    record = retention_record(
        build_retention(
            self_contained=True, predecessor_repo="agent-exec-trace", provenance_ref="x"
        )
    )
    assert record["self_contained"] is True
    assert record["never_delete"] is True
