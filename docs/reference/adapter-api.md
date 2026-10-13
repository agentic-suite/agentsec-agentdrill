# Adapter API

**Status:** normative for **drivers** (M4) and **targets** (M5); implemented in `src/agentdrill/drivers/`
and `src/agentdrill/targets/`. The Defense Contract remains design intent until M25. Design:
[../design/adapter-contract.md](../design/adapter-contract.md) · Recon: [../design/recon.md](../design/recon.md) ·
Guide: [custom-adapter-guide.md](custom-adapter-guide.md).

## Driver

```python
class Driver(ABC):
    name: ClassVar[str]                                   # matches case.driver.type
    def run(self, case: AttackCase, config: dict) -> CaseOutcome: ...
    # implement _invoke(payload, config) -> str | dict
```

| Aspect | Requirement |
|---|---|
| Input `payload` | `case_id`, `goal`, `target`, `attack` (steps), `budget` — **no `oracle`/`expect`/thresholds/benign_twin** |
| Return `str` | raw stdout → text output, empty trajectory |
| Return `dict` | `agentdrill.run_envelope.v1` (schema: [`schema/run-envelope.schema.json`](../../schema/run-envelope.schema.json)) |
| Timeout | raise `AgentTimeoutError` |
| Error | raise `AdapterError`; missing config → `ConfigError` |

Built-in drivers: `subprocess`, `python`, `http`, `claude-code`, `cursor`. The base handles payload
building + envelope normalization; the M3 runner owns timing, timeouts, status and artifact writing.

## Target

```python
class Target(ABC):
    component: ClassVar[str]                               # matches case.target.type
    def drive(self, case: AttackCase) -> None: ...
    def read_decision(self) -> Decision: ...
    def read_evidence(self) -> list[Evidence]: ...
```

Built-in targets (registry: `agentdrill.targets.registry.TARGETS`): `agentgate`, `agentkeys`,
`agentseatbelt`, `agentkernel`, `policyweave-output`, `agenthalt`. Targets drive the **deployed enforcement
path** (agentdrill owns no enforcement, ADR-0003) and record their `attestation`.

`CommandTarget` drives a component through `config["command"]` (attack payload on stdin → a
`{"decision": {...}, "evidence": [...]}` envelope on stdout). `Decision` carries
`decision ∈ {allow, deny, ask, unknown}` + `rationale`; `Evidence` carries an agentwatch `event`.

## Attestation

Every component records its realness — `live` / `fixture` / `mock`
(`agentdrill.attestation`). A run's published label is the **weakest link** in its chain
(`chain_attestation`); an empty chain is conservatively `mock`. The label is bound into `run.json`.

## Registration

The driver registry is `agentdrill.drivers.registry.DRIVERS`; register with `register(DriverClass)` or via
the `agentdrill.drivers` **entry-point group** (`discover()`). An `AdapterManifest` (name, capabilities,
required secrets **by name**, SHA-256 digest — `manifest_for(DriverClass)`) is bound into each run's
`run.json`. Unknown name → `ConfigError`.

## Defense Contract (BYOD — PRD 29)

Any **defense** (guardrail, policy engine, gateway, broker, sandbox, scanner, HITL control) can be drilled by
implementing the **Defense Contract** and passing the **conformance kit**:

```python
class Defense(ABC):
    decision_points: list[str]        # input_filter | tool_authorize | egress | grant | revoke ...
    def decide(self, request: DefenseRequest) -> Decision: ...
    def read_evidence(self) -> list[Evidence]: ...
    config_digest: str                # hash of the exact configuration (binds every result)
    fail_mode: Literal["open", "closed"]
    version: str
    tos_notes: str                    # license/ToS (benchmarking clauses) — recorded per run
```

Conformance levels and the Defense Zoo are in [design/byod-and-neutral-head-to-head](../design/byod-and-neutral-head-to-head.md).
Head-to-heads carry **no composite score or ranking**.

## Custom adapter

```python
from agentdrill.drivers import Driver

class MyDriver(Driver):
    name = "my-driver"
    def _invoke(self, payload, config):
        return {"schema_version": "agentdrill.run_envelope.v1", "status": "completed",
                "output": {"final": payload["goal"], "structured": None},
                "trajectory": {"steps": []}, "cost": None, "error": None}
```

## Guarantees

- **No ground-truth leakage** — asserted per driver.
- **Attestation** — a target declares its realness; results labeled at the weakest link.
- **Digest-bound** — a swap is detected by comparison, not mistaken for a regression.
