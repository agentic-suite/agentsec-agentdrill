# Reference

Normative reference for agentdrill — CLI, formats, compatibility, errors, policies. Design intent until the
build lands (v0.1.0 planned).

| Document | Scope | Status |
|---|---|---|
| [cli-reference.md](cli-reference.md) | Command surface + output/exit codes | draft |
| [pack-format-spec.md](pack-format-spec.md) | Normative attack-pack schema | **normative (M2)** |
| [pack-catalog.md](pack-catalog.md) | The v0.1.0 pack catalog + fixtures | **normative (M2)** |
| [run-artifact-spec.md](run-artifact-spec.md) | Run / per-case artifact schema | **normative (M3)** |
| [failure-taxonomy.md](failure-taxonomy.md) | Outcomes, dimensions, oracle catalog, divergence | **normative (M6)** |
| [evidence-and-telemetry.md](evidence-and-telemetry.md) | agentwatch reader, binding, telemetry-gap, coverage | **normative (M7)** |
| [determinism-methodology.md](determinism-methodology.md) | How each oracle decides blocked/missed/degraded; pins, fixtures, contamination | **normative (M8)** |
| [reporting-and-statistics.md](reporting-and-statistics.md) | Report formats, honesty rules, statistics policy, benchmark schema | **normative (M10)** |
| [ci-integration.md](ci-integration.md) | Exit codes, gating, CI output, trigger/watch/diff-aware, annotations, schedule | **normative (M11)** |
| [kill-chain-verification.md](kill-chain-verification.md) | Stage model, cessation probe, timing policy, findings, budgets | **normative (M12)** |
| [efficacy-and-utility.md](efficacy-and-utility.md) | Unguarded control group, inert flagging, utility-under-attack, cleanup | **normative (M13)** |
| [self-attack-and-meta-verification.md](self-attack-and-meta-verification.md) | Evasion pack, drill-the-drill checks, dark holdout, cadence, hidden case | **normative (M14)** |
| [chains-and-adaptive.md](chains-and-adaptive.md) | Chain structure, break point, bounded adaptive orchestration, review gate | **normative (M15)** |
| [registry-and-governance.md](registry-and-governance.md) | Signed registry index, verified publishers, trust levels, contribution flow, governance | **normative (M16)** |
| [interop-and-compliance.md](interop-and-compliance.md) | Interop importers, ATLAS/OWASP tagging, adversary profiles, compliance mapping, submission, competitor benchmark | **normative (M17)** |
| [lifecycle.md](lifecycle.md) | Intake SLA, fix-validation, seams, attestation, verifier, evidence privacy, quickstart, policy suggestion | **normative (M18)** |
| [oracle-credibility.md](oracle-credibility.md) | Oracle versioning, calibration corpus, judge drift, battery, labels, disputes | **normative (M19)** |
| [frontier-dx.md](frontier-dx.md) | Pack diff, dry-run, templates, CI-matrix, assertions, provenance, MCP surface, fleet | **normative (M20)** |
| [parity-and-gap-closure.md](parity-and-gap-closure.md) | Absorption ledger, gap closure G1–G14, parity gate, retention | **normative (M21)** |
| [hardening.md](hardening.md) | Performance, faults, sandbox, audit chain, portability, cost, observability | **normative (M22)** |
| [effect-witness-and-lab.md](effect-witness-and-lab.md) | Effect witnesses, two-oracle verdict, Adversary Lab | **normative (M23)** |
| [attacker-strength-and-bypass.md](attacker-strength-and-bypass.md) | Attacker tiers, Hold@k/ASR@k, pressure curves, route-family bypass search | **normative (M24)** |
| [byod-and-neutral-head-to-head.md](byod-and-neutral-head-to-head.md) | Defense contract/SDK/kit, Defense Zoo, neutral head-to-head, neutrality rules | **normative (M25)** |
| [integrations.md](integrations.md) | Output-format matrix, integration guide, deep-link contract, imports, SIEM validation | **normative (M26)** |
| [backtest-path-intake.md](backtest-path-intake.md) | Trace backtest/shadow, capability graph + path status, incident-to-pack compiler | **normative (M27)** |
| [exposure-attestation-roe.md](exposure-attestation-roe.md) | Ledger + waivers, drill attestation predicate, rules of engagement + interlocks | **normative (M28)** |
| [detonation-breakit-frontier.md](detonation-breakit-frontier.md) | Extension detonation, Break-It program, ASI frontier classes | **normative (M29)** |
| [trace-explorer-and-platform-standards.md](trace-explorer-and-platform-standards.md) | Viewer guide, compatibility matrix (L0–L4, AWC), standards/claims | **normative (M30)** |
| [adapter-api.md](adapter-api.md) | Driver + target adapter API | **drivers normative (M4)** |
| [custom-adapter-guide.md](custom-adapter-guide.md) | Build + register a custom driver | **normative (M4)** |
| [compatibility.md](compatibility.md) | Harness × version compatibility | draft |
| [errors.md](errors.md) | Error contract + exit codes | draft |
| [known-limitations.md](known-limitations.md) | Honest limitations | draft |
| [versioning-policy.md](versioning-policy.md) | Semver + pack-format policy | draft |
| [backwards-compatibility-policy.md](backwards-compatibility-policy.md) | What may change, when | draft |
| [framework-recipes.md](framework-recipes.md) | Tier-2 framework recipes | draft |
| [standards-participation.md](standards-participation.md) | ATLAS/OWASP/NIST/CAISI participation | draft |
| [tech-stack.md](tech-stack.md) | Runtime + tooling | draft |

> The **pack-format** contract is drafted in [../design/pack-format.md](../design/pack-format.md) and is
> **normative** for the schema/loader/resolution/hashing (M2); runtime semantics become normative with their
> milestones. The **agentwatch record + security-event schema** is an external contract — see
> [agentwatch](https://github.com/agentic-suite/agentsec-agentwatch).
