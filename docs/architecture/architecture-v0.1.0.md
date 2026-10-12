# agentdrill v0.1.0 — Architecture (components)

**Status:** draft (design intent).

> **Implementation status — M0 (port).** The component tree below was **ported from the predecessor eval
> harness at M0** and the package renamed to `agentdrill` (provenance:
> [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md); plan: [M0 port](../plans/m0-port-execution-plan.md);
> setup/layout: [development](../development.md)). The components are **present in code and tested**; the
> re-pointing from *agent-quality grading* to *defense proof* happens across M2–M30.

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

### v0.1.0 additions (PRD 25–42)

| Component | Responsibility | Design |
|---|---|---|
| Effect witness | adjudicate by observed effects outside the defended stack | [effect-witness-and-lab](../design/effect-witness-and-lab.md) |
| Adversary lab | hostile counterparties + sinks (loopback, deterministic) | [effect-witness-and-lab](../design/effect-witness-and-lab.md) |
| Attacker-strength & bypass search | tiers, `Hold@k`, pressure curves; route-family search | [attacker-strength-and-bypass](../design/attacker-strength-and-bypass.md) |
| Defense contract / BYOD | drill any defense; neutral head-to-head | [byod-and-neutral-head-to-head](../design/byod-and-neutral-head-to-head.md) |
| Integrations | SARIF/OTel/OCSF/OSCAL/STIX out; imports; SIEM validation | [integrations](../design/integrations.md) |
| Backtest/shadow, attack-path, intake | real-history replay; reachability graph; incident compiler | [backtest-path-intake](../design/backtest-path-intake.md) |
| Ledger, attestation, RoE | exposure lifecycle/waivers; signed proof; safe-fire | [exposure-attestation-roe](../design/exposure-attestation-roe.md) |
| Detonation, Break-It, frontier classes | dynamic extension analysis; crowd bypass; ASI gap classes | [detonation-breakit-frontier](../design/detonation-breakit-frontier.md) |
| Trace explorer, platform matrix, standards | local viewer; L0–L4 compatibility; claims vocabulary | [trace-explorer-and-platform-standards](../design/trace-explorer-and-platform-standards.md) |

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
