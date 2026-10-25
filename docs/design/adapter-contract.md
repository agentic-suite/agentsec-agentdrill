# Adapter Contract — Design

**BLUF:** Two adapter families: **drivers** deliver the attack (subprocess / python / http / per-harness),
**targets** drive the deployed stack and read back decisions + evidence. Both keep the predecessor's
contract discipline — a restricted payload, a normalized envelope, normalized errors — plus the invariant
that **oracles/expected outcomes never reach the driver** (DD-03).

> **Implemented (M4 drivers, M5 targets).** Drivers in `src/agentdrill/drivers/`; targets + recon in
> `src/agentdrill/targets/` and `src/agentdrill/recon.py`. The Defense Contract remains built (v0.1.0) (M25).
> Reference: [../reference/adapter-api.md](../reference/adapter-api.md) ·
> [../reference/custom-adapter-guide.md](../reference/custom-adapter-guide.md) ·
> [recon.md](recon.md).

## Driver contract

```python
class Driver(ABC):
    name: str
    def run(self, case: AttackCase, config: dict) -> RunArtifact: ...
```

Agents implement `_invoke(payload, config)`; the base handles payload building, timing, error
normalization, and artifact construction.

| Aspect | Requirement |
|---|---|
| Input | Restricted payload: `input`, `context`, `allowed_tools`, `disallowed_tools`, `budget`. **No `oracle`/`expect`/thresholds.** |
| Return `str` | raw stdout → parsed as text output (empty trajectory) |
| Return `dict` | a run envelope (below) |
| Timeout | raise `AgentTimeoutError` |
| Error | raise `AdapterError` for any other failure |

Run envelope (`agentdrill.run_envelope.v1`):
```json
{"schema_version":"agentdrill.run_envelope.v1","status":"completed",
 "output":{"final":"…","structured":null},
 "trajectory":{"steps":[]},"cost":{...},"error":null}
```

Adapters: `subprocess` (stdin JSON → stdout envelope, raw-text fallback unless `strict_output`),
`python` (callable in a separate process for hard timeout), `http`, and per-harness drivers
(`claude-code`, `cursor`).

## Target contract

```python
class Target(ABC):
    def drive(self, case: AttackCase) -> None: ...
    def read_decision(self) -> Decision: ...
    def read_evidence(self) -> list[Evidence]: ...
```

Targets: `agentgate` (MCP proxy), `agentkeys` (broker), `agentseatbelt`/`agentkernel` (confinement),
`policyweave-output` (compiled policy), `agenthalt` (halt/revoke). Each declares `attestation`
(`live`/`fixture`/`mock`).

## Registry & discovery

`ADAPTERS` / `TARGETS` registries + entry-point discovery; unknown → `ConfigError`. Each driver/target
carries an `AdapterManifest` with a SHA-256 digest bound into the run (comparison detects a swap, not a
regression).

## Invariants

- **No ground-truth leakage** (DD-03) — asserted by a guard test per driver.
- **Attestation weakest-link** — a run's published label is the weakest `live`/`fixture`/`mock` in its chain.
- **Never silent** — unknown names and unreachable model surfaces fail before any case runs.
