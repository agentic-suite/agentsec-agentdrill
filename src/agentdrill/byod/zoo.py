"""Defense Zoo (M25 25.3, F90).

OSS-first reference adapters — OPA/Cedar, Llama Guard / Prompt Guard, NeMo
Guardrails, Docker/gVisor profiles and harness-native sandboxes. At least two
ship at v0.1.0 across at least two classes (six classes by v0.2). Design:
``docs/prd/29-bring-your-own-defense.md``.
"""

from __future__ import annotations

from pydantic import BaseModel

from agentdrill.byod.contract import DefenseContract, build_contract

#: The defense classes the Zoo covers.
ZOO_CLASSES: tuple[str, ...] = (
    "policy-engine",
    "model-guard",
    "guardrails",
    "sandbox",
    "harness-native",
)


class ZooAdapter(BaseModel):
    """A reference defense adapter in the Zoo."""

    name: str
    klass: str
    contract: DefenseContract


def default_zoo() -> list[ZooAdapter]:
    """The default reference adapters (>= 2 across >= 2 classes)."""
    specs = [
        ("opa-cedar", "policy-engine", {"rego": "deny-destructive"}),
        ("llama-guard", "model-guard", {"model": "llama-guard-3"}),
        ("docker-sandbox", "sandbox", {"runtime": "gvisor", "network": "none"}),
    ]
    zoo: list[ZooAdapter] = []
    for name, klass, config in specs:
        contract = build_contract(
            name=name,
            decision_points=["pre_tool"],
            io_shape="request/response",
            evidence=["decision", "rationale"],
            config=config,
            fail_mode="closed",
            version="1.0.0",
            tos_notes="OSS reference adapter",
        )
        zoo.append(ZooAdapter(name=name, klass=klass, contract=contract))
    return zoo


def zoo_classes(adapters: list[ZooAdapter]) -> set[str]:
    """The classes covered by ``adapters``."""
    return {adapter.klass for adapter in adapters}
