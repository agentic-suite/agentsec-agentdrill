# agentdrill v0.1.0 — Architecture (components)

**Status:** draft (design intent).

## Components

| Component | Responsibility | Design |
|---|---|---|
| Pack loader/validator | parse + strictly validate packs; path-safety | [pack-format](../design/pack-format.md) |
| Runner | execute cases; artifacts; timeouts; non-abort | [runner](../design/runner.md) |
| Driver adapters | deliver the attack (subprocess/python/http/harness) | [adapter-contract](../design/adapter-contract.md) |
| Target adapters | drive the deployed stack; read decisions/evidence | [adapter-contract](../design/adapter-contract.md) |
| Recon | probe exposed surface; bind cases | [data-dictionary](../design/data-dictionary.md) |
| Oracle engine | blocked/missed/degraded; dimensions; taxonomy | [oracle-engine](../design/oracle-engine.md) |
| Evidence reader | agentwatch events; expected-telemetry | [evidence-integration](../design/evidence-integration.md) |
| Efficacy runner | unguarded control group | [efficacy](../design/efficacy.md) |
| Kill-chain timer | stage timestamps + cessation probe | [killchain](../design/killchain.md) |
| Comparison/attribution | golden results; change detection | [comparison](../design/comparison.md) |
| Reporter/benchmark | honest tables; heat-map; trends | [reporting](../design/reporting.md) |
| CI surface | exit codes; gating; trigger/CART | [ci-gate](../design/ci-gate.md) |
| Registry | signed, semver'd packs; trust | [PRD 17](../prd/17-pack-registry-and-governance.md) |
| Verifier | offline bundle verification | [privacy-data-handling](../design/privacy-data-handling.md) |

## Data flow

`pack → validate → recon → driver → target → evidence → oracle → (efficacy, kill-time) → result → store →
report → CI gate`.

## Trust boundaries

- agentdrill owns no enforcement; it observes and proves.
- No ground-truth leakage.
- Attestation-labeled; efficacy-backed; signed; independently verifiable.

## Seams

agentwatch (evidence) · agentpolicy/policyweave (policy, budgets) · the enforcers (targets) · agentcomply
(compliance evidence).
