"""Side-effect ledger + human-surface (M23 23.4, F87).

A witness DB / mock SaaS recording calls, and an approval-dialog vs
executed-action check so business-logic and approval effects are detected.
Design: ``docs/prd/26-independent-effect-witness.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MockSaas(BaseModel):
    """A mock SaaS surface that records the calls made against it."""

    name: str
    calls: list[str] = Field(default_factory=list)

    def call(self, action: str) -> None:
        """Record a call against the mock SaaS."""
        self.calls.append(action)


class SideEffectLedger(BaseModel):
    """A ledger of business-logic side effects observed by witnesses."""

    recorded: list[str] = Field(default_factory=list)

    def record(self, call: str) -> None:
        """Record a side-effect call."""
        self.recorded.append(call)


class ApprovalCheck(BaseModel):
    """An approval-dialog vs executed-action check."""

    approved: bool
    executed: bool

    @property
    def mismatch(self) -> bool:
        """Whether the action executed without approval (a human-surface effect)."""
        return self.executed and not self.approved


def check_approval(*, approved: bool, executed: bool) -> ApprovalCheck:
    """Check whether an action ran without approval."""
    return ApprovalCheck(approved=approved, executed=executed)
