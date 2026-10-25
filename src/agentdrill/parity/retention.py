"""Predecessor retention plan (M21 21.4).

Confirm agentdrill is self-contained and record the M32 instruction to make the
predecessor repository **private** — never delete it. Design:
``docs/prd/03-landscape.md``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

#: The recorded action for the release-readiness milestone.
M32_ACTION = "M32: make the predecessor repository private (never delete)"


class RetentionPlan(BaseModel):
    """The predecessor retention plan."""

    self_contained: bool
    predecessor_repo: str
    provenance_ref: str
    action_at_m32: str = M32_ACTION
    never_delete: bool = True


def build_retention(
    *, self_contained: bool, predecessor_repo: str, provenance_ref: str
) -> RetentionPlan:
    """Build the retention plan (self-contained + make-private at M32)."""
    return RetentionPlan(
        self_contained=self_contained,
        predecessor_repo=predecessor_repo,
        provenance_ref=provenance_ref,
    )


def retention_record(plan: RetentionPlan) -> dict[str, Any]:
    """The public retention record."""
    return {
        "self_contained": plan.self_contained,
        "predecessor_repo": plan.predecessor_repo,
        "provenance_ref": plan.provenance_ref,
        "action_at_m32": plan.action_at_m32,
        "never_delete": plan.never_delete,
    }
