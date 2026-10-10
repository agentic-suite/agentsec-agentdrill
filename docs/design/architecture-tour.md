# Architecture Tour

**BLUF:** A guided walkthrough of the drill path — from an attack pack case to a *deployed* enforcement
decision, an evidence-bound result, and an honest published number.

> **Design intent** (pre-build). Rewritten against the built system at M31–M32.

## The path

The runner, scoring engine, adapter contract, fixtures, and comparison/reporting are the **absorbed
predecessor mechanics** (WBS M0); the attack-pack format, target adapters, kill-chain probe, and the honest
benchmark are re-pointed/added in M2–M13.

1. **Pack** — a versioned attack pack is loaded and strictly validated ([pack-format](pack-format.md));
   identifiers enforced path-safe.
2. **Recon** — the recon phase probes the target's exposed surface and binds cases to what exists.
3. **Driver** — the case is delivered through a **driver** adapter (subprocess/python/http/harness) that
   receives a restricted payload — **never** the oracle/expected outcome ([adapter-contract](adapter-contract.md)).
4. **Target** — the **target** adapter drives the deployed component (agentgate / agentkeys / agentseatbelt
   / agentkernel / policyweave-output / agenthalt) into the attack posture.
5. **Evidence** — records/security events are read from **agentwatch** and bound to the result; expected
   telemetry is validated ([evidence-integration](evidence-integration.md)).
6. **Oracle** — deterministic oracles first, judge where needed → `blocked` / `missed` / `degraded`
   ([oracle-engine](oracle-engine.md)).
7. **Kill-time** — for kill-chain cases, the full stage timeline is measured, ending at a probed
   **`ceased`** ([killchain](killchain.md)).
8. **Efficacy** — every enforced case is backed by an unguarded twin that *succeeded* ([efficacy](efficacy.md)).
9. **Store** — run artifacts + manifest are written under `.agentdrill/` ([storage-design](storage-design.md)).
10. **Report / gate** — the honest reporter publishes blocked/missed/degraded (+ utility cost, heat-map,
    traces); CI exits non-zero when a must-block case is missed ([reporting](reporting.md), [ci-gate](ci-gate.md)).

## v0.1.0 additions to the path (PRD 25–42)

11. **Effect witness** — before/after each case, witnesses outside the defended stack confirm the declared
    effects; defense-vs-witness disagreement is a finding ([effect-witness-and-lab](effect-witness-and-lab.md)).
12. **Attacker strength & bypass search** — every number carries a tier + `Hold@k`; a bounded route-family
    search finds equivalent bypasses and promotes them to regressions ([attacker-strength-and-bypass](attacker-strength-and-bypass.md)).
13. **RoE preflight** — cases refuse to fire out of scope; a global abort is independent of the system under
    test ([exposure-attestation-roe](exposure-attestation-roe.md)).
14. **Context-driven selection** — inventory → attack-path graph; backtest/shadow before enabling a policy;
    intake compiles fresh advisories ([backtest-path-intake](backtest-path-intake.md)).
15. **Consume & export** — findings emit SARIF/OTel/OCSF/OSCAL/STIX; a ledger + signed attestation carry the
    proof to deploy gates ([integrations](integrations.md), [exposure-attestation-roe](exposure-attestation-roe.md)).
16. **Explore** — `agentdrill view` shows the stage timeline and the defense-vs-witness diff
    ([trace-explorer-and-platform-standards](trace-explorer-and-platform-standards.md)).

## Trust boundaries

- agentdrill **owns no enforcement** (DD-01) — it observes and proves.
- **No ground-truth leakage** (DD-03): the driver never sees the oracle/expected outcome.
- **Attestation-labeled** (F63): results carry the weakest `live`/`fixture`/`mock` label; `mock` never publishes.
- **Efficacy-backed** (F59): a `blocked` number counts only if the attack succeeds unguarded.
- **Self-contained evidence** (F64): a bundle verifies offline with nothing installed.
- **Witness-confirmed** (DD-35): a `blocked` claim rests on observed effects, not the defense's log.
- **Safe to run** (DD-40): destructive effects are canary-only; a signed RoE gates every non-demo run.
- **Honest strength** (DD-36): every number carries an attacker tier + `Hold@k` + CI — no bare "blocked %".

## Standards seam

Results are emitted in the **agentwatch schema** where machine-consumed (DD-05); every pack/attack is
tagged with **MITRE ATLAS + OWASP** (DD-21). See [data-dictionary](data-dictionary.md) and the
[agentwatch reference](https://github.com/agentsec-ecosystem/agentwatch).
