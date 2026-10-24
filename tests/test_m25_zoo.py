"""M25 25.3 — Defense Zoo, F90 (RED → GREEN).

OSS-first reference adapters (OPA/Cedar, Llama Guard, NeMo Guardrails,
Docker/gVisor, harness-native); ≥2 at v0.1.0 across ≥2 classes.
"""

from __future__ import annotations

from agentdrill.byod import ZOO_CLASSES, ZooAdapter, default_zoo


def test_at_least_two_reference_adapters() -> None:
    zoo = default_zoo()
    assert len(zoo) >= 2
    assert all(isinstance(adapter, ZooAdapter) for adapter in zoo)


def test_adapters_span_multiple_classes() -> None:
    classes = {adapter.klass for adapter in default_zoo()}
    assert len(classes) >= 2
    assert classes <= set(ZOO_CLASSES)


def test_each_adapter_has_a_contract() -> None:
    for adapter in default_zoo():
        assert adapter.contract.name == adapter.name
        assert adapter.contract.decision_points
        assert adapter.contract.config_digest
