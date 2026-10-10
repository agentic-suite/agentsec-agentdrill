# Plans

| Document | Scope |
|---|---|
| [v0.1.0 execution plan](v0.1.0-execution-plan.md) | Strategy, sequencing, and the port rule (milestones live in the WBS) |
| [testing-and-parity-strategy.md](testing-and-parity-strategy.md) | Test layers, gates, and the absorption/parity suite |
| [M0 port execution plan](m0-port-execution-plan.md) | Bulk-port the predecessor codebase and get the ported suite green |
| [M1 foundation execution plan](m1-foundation-execution-plan.md) | Identity, CLI, configuration, CI, packaging |
| [M2+M3 packs & runner execution plan](m2-m3-packs-runner-execution-plan.md) | Attack-pack format, loader/validator, catalog, runner |
| [M4 driver adapters](m4-driver-adapters-execution-plan.md) | Driver contract, subprocess/python/http, per-harness drivers |
| [M5 targets & recon](m5-targets-recon-execution-plan.md) | Deployed-stack targets, recon/scoping, attestation hooks |
| [M6 oracle engine](m6-oracle-engine-execution-plan.md) | Deterministic/judge/hybrid oracles, dimensions, taxonomy |
| [M7 evidence integration](m7-evidence-integration-execution-plan.md) | agentwatch schema read, evidence binding, expected telemetry |
| [M8 determinism](m8-determinism-execution-plan.md) | Fixtures/ToolStub, run manifest, pins, contamination |
| [M9 comparison & attribution](m9-comparison-attribution-execution-plan.md) | Golden results, comparison, change detection, attribution |
| [M10 benchmark](m10-benchmark-execution-plan.md) | Honest reporter, public benchmark, heat-map, trends |
| [M11 CI gate](m11-ci-gate-execution-plan.md) | Exit codes, gating, trigger/CART, watch, diff-aware |
| [M12 kill-chain](m12-killchain-execution-plan.md) | Stage timing, cessation probe, findings, budgets |
| [M13 efficacy](m13-efficacy-execution-plan.md) | Unguarded control group, utility-under-attack, cleanup |
| [M14 evasion & meta](m14-evasion-meta-execution-plan.md) | Evasion pack, drill-the-drill, dark holdout |
| [M15 chains & adaptive](m15-chains-adaptive-execution-plan.md) | Chain structure, break point, bounded adaptive orchestration |
| [M16 registry & governance](m16-registry-governance-execution-plan.md) | Signed registry, trust levels, contribution flow |
| [M17 interop & compliance](m17-interop-compliance-execution-plan.md) | Importers, tagging, compliance reporting, submission |
| [M18 lifecycle](m18-lifecycle-execution-plan.md) | Intake, fix-validation, seams, attestation, verifier, quickstart |
| [M19 oracle credibility](m19-oracle-credibility-execution-plan.md) | Versioning, calibration corpus, judge drift, adjudication |
| [M20 frontier & DX](m20-frontier-dx-execution-plan.md) | Pack diff/selection, dry-run, templates, MCP surface, fleet |
| [M21 absorption & gap closure](m21-absorption-closure-execution-plan.md) | Absorption ledger, gap closure G1–G14, parity gate |
| [M22 hardening](m22-hardening-execution-plan.md) | NFRs, fault injection, sandbox, audit integrity |
| [M23 field tests](m23-field-tests-execution-plan.md) | Run CUJ-1..27 end to end; publish the report |
| [M24 release readiness](m24-release-readiness-execution-plan.md) | Release tooling, audit, SBOM, tag v0.1.0, predecessor private |

> **Build risks** live in [PRD 08 — Risks](../../prd/08-risks.md). Milestones, work items, and exit gates
> live in the [WBS](../wbs/v0.1.0/wbs-v0.1.0-index.md). Every milestone carries the five standing gate
> items **`.T` tests · `.C` coverage · `.L` lint/types · `.CR` code review · `.D` docs**.
