# Errors

**Status:** built (v0.1.0). The error contract: structured codes, never a silent pass.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | all cases behaved as expected |
| 1 | one or more cases missed |
| 2 | configuration error (invalid pack, unknown oracle/target/driver, bad config) |
| 3 | oracle/judge infrastructure error |
| 4 | critical miss (a must-block enforcement case was not blocked) |
| 5 | critical divergence |

Resolution: critical miss (4) > config (2) > oracle infra (3) > miss (1) > pass (0).

## Error classes

| Class | Raised when |
|---|---|
| `PackParseError` | malformed pack; carries file + line |
| `ConfigError` | unknown oracle/target/driver; invalid config |
| `AdapterError` | a driver/target fails |
| `AgentTimeoutError` | per-case timeout |
| `OracleError` | deterministic oracle failure |
| `JudgeError` | judge call failure/malformed verdict |
| `WitnessError` | effect witness failed/untrusted → `witness_unavailable` (M23) |
| `RoEError` | RoE missing/invalid, or a case is **out of scope** → case refuses to fire (M28) |
| `AttestationError` | drill attestation invalid/forged/stale (M28) |

## Behaviors

| Failure | Behavior |
|---|---|
| Invalid pack | fail at load (exit 2) |
| Unknown reference | `ConfigError` before any case runs |
| Case timeout | `status="timeout"`, continue |
| Case crash | `status="error"` + stderr, continue |
| Oracle raises | result `error`, case failed, continue |
| Judge unavailable | `judge_not_evaluated: true`, deterministic result stands |
| Cleanup failure | `dirty_target` finding (release-blocking) |
| Evidence missing | `evidence_gap` finding |
| Witness failed/untrusted | `witness_unavailable`; the case **cannot** publish as `blocked` (M23) |
| Defense denied but effect landed | `witness_discrepancy` finding (integrity, highest severity) |
| Case out of RoE scope | refuses to fire; recorded; run continues (M28) |
| Attestation invalid/stale | consumer (deploy gate) rejects; re-drill required (M28) |
| Telemetry absent for a `blocked` | `telemetry_gap` finding |

> **Rule:** every failure is surfaced (§ taxonomy) and **never** silently green. A case failure never aborts
> the pack.
