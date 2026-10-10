# Adapter API

**Status:** draft (design intent). Design: [../design/adapter-contract.md](../design/adapter-contract.md).

## Driver

```python
class Driver(ABC):
    name: str
    def run(self, case: AttackCase, config: dict) -> RunArtifact: ...
    # implement _invoke(payload, config) -> str | dict
```

| Aspect | Requirement |
|---|---|
| Input `payload` | `input`, `context`, `allowed_tools`, `disallowed_tools`, `budget` — **no oracle/expect/thresholds** |
| Return `str` | raw stdout → text output, empty trajectory |
| Return `dict` | `agentdrill.run_envelope.v1` |
| Timeout | raise `AgentTimeoutError` |
| Error | raise `AdapterError` |

Built-in drivers: `subprocess`, `python`, `http`, `claude-code`, `cursor`.

## Target

```python
class Target(ABC):
    def drive(self, case: AttackCase) -> None: ...
    def read_decision(self) -> Decision: ...
    def read_evidence(self) -> list[Evidence]: ...
    attestation: Literal["live", "fixture", "mock"]
```

Built-in targets: `agentgate`, `agentkeys`, `agentseatbelt`, `agentkernel`, `policyweave-output`, `agenthalt`.

## Registration

Register in `ADAPTERS`/`TARGETS` or via entry points; an `AdapterManifest` (name, capabilities, required
secrets **by name**, SHA-256 digest) is bound into each run. Unknown name → `ConfigError`.

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
from agentdrill.adapters import Driver
class MyDriver(Driver):
    name = "my-driver"
    def _invoke(self, payload, config):
        return {"schema_version": "agentdrill.run_envelope.v1", "status": "completed",
                "output": {"final": payload["input"], "structured": None},
                "trajectory": {"steps": []}, "cost": None, "error": None}
```

## Guarantees

- **No ground-truth leakage** — asserted per driver.
- **Attestation** — a target declares its realness; results labeled at the weakest link.
- **Digest-bound** — a swap is detected by comparison, not mistaken for a regression.
